---
name: setting-up-external-knowledge-base
description: Guide the user through populating the bot's knowledge base — uploading documents, crawling a website, or teaching facts. Use when the knowledge base is empty, the user asks how to add information, or vector search returns no results.
---

# Setting Up External Knowledge Base

Use this skill when the user asks about adding information to the knowledge base, or when vector search returns no results and you need to help the user populate it.

## Option 1: Upload Documents

Users can upload PDFs, text files, Word documents, or other files through the Flexus web UI:

1. Go to the bot's group page in Flexus
2. Click the file upload area or drag files in
3. Documents are automatically indexed and searchable via `flexus_vector_search()`

Tell the user: "You can upload documents directly through the Flexus interface. PDFs, text files, and other common formats are supported. Once uploaded, I'll be able to search through them."

## Option 2: Crawl a Website

If the user wants to add content from a website:

```python
crawl_website(url="https://example.com", depth=1, eds_name="Example Docs", rescan_period=86400)
```

- `depth=0`: single page only
- `depth=1`: page + all linked pages on the same domain
- `rescan_period`: seconds between re-crawls (86400 = daily, 0 = one-time)

Tell the user: "I can crawl your website and add its content to my knowledge base. Just give me the URL and I'll get started."

## Option 3: Teach Facts Directly

For individual facts or information that isn't in a document:

```python
create_knowledge(knowledge_entry="Enterprise plan starts at $500/month with 50 seats included", context="pricing discussion")
```

Tell the user: "You can also just tell me facts during our conversations and I'll remember them. For example, tell me your pricing, key policies, or important details."

## After Setup

Once the knowledge base is populated, confirm by running a test search:

```python
flexus_vector_search(query="<topic the user cares about>", limit=3)
```

Report what was found so the user can verify the content is indexed correctly.
