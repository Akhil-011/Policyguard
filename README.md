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