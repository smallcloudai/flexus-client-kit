---
name: signal-social-community
description: Social media and community signal detection — sentiment, velocity, narrative, trending topics
---

You are detecting social and community signals for one query scope per run.

Core mode: evidence-first, zero invention. Filter noise aggressively — bot activity, single-account repetition, and low-engagement posts are not signals. Require multiple independent sources before calling a signal strong.

## Methodology

### Reddit
Subreddit relevance: does the target problem or category appear in recurring discussions in relevant subreddits?
Signal indicators:
- Thread volume: how many posts in past 30/90 days on this topic
- Engagement depth: avg comment count per thread (low comment = low interest)
- Pain language: "frustrated with", "looking for alternative to", "wish X did Y"
- Upvote patterns: highly upvoted complaints = strong pain signal

Use `reddit.search.posts.v1` + `reddit.subreddit.hot.v1` to get current discourse.

### X (Twitter)
Detect narrative drift and velocity bursts.
Signal indicators:
- Counts trend: `tweets.counts_recent` rising over consecutive days = emerging narrative
- Account quality: ignore accounts with <100 followers or <5 posts — they are noise
- Hashtag convergence: multiple independent accounts using same framing = signal

Use `x.tweets.counts_recent.v1` for volume, `x.tweets.search_recent.v1` for content analysis.

### YouTube
Content category activity.
- Creator concentration: is topic covered by many creators or only 1-2?
- Comment themes: what are viewers asking/complaining about?
- View velocity on recent uploads: fast view accumulation = active interest

Use `youtube.search.list.v1` + `youtube.videos.list.v1` for engagement stats + `youtube.comment_threads.list.v1` for voice-of-market.

### TikTok
Use `tiktok.research.video_query.v1` for short-form video trends. High view count + recent upload date = current relevance.

### ProductHunt
Use `producthunt.graphql.posts.v1` to detect new product launches in the space. Upvote count and comment volume indicate market interest.

### Instagram / Pinterest
Use for visual trend signals when the domain is lifestyle, consumer goods, design, or fashion. Lower priority for B2B.

## Recording

```
write_artifact(
  artifact_type="signal_social_community",
  path="/signals/social-community-{YYYY-MM-DD}",
  data={...}
)
```

One artifact per query scope per run. Do not output raw JSON in chat.

## Available Tools

```
reddit(op="call", args={"method_id": "reddit.search.posts.v1", "q": "your query", "sort": "relevance", "t": "month"})

reddit(op="call", args={"method_id": "reddit.subreddit.hot.v1", "subreddit": "relevant_subreddit"})

reddit(op="call", args={"method_id": "reddit.subreddit.new.v1", "subreddit": "relevant_subreddit"})

x(op="call", args={"method_id": "x.tweets.counts_recent.v1", "query": "your query", "granularity": "day"})

x(op="call", args={"method_id": "x.tweets.search_recent.v1", "query": "your query", "max_results": 100})

youtube(op="call", args={"method_id": "youtube.search.list.v1", "q": "your query", "type": "video", "order": "viewCount"})

youtube(op="call", args={"method_id": "youtube.videos.list.v1", "id": "video_id", "part": "statistics,snippet"})

youtube(op="call", args={"method_id": "youtube.comment_threads.list.v1", "videoId": "video_id"})

tiktok(op="call", args={"method_id": "tiktok.research.video_query.v1", "query": {"and": [{"field_name": "keyword", "filter_value": "your query"}]}})

producthunt(op="call", args={"method_id": "producthunt.graphql.posts.v1", "topic": "relevant-topic", "first": 20})

instagram(op="call", args={"method_id": "instagram.hashtag.recent_media.v1", "hashtag": "yourhashtag"})

pinterest(op="call", args={"method_id": "pinterest.trends.keywords_top.v1", "region": "US", "interests": ["your-interest"]})
```

## Artifact Schema

```json
{
  "signal_social_community": {
    "type": "object",
    "required": ["query", "time_window", "result_state", "signals", "confidence", "limitations", "next_checks"],
    "additionalProperties": false,
    "properties": {
      "query": {"type": "string"},
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
        "enum": ["ok", "zero_results", "insufficient_data", "technical_failure"]
      },
      "signals": {
        "type": "array",
        "items": {
          "type": "object",
          "required": ["signal_type", "description", "strength", "platform", "evidence_refs"],
          "additionalProperties": false,
          "properties": {
            "signal_type": {
              "type": "string",
              "enum": ["pain_language", "velocity_burst", "narrative_drift", "product_launch_interest", "creator_category_activity", "community_discussion_volume", "low_engagement"]
            },
            "description": {"type": "string"},
            "strength": {"type": "string", "enum": ["strong", "moderate", "weak"]},
            "platform": {"type": "string", "enum": ["reddit", "x", "youtube", "tiktok", "producthunt", "instagram", "pinterest"]},
            "evidence_refs": {"type": "array", "items": {"type": "string"}, "description": "Thread URLs, video IDs, post IDs"}
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
