"""Discovery agent: browse career sites and save job descriptions."""

import hashlib
import re
from pathlib import Path
from agno.agent import Agent
from agno.models.openai import OpenAIResponses
from agno.skills import LocalSkills, Skills
from agno.tools import tool

ROOT = Path(__file__).parent
SKILLS_DIR = ROOT / "skills"
JOBS_DIR = ROOT / "job-descriptions"

MODEL = "gpt-5.4-mini"
REASONING_EFFORT = "low"

@tool
def save_job_description(
    title: str,
    company: str,
    url: str,
    description: str,
    location: str = "",
) -> str:
    """Save one discovered job description as a Markdown file."""
    JOBS_DIR.mkdir(exist_ok=True)

    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:60] or "job"
    suffix = hashlib.sha1(url.encode("utf-8")).hexdigest()[:8]
    path = JOBS_DIR / f"{slug}-{suffix}.md"

    path.write_text(
        f"# {title}\n\n"
        f"Company: {company}\n"
        f"Location: {location or 'Not specified'}\n"
        f"URL: {url}\n\n"
        f"## Job Description\n\n{description.strip()}\n",
        encoding="utf-8",
    )
    return f"Saved {path.name}"

def create_discovery_agent(browser_tools):
    """Create the discovery agent using an active Playwright MCP toolset."""
    return Agent(
        model=OpenAIResponses(id=MODEL, reasoning_effort=REASONING_EFFORT),
        tools=[browser_tools, save_job_description],
        skills=Skills(loaders=[LocalSkills(str(SKILLS_DIR))]),
        instructions=[
            "You discover job postings on career sites.",
            "Load the pagination-strategies and job-link-extraction skills.",
            "The listing URL supplied in the prompt defines the exact scope of the search.",
            "Preserve filters encoded in that URL; never replace it with a broader site-wide jobs listing.",
            "Browse all pages or dynamically loaded results only within that scoped listing.",
            "Only process job-detail links found in that scoped result set or its pagination/load-more continuation.",
            "For each job, open its detail page and read the complete job description.",
            "Call save_job_description with the title, company, URL, location if available, and full JD text.",
            "Do not save navigation pages, search pages, or application forms as job descriptions.",
        ],
        markdown=False,
    )
