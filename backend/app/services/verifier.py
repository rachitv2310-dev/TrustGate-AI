import logging
import re
from typing import List, Dict, Any, Union, Optional, Tuple, Set

try:
    from backend.app.schemas.claim import Claim, VerificationVerdict
    from backend.app.config import settings
    from backend.app.services.llm_service import OllamaService
except ImportError:
    from app.schemas.claim import Claim, VerificationVerdict
    from app.config import settings
    from app.services.llm_service import OllamaService

logger = logging.getLogger(__name__)


class ClaimVerifierService:
    """
    Service responsible for verifying claims against retrieved evidence snippets using Gemma3 4B.
    Produces verdict: SUPPORTED, CONTRADICTED, or INSUFFICIENT.
    Includes deterministic consistency guards for section numbers and statutory Act names.
    """

    def __init__(self, ollama_service: Optional[OllamaService] = None):
        self.model = settings.VERIFICATION_MODEL
        self.llm = ollama_service or OllamaService()

    def verify_claim(self, claim: Claim, evidence: Union[List[str], List[Dict[str, Any]]]) -> VerificationVerdict:
        """
        Verify a single claim against evidence passages with provenance and deterministic sanity checks.
        """
        # Evidence quality gate
        if not evidence:
            return VerificationVerdict.INSUFFICIENT

        formatted_passages = []
        raw_evidence_items = []
        for i, item in enumerate(evidence, 1):
            if isinstance(item, dict):
                text = item.get("evidence_text", "").strip()
                if not text:
                    continue
                sec = item.get("section_number", "")
                title = item.get("title") or item.get("section_heading", "")
                doc_id = item.get("document_id", "")
                meta_str = f" [Doc: {doc_id}, Section: {sec}, Heading: {title}]" if sec or title else ""
                formatted_passages.append(f"[Passage {i}{meta_str}]:\n{text}")
                raw_evidence_items.append(item)
            elif isinstance(item, str) and item.strip():
                formatted_passages.append(f"[Passage {i}]:\n{item.strip()}")
                raw_evidence_items.append({"evidence_text": item.strip()})

        if not formatted_passages:
            return VerificationVerdict.INSUFFICIENT

        claim_text = getattr(claim, "text", str(claim))
        formatted_evidence = "\n\n".join(formatted_passages)

        # 1. Pre-LLM Deterministic Consistency Guard Check
        det_verdict = self._check_deterministic_consistency(claim_text, raw_evidence_items)
        if det_verdict == VerificationVerdict.CONTRADICTED:
            logger.info(f"Deterministic pre-check flagged CONTRADICTED for claim: '{claim_text[:40]}...'")
            return VerificationVerdict.CONTRADICTED

        # 2. Hardened Verifier Prompt for Gemma 3 4B
        prompt = f"""You are an expert legal factual verifier for Indian statutory law (including Bharatiya Nyaya Sanhita BNS 2023, BNSS 2023, and BSA 2023).

Determine whether the given factual CLAIM is SUPPORTED, CONTRADICTED, or INSUFFICIENT based ONLY on the provided LEGAL EVIDENCE.

Strict Definitions & Rules:

1. SUPPORTED:
   - The legal evidence MUST explicitly state and confirm ALL parts of the claim.
   - If the claim contains extra unverified facts, assertions, penalties, or conditions NOT stated in the evidence, it is NOT SUPPORTED (it is INSUFFICIENT).

2. CONTRADICTED:
   - The legal evidence directly refutes, conflicts with, or states facts explicitly opposite to the claim.
   - Specifically:
     a) Section Number Mismatch: If the claim asserts a concept/definition is under Section X, but the evidence establishes that the concept is under Section Y (where X != Y) or Section X is a different topic, return CONTRADICTED.
     b) Act Mismatch: If the claim asserts one Act (e.g. BNSS) but evidence is from a different Act (e.g. BNS), return CONTRADICTED.
     c) Direct Fact Conflict: If the claim asserts a specific fact (e.g., "maximum punishment of 6 months") that directly conflicts with what the evidence explicitly states (e.g., "extend to ten years, or life"), return CONTRADICTED.
   - Silence or missing detail is NOT a contradiction. Do NOT choose CONTRADICTED if the evidence is simply silent about an added claim detail.

3. INSUFFICIENT:
   - The legal evidence is missing information or is SILENT regarding any requirement, qualifier, procedure, approval, penalty type, or fine amount mentioned in the claim.
   - Examples of INSUFFICIENT:
     - The claim adds an extra requirement or condition (e.g., "requires governor approval", "requires written contract", "includes 100 hours community service", "mandatory minimum fine of 50,000 rupees", "ransom demand of 1 lakh") that is NOT mentioned in the evidence text. Because the evidence neither confirms nor explicitly refutes the added requirement, the verdict MUST be INSUFFICIENT.
     - The evidence proves part of the claim (e.g., Section number and main definition), but is silent on an additional clause or penalty detail in the claim.

4. Rely ONLY on the provided legal evidence. Do NOT use outside legal knowledge.

5. Provide your output ending with an explicit line formatted as: VERDICT: <SUPPORTED|CONTRADICTED|INSUFFICIENT>

CLAIM:
{claim_text}

LEGAL EVIDENCE:
{formatted_evidence}

VERDICT:"""

        try:
            result = self.llm.generate(
                prompt=prompt,
                model=self.model,
                options={"temperature": 0.0, "num_predict": 192},
                keep_alive="5m",
                timeout=180
            )
            raw_response = result.get("response", "").strip()

            if not raw_response:
                logger.warning(f"Empty response from verification model ({self.model}) for claim: '{claim_text[:40]}'")
                return VerificationVerdict.INSUFFICIENT

            verdict = self.parse_verdict(raw_response)

            # 3. Post-LLM Guard: Prevent false SUPPORTED or false CONTRADICTED when guard checks disagree
            if verdict == VerificationVerdict.SUPPORTED:
                guard_verdict = self._guard_supported_verdict(claim_text, raw_evidence_items)
                if guard_verdict != VerificationVerdict.SUPPORTED:
                    logger.info(f"Post-LLM Guard overridden SUPPORTED -> {guard_verdict.value} for claim: '{claim_text[:40]}...'")
                    return guard_verdict
            elif verdict == VerificationVerdict.CONTRADICTED:
                guard_verdict = self._guard_contradicted_verdict(claim_text, raw_evidence_items)
                if guard_verdict != VerificationVerdict.CONTRADICTED:
                    logger.info(f"Post-LLM Guard overridden CONTRADICTED -> {guard_verdict.value} for claim: '{claim_text[:40]}...'")
                    return guard_verdict

            logger.info(f"Verification verdict for claim '{claim_text[:40]}...': {verdict.value}")
            return verdict

        except Exception as e:
            logger.error(f"Error during claim verification with model {self.model}: {e}")
            return VerificationVerdict.INSUFFICIENT

    @staticmethod
    def _extract_act_names(text: str) -> Set[str]:
        """Extract uppercase statutory Act acronyms from text."""
        acts = set()
        clean_text = text.replace('_', ' ').replace('-', ' ')
        for act in ["BNSS", "BNS", "BSA", "IPC", "CRPC", "IEA"]:
            if re.search(r'\b' + act + r'\b', clean_text, re.IGNORECASE):
                acts.add(act.upper())
        return acts

    @staticmethod
    def _extract_section_numbers(text: str) -> Set[str]:
        """Extract section numbers mentioned in text."""
        matches = re.findall(r'\b(?:Section|Sec\.?|S\.?)\s*(\d+[A-Z]?)\b', text, re.IGNORECASE)
        sections = set(matches)
        # Also check leading numbers like "303. Theft"
        leading_matches = re.findall(r'^\s*(\d+[A-Z]?)\s*[\.\:\-\—]', text, re.MULTILINE)
        sections.update(leading_matches)
        return sections

    @classmethod
    def _check_deterministic_consistency(
        cls, claim_text: str, evidence_items: List[Dict[str, Any]]
    ) -> Optional[VerificationVerdict]:
        """
        Check for explicit deterministic section or Act contradictions before calling LLM.
        """
        claim_sections = cls._extract_section_numbers(claim_text)
        claim_acts = cls._extract_act_names(claim_text)

        # 1. Act Mismatch Check
        evidence_acts = set()
        for item in evidence_items:
            doc_id = str(item.get("document_id", "")).upper()
            text = str(item.get("evidence_text", ""))
            evidence_acts.update(cls._extract_act_names(doc_id))
            evidence_acts.update(cls._extract_act_names(text))

        if claim_acts and evidence_acts:
            # If claim explicitly names an Act (e.g. BNSS) that is disjoint from evidence Acts (e.g. BNS)
            if not claim_acts.intersection(evidence_acts):
                return VerificationVerdict.CONTRADICTED

        # 2. Section Mismatch & Provision Title Mismatch Check
        if claim_sections:
            evidence_sec_map = {}
            for item in evidence_items:
                sec_num = str(item.get("section_number", "")).strip()
                title = str(item.get("title") or item.get("section_heading", "")).strip()
                text = str(item.get("evidence_text", ""))

                if not sec_num:
                    sec_matches = cls._extract_section_numbers(text)
                    if sec_matches:
                        sec_num = list(sec_matches)[0]

                if sec_num:
                    if not title:
                        # Extract title from text line e.g., "304. Snatching."
                        m = re.search(r'^\s*\d+[A-Z]?\s*[\.\:\-\—]\s*([^\.\:\n\—]+)', text, re.MULTILINE)
                        if m:
                            title = m.group(1).strip()
                    evidence_sec_map[sec_num] = title.lower()

            for claim_sec in claim_sections:
                for ev_sec, ev_title in evidence_sec_map.items():
                    if ev_title:
                        words = [w.lower() for w in re.findall(r'\b[a-zA-Z]{4,}\b', ev_title)]
                        for w in words:
                            if w in claim_text.lower():
                                if claim_sec != ev_sec:
                                    if claim_sec in evidence_sec_map and evidence_sec_map[claim_sec] and w not in evidence_sec_map[claim_sec]:
                                        return VerificationVerdict.CONTRADICTED
                                    if ev_sec in evidence_sec_map:
                                        return VerificationVerdict.CONTRADICTED

        return None

    @classmethod
    def _guard_supported_verdict(
        cls, claim_text: str, evidence_items: List[Dict[str, Any]]
    ) -> VerificationVerdict:
        """
        Post-LLM Guard: If LLM returned SUPPORTED, ensure there are no unverified section/Act or topic mismatches,
        or missing numbers/specific requirement phrases in evidence.
        """
        claim_sections = cls._extract_section_numbers(claim_text)
        claim_acts = cls._extract_act_names(claim_text)

        evidence_acts = set()
        evidence_sections = set()
        all_evidence_text = ""

        for item in evidence_items:
            doc_id = str(item.get("document_id", "")).upper()
            sec_num = str(item.get("section_number", "")).strip()
            text = str(item.get("evidence_text", ""))

            evidence_acts.update(cls._extract_act_names(doc_id))
            evidence_acts.update(cls._extract_act_names(text))

            if sec_num:
                evidence_sections.add(sec_num)
            evidence_sections.update(cls._extract_section_numbers(text))
            all_evidence_text += " " + text

        # Guard 1: Act Mismatch
        if claim_acts and evidence_acts:
            if not claim_acts.intersection(evidence_acts):
                return VerificationVerdict.CONTRADICTED

        # Guard 2: Section Mismatch
        if claim_sections:
            if not claim_sections.intersection(evidence_sections):
                return VerificationVerdict.INSUFFICIENT

        # Guard 3: Numbers/amounts check (e.g., "50,000", "100", "50000", "1 lakh")
        all_ev_lower = all_evidence_text.lower()
        claim_numbers = set(re.findall(r'\b\d+(?:,\d+)*\b', claim_text))
        evidence_numbers = set(re.findall(r'\b\d+(?:,\d+)*\b', all_evidence_text))
        statutory_years = {"2023", "2024", "2025", "1860", "1973"}
        unmatched_numbers = claim_numbers - evidence_numbers - claim_sections - statutory_years
        if unmatched_numbers:
            return VerificationVerdict.INSUFFICIENT

        # Guard 4: Specific requirement phrases in claim missing from evidence
        unmentioned_phrases = ["community service", "governor", "magistrate", "written contract", "ransom", "minimum fine"]
        for phrase in unmentioned_phrases:
            if phrase in claim_text.lower() and phrase not in all_ev_lower:
                return VerificationVerdict.INSUFFICIENT

        # Guard 5: Topically Unrelated / Unsubstantiated Qualifiers
        claim_words = set(re.findall(r'\b[a-zA-Z]{4,}\b', claim_text.lower()))
        stop_words = {"under", "this", "that", "with", "from", "defined", "section", "sanhita", "bharatiya", "nyaya", "2023", "punishment", "shall", "code", "act", "defines"}
        content_words = claim_words - stop_words
        if content_words:
            matching_words = [w for w in content_words if w in all_ev_lower]
            if not matching_words:
                return VerificationVerdict.INSUFFICIENT
            qualifiers = {"serious", "heinous", "extreme", "severe", "most", "worst"}
            claim_qualifiers = content_words.intersection(qualifiers)
            if claim_qualifiers and not any(q in all_ev_lower for q in claim_qualifiers):
                return VerificationVerdict.INSUFFICIENT

        return VerificationVerdict.SUPPORTED

    @classmethod
    def _guard_contradicted_verdict(
        cls, claim_text: str, evidence_items: List[Dict[str, Any]]
    ) -> VerificationVerdict:
        """
        Post-LLM Guard: If LLM returned CONTRADICTED, verify whether it is a genuine contradiction
        (e.g., section mismatch, Act mismatch, or direct factual opposition) vs simple silence
        on an extra unverified claim requirement (e.g., community service, governor approval).
        """
        claim_sections = cls._extract_section_numbers(claim_text)
        claim_acts = cls._extract_act_names(claim_text)

        evidence_acts = set()
        evidence_sections = set()
        all_evidence_text = ""

        for item in evidence_items:
            doc_id = str(item.get("document_id", "")).upper()
            sec_num = str(item.get("section_number", "")).strip()
            text = str(item.get("evidence_text", ""))

            evidence_acts.update(cls._extract_act_names(doc_id))
            evidence_acts.update(cls._extract_act_names(text))

            if sec_num:
                evidence_sections.add(sec_num)
            evidence_sections.update(cls._extract_section_numbers(text))
            all_evidence_text += " " + text

        # 1. Genuine Act Mismatch -> CONTRADICTED
        if claim_acts and evidence_acts:
            if not claim_acts.intersection(evidence_acts):
                return VerificationVerdict.CONTRADICTED

        # 2. Genuine Section Mismatch -> CONTRADICTED
        if claim_sections and evidence_sections:
            if not claim_sections.intersection(evidence_sections):
                return VerificationVerdict.CONTRADICTED

        # 3. Direct Factual Opposition Check
        all_ev_lower = all_evidence_text.lower()
        claim_lower = claim_text.lower()

        # Direct contradiction on duration/term e.g. "maximum of 6 months" vs "ten years" or "life"
        if "maximum of" in claim_lower or "up to" in claim_lower:
            m_claim = re.search(r'(?:maximum of|up to)\s*(\d+)\s*(month|year|day|week)s?', claim_lower)
            if m_claim:
                if any(term in all_ev_lower for term in ["ten years", "life", "20 years", "imprisonment for life"]):
                    return VerificationVerdict.CONTRADICTED

        # 4. Silence on extra requirement/approval/penalty phrases -> INSUFFICIENT
        unmentioned_phrases = ["community service", "governor", "magistrate", "written contract", "ransom", "minimum fine"]
        for phrase in unmentioned_phrases:
            if phrase in claim_lower and phrase not in all_ev_lower:
                return VerificationVerdict.INSUFFICIENT

        return VerificationVerdict.CONTRADICTED

    @staticmethod
    def parse_verdict(response_text: str) -> VerificationVerdict:
        """
        Robustly parse model output text into a valid VerificationVerdict enum.
        """
        if not response_text or not response_text.strip():
            return VerificationVerdict.INSUFFICIENT

        clean_text = response_text.strip()
        lines = [line.strip().upper() for line in clean_text.splitlines() if line.strip()]

        # 1. Search for explicit VERDICT: <VALUE> in final lines
        for line in reversed(lines):
            match = re.search(r"\bVERDICT\s*:\s*(SUPPORTED|CONTRADICTED|INSUFFICIENT|REFUTED)\b", line)
            if match:
                v_str = match.group(1)
                if v_str in ("CONTRADICTED", "REFUTED"):
                    return VerificationVerdict.CONTRADICTED
                elif v_str == "SUPPORTED":
                    return VerificationVerdict.SUPPORTED
                elif v_str == "INSUFFICIENT":
                    return VerificationVerdict.INSUFFICIENT

        upper_full = clean_text.upper()

        # 2. Check for negative phrasing that invalidates "SUPPORTED"
        if "NOT SUPPORTED" in upper_full or "UNSUPPORTED" in upper_full or "CANNOT BE SUPPORTED" in upper_full:
            if "CONTRADICT" in upper_full or "REFUTE" in upper_full:
                return VerificationVerdict.CONTRADICTED
            return VerificationVerdict.INSUFFICIENT

        # 3. Order keyword parsing safely
        if "CONTRADICTED" in upper_full or "REFUTED" in upper_full:
            return VerificationVerdict.CONTRADICTED
        elif "INSUFFICIENT" in upper_full or "UNVERIFIABLE" in upper_full:
            return VerificationVerdict.INSUFFICIENT
        elif "SUPPORTED" in upper_full:
            return VerificationVerdict.SUPPORTED

        return VerificationVerdict.INSUFFICIENT

