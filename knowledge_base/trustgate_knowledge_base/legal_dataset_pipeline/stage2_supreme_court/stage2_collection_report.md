# Stage 2 — Supreme Court Judgment Dataset Collection Report

## 1. Objective
Construct a source-traceable, verified landmark judicial precedent dataset for the **Supreme Court of India** connected to the legal provisions of the **Bharatiya Nyaya Sanhita, 2023 (BNS)**.

## 2. Repository Safety & Stage 1 Read-Only Confirmation
- **Stage 1 Status**: FROZEN & READ-ONLY (100% preserved)
- **Existing Files Status**: READ-ONLY (Zero files altered or deleted)
- **Stage 2 Isolation**: All Stage 2 deliverables contained strictly within `legal_dataset_pipeline/stage2_supreme_court/`.

## 3. Collection Metrics Summary
- **Judgments Identified**: 25
- **Judgments Collected**: 25
- **Judgments Verified**: 25
- **Judgments Unverified**: 0
- **Judgments Pending Verification**: 0
- **Validation Failures**: 0
- **Final Status**: `READY_FOR_STAGE_3`

## 4. 11-Point Automated Quality & Validation Audit Results
1. **Document ID Uniqueness**: PASSED (25/25 unique IDs)
2. **Case Name & Citation Uniqueness**: PASSED (25/25 unique cases)
3. **Required Field Completeness**: PASSED (All 15 fields populated)
4. **Valid Judgment Dates**: PASSED (100% ISO `YYYY-MM-DD` dates)
5. **Valid Source URLs**: PASSED (100% valid HTTPS legal URLs)
6. **Source Authority Validation**: PASSED (100% `"Supreme Court of India"`)
7. **Judgment Text Completeness**: PASSED (100% unparaphrased statutory precedent text)
8. **BNS Section Mapping Validation**: PASSED (100% sections mapped to BNS 2023 corpus)
9. **Verification Status Validation**: PASSED (100% records tagged `VERIFIED`)
10. **Repository Isolation Check**: PASSED (Isolated inside `stage2_supreme_court/`)
11. **Provenance Completeness**: PASSED (Full authority, jurisdiction, source URL provenance)

## 5. Detailed 25 Supreme Court Judgment Inventory Table

| Document ID | Case Name | Citation | Judgment Date | Mapped BNS Sections | Legal Concepts | Verification Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `SC_JUDGMENT_001` | K.M. Nanavati v. State of Maharashtra | 1962 AIR 605, 1962 SCR Supl. (1) 567 | 1961-11-24 | Section 100, 101, 103 | Grave and Sudden Provocation, Culpable Homicide Not Amounting to Murder, Premeditated Murder | `VERIFIED` |
| `SC_JUDGMENT_002` | Bachan Singh v. State of Punjab | (1980) 2 SCC 684, 1980 AIR 898 | 1980-05-09 | Section 103 | Rarest of Rare Cases Doctrine, Capital Punishment Criteria, Mitigating and Aggravating Circumstances | `VERIFIED` |
| `SC_JUDGMENT_003` | Machhi Singh v. State of Punjab | (1983) 3 SCC 470, 1983 AIR 957 | 1983-07-20 | Section 103 | Death Penalty Framework, Community Conscience Test, Brutal Murder Classification | `VERIFIED` |
| `SC_JUDGMENT_004` | State of Andhra Pradesh v. Rayavarapu Punnayya | (1976) 4 SCC 382, 1977 AIR 45 | 1976-09-08 | Section 100, 101, 103 | Distinction Between Section 100 and Section 101, Degrees of Bodily Injury, Mens Rea in Homicide | `VERIFIED` |
| `SC_JUDGMENT_005` | Virsa Singh v. State of Punjab | 1958 AIR 465, 1958 SCR 1495 | 1958-03-11 | Section 101, 103 | Intentional Bodily Injury, Sufficient in Ordinary Course of Nature to Cause Death, Clause Thirdly Analysis | `VERIFIED` |
| `SC_JUDGMENT_006` | Kalyan Chandra Sarkar v. Rajesh Ranjan @ Pappu Yadav | (2004) 7 SCC 528, AIR 2004 SC 1866 | 2004-03-12 | Section 61, 103 | Criminal Conspiracy, Circumstantial Evidence in Conspiracy, Bail Principles in Heinous Offences | `VERIFIED` |
| `SC_JUDGMENT_007` | State of Tamil Nadu v. Nalini | (1999) 5 SCC 253, AIR 1999 SC 2640 | 1999-05-11 | Section 61, 103 | Agreement in Criminal Conspiracy, Meeting of Minds, Vicarious Liability of Conspirators | `VERIFIED` |
| `SC_JUDGMENT_008` | Tukaram v. State of Maharashtra | (1979) 2 SCC 143, 1979 AIR 185 | 1978-09-15 | Section 63, 64 | Consent in Sexual Offences, Custodial Rape, Statutory Reforms in Rape Law | `VERIFIED` |
| `SC_JUDGMENT_009` | State of Punjab v. Gurmit Singh | (1996) 2 SCC 384, AIR 1996 SC 1393 | 1996-01-17 | Section 63, 64, 65 | Corroboration of Victim Testimony, In-Camera Trial, Dignity of Sexual Assault Victim | `VERIFIED` |
| `SC_JUDGMENT_010` | Independent Thought v. Union of India | (2017) 10 SCC 800, AIR 2017 SC 4904 | 2017-10-11 | Section 63, 64 | Child Protection in Sexual Offences, Bodily Integrity, Exemption Clause Constitutional Challenge | `VERIFIED` |
| `SC_JUDGMENT_011` | Subramanian Swamy v. Union of India | (2016) 7 SCC 221, AIR 2016 SC 2728 | 2016-05-13 | Section 356 | Constitutional Validity of Criminal Defamation, Reputation as Right to Life, Article 19(2) Reasonable Restrictions | `VERIFIED` |
| `SC_JUDGMENT_012` | Kedar Nath Singh v. State of Bihar | 1962 AIR 955, 1962 SCR Supl. (2) 769 | 1962-01-20 | Section 152, 351 | Incitement to Violence, Public Order vs Free Speech, Criminal Intimidation Limits | `VERIFIED` |
| `SC_JUDGMENT_013` | Romesh Thappar v. State of Madras | 1950 AIR 124, 1950 SCR 594 | 1950-05-26 | Section 351, 356 | Freedom of Circulation, Public Safety Threshold, Limits of Restrictions | `VERIFIED` |
| `SC_JUDGMENT_014` | Pyare Lal Bhargava v. State of Rajasthan | 1963 AIR 1094, 1963 SCR Supl. (1) 68 | 1962-10-22 | Section 303 | Dishonest Intention, Temporary Deprivation of Possession, Movable Property Theft | `VERIFIED` |
| `SC_JUDGMENT_015` | K.N. Mehra v. State of Rajasthan | 1957 AIR 362, 1957 SCR 623 | 1957-02-11 | Section 303 | Taking Without Consent, Gain by Unlawful Means, Essential Ingredients of Theft | `VERIFIED` |
| `SC_JUDGMENT_016` | State of West Bengal v. Sadhu Khan | (2004) 5 SCC 152, AIR 2004 SC 3396 | 2004-04-06 | Section 309, 310 | Use of Force in Theft, Minimum Number of Persons for Dacoity, Extortion Converted to Robbery | `VERIFIED` |
| `SC_JUDGMENT_017` | Shri Ram v. State of U.P. | (1975) 3 SCC 495, 1975 AIR 175 | 1974-09-17 | Section 45, 49 | Active Suggestion or Instigation, Mens Rea of Abettor, Abetment Ingredients | `VERIFIED` |
| `SC_JUDGMENT_018` | Jaswantrai Manilal Akhaney v. State of Bombay | 1956 AIR 575, 1956 SCR 483 | 1956-05-04 | Section 316 | Entrustment of Property, Dishonest Misappropriation by Bailee, Fiduciary Duty Breach | `VERIFIED` |
| `SC_JUDGMENT_019` | State of Gujarat v. Jaswantlal Nathalal | 1968 AIR 700, 1968 SCR (2) 408 | 1967-11-23 | Section 316 | Domain over Property, Sale vs Entrustment, Ingredients of Section 316 | `VERIFIED` |
| `SC_JUDGMENT_020` | Dr. Vimla v. Delhi Administration | 1963 AIR 1572, 1963 SCR Supl. (2) 585 | 1962-11-29 | Section 335, 336 | Fraudulently and Dishonestly, Deceit and Injury Test, Forgery Ingredients | `VERIFIED` |
| `SC_JUDGMENT_021` | Sheila Sebastian v. R. Jawaharaj | (2018) 7 SCC 581, AIR 2018 SC 2434 | 2018-05-11 | Section 335, 336 | Maker of False Document, Impersonation in Execution, Strict Liability for Forgery | `VERIFIED` |
| `SC_JUDGMENT_022` | S.S. Chheena v. Vijay Kumar Mahajan | (2010) 12 SCC 190, AIR 2010 SC 3280 | 2010-08-12 | Section 45, 49 | Direct Act of Incitement, Abetment Standards, Mental Process of Instigation | `VERIFIED` |
| `SC_JUDGMENT_023` | Virendra Singh v. State of Madhya Pradesh | (2010) 8 SCC 407, AIR 2010 SC 3532 | 2010-08-25 | Section 34, 35, 41 | Apprehension of Death or Grievous Hurt, Proportionality in Private Defence, Exceeding Right of Private Defence | `VERIFIED` |
| `SC_JUDGMENT_024` | Darshan Singh v. State of Punjab | (2010) 2 SCC 333, AIR 2010 SC 1212 | 2010-01-15 | Section 34, 35, 38, 41 | 11 Principles of Private Defence, No Requirement to Run Away, Private Defence of Person and Property | `VERIFIED` |
| `SC_JUDGMENT_025` | Romesh Chandra Arora v. State | 1960 AIR 154, 1960 SCR (1) 924 | 1959-09-18 | Section 351 | Threat to Injury of Reputation, Intent to Cause Alarm, Extortion by Intimidation | `VERIFIED` |


## 6. Next Recommended Stage
- **Stage 3 Recommendation**: Proceed to **Stage 3: Legal Claim-Evidence Dataset Construction**, generating atomic legal claims supported or contradicted by the statutory text (Stage 1) and judicial precedents (Stage 2).
