#!/usr/bin/env python3
import asyncio
import json
import re
from datetime import date
from pathlib import Path
from agno.tools.mcp import MCPTools
from discovery import create_discovery_agent
from evaluation import Evaluation, evaluation_agent

ROOT = Path(__file__).parent
CONFIG_FILE = ROOT / "config.json"
RESUME_FILE = ROOT / "data" / "resume.md"
SEEN_FILE = ROOT / "data" / "seen.txt"
JOBS_DIR = ROOT / "job-descriptions"
REPORTS_DIR = ROOT / "reports"

MAX_JOBS_PER_RUN = 50
FITNESS_THRESHOLD = 7.5

def get_job_url(jd: str) -> str:
    """Extract the source URL written into a JD Markdown file."""
    match = re.search(r"^URL:\s*(.+)$", jd, re.MULTILINE)
    if not match:
        raise ValueError("JD is missing a URL field")
    return match.group(1).strip()

async def main():
    config = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    resume = RESUME_FILE.read_text(encoding="utf-8")

    seen = set()
    if SEEN_FILE.exists():
        seen = {
            line.strip()
            for line in SEEN_FILE.read_text(encoding="utf-8").splitlines()
            if line.strip()
        }

    # job-descriptions is scratch space for the current run.
    JOBS_DIR.mkdir(exist_ok=True)
    for path in JOBS_DIR.glob("*.md"):
        path.unlink()

    # Discovery uses Playwright MCP and saves each JD as Markdown.
    async with MCPTools(command="npx -y @playwright/mcp@latest --headless") as browser_tools:
        discovery_agent = create_discovery_agent(browser_tools)

        for site in config["sites"]:
            print(f"Discovering jobs at {site['name']}...")
            await discovery_agent.arun(
                f"""
Find jobs for {site['name']} using this exact listing URL:
{site['url']}

Treat that URL as the authoritative scope of the search. Preserve any filters
encoded in the URL and only process jobs that belong to that filtered result
set. You may follow pagination, Load More, or infinite scrolling within that
result set, but do not broaden the search to other jobs on the site.
"""
            )

    job_files = sorted(JOBS_DIR.glob("*.md"))
    matches: list[tuple[Evaluation, str]] = []
    evaluated_count = 0
    skipped_count = 0

    # main.py decides what needs evaluation. The agent never sees an old JD.
    for path in job_files:
        jd = path.read_text(encoding="utf-8")
        url = get_job_url(jd)

        if url in seen:
            skipped_count += 1
            continue

        if evaluated_count >= MAX_JOBS_PER_RUN:
            break

        print(f"Evaluating {path.name}...")
        response = await evaluation_agent.arun(
            f"""
Evaluate this job against the candidate's resume.

RESUME
------
{resume}

JOB DESCRIPTION
---------------
{jd}
"""
        )

        result = response.content
        if not isinstance(result, Evaluation):
            raise ValueError(f"Expected structured Evaluation result, got: {result!r}")

        evaluated_count += 1

        # Mark every successfully evaluated job as seen, regardless of score.
        seen.add(url)
        SEEN_FILE.parent.mkdir(exist_ok=True)
        with SEEN_FILE.open("a", encoding="utf-8") as f:
            f.write(url + "\n")

        if result.score >= FITNESS_THRESHOLD:
            matches.append((result, url))

    # Write one report for the run, with the summary at the top.
    REPORTS_DIR.mkdir(exist_ok=True)
    report = REPORTS_DIR / f"{date.today().isoformat()}.md"

    lines = [
        f"# Job Report — {date.today().isoformat()}",
        "",
        f"- JDs discovered: {len(job_files)}",
        f"- Previously evaluated JDs skipped: {skipped_count}",
        f"- New JDs evaluated: {evaluated_count}",
        f"- Matches scoring {FITNESS_THRESHOLD:.1f} or higher: {len(matches)}",
        "",
        "## Matches",
        "",
    ]

    if matches:
        for result, url in matches:
            lines.extend(
                [
                    f"### {result.title} — {result.company}",
                    "",
                    f"**Match score:** {result.score:.1f}/10  ",
                    f"**URL:** {url}",
                    "",
                    result.summary.strip(),
                    "",
                ]
            )
    else:
        lines.extend(["No jobs met the reporting threshold.", ""])

    report.write_text("\n".join(lines), encoding="utf-8")

    print(
        f"Done. Discovered {len(job_files)}, skipped {skipped_count}, "
        f"evaluated {evaluated_count}, matched {len(matches)}."
    )

if __name__ == "__main__":
    asyncio.run(main())
