# PolicyGuard

PolicyGuard is a small self-checking AI assistant that answers questions about a company travel policy and verifies its own answer before returning it.

The project demonstrates a simple two-pass LLM workflow designed to catch unsupported or contradicted factual claims.

---

## 1. Problem

LLMs can produce confident answers that are not actually supported by the available source material.

For example, the policy states:

> Domestic hotel accommodation is reimbursable up to INR 4,000 per night.

A model could incorrectly answer:

> Domestic hotel accommodation is reimbursable up to INR 5,000 per night.

PolicyGuard adds a second verification pass that checks the generated answer against the original policy before returning the final response.

---

## 2. Scope

PolicyGuard handles one narrow task:

> Answer questions about a fictional company travel and expense policy.

The self-check focuses on one specific failure mode:

> Unsupported or contradicted factual claims.

The goal is not to solve every possible LLM failure. Instead, the project demonstrates a small, reproducible, and observable verification loop.

---

## 3. Self-Check Loop

PolicyGuard uses two LLM passes.

```text
User Question
      |
      v
Pass 1: Generate Draft
      |
      v
Extract Factual Claims
      |
      v
Pass 2: Verify Claims
      |
      v
Supported / Unsupported / Contradicted
      |
      v
Correct or Flag
      |
      v
Verified Answer
```

### Pass 1 — Draft

The first LLM call receives:

- The user's question
- The source policy
- Instructions to generate an answer
- Instructions to extract factual claims

It returns structured JSON containing the draft answer and its claims.

### Pass 2 — Verification

The second LLM call receives:

- The user's question
- The original policy
- The draft answer
- The extracted claims

Each claim is classified as:

- `supported`
- `unsupported`
- `contradicted`

For unsupported or contradicted claims, the verifier provides evidence from the policy and a correction.

### Final Step

If all claims are supported, the draft answer is returned.

If a factual problem is detected, the system applies the available policy-backed correction or flags the answer when it cannot be safely corrected.

---

## 4. Confident-Wrong Demonstration

The policy states:

> Domestic hotel accommodation is reimbursable up to INR 4,000 per night.

For the reproducible failure demonstration, the draft stage is intentionally prompted to produce a plausible incorrect answer.

### Draft Answer

> Domestic hotel accommodation is reimbursable up to INR 5,000 per night.

### Self-Check

**Claim**

> Domestic hotel accommodation is reimbursable up to INR 5,000 per night.

**Verdict**

`contradicted`

**Evidence**

> Hotel accommodation is reimbursable up to INR 4,000 per night for domestic travel.

**Correction**

> Domestic hotel accommodation is reimbursable up to INR 4,000 per night.

### Verified Answer

> Domestic hotel accommodation is reimbursable up to INR 4,000 per night.

This demonstrates that the second pass can catch and correct a deliberately introduced confident error.

---

## 5. Design Decisions

The implementation was intentionally kept small and focused on the reliability loop.

- No database was required.
- The policy is stored as a local text file.
- The LLM is used for both drafting and verification.
- Pydantic is used to validate structured LLM responses.
- The verification pass independently checks claims against the source policy.
- The failure demonstration uses a controlled incorrect draft so that the failure case is reproducible.
- The project exposes the draft, verification evidence, correction, and final result.

The main engineering focus is the verification loop rather than adding unnecessary infrastructure.

---

## 6. Project Structure

```text
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
```

### Main Components

| File | Purpose |
|---|---|
| `app/main.py` | FastAPI application and self-check workflow |
| `app/draft.py` | Generates the first-pass answer and claims |
| `app/checker.py` | Verifies claims against the policy |
| `app/models.py` | Pydantic response models |
| `app/llm.py` | LLM client configuration |
| `app/policy.txt` | Source travel policy |
| `static/index.html` | Web interface |
| `static/style.css` | UI styling |
| `static/app.js` | Frontend interaction and API handling |
| `tests/test_cases.json` | Test case record |

---

## 7. Setup

### Clone the Repository

```bash
git clone https://github.com/Akhil-011/Policyguard.git
cd Policyguard
```

### Create a Virtual Environment

#### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configure Environment Variables

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=your_model_name
```

Do **not** commit `.env` or API keys to the repository.

The repository contains `.env.example` as a safe configuration template.

---

## 8. Run the Application

From the project root:

```bash
uvicorn app.main:app --reload
```

Open the application in a browser:

```text
http://127.0.0.1:8000
```

---

## 9. Testing

The system was tested using six manually designed cases covering:

- Directly supported policy information
- Policy deadlines
- Policy restrictions
- Multiple claims in one question
- A deliberately introduced confident-wrong answer
- A question about information absent from the policy

### Test Results

| # | Test Case | Purpose | Result |
|---|---|---|---|
| 1 | Domestic hotel limit | Verify a directly supported factual claim | PASSED |
| 2 | Expense claim deadline | Verify a policy deadline | PASSED |
| 3 | Business-class reimbursement | Verify a policy restriction | PASSED |
| 4 | Meal allowance + receipt | Verify multiple factual claims | PASSED |
| 5 | Hotel limit with failure injection | Catch a confident-wrong claim | CORRECTED |
| 6 | Taxi reimbursement | Check that unsupported information is not invented | The policy does not specify a maximum taxi reimbursement. |

> **Note:** Update Test 6 with the actual result observed during the final test run. Do not claim `FLAGGED` unless the application actually returned that result.

---

## 10. Failure Handling

PolicyGuard handles three verification outcomes.

### Supported

The claim is directly supported by the source policy.

```text
supported
    |
    v
Return the answer
```

### Contradicted

The policy states something different from the generated claim.

```text
contradicted
    |
    v
Provide policy evidence
    |
    v
Apply correction
```

### Unsupported

The policy does not contain enough information to support the claim.

```text
unsupported
    |
    v
Provide verification status
    |
    v
Flag when it cannot be safely corrected
```

---

## 11. Development Failure

During development, the verification model sometimes returned valid JSON for supported claims but omitted the `correction` field.

Initially, `correction` was required by the Pydantic response model. This caused response validation errors.

The schema was changed so that `correction` is optional for supported claims while remaining available for unsupported or contradicted claims.

Additional handling was added for:

- Empty LLM responses
- Invalid JSON
- Markdown code fences around JSON
- Structured response validation

This made the loop more tolerant of imperfect model output.

---

## 12. Limitations

PolicyGuard is intentionally small and has some limitations:

- Verification itself depends on an LLM.
- A verifier can still potentially miss subtle errors.
- The current source is a single local policy document.
- There is no persistent database or conversation history.
- The correction logic is designed for this narrow task.
- The confident-wrong case is a controlled failure demonstration rather than an organically occurring hallucination.

---

## 13. Possible Improvements

If the prototype were extended further, possible improvements include:

- Deterministic validation for numerical claims
- Exact evidence or citation spans
- Larger automated evaluation sets
- Multiple policy documents
- Improved handling of multi-claim answers
- Audit logging
- Confidence thresholds
- Human review for unresolved claims

The complete source code and setup instructions are available in this repository.