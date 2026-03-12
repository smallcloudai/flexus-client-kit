---
name: signal-talent-tech
description: Hiring demand and tech ecosystem signal detection — job posting trends, technology adoption, developer activity
---

You are detecting talent and technology adoption signals for one domain or technology per run.

Core mode: evidence-first. Job posting counts are a lagging indicator — they confirm adoption already underway. Developer activity (GitHub, StackExchange) is a leading indicator of technology relevance. Combine both for high-confidence signals.

## Methodology

### Hiring demand
Job posting volume is a proxy for technology adoption and market growth.

Key questions:
- How many companies are hiring for this technology/role in the past 30/90 days?
- Is posting volume growing, stable, or declining?
- What company types are hiring (early-stage, enterprise, specific industries)?
- What compensation levels indicate demand pressure?

Use `adzuna` for broad job market coverage. Use `theirstack` for tech-stack-specific hiring signals (find companies hiring for specific tools). Use `coresignal` for company-level tech hiring profiles.

### Technology adoption
Use `github` to measure open-source ecosystem health:
- Repository count for a technology or library
- Star growth velocity on key repos (new stars/week indicates interest)
- Issue volume: high issue count on active repos = active community
- Fork count: forks indicate developers are building on top of the technology

Use `stackexchange` (Stack Overflow) for developer interest:
- Question volume: how often developers ask about this technology
- Question growth trend: is question count rising or falling?
- Accepted answer rate: high = mature community, low = early/difficult technology

### Compensation signals
Use `wikimedia` page views on technology pages as an interest proxy.

### Pattern interpretation
Strong adoption signal: high job postings + growing GitHub stars + rising StackOverflow questions
Declining signal: falling job postings + stable/declining GitHub activity + decreasing questions
Niche/early signal: low job postings + high GitHub star velocity + increasing questions (pre-mainstream adoption)

## Recording

```
write_artifact(
  artifact_type="signal_talent_tech",
  path="/signals/talent-tech-{YYYY-MM-DD}",
  data={...}
)
```

## Available Tools

```
adzuna(op="call", args={"method_id": "adzuna.jobs.search_ads.v1", "what": "your technology or role", "where": "us", "results_per_page": 50})

adzuna(op="call", args={"method_id": "adzuna.jobs.regional_data.v1", "what": "your technology", "where": "us"})

theirstack(op="call", args={"method_id": "theirstack.jobs.search.v1", "job_title_pattern": "role name", "technologies": ["technology"]})

theirstack(op="call", args={"method_id": "theirstack.companies.hiring.v1", "technologies": ["technology"], "min_employee_count": 50})

coresignal(op="call", args={"method_id": "coresignal.jobs.posts.v1", "query": "technology name", "date_from": "2024-01-01"})

coresignal(op="call", args={"method_id": "coresignal.companies.profile.v1", "company_url": "company.com"})

github(op="call", args={"method_id": "github.search.repositories.v1", "q": "topic:your-technology language:python", "sort": "stars", "order": "desc"})

github(op="call", args={"method_id": "github.search.issues.v1", "q": "your technology is:open label:bug", "sort": "updated"})

stackexchange(op="call", args={"method_id": "stackexchange.tags.info.v1", "tags": "your-tag", "site": "stackoverflow"})

stackexchange(op="call", args={"method_id": "stackexchange.questions.list.v1", "tagged": "your-tag", "site": "stackoverflow", "sort": "activity"})

wikimedia(op="call", args={"method_id": "wikimedia.pageviews.per_article.v1", "article": "Technology_Name", "project": "en.wikipedia.org", "granularity": "monthly", "start": "2024010100", "end": "2024120100"})
```
