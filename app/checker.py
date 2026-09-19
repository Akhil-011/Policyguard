import json
from typing import List

from app.llm import client, MODEL
from app.models import ClaimCheck


def check_claims(
    question: str,
    draft_answer: str,
    claims: List[str],
    policy: str
) -> List[ClaimCheck]:

    claims_text = "\n".join(
        f"{i + 1}. {claim}"
        for i, claim in enumerate(claims)
    )

    prompt = f"""
You are a strict factual verification system.

Your job is to check whether each claim in an AI-generated answer
is supported by the provided policy.

Only use the policy as evidence.

For every claim:

- "supported" = directly supported by the policy
- "unsupported" = the policy does not provide support
- "contradicted" = the policy states something different

For unsupported or contradicted claims, provide a correction
based only on the policy.

USER QUESTION:
{question}

POLICY:
{policy}

DRAFT ANSWER:
{draft_answer}

CLAIMS TO VERIFY:
{claims_text}

Return ONLY a JSON array.
Do not use markdown.
Do not use ```.

Example:
[
  {{
    "claim": "Hotel reimbursement is INR 5000 per night.",
    "verdict": "contradicted",
    "evidence": "Hotel accommodation is reimbursable up to INR 4000 per night.",
    "correction": "Hotel accommodation is reimbursable up to INR 4000 per night."
  }}
]
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are a strict source-grounded verification system. Return valid JSON only."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0,
        max_tokens=1500
    )

    content = response.choices[0].message.content

    if not content:
        raise RuntimeError(
            "The verification model returned an empty response. "
            "Try running the test again."
        )

    # Remove accidental markdown fences if the model adds them.
    content = content.strip()

    if content.startswith("```"):
        content = content.replace("```json", "")
        content = content.replace("```", "")
        content = content.strip()

    try:
        data = json.loads(content)
    except json.JSONDecodeError as error:
        raise RuntimeError(
            f"The verification model returned invalid JSON.\n"
            f"Model output:\n{content}\n"
            f"JSON error: {error}"
        )

    return [
        ClaimCheck.model_validate(item)
        for item in data
    ]