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
    from backend.app.services.trust_score import TrustScoreCalculatorService
except ImportError:
    from tests.test_retrieval_accuracy_15 import TEST_CASES
    from app.services.pipeline import VerificationPipeline
    from app.schemas.verification import VerificationRequest
    from app.services.trust_score import TrustScoreCalculatorService


async def evaluate_end_to_end():
    print("=" * 115)
    print("TRUSTGATE-AI 15-CASE END-TO-END PIPELINE EVALUATION")
    print("Full Flow: Question -> Generation -> Claim Extraction -> Classification -> Hybrid Retrieval -> Gemma Verifier -> Trust Score")
    print("=" * 115)

    pipeline = VerificationPipeline()
    calculator = TrustScoreCalculatorService()

    case_results = []
    total_start_time = time.time()

    completed_count = 0
    failed_count = 0

    total_trust_score = 0.0
    total_hallucination_pct = 0.0
    total_claims_count = 0
    total_supported = 0
    total_insufficient = 0
    total_contradicted = 0

    for item in TEST_CASES:
        case_num = item["id"]
        question = item["question"]
        expected_sec = item.get("expected_section", "")

        print(f"\n--- CASE {case_num:02d} ---")
        print(f"Question: {question}")

        case_start_time = time.time()
        status = "SUCCESS"
        error_msg = None

        try:
            req = VerificationRequest(question=question)
            # Run end-to-end pipeline with per-case timeout of 240 seconds
            report = await asyncio.wait_for(pipeline.run(req), timeout=240.0)
            elapsed_case = time.time() - case_start_time

            response_text = report.response
            trust_score = float(report.trust_score)
            hallucination_pct = calculator.calculate_hallucination_percentage(report.claims)

            claims_data = []
            c_sup = 0
            c_ins = 0
            c_con = 0

            for claim in report.claims:
                v_str = claim.verdict.value if hasattr(claim.verdict, "value") else str(claim.verdict)
                if v_str == "SUPPORTED":
                    c_sup += 1
                elif v_str == "CONTRADICTED":
                    c_con += 1
                else:
                    c_ins += 1

                claims_data.append({
                    "id": claim.id,
                    "text": claim.text,
                    "verdict": v_str,
                    "evidence": claim.evidence or []
                })

            completed_count += 1
            total_trust_score += trust_score
            total_hallucination_pct += hallucination_pct
            total_claims_count += len(report.claims)
            total_supported += c_sup
            total_insufficient += c_ins
            total_contradicted += c_con

            print(f"Generated Answer: {response_text[:120]}...")
            print(f"Claims Extracted ({len(report.claims)}):")
            for c in report.claims:
                v_str = c.verdict.value if hasattr(c.verdict, "value") else str(c.verdict)
                print(f"  - [{v_str}] {c.text}")
            print(f"Trust Score: {trust_score:.2f} / 100")
            print(f"Hallucination %: {hallucination_pct:.2f}%")
            print(f"Verdict Summary: SUPPORTED = {c_sup} | INSUFFICIENT = {c_ins} | CONTRADICTED = {c_con}")
            print(f"Case Time: {elapsed_case:.2f}s")

            case_results.append({
                "case_number": case_num,
                "expected_section": str(expected_sec),
                "question": question,
                "generated_answer": response_text,
                "claims": claims_data,
                "trust_score": trust_score,
                "hallucination_percentage": hallucination_pct,
                "execution_time_seconds": round(elapsed_case, 2),
                "status": "SUCCESS",
                "error": None
            })

        except Exception as e:
            elapsed_case = time.time() - case_start_time
            failed_count += 1
            error_msg = str(e)
            print(f"ERROR processing Case {case_num:02d}: {error_msg}")
            print(f"Case Time: {elapsed_case:.2f}s")

            case_results.append({
                "case_number": case_num,
                "expected_section": str(expected_sec),
                "question": question,
                "generated_answer": "",
                "claims": [],
                "trust_score": 0.0,
                "hallucination_percentage": 0.0,
                "execution_time_seconds": round(elapsed_case, 2),
                "status": "ERROR",
                "error": error_msg
            })

    total_elapsed = time.time() - total_start_time

    avg_trust_score = (total_trust_score / completed_count) if completed_count > 0 else 0.0
    avg_hallucination_pct = (total_hallucination_pct / completed_count) if completed_count > 0 else 0.0
    avg_time_per_case = (total_elapsed / completed_count) if completed_count > 0 else 0.0

    print("\n" + "=" * 115)
    print("OVERALL END-TO-END EVALUATION SUMMARY")
    print("=" * 115)
    print(f"Total Cases: {len(TEST_CASES)}")
    print(f"Successfully Completed: {completed_count}")
    print(f"Failed / Timed Out: {failed_count}")
    print(f"Average Trust Score (Completed): {avg_trust_score:.2f} / 100")
    print(f"Average Hallucination % (Completed): {avg_hallucination_pct:.2f}%")
    print(f"Total Claims Processed: {total_claims_count}")
    print(f"Total SUPPORTED Claims: {total_supported}")
    print(f"Total INSUFFICIENT Claims: {total_insufficient}")
    print(f"Total CONTRADICTED Claims: {total_contradicted}")
    print(f"Total Execution Time: {total_elapsed:.2f} seconds ({total_elapsed/60:.2f} mins)")
    print(f"Average Time per Completed Case: {avg_time_per_case:.2f} seconds")
    print("=" * 115)

    out_path = project_root / "backend" / "tests" / "end_to_end_15_results.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(case_results, f, indent=2)
    print(f"\nSaved detailed JSON results to: {out_path}")


def main():
    asyncio.run(evaluate_end_to_end())


if __name__ == "__main__":
    main()
