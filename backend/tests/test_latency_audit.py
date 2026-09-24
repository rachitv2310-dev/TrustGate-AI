import sys
import json
import time
import asyncio
from pathlib import Path
from typing import List, Dict, Any

# Ensure project root is in sys.path
project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from backend.tests.test_retrieval_accuracy_15 import TEST_CASES
    from backend.app.services.pipeline import VerificationPipeline
    from backend.app.schemas.verification import VerificationRequest
    from backend.services import claim_classification_service
except ImportError:
    from tests.test_retrieval_accuracy_15 import TEST_CASES
    from app.services.pipeline import VerificationPipeline
    from app.schemas.verification import VerificationRequest
    import claim_classification_service


async def run_latency_audit():
    print("=" * 115)
    print("TRUSTGATE-AI LATENCY AUDIT — STAGE-BY-STAGE PERFORMANCE MEASUREMENT")
    print("Executing current real production pipeline over 15 evaluation cases...")
    print("=" * 115)

    case_results = []
    total_gemma_call_durations = []
    
    stage_totals = {
        "generation": 0.0,
        "claim_extraction": 0.0,
        "classification": 0.0,
        "retrieval": 0.0,
        "gemma_verification": 0.0,
        "trust_score": 0.0,
        "other": 0.0
    }

    total_claims = 0
    total_verifier_calls = 0
    completed_cases = 0
    failed_cases = 0

    overall_start_time = time.time()

    for item in TEST_CASES:
        case_num = item["id"]
        question = item["question"]

        print(f"\n--- CASE {case_num:02d}: '{question[:50]}...' ---")

        # Create fresh pipeline instance per case
        pipeline = VerificationPipeline()

        # Capture active model configurations and backend settings
        gen_model = getattr(pipeline, "generation_model", "unknown")
        ext_model = getattr(pipeline.claim_extractor, "model", "unknown")
        ver_model = getattr(pipeline.verifier, "model", "unknown")

        hybrid_retriever = getattr(pipeline.retriever, "hybrid_retriever", None)
        active_backend = getattr(hybrid_retriever, "semantic_backend", "tfidf") if hybrid_retriever else "unknown"

        # Per-case timing accumulators
        case_stage_times = {
            "generation": 0.0,
            "claim_extraction": 0.0,
            "classification": 0.0,
            "retrieval": 0.0,
            "gemma_verification": 0.0,
            "trust_score": 0.0,
            "other": 0.0
        }

        gemma_call_durations = []
        claims_entering_retrieval_count = 0

        # Monkey-patch Step 1: Generation LLM
        orig_gen = pipeline.ollama_service.generate
        def timed_generate(prompt, model=None):
            t0 = time.time()
            res = orig_gen(prompt=prompt, model=model)
            case_stage_times["generation"] += (time.time() - t0)
            return res
        pipeline.ollama_service.generate = timed_generate

        # Monkey-patch Step 2: Atomic Claim Extraction
        orig_extract = pipeline.claim_extractor.extract_claims
        def timed_extract(text):
            t0 = time.time()
            res = orig_extract(text)
            case_stage_times["claim_extraction"] += (time.time() - t0)
            return res
        pipeline.claim_extractor.extract_claims = timed_extract

        # Monkey-patch Classification function
        orig_classify = claim_classification_service.classify_claim
        def timed_classify(text):
            t0 = time.time()
            res = orig_classify(text)
            case_stage_times["classification"] += (time.time() - t0)
            return res
        # Patch local reference inside module scope
        sys.modules[pipeline.run.__module__].classify_claim = timed_classify

        # Monkey-patch Step 3: Retrieval
        orig_retrieve = pipeline.retriever.retrieve
        def timed_retrieve(query, top_k=3, candidate_k=50):
            nonlocal claims_entering_retrieval_count
            claims_entering_retrieval_count += 1
            t0 = time.time()
            res = orig_retrieve(query, top_k=top_k, candidate_k=candidate_k)
            case_stage_times["retrieval"] += (time.time() - t0)
            return res
        pipeline.retriever.retrieve = timed_retrieve

        # Monkey-patch Step 3: Stance Verification (Gemma)
        orig_verify = pipeline.verifier.verify_claim
        def timed_verify(claim, evidence):
            t0 = time.time()
            res = orig_verify(claim, evidence)
            dur = time.time() - t0
            case_stage_times["gemma_verification"] += dur
            gemma_call_durations.append(dur)
            total_gemma_call_durations.append(dur)
            return res
        pipeline.verifier.verify_claim = timed_verify

        # Monkey-patch Step 4: Trust Score Calculation
        orig_calc_score = pipeline.trust_calculator.calculate_score
        orig_calc_hall = pipeline.trust_calculator.calculate_hallucination_percentage
        def timed_calc_score(claims):
            t0 = time.time()
            res = orig_calc_score(claims)
            case_stage_times["trust_score"] += (time.time() - t0)
            return res
        def timed_calc_hall(claims):
            t0 = time.time()
            res = orig_calc_hall(claims)
            case_stage_times["trust_score"] += (time.time() - t0)
            return res
        pipeline.trust_calculator.calculate_score = timed_calc_score
        pipeline.trust_calculator.calculate_hallucination_percentage = timed_calc_hall

        # Execute case with timeout limit
        case_start = time.time()
        status = "SUCCESS"
        error_msg = None

        try:
            req = VerificationRequest(question=question)
            report = await asyncio.wait_for(pipeline.run(req), timeout=300.0)
            total_case_time = time.time() - case_start

            # Restore original classify_claim
            sys.modules[pipeline.run.__module__].classify_claim = orig_classify

            claim_cnt = len(report.claims)
            ver_cnt = len(gemma_call_durations)

            sum_measured_stages = sum(case_stage_times.values())
            case_stage_times["other"] = max(0.0, total_case_time - sum_measured_stages)

            for stage, dt in case_stage_times.items():
                stage_totals[stage] += dt

            total_claims += claim_cnt
            total_verifier_calls += ver_cnt
            completed_cases += 1

            print(f"Total Case Time: {total_case_time:.2f}s | Claims: {claim_cnt} | Gemma Calls: {ver_cnt}")
            print(f"  [1] Generation ({gen_model}): {case_stage_times['generation']:.2f}s")
            print(f"  [2] Extraction ({ext_model}): {case_stage_times['claim_extraction']:.2f}s")
            print(f"  [3] Classification: {case_stage_times['classification']:.4f}s")
            print(f"  [4] Retrieval ({active_backend}): {case_stage_times['retrieval']:.2f}s ({claims_entering_retrieval_count} claims)")
            print(f"  [5] Gemma Verification ({ver_model}): {case_stage_times['gemma_verification']:.2f}s ({ver_cnt} calls, avg {case_stage_times['gemma_verification']/ver_cnt if ver_cnt else 0:.2f}s/call)")
            print(f"  [6] Trust Score: {case_stage_times['trust_score']:.4f}s")
            print(f"  [7] Other / Overhead: {case_stage_times['other']:.4f}s")

            case_results.append({
                "case_number": case_num,
                "question": question,
                "total_case_time_seconds": round(total_case_time, 2),
                "claim_count": claim_cnt,
                "verifier_call_count": ver_cnt,
                "models": {
                    "generation": gen_model,
                    "claim_extraction": ext_model,
                    "verification": ver_model
                },
                "retrieval_backend": active_backend,
                "stage_timings_seconds": {k: round(v, 4) for k, v in case_stage_times.items()},
                "gemma_call_durations_seconds": [round(d, 2) for d in gemma_call_durations],
                "status": "SUCCESS",
                "error": None
            })

        except Exception as e:
            total_case_time = time.time() - case_start
            sys.modules[pipeline.run.__module__].classify_claim = orig_classify
            failed_cases += 1
            error_msg = str(e)
            print(f"ERROR processing Case {case_num:02d}: {error_msg} (Time: {total_case_time:.2f}s)")

            case_results.append({
                "case_number": case_num,
                "question": question,
                "total_case_time_seconds": round(total_case_time, 2),
                "claim_count": 0,
                "verifier_call_count": 0,
                "models": {
                    "generation": gen_model,
                    "claim_extraction": ext_model,
                    "verification": ver_model
                },
                "retrieval_backend": active_backend,
                "stage_timings_seconds": {k: round(v, 4) for k, v in case_stage_times.items()},
                "gemma_call_durations_seconds": [],
                "status": "ERROR",
                "error": error_msg
            })

    total_eval_time = time.time() - overall_start_time
    total_measured_time = sum(stage_totals.values())

    stage_percentages = {
        stage: (t / total_measured_time * 100.0) if total_measured_time > 0 else 0.0
        for stage, t in stage_totals.items()
    }

    avg_case_time = (total_eval_time / completed_cases) if completed_cases > 0 else 0.0
    avg_claims_per_case = (total_claims / completed_cases) if completed_cases > 0 else 0.0
    avg_verifier_calls = (total_verifier_calls / completed_cases) if completed_cases > 0 else 0.0

    avg_gemma_call_time = (sum(total_gemma_call_durations) / len(total_gemma_call_durations)) if total_gemma_call_durations else 0.0
    max_gemma_call_time = max(total_gemma_call_durations) if total_gemma_call_durations else 0.0
    min_gemma_call_time = min(total_gemma_call_durations) if total_gemma_call_durations else 0.0

    # Print Summary Table
    print("\n" + "=" * 115)
    print("SUMMARY STAGE-BY-STAGE LATENCY TABLE")
    print("=" * 115)
    print(f"{'Stage':<30} | {'Total Time (s)':<15} | {'Avg/Case (s)':<15} | {'% of Total':<12}")
    print("-" * 115)

    stage_display_names = {
        "generation": "Generation LLM",
        "claim_extraction": "Atomic Claim Extraction",
        "classification": "Claim Classification",
        "retrieval": "Hybrid Evidence Retrieval",
        "gemma_verification": "Gemma Verification",
        "trust_score": "Trust Score Calculation",
        "other": "Other / Overhead"
    }

    for stage, t_val in stage_totals.items():
        disp_name = stage_display_names.get(stage, stage)
        avg_val = (t_val / completed_cases) if completed_cases > 0 else 0.0
        pct_val = stage_percentages[stage]
        print(f"{disp_name:<30} | {t_val:<15.2f} | {avg_val:<15.2f} | {pct_val:<12.1f}%")

    print("-" * 115)
    print(f"Total Evaluation Time: {total_eval_time:.2f} seconds ({total_eval_time/60:.2f} mins)")
    print(f"Average Case Time: {avg_case_time:.2f} seconds")
    print(f"Average Claims / Case: {avg_claims_per_case:.2f}")
    print(f"Total Verifier Calls: {total_verifier_calls}")
    print(f"Average Verifier Calls / Case: {avg_verifier_calls:.2f}")
    print(f"Average Gemma Call Time: {avg_gemma_call_time:.2f} seconds")
    print(f"Maximum Gemma Call Time: {max_gemma_call_time:.2f} seconds")
    print(f"Minimum Gemma Call Time: {min_gemma_call_time:.2f} seconds")

    # Ranked Bottlenecks
    ranked_stages = sorted(stage_totals.items(), key=lambda x: x[1], reverse=True)

    print("\n" + "=" * 115)
    print("RANKED PERFORMANCE BOTTLENECKS (MEASURED DATA ONLY)")
    print("=" * 115)
    
    ranked_list_json = []
    for rank, (stage, t_val) in enumerate(ranked_stages, 1):
        disp_name = stage_display_names.get(stage, stage)
        pct_val = stage_percentages[stage]
        avg_val = (t_val / completed_cases) if completed_cases > 0 else 0.0
        print(f"{rank}. {disp_name} — {pct_val:.1f}% of total time (Total: {t_val:.2f}s, Avg/Case: {avg_val:.2f}s)")
        ranked_list_json.append({
            "rank": rank,
            "stage": disp_name,
            "percentage": round(pct_val, 1),
            "total_seconds": round(t_val, 2),
            "avg_case_seconds": round(avg_val, 2)
        })

    print("=" * 115)

    # Save latency audit JSON
    json_output = {
        "summary": {
            "total_evaluation_time_seconds": round(total_eval_time, 2),
            "average_case_time_seconds": round(avg_case_time, 2),
            "total_cases": len(TEST_CASES),
            "completed_cases": completed_cases,
            "failed_cases": failed_cases,
            "total_claims": total_claims,
            "average_claims_per_case": round(avg_claims_per_case, 2),
            "total_verifier_calls": total_verifier_calls,
            "average_verifier_calls_per_case": round(avg_verifier_calls, 2),
            "gemma_call_stats": {
                "average_seconds": round(avg_gemma_call_time, 2),
                "maximum_seconds": round(max_gemma_call_time, 2),
                "minimum_seconds": round(min_gemma_call_time, 2)
            },
            "stage_totals_seconds": {k: round(v, 2) for k, v in stage_totals.items()},
            "stage_percentages": {k: round(v, 1) for k, v in stage_percentages.items()},
            "ranked_bottlenecks": ranked_list_json
        },
        "cases": case_results
    }

    out_path = project_root / "backend" / "tests" / "latency_audit_results.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(json_output, f, indent=2)
    print(f"\nSaved detailed latency audit JSON to: {out_path}")


def main():
    asyncio.run(run_latency_audit())


if __name__ == "__main__":
    main()
