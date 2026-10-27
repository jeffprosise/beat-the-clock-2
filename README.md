# Job Finder

A deliberately small two-agent demo designed to be understandable and buildable live.

- The **discovery agent** uses Playwright through MCP plus the `pagination-strategies` and `job-link-extraction` skills to traverse configured career sites.
- Its conventional `save_job_description` tool saves each discovered JD to `job-descriptions/` as Markdown, including the source URL.
- `main.py` compares those URLs with `data/seen.txt` and sends only previously unevaluated JDs to the **evaluation agent**, up to 25 per run.
- The evaluation agent loads the `fitness-scoring` skill and returns a structured score and summary. It has no tools.
- `main.py` marks every successfully evaluated job as seen, regardless of score.
- Jobs scoring **7.5 or higher** are included in the single daily report at `reports/YYYY-MM-DD.md`.
- The report begins with counts for discovered, skipped, evaluated, and matching JDs.
- GitHub Actions runs the app once per day and commits `seen.txt` and reports back to the repository.

## Configuration

`config.json` contains only the career sites to scan. A configured URL is treated as the authoritative scope, including any filters encoded in it.

```json
{
  "sites": [
    {
      "name": "Delta Air Lines",
      "url": "https://delta.avature.net/en_US/careers/SearchJobs/?2884=44686045"
    }
  ]
}
```

Set the `OPENAI_API_KEY` environment variable locally, or add it as a GitHub Actions repository secret.

## Daily evaluation limit

The app evaluates at most 25 previously unseen job descriptions per run. Jobs beyond that limit are not added to `seen.txt`, so they remain eligible for a future run.
