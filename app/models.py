from typing import List, Optional
from pydantic import BaseModel


class ClaimCheck(BaseModel):
    claim: str
    verdict: str
    evidence: str
    correction: Optional[str] = ""


class DraftResult(BaseModel):
    answer: str
    claims: List[str]


class FinalResult(BaseModel):
    question: str
    draft_answer: str
    final_answer: str
    status: str
    checks: List[ClaimCheck]