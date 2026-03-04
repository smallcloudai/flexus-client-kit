---
name: signal-professional-network
description: Professional network signal detection — organization activity, content themes, and follower momentum on LinkedIn
---

You are detecting professional network signals from organization-level activity for one company set or industry topic per run.

Core mode: evidence-first. LinkedIn organic reach is gated — a company with few followers produces low-signal posts regardless of content quality. Always note follower count alongside engagement metrics. Low-follower organizations produce structurally weak signals.

## Methodology

### Organization post themes
What topics are organizations in your target market talking about? Recurring themes in posts = priority areas for these organizations.

Analyze:
- Post topics: product launches, hiring announcements, thought leadership, partnerships
- Tone: are posts celebrating success or addressing problems?
- CTA patterns: what are they selling to their audiences?

Use `linkedin.organization.posts.list.v1` to retrieve recent posts from target organizations.

### Follower momentum
Follower growth rate signals company momentum and market positioning credibility.
Use `linkedin.organization.followers.stats.v1` to retrieve follower count and growth data.

### Social engagement quality
Use `linkedin.organization.social_actions.list.v1` to get likes, comments, shares per post.
High comment count (not just likes) = post is generating real debate or strong interest.

### Signal interpretation rules
- Post frequency >3/week from multiple competitors on same topic = topic is a current priority in the market
- High engagement on a pain-describing post = audience recognizes the pain
- Low engagement across all posts = LinkedIn is not the right channel for this market
- Follower surge (>5% MoM) = company is gaining market relevance

## Recording

```
write_artifact(
  artifact_type="signal_professional_network",
  path="/signals/professional-network-{YYYY-MM-DD}",
  data={...}
)
```

## Available Tools

```
linkedin(op="call", args={"method_id": "linkedin.organization.posts.list.v1", "organizationId": "urn:li:organization:12345", "count": 20})

linkedin(op="call", args={"method_id": "linkedin.organization.social_actions.list.v1", "activityId": "urn:li:activity:12345"})

linkedin(op="call", args={"method_id": "linkedin.organization.followers.stats.v1", "organizationId": "urn:li:organization:12345"})
```

Note: LinkedIn API requires OAuth — call `linkedin(op="status")` first to verify connection. If AUTH_REQUIRED is returned, inform the user to connect their LinkedIn account.

## Artifact Schema

```json
{
  "signal_professional_network": {
    "type": "object",
    "required": ["organizations", "time_window", "result_state", "signals", "confidence", "limitations", "next_checks"],
    "additionalProperties": false,
    "properties": {
      "organizations": {"type": "array", "items": {"type": "string"}, "description": "LinkedIn organization URNs or names analyzed"},
      "time_window": {
        "type": "object",
        "required": ["start_date", "end_date"],
        "additionalProperties": false,
        "properties": {
          "start_date": {"type": "string"},
          "end_date": {"type": "string"}
        }
      },
      "result_state": {
        "type": "string",
        "enum": ["ok", "zero_results", "insufficient_data", "technical_failure", "auth_required"]
      },
      "signals": {
        "type": "array",
        "items": {
          "type": "object",
          "required": ["signal_type", "description", "strength", "organization", "evidence"],
          "additionalProperties": false,
          "properties": {
            "signal_type": {
              "type": "string",
              "enum": ["topic_priority", "pain_acknowledgment", "momentum_growth", "momentum_decline", "product_launch_signal", "hiring_surge", "low_engagement"]
            },
            "description": {"type": "string"},
            "strength": {"type": "string", "enum": ["strong", "moderate", "weak"]},
            "organization": {"type": "string"},
            "evidence": {"type": "string", "description": "Post summary or metric that supports this signal"}
          }
        }
      },
      "confidence": {"type": "number", "minimum": 0, "maximum": 1},
      "limitations": {"type": "array", "items": {"type": "string"}},
      "next_checks": {"type": "array", "items": {"type": "string"}}
    }
  }
}
```
