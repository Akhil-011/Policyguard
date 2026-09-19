PolicyGuard

PolicyGuard is a small self-checking AI assistant that answers questions about a company travel policy and verifies its own answer before returning it.

It demonstrates a two-pass LLM workflow:

User Question
     ↓
Pass 1 — LLM generates answer
     ↓
Extract factual claims
     ↓
Pass 2 — LLM checks claims against policy
     ↓
Supported / Unsupported / Contradicted
     ↓
Correct or Flag
     ↓
Verified Answer

1. Problem
LLMs can produce confident answers that aren't actually supported by the available source material.

For example, the policy says:

Domestic hotel reimbursement: INR 4,000 per night.

A model might incorrectly answer:

Domestic hotel reimbursement: INR 5,000 per night.

PolicyGuard adds a second verification pass to detect this type of factual error before the answer is returned.

2. Scope
The tool handles one narrow task:

Answer questions about a fictional company travel and expense policy.

The self-check focuses on one specific failure mode:

Unsupported or contradicted factual claims.

The system doesn't attempt to solve every type of LLM failure. The goal is to demonstrate a small, reliable verification loop.

3. How the Self-Check Loop Works
Pass 1 — Draft

The first LLM call receives:

User question
Travel policy
Instructions to generate an answer
Instructions to extract factual claims

It returns structured JSON containing the answer and claims.

Pass 2 — Verification

The second LLM call receives:

User question
Policy
Draft answer
Claims from the draft

Each claim is classified as:

supported
unsupported
contradicted

If a claim is unsupported or contradicted, the checker provides evidence from the policy and a correction.

Final Step

If all claims are supported, the draft answer is returned.

If a factual problem is detected, the system uses the correction or flags the answer if it cannot safely correct it.

4. Confident-Wrong Demonstration
Policy:

Domestic hotel accommodation is reimbursable up to INR 4,000 per night.

For the required failure demonstration, the draft stage is intentionally prompted to produce a plausible incorrect answer:

Draft:

Domestic hotel accommodation is reimbursable up to INR 5,000 per night.

Self-check:

Claim: Hotel reimbursement is INR 5,000 per night.

Verdict: contradicted

Evidence: The policy states that domestic hotel accommodation
is reimbursable up to INR 4,000 per night.

Correction: Hotel accommodation is reimbursable up to
INR 4,000 per night.

Verified answer:

Hotel accommodation is reimbursable up to INR 4,000 per night.

This demonstrates that the second pass can catch and correct a deliberately introduced confident error.

5. Design Decisions
I kept the implementation intentionally small.

No database was required.
The policy is stored as a local text file.
The LLM is used for both drafting and verification.
Pydantic is used to validate structured responses.
The checker independently compares claims against the policy.
The failure demonstration uses a controlled incorrect draft so the failure case is reproducible.

The important part of the project is the verification loop, rather than building a large application around it.

6. Project Structure
policyguard/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── models.py
│   ├── llm.py
│   ├── draft.py
│   ├── checker.py
│   └── policy.txt
│
├── static/
│   ├── index.html
│   ├── style.css
│   └── app.js
│
├── tests/
│   └── test_cases.json
│
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md

7. Setup
Clone the repository
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd policyguard
Create virtual environment

Windows:

python -m venv venv
venv\Scripts\activate
Install dependencies
pip install -r requirements.txt
Configure environment variables

Create a .env file:

OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=your_model_name

Do not commit .env or API keys to the repository.

8. Run the Application

From the project root:

uvicorn app.main:app --reload

Open:

http://127.0.0.1:8000

9. Testing

I tested the system using six cases covering:

Directly supported policy information
Policy deadlines
Policy restrictions
Multiple claims in one question
A deliberately introduced confident-wrong answer
A question about information that is absent from the policy
Test Results
#	Test	Purpose	Result
1	Domestic hotel limit	Supported factual claim	PASSED
2	Expense claim deadline	Policy deadline	PASSED
3	Business-class reimbursement	Policy restriction	PASSED
4	Meal allowance + receipt	Multiple claims	PASSED
5	Hotel limit with failure injection	Catch confident wrong claim	CORRECTED
6	Taxi reimbursement	Avoid unsupported information	PUT YOUR ACTUAL RESULT HERE

Important: For Test 6, don't write FLAGGED unless that's what your actual run returned.

10. Failure Handling
The system handles three verification outcomes:

Supported

The claim is directly supported by the policy.

supported → return the answer
Contradicted

The policy says something different.

contradicted → provide evidence → correct the answer
Unsupported

The policy doesn't contain enough information to support the claim.

unsupported → provide evidence/status → flag if it cannot be safely corrected

11. Limitations

PolicyGuard is intentionally small and has some limitations:

Verification itself depends on an LLM.
A verifier can still potentially miss subtle errors.
The current source is a single local policy document.
There is no persistent database or conversation history.
The correction logic is designed for this narrow task.
The confident-wrong case is a controlled failure demonstration rather than an organically occurring hallucination.

12. Possible Improvements
If this were extended beyond the prototype, possible improvements include:

Deterministic validation for numerical claims
Exact evidence/citation spans
Larger automated evaluation sets
Multiple policy documents
Better handling of multi-claim answers
Audit logging
Confidence thresholds
Human review for unresolved claims