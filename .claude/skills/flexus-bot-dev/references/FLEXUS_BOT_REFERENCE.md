# Flexus Bot Reference

Supplement to AGENTS.md. Read frog_*.py first — most patterns are demonstrated there.

---

## Custom Forms Iframe Protocol

Parent → Form: `INIT` (content, themeCss), `CONTENT_UPDATE`, `FOCUS`
Form → Parent: `FORM_READY`, `FORM_CONTENT_CHANGED` (content)

Theme CSS variables (use instead of hardcoded colors):
`--p-primary-contrast-color` (paper bg), `--p-primary-color` (paper text),
`--p-content-hover-background` (desk/input bg), `--p-text-muted-color` (muted)

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Tool calls silently ignored | Missing `@rcx.on_tool_call(TOOL.name)` handler |
| LLM doesn't see error details | Return error string, don't raise exception |
| Subchat hangs forever | Subchat expert kernel must set `subchat_result` |
