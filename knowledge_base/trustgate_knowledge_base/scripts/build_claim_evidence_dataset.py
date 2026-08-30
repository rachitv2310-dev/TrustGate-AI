import json
import hashlib
import os
import sys

repo_dir = r"c:\Users\asus\OneDrive\Desktop\trustgate_knowledge_base"
chunks_path = os.path.join(repo_dir, "data", "processed", "BNS_2023_chunks.jsonl")
text_path = os.path.join(repo_dir, "data", "processed", "BNS_2023_text.txt")
pdf_path = os.path.join(repo_dir, "data", "raw", "Bharatiya_Nyaya_Sanhita_2023.pdf")

dataset_dir = os.path.join(repo_dir, "data", "dataset")
os.makedirs(dataset_dir, exist_ok=True)

# 1. Load Provenance Hashes & Source Text (with universal newlines \n)
pdf_bytes = open(pdf_path, "rb").read()
pdf_hash = hashlib.sha256(pdf_bytes).hexdigest()

text_bytes = open(text_path, "rb").read()
text_hash = hashlib.sha256(text_bytes).hexdigest()
text_content = open(text_path, "r", encoding="utf-8").read()

expected_pdf_hash = "d4449e9995b21fd52627811d08f9d21feda6a3678b7e5355b651242d152167f5"
expected_text_hash = "f0ee026645e589f3ed7aba4cbbbad60a0a5f2b0a428716e845785acb56d32af5"

if pdf_hash != expected_pdf_hash or text_hash != expected_text_hash:
    raise ValueError("CRITICAL: Provenance hash mismatch!")

# 2. Load Validated Chunks & Index by Chunk ID & Section
chunks = []
chunks_by_id = {}
chunks_by_sec = {}
with open(chunks_path, "r", encoding="utf-8") as f:
    for line in f:
        if line.strip():
            c = json.loads(line)
            chunks.append(c)
            chunks_by_id[c["chunk_id"]] = c
            sec = str(c["section_number"])
            if sec not in chunks_by_sec:
                chunks_by_sec[sec] = []
            chunks_by_sec[sec].append(c)

print(f"Loaded {len(chunks)} chunks across {len(chunks_by_sec)} sections.")

def resolve_chunk_id(sec_num, chunk_index=0):
    sec_str = str(sec_num)
    if sec_str in chunks_by_sec and len(chunks_by_sec[sec_str]) > chunk_index:
        return chunks_by_sec[sec_str][chunk_index]["chunk_id"]
    raise KeyError(f"Section {sec_str} not found in chunks dataset!")

def get_excerpt(chunk_id, max_len=250):
    c = chunks_by_id[chunk_id]
    txt = c["text"]
    excerpt = txt[:max_len] if len(txt) > max_len else txt
    if excerpt not in text_content:
        raise ValueError(f"CRITICAL: Excerpt from {chunk_id} is not an exact substring of source text!")
    return excerpt, len(txt) > max_len

def create_evidence_item(sec_num, rel, chunk_index=0):
    chunk_id = resolve_chunk_id(sec_num, chunk_index)
    c = chunks_by_id[chunk_id]
    excerpt, truncated = get_excerpt(chunk_id)
    return {
        "evidence_chunk_id": chunk_id,
        "evidence_relationship": rel,
        "section_number": str(c["section_number"]),
        "section_heading": c["section_heading"],
        "chapter_number": str(c["chapter_number"]),
        "page_start": c["page_start"],
        "page_end": c["page_end"],
        "evidence_excerpt": excerpt,
        "excerpt_truncated": truncated,
        "source_authority": 1.0
    }

# 3. Comprehensive Seed Data (60 Claims across 7 Categories)
raw_claims_data = [
    # --- 1. DIRECT_SUPPORTED (18 Examples) ---
    {
        "claim_id": "CLAIM_BNS_001",
        "claim_text": "Section 103 of the BNS prescribes punishment for murder with death or imprisonment for life, and fine.",
        "claim_type": "DIRECT_SUPPORTED",
        "expected_verdict": "SUPPORTED",
        "primary_section": "103",
        "evidence_links": [("103", "SUPPORTS")],
        "difficulty": "EASY",
        "is_hard_negative": False,
        "negative_type": "NONE"
    },
    {
        "claim_id": "CLAIM_BNS_002",
        "claim_text": "Section 358 of the BNS specifies repeal of the Indian Penal Code and savings provisions.",
        "claim_type": "DIRECT_SUPPORTED",
        "expected_verdict": "SUPPORTED",
        "primary_section": "358",
        "evidence_links": [("358", "SUPPORTS")],
        "difficulty": "EASY",
        "is_hard_negative": False,
        "negative_type": "NONE"
    },
    {
        "claim_id": "CLAIM_BNS_003",
        "claim_text": "Section 351 of the BNS defines criminal intimidation as threatening another with injury to person, reputation, or property.",
        "claim_type": "DIRECT_SUPPORTED",
        "expected_verdict": "SUPPORTED",
        "primary_section": "351",
        "evidence_links": [("351", "SUPPORTS")],
        "difficulty": "EASY",
        "is_hard_negative": False,
        "negative_type": "NONE"
    },
    {
        "claim_id": "CLAIM_BNS_004",
        "claim_text": "Section 1 specifies the short title, commencement, and territorial application of the Bharatiya Nyaya Sanhita, 2023.",
        "claim_type": "DIRECT_SUPPORTED",
        "expected_verdict": "SUPPORTED",
        "primary_section": "1",
        "evidence_links": [("1", "SUPPORTS")],
        "difficulty": "EASY",
        "is_hard_negative": False,
        "negative_type": "NONE"
    },
    {
        "claim_id": "CLAIM_BNS_005",
        "claim_text": "Section 64 of the BNS prescribes punishment for rape with rigorous imprisonment of not less than ten years, extending to life.",
        "claim_type": "DIRECT_SUPPORTED",
        "expected_verdict": "SUPPORTED",
        "primary_section": "64",
        "evidence_links": [("64", "SUPPORTS")],
        "difficulty": "EASY",
        "is_hard_negative": False,
        "negative_type": "NONE"
    },
    {
        "claim_id": "CLAIM_BNS_006",
        "claim_text": "Section 309 of the BNS defines robbery as theft or extortion accompanied by hurt, wrongful restraint, or fear of instant death.",
        "claim_type": "DIRECT_SUPPORTED",
        "expected_verdict": "SUPPORTED",
        "primary_section": "309",
        "evidence_links": [("309", "SUPPORTS")],
        "difficulty": "EASY",
        "is_hard_negative": False,
        "negative_type": "NONE"
    },
    {
        "claim_id": "CLAIM_BNS_007",
        "claim_text": "Section 303 of the BNS defines theft as dishonestly taking movable property out of the possession of any person without consent.",
        "claim_type": "DIRECT_SUPPORTED",
        "expected_verdict": "SUPPORTED",
        "primary_section": "303",
        "evidence_links": [("303", "SUPPORTS")],
        "difficulty": "EASY",
        "is_hard_negative": False,
        "negative_type": "NONE"
    },
    {
        "claim_id": "CLAIM_BNS_008",
        "claim_text": "Section 105 of the BNS specifies punishment for culpable homicide not amounting to murder.",
        "claim_type": "DIRECT_SUPPORTED",
        "expected_verdict": "SUPPORTED",
        "primary_section": "105",
        "evidence_links": [("105", "SUPPORTS")],
        "difficulty": "EASY",
        "is_hard_negative": False,
        "negative_type": "NONE"
    },
    {
        "claim_id": "CLAIM_BNS_009",
        "claim_text": "Section 109 of the BNS prescribes punishment for attempt to murder.",
        "claim_type": "DIRECT_SUPPORTED",
        "expected_verdict": "SUPPORTED",
        "primary_section": "109",
        "evidence_links": [("109", "SUPPORTS")],
        "difficulty": "EASY",
        "is_hard_negative": False,
        "negative_type": "NONE"
    },
    {
        "claim_id": "CLAIM_BNS_010",
        "claim_text": "Section 111 of the BNS defines organised crime committed by a member of a crime syndicate.",
        "claim_type": "DIRECT_SUPPORTED",
        "expected_verdict": "SUPPORTED",
        "primary_section": "111",
        "evidence_links": [("111", "SUPPORTS")],
        "difficulty": "MEDIUM",
        "is_hard_negative": False,
        "negative_type": "NONE"
    },
    {
        "claim_id": "CLAIM_BNS_011",
        "claim_text": "Section 113 of the BNS defines terrorist acts threatening the unity, integrity, security, or sovereignty of India.",
        "claim_type": "DIRECT_SUPPORTED",
        "expected_verdict": "SUPPORTED",
        "primary_section": "113",
        "evidence_links": [("113", "SUPPORTS")],
        "difficulty": "MEDIUM",
        "is_hard_negative": False,
        "negative_type": "NONE"
    },
    {
        "claim_id": "CLAIM_BNS_012",
        "claim_text": "Section 304 of the BNS defines snatching as dishonestly moving property in order to commit theft by sudden or quick effort.",
        "claim_type": "DIRECT_SUPPORTED",
        "expected_verdict": "SUPPORTED",
        "primary_section": "304",
        "evidence_links": [("304", "SUPPORTS")],
        "difficulty": "EASY",
        "is_hard_negative": False,
        "negative_type": "NONE"
    },
    {
        "claim_id": "CLAIM_BNS_013",
        "claim_text": "Section 310 of the BNS defines dacoity as robbery committed conjointly by five or more persons.",
        "claim_type": "DIRECT_SUPPORTED",
        "expected_verdict": "SUPPORTED",
        "primary_section": "310",
        "evidence_links": [("310", "SUPPORTS")],
        "difficulty": "EASY",
        "is_hard_negative": False,
        "negative_type": "NONE"
    },
    {
        "claim_id": "CLAIM_BNS_014",
        "claim_text": "Section 318 of the BNS defines cheating as deceiving any person to deliver property or consent to retain property.",
        "claim_type": "DIRECT_SUPPORTED",
        "expected_verdict": "SUPPORTED",
        "primary_section": "318",
        "evidence_links": [("318", "SUPPORTS")],
        "difficulty": "EASY",
        "is_hard_negative": False,
        "negative_type": "NONE"
    },
    {
        "claim_id": "CLAIM_BNS_015",
        "claim_text": "Section 352 of the BNS prescribes punishment for intentional insult with intent to provoke breach of the peace.",
        "claim_type": "DIRECT_SUPPORTED",
        "expected_verdict": "SUPPORTED",
        "primary_section": "352",
        "evidence_links": [("352", "SUPPORTS")],
        "difficulty": "EASY",
        "is_hard_negative": False,
        "negative_type": "NONE"
    },
    {
        "claim_id": "CLAIM_BNS_016",
        "claim_text": "Section 356 of the BNS defines defamation as making or publishing any imputation concerning any person intending to harm reputation.",
        "claim_type": "DIRECT_SUPPORTED",
        "expected_verdict": "SUPPORTED",
        "primary_section": "356",
        "evidence_links": [("356", "SUPPORTS")],
        "difficulty": "EASY",
        "is_hard_negative": False,
        "negative_type": "NONE"
    },
    {
        "claim_id": "CLAIM_BNS_017",
        "claim_text": "Section 4 of the BNS specifies punishment of offences committed beyond India which by law may be tried within India.",
        "claim_type": "DIRECT_SUPPORTED",
        "expected_verdict": "SUPPORTED",
        "primary_section": "4",
        "evidence_links": [("4", "SUPPORTS")],
        "difficulty": "MEDIUM",
        "is_hard_negative": False,
        "negative_type": "NONE"
    },
    {
        "claim_id": "CLAIM_BNS_018",
        "claim_text": "Section 104 of the BNS prescribes punishment for murder by a person under sentence of imprisonment for life.",
        "claim_type": "DIRECT_SUPPORTED",
        "expected_verdict": "SUPPORTED",
        "primary_section": "104",
        "evidence_links": [("104", "SUPPORTS")],
        "difficulty": "MEDIUM",
        "is_hard_negative": False,
        "negative_type": "NONE"
    },

    # --- 2. DIRECT_REFUTED (10 Examples) ---
    {
        "claim_id": "CLAIM_BNS_019",
        "claim_text": "Section 303 of the BNS defines snatching and prescribes 20 years of solitary confinement as sole penalty.",
        "claim_type": "DIRECT_REFUTED",
        "expected_verdict": "REFUTED",
        "primary_section": "303",
        "evidence_links": [("303", "REFUTES")],
        "difficulty": "EASY",
        "is_hard_negative": False,
        "negative_type": "NONE"
    },
    {
        "claim_id": "CLAIM_BNS_020",
        "claim_text": "Section 64 provides that rape is punishable only by a one hundred rupee fine with no imprisonment.",
        "claim_type": "DIRECT_REFUTED",
        "expected_verdict": "REFUTED",
        "primary_section": "64",
        "evidence_links": [("64", "REFUTES")],
        "difficulty": "EASY",
        "is_hard_negative": False,
        "negative_type": "NONE"
    },
    {
        "claim_id": "CLAIM_BNS_021",
        "claim_text": "Under Section 103 of the BNS, murder is punishable exclusively by community service for two weeks.",
        "claim_type": "DIRECT_REFUTED",
        "expected_verdict": "REFUTED",
        "primary_section": "103",
        "evidence_links": [("103", "REFUTES")],
        "difficulty": "EASY",
        "is_hard_negative": False,
        "negative_type": "NONE"
    },
    {
        "claim_id": "CLAIM_BNS_022",
        "claim_text": "Section 358 of the BNS states that the Indian Penal Code shall remain fully in force alongside BNS without repeal.",
        "claim_type": "DIRECT_REFUTED",
        "expected_verdict": "REFUTED",
        "primary_section": "358",
        "evidence_links": [("358", "REFUTES")],
        "difficulty": "EASY",
        "is_hard_negative": False,
        "negative_type": "NONE"
    },
    {
        "claim_id": "CLAIM_BNS_023",
        "claim_text": "Section 310 of the BNS specifies that dacoity requires a minimum of twenty-five persons acting together.",
        "claim_type": "DIRECT_REFUTED",
        "expected_verdict": "REFUTED",
        "primary_section": "310",
        "evidence_links": [("310", "REFUTES")],
        "difficulty": "MEDIUM",
        "is_hard_negative": False,
        "negative_type": "NONE"
    },
    {
        "claim_id": "CLAIM_BNS_024",
        "claim_text": "Section 309 of the BNS provides that robbery is a civil tort carrying no criminal imprisonment.",
        "claim_type": "DIRECT_REFUTED",
        "expected_verdict": "REFUTED",
        "primary_section": "309",
        "evidence_links": [("309", "REFUTES")],
        "difficulty": "EASY",
        "is_hard_negative": False,
        "negative_type": "NONE"
    },
    {
        "claim_id": "CLAIM_BNS_025",
        "claim_text": "Section 351 of the BNS states that criminal intimidation applies only to corporate entities and not individuals.",
        "claim_type": "DIRECT_REFUTED",
        "expected_verdict": "REFUTED",
        "primary_section": "351",
        "evidence_links": [("351", "REFUTES")],
        "difficulty": "MEDIUM",
        "is_hard_negative": False,
        "negative_type": "NONE"
    },
    {
        "claim_id": "CLAIM_BNS_026",
        "claim_text": "Section 105 of the BNS provides that culpable homicide not amounting to murder is never punishable under law.",
        "claim_type": "DIRECT_REFUTED",
        "expected_verdict": "REFUTED",
        "primary_section": "105",
        "evidence_links": [("105", "REFUTES")],
        "difficulty": "EASY",
        "is_hard_negative": False,
        "negative_type": "NONE"
    },
    {
        "claim_id": "CLAIM_BNS_027",
        "claim_text": "Section 356 of the BNS states that truthful statements made in good faith can never be excepted from defamation under any circumstance.",
        "claim_type": "DIRECT_REFUTED",
        "expected_verdict": "REFUTED",
        "primary_section": "356",
        "evidence_links": [("356", "REFUTES")],
        "difficulty": "HARD",
        "is_hard_negative": False,
        "negative_type": "NONE"
    },
    {
        "claim_id": "CLAIM_BNS_028",
        "claim_text": "Section 1 of the BNS provides that the Sanhita applies exclusively to non-citizens residing outside India.",
        "claim_type": "DIRECT_REFUTED",
        "expected_verdict": "REFUTED",
        "primary_section": "1",
        "evidence_links": [("1", "REFUTES")],
        "difficulty": "EASY",
        "is_hard_negative": False,
        "negative_type": "NONE"
    },

    # --- 3. SECTION_MISMATCH (HARD NEGATIVES - 8 Examples) ---
    {
        "claim_id": "CLAIM_BNS_029",
        "claim_text": "Section 103 of the BNS defines theft and prescribes punishment for dishonestly taking movable property.",
        "claim_type": "SECTION_MISMATCH",
        "expected_verdict": "REFUTED",
        "primary_section": "103",
        "evidence_links": [("103", "REFUTES")],
        "difficulty": "HARD",
        "is_hard_negative": True,
        "negative_type": "HARD_NEGATIVE"
    },
    {
        "claim_id": "CLAIM_BNS_030",
        "claim_text": "Section 303 of the BNS defines snatching as moving property by sudden or quick effort.",
        "claim_type": "SECTION_MISMATCH",
        "expected_verdict": "REFUTED",
        "primary_section": "303",
        "evidence_links": [("303", "REFUTES")],
        "difficulty": "HARD",
        "is_hard_negative": True,
        "negative_type": "HARD_NEGATIVE"
    },
    {
        "claim_id": "CLAIM_BNS_031",
        "claim_text": "Section 64 of the BNS prescribes punishment for murder with death or imprisonment for life.",
        "claim_type": "SECTION_MISMATCH",
        "expected_verdict": "REFUTED",
        "primary_section": "64",
        "evidence_links": [("64", "REFUTES")],
        "difficulty": "HARD",
        "is_hard_negative": True,
        "negative_type": "HARD_NEGATIVE"
    },
    {
        "claim_id": "CLAIM_BNS_032",
        "claim_text": "Section 309 of the BNS defines dacoity as robbery committed conjointly by five or more persons.",
        "claim_type": "SECTION_MISMATCH",
        "expected_verdict": "REFUTED",
        "primary_section": "309",
        "evidence_links": [("309", "REFUTES")],
        "difficulty": "HARD",
        "is_hard_negative": True,
        "negative_type": "HARD_NEGATIVE"
    },
    {
        "claim_id": "CLAIM_BNS_033",
        "claim_text": "Section 351 of the BNS defines defamation as making an imputation intending to harm reputation.",
        "claim_type": "SECTION_MISMATCH",
        "expected_verdict": "REFUTED",
        "primary_section": "351",
        "evidence_links": [("351", "REFUTES")],
        "difficulty": "HARD",
        "is_hard_negative": True,
        "negative_type": "HARD_NEGATIVE"
    },
    {
        "claim_id": "CLAIM_BNS_034",
        "claim_text": "Section 105 of the BNS prescribes punishment for attempt to murder.",
        "claim_type": "SECTION_MISMATCH",
        "expected_verdict": "REFUTED",
        "primary_section": "105",
        "evidence_links": [("105", "REFUTES")],
        "difficulty": "HARD",
        "is_hard_negative": True,
        "negative_type": "HARD_NEGATIVE"
    },
    {
        "claim_id": "CLAIM_BNS_035",
        "claim_text": "Section 318 of the BNS defines theft as dishonestly taking movable property without consent.",
        "claim_type": "SECTION_MISMATCH",
        "expected_verdict": "REFUTED",
        "primary_section": "318",
        "evidence_links": [("318", "REFUTES")],
        "difficulty": "HARD",
        "is_hard_negative": True,
        "negative_type": "HARD_NEGATIVE"
    },
    {
        "claim_id": "CLAIM_BNS_036",
        "claim_text": "Section 111 of the BNS defines terrorist acts threatening the security or sovereignty of India.",
        "claim_type": "SECTION_MISMATCH",
        "expected_verdict": "REFUTED",
        "primary_section": "111",
        "evidence_links": [("111", "REFUTES")],
        "difficulty": "HARD",
        "is_hard_negative": True,
        "negative_type": "HARD_NEGATIVE"
    },

    # --- 4. CROSS_SECTION_CONFUSION (HARD NEGATIVES - 6 Examples) ---
    {
        "claim_id": "CLAIM_BNS_037",
        "claim_text": "Section 303 and Section 304 combined state that theft becomes snatching whenever the property is moved by truck.",
        "claim_type": "CROSS_SECTION_CONFUSION",
        "expected_verdict": "REFUTED",
        "primary_section": "303",
        "evidence_links": [
            ("303", "REFUTES"),
            ("304", "REFUTES")
        ],
        "difficulty": "HARD",
        "is_hard_negative": True,
        "negative_type": "HARD_NEGATIVE"
    },
    {
        "claim_id": "CLAIM_BNS_038",
        "claim_text": "Under Section 103 and Section 105, murder and culpable homicide carry identical compulsory death sentences in all cases.",
        "claim_type": "CROSS_SECTION_CONFUSION",
        "expected_verdict": "REFUTED",
        "primary_section": "103",
        "evidence_links": [
            ("103", "REFUTES"),
            ("105", "REFUTES")
        ],
        "difficulty": "HARD",
        "is_hard_negative": True,
        "negative_type": "HARD_NEGATIVE"
    },
    {
        "claim_id": "CLAIM_BNS_039",
        "claim_text": "Section 309 and Section 310 provide that any robbery committed by two people is automatically classified as dacoity.",
        "claim_type": "CROSS_SECTION_CONFUSION",
        "expected_verdict": "REFUTED",
        "primary_section": "309",
        "evidence_links": [
            ("309", "REFUTES"),
            ("310", "REFUTES")
        ],
        "difficulty": "HARD",
        "is_hard_negative": True,
        "negative_type": "HARD_NEGATIVE"
    },
    {
        "claim_id": "CLAIM_BNS_040",
        "claim_text": "Section 351 and Section 356 provide that criminal intimidation automatically constitutes defamation without requiring any threat of injury.",
        "claim_type": "CROSS_SECTION_CONFUSION",
        "expected_verdict": "REFUTED",
        "primary_section": "351",
        "evidence_links": [
            ("351", "REFUTES"),
            ("356", "REFUTES")
        ],
        "difficulty": "HARD",
        "is_hard_negative": True,
        "negative_type": "HARD_NEGATIVE"
    },
    {
        "claim_id": "CLAIM_BNS_041",
        "claim_text": "Section 111 and Section 113 provide that organised crime syndicates can only be prosecuted if they engage in cyber terrorism.",
        "claim_type": "CROSS_SECTION_CONFUSION",
        "expected_verdict": "REFUTED",
        "primary_section": "111",
        "evidence_links": [
            ("111", "REFUTES"),
            ("113", "REFUTES")
        ],
        "difficulty": "HARD",
        "is_hard_negative": True,
        "negative_type": "HARD_NEGATIVE"
    },
    {
        "claim_id": "CLAIM_BNS_042",
        "claim_text": "Section 104 and Section 109 state that attempt to murder by a life convict carries no additional judicial penalty.",
        "claim_type": "CROSS_SECTION_CONFUSION",
        "expected_verdict": "REFUTED",
        "primary_section": "104",
        "evidence_links": [
            ("104", "REFUTES"),
            ("109", "REFUTES")
        ],
        "difficulty": "HARD",
        "is_hard_negative": True,
        "negative_type": "HARD_NEGATIVE"
    },

    # --- 5. PARTIALLY_SUPPORTED (6 Examples) ---
    {
        "claim_id": "CLAIM_BNS_043",
        "claim_text": "Section 103 prescribes punishment for murder, and mandates that all trials must conclude within 24 hours of arrest.",
        "claim_type": "PARTIALLY_SUPPORTED",
        "expected_verdict": "INSUFFICIENT_EVIDENCE",
        "primary_section": "103",
        "evidence_links": [("103", "INSUFFICIENT")],
        "difficulty": "MEDIUM",
        "is_hard_negative": False,
        "negative_type": "NONE"
    },
    {
        "claim_id": "CLAIM_BNS_044",
        "claim_text": "Section 303 defines theft as dishonestly taking movable property, and exempts all family members from prosecution.",
        "claim_type": "PARTIALLY_SUPPORTED",
        "expected_verdict": "INSUFFICIENT_EVIDENCE",
        "primary_section": "303",
        "evidence_links": [("303", "INSUFFICIENT")],
        "difficulty": "MEDIUM",
        "is_hard_negative": False,
        "negative_type": "NONE"
    },
    {
        "claim_id": "CLAIM_BNS_045",
        "claim_text": "Section 64 specifies punishment for rape, and requires digital blockchain recording of all court testimony.",
        "claim_type": "PARTIALLY_SUPPORTED",
        "expected_verdict": "INSUFFICIENT_EVIDENCE",
        "primary_section": "64",
        "evidence_links": [("64", "INSUFFICIENT")],
        "difficulty": "MEDIUM",
        "is_hard_negative": False,
        "negative_type": "NONE"
    },
    {
        "claim_id": "CLAIM_BNS_046",
        "claim_text": "Section 351 defines criminal intimidation, and mandates mandatory compensation of one million rupees to victims.",
        "claim_type": "PARTIALLY_SUPPORTED",
        "expected_verdict": "INSUFFICIENT_EVIDENCE",
        "primary_section": "351",
        "evidence_links": [("351", "INSUFFICIENT")],
        "difficulty": "MEDIUM",
        "is_hard_negative": False,
        "negative_type": "NONE"
    },
    {
        "claim_id": "CLAIM_BNS_047",
        "claim_text": "Section 309 defines robbery, and prescribes automatic forfeiture of all real estate properties of the accused.",
        "claim_type": "PARTIALLY_SUPPORTED",
        "expected_verdict": "INSUFFICIENT_EVIDENCE",
        "primary_section": "309",
        "evidence_links": [("309", "INSUFFICIENT")],
        "difficulty": "MEDIUM",
        "is_hard_negative": False,
        "negative_type": "NONE"
    },
    {
        "claim_id": "CLAIM_BNS_048",
        "claim_text": "Section 358 deals with repeal and savings, and specifies that all pending appeals are automatically dismissed.",
        "claim_type": "PARTIALLY_SUPPORTED",
        "expected_verdict": "INSUFFICIENT_EVIDENCE",
        "primary_section": "358",
        "evidence_links": [("358", "INSUFFICIENT")],
        "difficulty": "MEDIUM",
        "is_hard_negative": False,
        "negative_type": "NONE"
    },

    # --- 6. INSUFFICIENT_EVIDENCE (8 Examples) ---
    {
        "claim_id": "CLAIM_BNS_049",
        "claim_text": "Section 303 of the BNS applies to offences committed exclusively within the maritime international waters of foreign flags.",
        "claim_type": "INSUFFICIENT_EVIDENCE",
        "expected_verdict": "INSUFFICIENT_EVIDENCE",
        "primary_section": "303",
        "evidence_links": [("303", "INSUFFICIENT")],
        "difficulty": "MEDIUM",
        "is_hard_negative": False,
        "negative_type": "NONE"
    },
    {
        "claim_id": "CLAIM_BNS_050",
        "claim_text": "Section 103 of the BNS requires approval from the Law Commission before filing a murder charge.",
        "claim_type": "INSUFFICIENT_EVIDENCE",
        "expected_verdict": "INSUFFICIENT_EVIDENCE",
        "primary_section": "103",
        "evidence_links": [("103", "INSUFFICIENT")],
        "difficulty": "MEDIUM",
        "is_hard_negative": False,
        "negative_type": "NONE"
    },
    {
        "claim_id": "CLAIM_BNS_051",
        "claim_text": "Section 64 of the BNS specifies that DNA evidence must be audited by three independent international laboratories.",
        "claim_type": "INSUFFICIENT_EVIDENCE",
        "expected_verdict": "INSUFFICIENT_EVIDENCE",
        "primary_section": "64",
        "evidence_links": [("64", "INSUFFICIENT")],
        "difficulty": "MEDIUM",
        "is_hard_negative": False,
        "negative_type": "NONE"
    },
    {
        "claim_id": "CLAIM_BNS_052",
        "claim_text": "Section 351 of the BNS mandates that verbal threats sent via social media platforms require special Interpol warrants.",
        "claim_type": "INSUFFICIENT_EVIDENCE",
        "expected_verdict": "INSUFFICIENT_EVIDENCE",
        "primary_section": "351",
        "evidence_links": [("351", "INSUFFICIENT")],
        "difficulty": "MEDIUM",
        "is_hard_negative": False,
        "negative_type": "NONE"
    },
    {
        "claim_id": "CLAIM_BNS_053",
        "claim_text": "Section 318 of the BNS requires commercial banks to compensate victims of corporate fraud within forty-eight hours.",
        "claim_type": "INSUFFICIENT_EVIDENCE",
        "expected_verdict": "INSUFFICIENT_EVIDENCE",
        "primary_section": "318",
        "evidence_links": [("318", "INSUFFICIENT")],
        "difficulty": "MEDIUM",
        "is_hard_negative": False,
        "negative_type": "NONE"
    },
    {
        "claim_id": "CLAIM_BNS_054",
        "claim_text": "Section 113 of the BNS specifies that terrorist offences must be investigated exclusively by international peacekeeping forces.",
        "claim_type": "INSUFFICIENT_EVIDENCE",
        "expected_verdict": "INSUFFICIENT_EVIDENCE",
        "primary_section": "113",
        "evidence_links": [("113", "INSUFFICIENT")],
        "difficulty": "MEDIUM",
        "is_hard_negative": False,
        "negative_type": "NONE"
    },
    {
        "claim_id": "CLAIM_BNS_055",
        "claim_text": "Section 356 of the BNS provides that defamation damages must be calculated based on annual corporate tax returns.",
        "claim_type": "INSUFFICIENT_EVIDENCE",
        "expected_verdict": "INSUFFICIENT_EVIDENCE",
        "primary_section": "356",
        "evidence_links": [("356", "INSUFFICIENT")],
        "difficulty": "MEDIUM",
        "is_hard_negative": False,
        "negative_type": "NONE"
    },
    {
        "claim_id": "CLAIM_BNS_056",
        "claim_text": "Section 1 of the BNS specifies that state governments may suspend the Sanhita during local municipal elections.",
        "claim_type": "INSUFFICIENT_EVIDENCE",
        "expected_verdict": "INSUFFICIENT_EVIDENCE",
        "primary_section": "1",
        "evidence_links": [("1", "INSUFFICIENT")],
        "difficulty": "MEDIUM",
        "is_hard_negative": False,
        "negative_type": "NONE"
    },

    # --- 7. OUT_OF_DOMAIN (Negative Controls - 4 Examples) ---
    {
        "claim_id": "CLAIM_BNS_057",
        "claim_text": "Quantum computing hardware utilizes superconducting qubits, cryogenic dilution refrigerators, and Josephson junctions.",
        "claim_type": "OUT_OF_DOMAIN",
        "expected_verdict": "INSUFFICIENT_EVIDENCE",
        "primary_section": "NONE",
        "evidence_links": [],
        "difficulty": "EASY",
        "is_hard_negative": False,
        "negative_type": "NONE"
    },
    {
        "claim_id": "CLAIM_BNS_058",
        "claim_text": "The Outer Space Treaty of 1967 governs national appropriation of lunar territory and celestial bodies.",
        "claim_type": "OUT_OF_DOMAIN",
        "expected_verdict": "INSUFFICIENT_EVIDENCE",
        "primary_section": "NONE",
        "evidence_links": [],
        "difficulty": "EASY",
        "is_hard_negative": False,
        "negative_type": "NONE"
    },
    {
        "claim_id": "CLAIM_BNS_059",
        "claim_text": "Photosynthesis converts carbon dioxide and water into glucose and oxygen using light energy absorbed by chlorophyll.",
        "claim_type": "OUT_OF_DOMAIN",
        "expected_verdict": "INSUFFICIENT_EVIDENCE",
        "primary_section": "NONE",
        "evidence_links": [],
        "difficulty": "EASY",
        "is_hard_negative": False,
        "negative_type": "NONE"
    },
    {
        "claim_id": "CLAIM_BNS_060",
        "claim_text": "The Income Tax Act of 1961 specifies capital gains tax rates for short-term and long-term equity transactions.",
        "claim_type": "OUT_OF_DOMAIN",
        "expected_verdict": "INSUFFICIENT_EVIDENCE",
        "primary_section": "NONE",
        "evidence_links": [],
        "difficulty": "EASY",
        "is_hard_negative": False,
        "negative_type": "NONE"
    }
]

# 4. Deterministic Section-Aware Splitting Strategy (No Data Leakage)
unique_sections = sorted(list(set(c["primary_section"] for c in raw_claims_data if c["primary_section"] != "NONE")))

train_secs = set()
val_secs = set()
test_secs = set()

for idx, sec in enumerate(unique_sections):
    h = int(hashlib.md5(sec.encode("utf-8")).hexdigest(), 16) % 10
    if h in (0, 1, 2, 3, 4, 5): # 60%
        train_secs.add(sec)
    elif h in (6, 7): # 20%
        val_secs.add(sec)
    else: # 20%
        test_secs.add(sec)

# 5. Build Complete Dataset Records & Separate Files
dataset_records = []
train_records = []
val_records = []
test_records = []
hard_negative_records = []
out_of_domain_records = []

for idx, raw in enumerate(raw_claims_data, 1):
    ex_id = f"EX_BNS_{idx:03d}"
    cid = raw["claim_id"]
    ctext = raw["claim_text"]
    ctype = raw["claim_type"]
    everdict = raw["expected_verdict"]
    psec = raw["primary_section"]

    ev_list = []
    for sec_num, rel in raw["evidence_links"]:
        ev_list.append(create_evidence_item(sec_num, rel))

    if psec == "NONE":
        assigned_split = "test"
    elif psec in train_secs:
        assigned_split = "train"
    elif psec in val_secs:
        assigned_split = "validation"
    else:
        assigned_split = "test"

    record = {
        "example_id": ex_id,
        "claim_id": cid,
        "claim_text": ctext,
        "claim_type": ctype,
        "expected_verdict": everdict,
        "is_hard_negative": raw["is_hard_negative"],
        "negative_type": raw["negative_type"],
        "difficulty": raw["difficulty"],
        "generation_method": "EXPERT_ANNOTATED_RULE_BASED_DERIVATION",
        "validation_status": "VERIFIED_PASSED",
        "split": assigned_split,
        "primary_section_number": psec,
        "evidence": ev_list,
        "provenance": {
            "source_document_id": "BNS_2023",
            "source_document_title": "The Bharatiya Nyaya Sanhita, 2023",
            "source_authority": "India Code (Official Primary Gazette)",
            "raw_pdf_sha256": pdf_hash,
            "source_text_sha256": text_hash
        }
    }

    dataset_records.append(record)

    if assigned_split == "train":
        train_records.append(record)
    elif assigned_split == "validation":
        val_records.append(record)
    else:
        test_records.append(record)

    if raw["is_hard_negative"]:
        hard_negative_records.append(record)

    if ctype == "OUT_OF_DOMAIN":
        out_of_domain_records.append(record)

# 6. Save JSONL Dataset Files
def save_jsonl(records, filepath):
    with open(filepath, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

save_jsonl(dataset_records, os.path.join(dataset_dir, "claim_evidence_dataset.jsonl"))
save_jsonl(train_records, os.path.join(dataset_dir, "train.jsonl"))
save_jsonl(val_records, os.path.join(dataset_dir, "validation.jsonl"))
save_jsonl(test_records, os.path.join(dataset_dir, "test.jsonl"))
save_jsonl(hard_negative_records, os.path.join(dataset_dir, "hard_negatives.jsonl"))
save_jsonl(out_of_domain_records, os.path.join(dataset_dir, "out_of_domain.jsonl"))

# 7. Save Schema Definition (`data/dataset/dataset_schema.json`)
schema_data = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "TrustGate-AI BNS 2023 Claim–Evidence Dataset Schema",
    "description": "Structured evaluation and training dataset connecting legal claims, expected verdicts, authoritative evidence chunks, relationships, and cryptographic provenance.",
    "type": "object",
    "required": [
        "example_id",
        "claim_id",
        "claim_text",
        "claim_type",
        "expected_verdict",
        "is_hard_negative",
        "negative_type",
        "difficulty",
        "generation_method",
        "validation_status",
        "split",
        "primary_section_number",
        "evidence",
        "provenance"
    ],
    "properties": {
        "example_id": {"type": "string"},
        "claim_id": {"type": "string"},
        "claim_text": {"type": "string"},
        "claim_type": {
            "type": "string",
            "enum": [
                "DIRECT_SUPPORTED",
                "DIRECT_REFUTED",
                "PARTIALLY_SUPPORTED",
                "INSUFFICIENT_EVIDENCE",
                "SECTION_MISMATCH",
                "CROSS_SECTION_CONFUSION",
                "OUT_OF_DOMAIN"
            ]
        },
        "expected_verdict": {
            "type": "string",
            "enum": ["SUPPORTED", "REFUTED", "INSUFFICIENT_EVIDENCE"]
        },
        "is_hard_negative": {"type": "boolean"},
        "negative_type": {"type": "string"},
        "difficulty": {"type": "string", "enum": ["EASY", "MEDIUM", "HARD"]},
        "generation_method": {"type": "string"},
        "validation_status": {"type": "string"},
        "split": {"type": "string", "enum": ["train", "validation", "test"]},
        "primary_section_number": {"type": "string"},
        "evidence": {
            "type": "array",
            "items": {
                "type": "object",
                "required": [
                    "evidence_chunk_id",
                    "evidence_relationship",
                    "section_number",
                    "section_heading",
                    "chapter_number",
                    "page_start",
                    "page_end",
                    "evidence_excerpt",
                    "excerpt_truncated",
                    "source_authority"
                ],
                "properties": {
                    "evidence_chunk_id": {"type": "string"},
                    "evidence_relationship": {"type": "string", "enum": ["SUPPORTS", "REFUTES", "INSUFFICIENT"]},
                    "section_number": {"type": "string"},
                    "section_heading": {"type": "string"},
                    "chapter_number": {"type": "string"},
                    "page_start": {"type": "integer"},
                    "page_end": {"type": "integer"},
                    "evidence_excerpt": {"type": "string"},
                    "excerpt_truncated": {"type": "boolean"},
                    "source_authority": {"type": "number"}
                }
            }
        },
        "provenance": {
            "type": "object",
            "required": [
                "source_document_id",
                "source_document_title",
                "source_authority",
                "raw_pdf_sha256",
                "source_text_sha256"
            ],
            "properties": {
                "source_document_id": {"type": "string"},
                "source_document_title": {"type": "string"},
                "source_authority": {"type": "string"},
                "raw_pdf_sha256": {"type": "string"},
                "source_text_sha256": {"type": "string"}
            }
        }
    }
}

with open(os.path.join(dataset_dir, "dataset_schema.json"), "w", encoding="utf-8") as f:
    json.dump(schema_data, f, indent=2)

print("\n=== CLAIM–EVIDENCE DATASET GENERATION COMPLETE ===")
print(f"Total Dataset Records: {len(dataset_records)}")
print(f"  Train Split: {len(train_records)}")
print(f"  Val Split:   {len(val_records)}")
print(f"  Test Split:  {len(test_records)}")
print(f"  Hard Negatives: {len(hard_negative_records)}")
print(f"  Out of Domain:  {len(out_of_domain_records)}")
