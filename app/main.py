from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.draft import generate_draft
from app.checker import check_claims
from app.models import FinalResult


POLICY_PATH = Path(__file__).parent / "policy.txt"

app = FastAPI(title="PolicyGuard")


class QuestionRequest(BaseModel):
    question: str
    demo_failure: bool = False


def load_policy() -> str:
    return POLICY_PATH.read_text(encoding="utf-8")


def run_self_check(
    question: str,
    force_failure: bool = False
) -> FinalResult:

    policy = load_policy()

    # Pass 1: Generate draft
    draft = generate_draft(
        question=question,
        policy=policy,
        force_failure=force_failure
    )

    # Pass 2: Verify draft claims
    checks = check_claims(
        question=question,
        draft_answer=draft.answer,
        claims=draft.claims,
        policy=policy
    )

    failed_checks = [
        check
        for check in checks
        if check.verdict in {"unsupported", "contradicted"}
    ]

    # No problems found
    if not failed_checks:
        final_answer = draft.answer
        status = "passed"

    # Problems found
    else:
        corrections = [
            check.correction
            for check in failed_checks
            if check.correction
        ]

        if corrections:
            final_answer = " ".join(corrections)
            status = "corrected"

        else:
            final_answer = (
                "The draft answer could not be safely verified "
                "against the provided policy."
            )
            status = "flagged"

    return FinalResult(
        question=question,
        draft_answer=draft.answer,
        final_answer=final_answer,
        status=status,
        checks=checks
    )


@app.post("/check", response_model=FinalResult)
def check_question(request: QuestionRequest):

    return run_self_check(
        question=request.question,
        force_failure=request.demo_failure
    )


@app.get("/health")
def health():
    return {"status": "ok"}


app.mount(
    "/",
    StaticFiles(directory="static", html=True),
    name="static"
)