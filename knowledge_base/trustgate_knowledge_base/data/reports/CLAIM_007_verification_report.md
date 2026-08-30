# TrustGate Verification Report
**Report ID**: `REPORT_CLAIM_007` | **Pipeline**: `TrustGate-AI v1.0.0`
**Processing Time**: `31.17 ms`

---

## Claim
> Under Section 303 of the BNS, a person convicted of theft is sentenced only to twenty years of mandatory solitary confinement.

## Final Verdict
### **`REFUTED`** (Confidence: `0.92`)

## Trust Score
### **`5.66 / 100.0`** — **`VERY_LOW`**

| Component | Score | Weight |
| :--- | :--- | :--- |
| Verification Confidence | `0.9200` | 0.35 |
| Evidence Relevance | `0.4480` | 0.25 |
| Evidence Sufficiency | `0.7240` | 0.15 |
| Source Authority | `1.0000` | 0.15 |
| Evidence Consistency | `0.8000` | 0.10 |

## Verification Explanation
Retrieved authoritative evidence directly contradicts the legal or factual proposition in the claim.

## Trust Score Explanation
Trust Score is very low (5.66) because authoritative evidence strongly contradicts the claim, even though the verifier has high confidence (0.92) in the REFUTED verdict.

## Evidence Summary

| Rank | Section | Heading | Rerank Score | Relationship | Source File |
| :---: | :---: | :--- | :---: | :---: | :--- |
| 1 | Sec 11 | Solitary confinement | 0.7035 | `REFUTES` | `BNS_2023` (p. 23-24) |
| 2 | Sec 12 | Limit  of  solitary  confinement | 0.5713 | `REFUTES` | `BNS_2023` (p. 24-24) |
| 3 | Sec 261 | Escape  from  confinement  or  custody  negligently  suffered  by  public  servant | 0.3270 | `REFUTES` | `BNS_2023` (p. 82-82) |
| 4 | Sec 303 | Theft | 0.3229 | `INSUFFICIENT` | `BNS_2023` (p. 88-88) |
| 5 | Sec 232 | Threatening  any  person  to  give  false  evidence | 0.3155 | `REFUTES` | `BNS_2023` (p. 76-76) |

### Top Evidence Excerpt
```text

11
.
Solitary confinement
.
—
Whenever any person is convicted of an offence for which under this
Sanhita the Court has power to sentence him to rigorous imprisonment, the Court may, by its sentence,
IndiaCode

[PAGE 24]

24
order  that  the  offend
```

## Evidence Provenance
- **Document**: The Bharatiya Nyaya Sanhita, 2023 (Act No. 45 of 2023)
- **Source Authority**: India Code (Official Primary Gazette)
- **Raw PDF Hash (SHA-256)**: `d4449e9995b21fd52627811d08f9d21feda6a3678b7e5355b651242d152167f5`
- **Extracted Text Hash (SHA-256)**: `f0ee026645e589f3ed7aba4cbbbad60a0a5f2b0a428716e845785acb56d32af5`
- **Traceable Chunks**: `BNS_2023_CH02_SEC11_CHUNK01`, `BNS_2023_CH02_SEC12_CHUNK01`, `BNS_2023_CH14_SEC261_CHUNK01`

---
*Architectural Disclaimer: Claim–evidence verification is a deterministic evidence assessment layer. It does not constitute independent legal advice, does not replace legal professionals, and does not determine legal truth beyond the available retrieved evidence.*