from app.llm import client, MODEL
from app.models import DraftResult


def generate_draft(
    question: str,
    policy: str,
    force_failure: bool = False
) -> DraftResult:

    failure_instruction = ""

    if force_failure:
        failure_instruction = """
For this test case only, produce a plausible but incorrect answer.
Use INR 5,000 as the domestic hotel reimbursement limit, even though
the policy contains the correct value.

This is a deliberate test of the verification system.
Do not mention that the answer was deliberately made wrong.
"""

    prompt = f"""
You are an AI assistant answering questions about a company travel policy.

Use the policy below to answer the user's question.

IMPORTANT:
- Give a concise answer.
- Extract only the minimum number of distinct factual claims needed to verify the answer.
- Do not split one fact into multiple overlapping claims.
- Avoid duplicate or restated claims.
- Return valid JSON only.

{failure_instruction}

POLICY:
{policy}

USER QUESTION:
{question}

Return JSON in exactly this structure:
{{
  "answer": "your answer",
  "claims": [
    "factual claim 1",
    "factual claim 2"
  ]
}}
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": "You answer questions using provided source material."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0,
        max_tokens=1000
    )

    return DraftResult.model_validate_json(
        response.choices[0].message.content
    )