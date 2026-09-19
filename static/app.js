async function checkAnswer() {

    const question =
        document.getElementById("question").value.trim();

    const demoFailure =
        document.getElementById("demoFailure").checked;

    const button =
        document.getElementById("checkButton");

    if (!question) {
        alert("Please enter a question.");
        return;
    }

    document.getElementById("loading")
        .classList.remove("hidden");

    document.getElementById("result")
        .classList.add("hidden");

    button.disabled = true;
    button.style.opacity = "0.6";

    try {

        const response = await fetch("/check", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                question: question,
                demo_failure: demoFailure
            })

        });

        if (!response.ok) {
            throw new Error(
                `Server returned ${response.status}`
            );
        }

        const data = await response.json();


        // -------------------------
        // Draft answer
        // -------------------------

        document.getElementById("draft").textContent =
            data.draft_answer;


        // -------------------------
        // Verification checks
        // -------------------------

        const checksContainer =
            document.getElementById("checks");

        checksContainer.innerHTML = "";


        data.checks.forEach(check => {

            const item =
                document.createElement("div");

            item.className = "check";

            item.innerHTML = `
                <p>
                    <strong>Claim:</strong>
                    ${escapeHtml(check.claim)}
                </p>

                <p>
                    <strong>Verdict:</strong>
                    ${escapeHtml(check.verdict)}
                </p>

                <p>
                    <strong>Evidence:</strong>
                    ${escapeHtml(check.evidence)}
                </p>

                ${
                    check.correction
                    ?
                    `
                    <p>
                        <strong>Correction:</strong>
                        ${escapeHtml(check.correction)}
                    </p>
                    `
                    :
                    ""
                }
            `;

            checksContainer.appendChild(item);

        });


        // -------------------------
        // Final answer
        // -------------------------

        document.getElementById("final").textContent =
            data.final_answer;


        // -------------------------
        // Status
        // -------------------------

        const statusElement =
            document.getElementById("status");

        const resultBadge =
            document.getElementById("resultBadge");


        if (data.status === "corrected") {

            resultBadge.textContent = "CORRECTED";

            resultBadge.className =
                "result-badge result-corrected";

            statusElement.textContent =
                "The self-check detected a contradicted or unsupported claim and applied a policy-backed correction.";

        }

        else if (data.status === "flagged") {

            resultBadge.textContent = "FLAGGED";

            resultBadge.className =
                "result-badge result-flagged";

            statusElement.textContent =
                "The answer could not be safely verified against the provided policy.";

        }

        else {

            resultBadge.textContent = "PASSED";

            resultBadge.className =
                "result-badge result-passed";

            statusElement.textContent =
                "All generated claims were supported by the provided policy.";

        }


        document.getElementById("result")
            .classList.remove("hidden");

    }

    catch (error) {

        alert(
            "Something went wrong: " +
            error.message
        );

    }

    finally {

        document.getElementById("loading")
            .classList.add("hidden");

        button.disabled = false;
        button.style.opacity = "1";

    }
}


function escapeHtml(value) {

    const div =
        document.createElement("div");

    div.textContent = value;

    return div.innerHTML;
}