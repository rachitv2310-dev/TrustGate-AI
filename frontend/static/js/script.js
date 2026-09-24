/**
 * TrustGate-AI - Complete Frontend Integration Script
 * Handles verification form submission, calls POST /api/v1/verify/,
 * and renders verification report with trust metrics, claims, verdicts, and evidence.
 */

document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("verification-form");
    if (!form) return;

    const questionInput = document.getElementById("question");
    const responseInput = document.getElementById("response");
    const submitBtn = document.getElementById("btn-submit");

    const loadingContainer = document.getElementById("loading-container");
    const errorContainer = document.getElementById("error-container");
    const errorMessageText = document.getElementById("error-message-text");
    const resultContainer = document.getElementById("result-container");

    const trustScoreEl = document.getElementById("trust-score-value");
    const hallucinationEl = document.getElementById("hallucination-value");
    const resultQuestionEl = document.getElementById("result-question");
    const resultResponseEl = document.getElementById("result-response");
    const claimsContainerEl = document.getElementById("claims-container");

    const API_ENDPOINT = "/api/v1/verify/";

    form.addEventListener("submit", async (event) => {
        event.preventDefault();

        const question = questionInput ? questionInput.value.trim() : "";
        const response = responseInput ? responseInput.value.trim() : "";

        if (!question) {
            showError("Please enter a legal question before starting verification.");
            return;
        }

        // Set Loading State
        setLoadingState(true);

        try {
            const payload = {
                question: question,
                response: response || null
            };

            const res = await fetch(API_ENDPOINT, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(payload)
            });

            if (!res.ok) {
                let errDetail = `HTTP Error ${res.status}`;
                try {
                    const errJson = await res.json();
                    if (errJson && errJson.detail) {
                        errDetail = typeof errJson.detail === "string" ? errJson.detail : JSON.stringify(errJson.detail);
                    }
                } catch (e) {}
                throw new Error(errDetail);
            }

            const report = await res.json();

            if (!report || typeof report !== "object") {
                throw new Error("Invalid response format received from server.");
            }

            renderReport(report);

        } catch (error) {
            console.error("Verification Request Error:", error);
            showError(error.message || "Verification failed. Please check backend connection and try again.");
        } finally {
            setLoadingState(false);
        }
    });

    function setLoadingState(isLoading) {
        if (submitBtn) {
            submitBtn.disabled = isLoading;
            submitBtn.textContent = isLoading ? "Verifying..." : "Verify Response";
        }

        if (isLoading) {
            if (errorContainer) errorContainer.style.display = "none";
            if (resultContainer) resultContainer.style.display = "none";
            if (loadingContainer) loadingContainer.style.display = "block";
        } else {
            if (loadingContainer) loadingContainer.style.display = "none";
        }
    }

    function showError(message) {
        if (errorMessageText) errorMessageText.textContent = message;
        if (loadingContainer) loadingContainer.style.display = "none";
        if (resultContainer) resultContainer.style.display = "none";
        if (errorContainer) errorContainer.style.display = "block";
    }

    function renderReport(report) {
        if (errorContainer) errorContainer.style.display = "none";
        if (loadingContainer) loadingContainer.style.display = "none";

        // Trust Score & Hallucination %
        const trustVal = typeof report.trust_score === "number" ? report.trust_score.toFixed(1) : "0.0";
        const halVal = typeof report.hallucination_percentage === "number" ? report.hallucination_percentage.toFixed(1) : "0.0";

        if (trustScoreEl) trustScoreEl.textContent = `${trustVal} / 100`;
        if (hallucinationEl) hallucinationEl.textContent = `${halVal}%`;

        // Question & AI Response Text
        if (resultQuestionEl) resultQuestionEl.textContent = report.question || "N/A";
        if (resultResponseEl) resultResponseEl.textContent = report.response || "No response text available.";

        // Claims Section
        if (!claimsContainerEl) return;
        claimsContainerEl.innerHTML = "";

        const claims = Array.isArray(report.claims) ? report.claims : [];

        if (claims.length === 0) {
            claimsContainerEl.innerHTML = `
                <div class="no-claims-message">
                    No verifiable claims were extracted from this response.
                </div>
            `;
        } else {
            claims.forEach((claim) => {
                const claimCard = document.createElement("div");
                claimCard.className = "claim-card-wrapper";

                // Claim Header (Title & Badges)
                const claimHeader = document.createElement("div");
                claimHeader.className = "claim-header";

                const claimTitle = document.createElement("div");
                claimTitle.className = "claim-text-title";
                claimTitle.textContent = claim.text || "Unspecified claim statement";

                const claimBadges = document.createElement("div");
                claimBadges.className = "claim-meta-badges";

                // Claim Type Badge
                if (claim.type) {
                    const typeBadge = document.createElement("span");
                    typeBadge.className = `claim-badge claim-badge-${String(claim.type).toLowerCase()}`;
                    typeBadge.textContent = claim.type;
                    claimBadges.appendChild(typeBadge);
                }

                // Verdict Badge (SUPPORTED, CONTRADICTED, INSUFFICIENT)
                const verdictStr = normalizeVerdict(claim.verdict);
                const verdictBadge = document.createElement("span");
                verdictBadge.className = `verdict-badge verdict-${verdictStr.toLowerCase()}`;

                if (verdictStr === "SUPPORTED") {
                    verdictBadge.innerHTML = "&#10004; SUPPORTED";
                } else if (verdictStr === "CONTRADICTED") {
                    verdictBadge.innerHTML = "&#10008; CONTRADICTED";
                } else {
                    verdictBadge.innerHTML = "&#9888; INSUFFICIENT";
                }
                claimBadges.appendChild(verdictBadge);

                claimHeader.appendChild(claimTitle);
                claimHeader.appendChild(claimBadges);
                claimCard.appendChild(claimHeader);

                // Evidence Section
                const evidenceSec = document.createElement("div");
                evidenceSec.className = "evidence-section";

                const evidenceTitle = document.createElement("div");
                evidenceTitle.className = "evidence-title";
                evidenceTitle.textContent = "Supporting Legal Evidence";
                evidenceSec.appendChild(evidenceTitle);

                const evidenceList = document.createElement("div");
                evidenceList.className = "evidence-list";

                const passages = Array.isArray(claim.evidence) ? claim.evidence : [];

                if (passages.length > 0) {
                    passages.forEach((passage) => {
                        const item = document.createElement("div");
                        item.className = "evidence-item";
                        item.textContent = passage;
                        evidenceList.appendChild(item);
                    });
                } else {
                    const noEv = document.createElement("div");
                    noEv.className = "no-evidence";
                    noEv.textContent = "No evidence available.";
                    evidenceList.appendChild(noEv);
                }

                evidenceSec.appendChild(evidenceList);
                claimCard.appendChild(evidenceSec);

                claimsContainerEl.appendChild(claimCard);
            });
        }

        if (resultContainer) resultContainer.style.display = "block";
    }

    function normalizeVerdict(rawVerdict) {
        if (!rawVerdict) return "INSUFFICIENT";
        const v = String(rawVerdict).trim().toUpperCase();
        if (v === "SUPPORTED") return "SUPPORTED";
        if (v === "CONTRADICTED") return "CONTRADICTED";
        return "INSUFFICIENT";
    }
});


