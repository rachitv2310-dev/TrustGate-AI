import sys
import time
from pathlib import Path
from typing import List, Dict, Any

# Ensure project root is in sys.path
project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from backend.app.schemas.claim import Claim, VerificationVerdict
    from backend.app.services.verifier import ClaimVerifierService
except ImportError:
    from app.schemas.claim import Claim, VerificationVerdict
    from app.services.verifier import ClaimVerifierService


TEST_CASES: List[Dict[str, Any]] = [
    {
        "id": 1,
        "concept": "Theft (Section 303)",
        "claim": "Theft is defined under Section 303 of the Bharatiya Nyaya Sanhita, 2023 as dishonestly taking movable property out of the possession of any person without consent.",
        "expected_verdict": VerificationVerdict.SUPPORTED,
        "evidence": [
            {
                "section_number": "303",
                "title": "Theft",
                "evidence_text": "303. Theft.—(1) Whoever, intending to take dishonestly any movable property out of the possession of any person without that person's consent, moves that property in order to such taking, is said to commit theft."
            }
        ]
    },
    {
        "id": 2,
        "concept": "Robbery (Section 309)",
        "claim": "Robbery is defined under Section 304 of the Bharatiya Nyaya Sanhita, 2023.",
        "expected_verdict": VerificationVerdict.CONTRADICTED,
        "evidence": [
            {
                "section_number": "309",
                "title": "Robbery",
                "evidence_text": "309. Robbery.—In all robbery there is either theft or extortion. Theft is robbery if, in order to the committing of the theft, the offender voluntarily causes death or hurt."
            }
        ]
    },
    {
        "id": 3,
        "concept": "Theft vs Robbery (Section 309)",
        "claim": "Theft becomes robbery under Section 309 of BNS, which carries a mandatory minimum fine of 50,000 rupees.",
        "expected_verdict": VerificationVerdict.INSUFFICIENT,
        "evidence": [
            {
                "section_number": "309",
                "title": "Robbery",
                "evidence_text": "309. Robbery.—In all robbery there is either theft or extortion. Theft is robbery if, in order to the committing of the theft, or in committing the theft, or in carrying away property obtained by theft, the offender voluntarily causes death or hurt or wrongful restraint."
            }
        ]
    },
    {
        "id": 4,
        "concept": "Dacoity (Section 310)",
        "claim": "Dacoity under Section 310 of Bharatiya Nyaya Sanhita 2023 requires five or more persons conjointly committing robbery.",
        "expected_verdict": VerificationVerdict.SUPPORTED,
        "evidence": [
            {
                "section_number": "310",
                "title": "Dacoity",
                "evidence_text": "310. Dacoity.—When five or more persons conjointly commit or attempt to commit a robbery, or where the whole number of persons conjointly committing or attempting to commit a robbery, and persons present and aiding such commission or attempt, amount to five or more, every person so committing, attempting or aiding, is said to commit dacoity."
            }
        ]
    },
    {
        "id": 5,
        "concept": "Punishment for Dacoity (Section 310)",
        "claim": "Under Section 310 of BNS 2023, the punishment for dacoity is imprisonment for a maximum of 6 months.",
        "expected_verdict": VerificationVerdict.CONTRADICTED,
        "evidence": [
            {
                "section_number": "310",
                "title": "Dacoity",
                "evidence_text": "310. Dacoity.—(2) Whoever commits dacoity shall be punished with imprisonment for life, or with rigorous imprisonment for a term which may extend to ten years, and shall also be liable to fine."
            }
        ]
    },
    {
        "id": 6,
        "concept": "Criminal Breach of Trust (Section 316)",
        "claim": "Criminal breach of trust under Section 316 of BNS requires a written contract signed before a magistrate.",
        "expected_verdict": VerificationVerdict.INSUFFICIENT,
        "evidence": [
            {
                "section_number": "316",
                "title": "Criminal breach of trust",
                "evidence_text": "316. Criminal breach of trust.—(1) Whoever, being in any manner entrusted with property, or with any dominion over property, dishonestly misappropriates or converts to his own use that property, or dishonestly uses or disposes of that property in violation of any direction of law prescribing the mode in which such trust is to be discharged, commits criminal breach of trust."
            }
        ]
    },
    {
        "id": 7,
        "concept": "Cheating (Section 318)",
        "claim": "Cheating is defined under Section 318 of the Bharatiya Nyaya Sanhita 2023.",
        "expected_verdict": VerificationVerdict.SUPPORTED,
        "evidence": [
            {
                "section_number": "318",
                "title": "Cheating",
                "evidence_text": "318. Cheating.—(1) Whoever, by deceiving any person, fraudulently or dishonestly induces the person so deceived to deliver any property to any person, or to consent that any person shall retain any property, is said to cheat."
            }
        ]
    },
    {
        "id": 8,
        "concept": "Making a False Document (Section 335)",
        "claim": "Making a false document is defined under Section 318 of the Bharatiya Nyaya Sanhita 2023.",
        "expected_verdict": VerificationVerdict.CONTRADICTED,
        "evidence": [
            {
                "section_number": "335",
                "title": "Making a false document",
                "evidence_text": "335. Making a false document.—A person is said to make a false document or false electronic record who dishonestly or fraudulently makes, signs, seals or executes a document."
            }
        ]
    },
    {
        "id": 9,
        "concept": "Forgery (Section 336)",
        "claim": "Forgery is defined under Section 336 of the Bharatiya Nyaya Sanhita 2023 as making a false document with intent to cause damage or injury.",
        "expected_verdict": VerificationVerdict.SUPPORTED,
        "evidence": [
            {
                "section_number": "336",
                "title": "Forgery",
                "evidence_text": "336. Forgery.—(1) Whoever makes any false document or false electronic record or part of a document or electronic record, with intent to cause damage or injury, to the public or to any person, or to support any claim or title, commits forgery."
            }
        ]
    },
    {
        "id": 10,
        "concept": "Punishment for Forgery (Section 336)",
        "claim": "Under Section 336 of BNS 2023, punishment for forgery includes mandatory 100 hours of community service.",
        "expected_verdict": VerificationVerdict.INSUFFICIENT,
        "evidence": [
            {
                "section_number": "336",
                "title": "Forgery",
                "evidence_text": "336. Forgery.—(2) Whoever commits forgery shall be punished with imprisonment of either description for a term which may extend to two years, or with fine, or with both."
            }
        ]
    },
    {
        "id": 11,
        "concept": "Criminal Intimidation (Section 351)",
        "claim": "Criminal intimidation is defined under Section 351 of the Bharatiya Nyaya Sanhita 2023.",
        "expected_verdict": VerificationVerdict.SUPPORTED,
        "evidence": [
            {
                "section_number": "351",
                "title": "Criminal intimidation",
                "evidence_text": "351. Criminal intimidation.—(1) Whoever threatens another with any injury to his person, reputation or property, or to the person or reputation of any one in whom that person is interested, with intent to cause alarm to that person, commits criminal intimidation."
            }
        ]
    },
    {
        "id": 12,
        "concept": "Defamation (Section 356)",
        "claim": "Defamation is defined under Section 351 of the Bharatiya Nyaya Sanhita 2023.",
        "expected_verdict": VerificationVerdict.CONTRADICTED,
        "evidence": [
            {
                "section_number": "356",
                "title": "Defamation",
                "evidence_text": "356. Defamation.—(1) Whoever, by words either spoken or intended to be read, or by signs or by visible representations, makes or publishes any imputation concerning any person intending to harm the reputation of such person, is said to defame that person."
            }
        ]
    },
    {
        "id": 13,
        "concept": "Kidnapping (Section 137)",
        "claim": "Kidnapping under Section 137 of BNS requires a ransom demand of at least one lakh rupees.",
        "expected_verdict": VerificationVerdict.INSUFFICIENT,
        "evidence": [
            {
                "section_number": "137",
                "title": "Kidnapping",
                "evidence_text": "137. Kidnapping.—(1) Kidnapping is of two kinds: kidnapping from India, and kidnapping from lawful guardianship. Whoever conveys any person beyond the limits of India without consent commits kidnapping from India."
            }
        ]
    },
    {
        "id": 14,
        "concept": "Abduction (Section 138)",
        "claim": "Abduction is defined under Section 137 of the Bharatiya Nyaya Sanhita 2023.",
        "expected_verdict": VerificationVerdict.CONTRADICTED,
        "evidence": [
            {
                "section_number": "138",
                "title": "Abduction",
                "evidence_text": "138. Abduction.—Whoever by force compels, or by any deceitful means induces, any person to go from any place, is said to abduct that person."
            }
        ]
    },
    {
        "id": 15,
        "concept": "Murder (Section 101)",
        "claim": "Murder under Section 101 of BNS requires approval from a state governor before prosecution.",
        "expected_verdict": VerificationVerdict.INSUFFICIENT,
        "evidence": [
            {
                "section_number": "101",
                "title": "Murder",
                "evidence_text": "101. Murder.—Except in the cases hereinafter excepted, culpable homicide is murder, if the act by which the death is caused is done with the intention of causing death."
            }
        ]
    }
]


def run_verification_evaluation():
    print("=" * 115)
    print("TRUSTGATE-AI 15-CASE VERIFICATION ACCURACY EVALUATION")
    print("Verification Model: Gemma3 4B (via ClaimVerifierService with deterministic guards)")
    print("Verdict Scope: SUPPORTED (5) | CONTRADICTED (5) | INSUFFICIENT (5)")
    print("=" * 115)

    start_time = time.time()
    verifier = ClaimVerifierService()

    correct_count = 0
    failures = []

    verdict_labels = [VerificationVerdict.SUPPORTED, VerificationVerdict.CONTRADICTED, VerificationVerdict.INSUFFICIENT]
    verdict_strings = [v.value for v in verdict_labels]
    confusion_counts = {exp_s: {act_s: 0 for act_s in verdict_strings} for exp_s in verdict_strings}

    print(f"{'ID':<3} | {'Concept / Case':<32} | {'Expected':<13} | {'Actual':<13} | {'Result':<6}")
    print("-" * 115)

    for case in TEST_CASES:
        case_id = case["id"]
        concept = case["concept"]
        claim_text = case["claim"]
        expected_v = case["expected_verdict"]
        evidence = case["evidence"]

        claim_obj = Claim(id=f"c_{case_id}", text=claim_text)
        actual_v = verifier.verify_claim(claim_obj, evidence)

        confusion_counts[expected_v.value][actual_v.value] += 1

        is_pass = (actual_v == expected_v)
        res_str = "PASS" if is_pass else "FAIL"

        if is_pass:
            correct_count += 1
        else:
            failures.append({
                "id": case_id,
                "concept": concept,
                "claim": claim_text,
                "expected": expected_v.value,
                "actual": actual_v.value,
            })

        print(f"{case_id:02d} | {concept:<32} | {expected_v.value:<13} | {actual_v.value:<13} | {res_str:<6}")

    elapsed_time = time.time() - start_time
    total_cases = len(TEST_CASES)
    accuracy_pct = (correct_count / total_cases) * 100

    print("-" * 115)
    print("\nVERIFICATION ACCURACY SUMMARY")
    print(f"Overall Accuracy: {correct_count}/{total_cases} = {accuracy_pct:.1f}%")
    print(f"Total Execution Time: {elapsed_time:.2f} seconds (Avg {elapsed_time/total_cases:.2f}s per claim)")

    print("\nVERDICT CONFUSION MATRIX & COUNTS:")
    print(f"{'Expected \\ Actual':<20} | {'SUPPORTED':<12} | {'CONTRADICTED':<13} | {'INSUFFICIENT':<12}")
    print("-" * 65)
    for exp_v in verdict_strings:
        sup_cnt = confusion_counts[exp_v]["SUPPORTED"]
        con_cnt = confusion_counts[exp_v]["CONTRADICTED"]
        ins_cnt = confusion_counts[exp_v]["INSUFFICIENT"]
        print(f"{exp_v:<20} | {sup_cnt:<12} | {con_cnt:<13} | {ins_cnt:<12}")

    if failures:
        print("\nFAILED TEST CASES DETAIL:")
        for f in failures:
            print(f"- Case {f['id']:02d} ({f['concept']}): Expected {f['expected']}, got {f['actual']}")
            print(f"  Claim: '{f['claim']}'\n")
    else:
        print("\nALL 15 VERIFICATION TEST CASES PASSED PERFECTLY!")


if __name__ == "__main__":
    run_verification_evaluation()
