"""Evaluation agent: score one JD against the supplied resume."""

from pathlib import Path
from agno.agent import Agent
from agno.models.openai import OpenAIResponses
from agno.skills import LocalSkills, Skills
from pydantic import BaseModel, Field

ROOT = Path(__file__).parent
SKILLS_DIR = ROOT / "skills"

MODEL = "gpt-5.4-mini"
REASONING_EFFORT = "low"

class Evaluation(BaseModel):
    """Structured result returned by the evaluation agent."""

    title: str = Field(description="Job title from the supplied JD")
    company: str = Field(description="Company name from the supplied JD")
    score: float = Field(ge=0.0, le=10.0, description="Fitness score from 0.0 to 10.0")
    summary: str = Field(
        description=(
            "For a strong match, one concise paragraph describing the role and the "
            "candidate's strongest matches and important gaps. May be empty for a weak match."
        )
    )

evaluation_agent = Agent(
    model=OpenAIResponses(id=MODEL, reasoning_effort=REASONING_EFFORT),
    skills=Skills(loaders=[LocalSkills(str(SKILLS_DIR))]),
    output_schema=Evaluation,
    instructions=[
        "You evaluate one job at a time against one candidate's resume.",
        "Load the fitness-scoring skill and follow its rubric.",
        "Use only evidence in the supplied resume and job description.",
        "Return the job title, company, fitness score, and a concise summary.",
        "For strong matches, the summary should explain the role, strongest matches, and important gaps.",
    ],
    markdown=False,
)
