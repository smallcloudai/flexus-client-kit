import argparse
import html
import json
import logging
from pathlib import Path

from aiohttp import web

from flexus_client_kit.builder import bot_registry_engine
from flexus_client_kit.builder import control_plane
from flexus_client_kit.runtime import no_special_code_bot

logger = logging.getLogger("bot_registry_app")
BS_TYPES = ["string_short", "string_long", "string_multiline", "bool", "int", "float"]


def _escape(v: str) -> str:
    return html.escape(v, quote=True)


def _js_json(v) -> str:
    try:
        return json.dumps(v).replace("</", "<\\/")
    except (TypeError, ValueError) as e:
        raise RuntimeError(f"Cannot serialize JSON for script: {e}") from e


def _load_registry(registry_path: Path) -> tuple[dict, Path]:
    try:
        return bot_registry_engine.load_registry(registry_path)
    except RuntimeError:
        raise


def _resolve_bot_entry(registry_path: Path, bot_id: str) -> tuple[dict, Path, dict]:
    try:
        reg, repo_root = _load_registry(registry_path)
        items = [x for x in reg["bots"] if x["bot_id"] == bot_id]
        if len(items) != 1:
            raise RuntimeError(f"Bot {bot_id!r} not found in registry")
        item = items[0]
        bot_json_path = bot_registry_engine._resolve_input_path(item["bot_json_path"], registry_path.parent, repo_root)
        cfg = bot_registry_engine._read_json(bot_json_path)
        return item, bot_json_path, cfg
    except RuntimeError:
        raise


def _page(title: str, body: str) -> str:
    try:
        return f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <title>{_escape(title)}</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 16px; }}
    h1, h2 {{ margin: 0 0 12px 0; }}
    .row {{ margin-bottom: 10px; }}
    label {{ display: block; font-weight: bold; margin-bottom: 4px; }}
    input[type=text], input[type=number], textarea, select {{ width: 100%; max-width: 1200px; box-sizing: border-box; }}
    textarea {{ min-height: 100px; font-family: Consolas, monospace; }}
    .card {{ border: 1px solid #ddd; padding: 12px; margin-bottom: 12px; border-radius: 8px; background: #fff; }}
    .ok {{ color: #006400; }}
    .err {{ color: #8b0000; white-space: pre-wrap; }}
    .mono {{ font-family: Consolas, monospace; white-space: pre-wrap; }}
    .line {{ margin-bottom: 6px; }}
    a {{ text-decoration: none; }}
    .layout {{ display: grid; grid-template-columns: 260px 1fr; gap: 16px; align-items: start; }}
    .sidebar {{ border: 1px solid #ddd; border-radius: 8px; padding: 12px; position: sticky; top: 16px; background: #fff; }}
    .sidebar h2 {{ font-size: 16px; margin-bottom: 8px; }}
    .nav-link {{ display: block; padding: 8px; border-radius: 6px; margin-bottom: 4px; color: #222; border: 1px solid transparent; }}
    .nav-link:hover {{ background: #f5f7ff; border-color: #dbe5ff; }}
    .nav-link.active {{ background: #eef3ff; border-color: #b9ccff; color: #0f3ea8; font-weight: bold; }}
    .main {{ min-width: 0; }}
    .section-panel {{ display: none; }}
    .section-panel.active {{ display: block; }}
    .action-row {{ margin-top: 12px; display: flex; gap: 8px; flex-wrap: wrap; }}
    .header-tabs {{ display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 12px; }}
    .header-tab {{ display: inline-block; padding: 8px 12px; border: 1px solid #cdd6e6; border-radius: 8px; color: #223; background: #f8fbff; }}
    .header-tab.active {{ background: #e9f1ff; border-color: #9eb8e8; font-weight: bold; color: #0f3ea8; }}
    .split-layout {{ display: grid; grid-template-columns: 320px 1fr; gap: 16px; align-items: start; }}
    .split-sidebar {{ border: 1px solid #ddd; border-radius: 8px; padding: 10px; position: sticky; top: 16px; background: #fff; max-height: 80vh; overflow: auto; }}
    .split-main {{ min-width: 0; }}
    .side-item {{ display: block; padding: 8px; border-radius: 6px; border: 1px solid transparent; color: #222; margin-bottom: 4px; }}
    .side-item:hover {{ background: #f5f7ff; border-color: #dbe5ff; }}
    .side-item.active {{ background: #eef3ff; border-color: #b9ccff; color: #0f3ea8; font-weight: bold; }}
  </style>
</head>
<body>
{body}
</body>
</html>"""
    except RuntimeError:
        raise


def _header_tabs(active: str) -> str:
    try:
        tabs = [
            ("integrations", "/integrations", "Integrations"),
            ("tools", "/tools", "Tools"),
            ("bots", "/bots", "Bots"),
            ("control-plane", "/control-plane", "Control Plane"),
        ]
        home_cls = "header-tab active" if active == "home" else "header-tab"
        out = ['<div class="header-tabs">', f'<a class="{home_cls}" href="/">Home</a>']
        for key, href, label in tabs:
            cls = "header-tab active" if key == active else "header-tab"
            out.append(f'<a class="{cls}" href="{_escape(href)}">{_escape(label)}</a>')
        out.append("</div>")
        return "".join(out)
    except RuntimeError:
        raise


def _bot_editor_form(bot_id: str, cfg: dict, message: str = "", error: str = "") -> str:
    try:
        msg_html = f'<div class="ok">{_escape(message)}</div>' if message else ""
        err_html = f'<div class="err">{_escape(error)}</div>' if error else ""
        tools_catalog = sorted(list(no_special_code_bot.TOOL_REGISTRY.keys()))
        return f"""
<h1>Bot Editor: {_escape(bot_id)}</h1>
<div class="line"><a href="/">Back to bots list</a></div>
{msg_html}
{err_html}
<div class="layout">
  <aside class="sidebar">
    <h2>Navigation</h2>
    <a class="nav-link" data-nav="core" href="#core">Core</a>
    <a class="nav-link" data-nav="tools" href="#tools">Tools</a>
    <a class="nav-link" data-nav="tags" href="#tags">Tags</a>
    <a class="nav-link" data-nav="featured" href="#featured">Featured Actions</a>
    <a class="nav-link" data-nav="setup" href="#setup">Setup Schema</a>
    <a class="nav-link" data-nav="experts" href="#experts">Experts</a>
    <a class="nav-link" data-nav="skills" href="#skills">Skills</a>
    <a class="nav-link" data-nav="runtime" href="#runtime">Runtime Advanced</a>
    <a class="nav-link" data-nav="prompts" href="#prompts">Prompts / Readme</a>
    <a class="nav-link" data-nav="build" href="#build">Build</a>
  </aside>

  <main class="main">
    <form id="bot-form" method="post" action="/bot/{_escape(bot_id)}/save">
      <section class="card section-panel" data-section="core">
        <h2>Core</h2>
        <div class="row"><label>bot_name</label><input type="text" name="bot_name" value="{_escape(str(cfg['bot_name']))}" readonly /></div>
        <div class="row"><label>accent_color</label><input type="text" name="accent_color" value="{_escape(str(cfg['accent_color']))}" /></div>
        <div class="row"><label>title1</label><input type="text" name="title1" value="{_escape(str(cfg['title1']))}" /></div>
        <div class="row"><label>title2</label><input type="text" name="title2" value="{_escape(str(cfg['title2']))}" /></div>
        <div class="row"><label>author</label><input type="text" name="author" value="{_escape(str(cfg['author']))}" /></div>
        <div class="row"><label>occupation</label><input type="text" name="occupation" value="{_escape(str(cfg['occupation']))}" /></div>
        <div class="row"><label>typical_group</label><input type="text" name="typical_group" value="{_escape(str(cfg['typical_group']))}" /></div>
        <div class="row"><label>github_repo</label><input type="text" name="github_repo" value="{_escape(str(cfg['github_repo']))}" /></div>
        <div class="row"><label>intro_message</label><textarea name="intro_message">{_escape(str(cfg['intro_message']))}</textarea></div>
        <div class="row"><label>preferred_model_default</label><input type="text" name="preferred_model_default" value="{_escape(str(cfg['preferred_model_default']))}" /></div>
        <div class="row"><label>daily_budget_default</label><input type="number" name="daily_budget_default" value="{_escape(str(cfg['daily_budget_default']))}" /></div>
        <div class="row"><label>default_inbox_default</label><input type="number" name="default_inbox_default" value="{_escape(str(cfg['default_inbox_default']))}" /></div>
      </section>

      <section class="card section-panel" data-section="tools">
        <h2>Tools</h2>
        <div class="line">Available tools come from real `no_special_code_bot.TOOL_REGISTRY`.</div>
        <div id="tools-box"></div>
      </section>

      <section class="card section-panel" data-section="tags">
        <h2>Tags</h2>
        <div class="row">
          <label>Add tag</label>
          <input id="tag-input" type="text" placeholder="marketing" />
          <button id="tag-add" type="button">Add tag</button>
        </div>
        <div id="tags-box"></div>
      </section>

      <section class="card section-panel" data-section="featured">
        <h2>Featured Actions</h2>
        <div id="featured-box"></div>
        <div class="row"><button id="featured-add" type="button">+ Add featured action</button></div>
      </section>

      <section class="card section-panel" data-section="setup">
        <h2>Setup Schema</h2>
        <div class="line">Human-editable rows: name, type, default, group, order, importance, description.</div>
        <div id="setup-box"></div>
        <div class="row"><button id="setup-add" type="button">+ Add setup field</button></div>
      </section>

      <section class="card section-panel" data-section="experts">
        <h2>Experts</h2>
        <div class="line">Editable expert cards with add/remove. `default` expert is required.</div>
        <div id="experts-box"></div>
        <div class="row"><button id="experts-add" type="button">+ Add expert</button></div>
      </section>

      <section class="card section-panel" data-section="skills">
        <h2>Skills</h2>
        <div class="line">Reusable skill blocks referenced by experts via `skills`.</div>
        <div id="skills-box"></div>
        <div class="row"><button id="skills-add" type="button">+ Add skill</button></div>
      </section>

      <section class="card section-panel" data-section="runtime">
        <h2>Runtime Advanced</h2>
        <div class="line">Optional fields from code runtime: schedule, forms, auth_supported, auth_scopes.</div>
        <div class="row"><label>auth_supported (comma-separated)</label><input id="auth-supported-csv" type="text" value="{_escape(','.join(cfg.get('auth_supported', [])))}" /></div>
        <div class="row"><label>auth_scopes (json object)</label><textarea id="auth-scopes-json" style="min-height:120px;">{_escape(json.dumps(cfg.get("auth_scopes", {}), indent=2))}</textarea></div>
        <div class="row"><label>schedule (json array)</label><textarea id="schedule-json" style="min-height:120px;">{_escape(json.dumps(cfg.get("schedule", []), indent=2))}</textarea></div>
        <div class="row"><label>forms (json object)</label><textarea id="forms-json" style="min-height:120px;">{_escape(json.dumps(cfg.get("forms", {}), indent=2))}</textarea></div>
      </section>

      <section class="card section-panel" data-section="prompts">
        <h2>Prompts / Readme</h2>
        <div class="row"><label>personality_md</label><textarea name="personality_md" style="min-height:220px;">{_escape(str(cfg['personality_md']))}</textarea></div>
        <div class="row"><label>readme_md</label><textarea name="readme_md" style="min-height:220px;">{_escape(str(cfg.get('readme_md', '')))}</textarea></div>
      </section>

      <input type="hidden" name="tools_json" />
      <input type="hidden" name="tags_json" />
      <input type="hidden" name="featured_actions_json" />
      <input type="hidden" name="setup_schema_json" />
      <input type="hidden" name="experts_json" />
      <input type="hidden" name="skills_json" />
      <input type="hidden" name="auth_supported_json" />
      <input type="hidden" name="auth_scopes_json" />
      <input type="hidden" name="schedule_json" />
      <input type="hidden" name="forms_json" />
      <div class="action-row">
        <button type="submit">Save</button>
      </div>
    </form>

    <section class="card section-panel" data-section="build">
      <h2>Build</h2>
      <form method="post" action="/build">
        <input type="hidden" name="bot_id" value="{_escape(bot_id)}" />
        <button type="submit" name="mode" value="dry_run">Build bot (dry run)</button>
        <button type="submit" name="mode" value="write">Build bot (write)</button>
      </form>
    </section>
  </main>
</div>
<script>
(() => {{
  const availableTools = {_js_json(tools_catalog)};
  const bsTypes = {_js_json(BS_TYPES)};
  const initTools = {_js_json(cfg["tools"])};
  const initTags = {_js_json(cfg["tags"])};
  const initFeatured = {_js_json(cfg["featured_actions"])};
  const initSetup = {_js_json(cfg["setup_schema"])};
  const initExperts = {_js_json(cfg["experts"])};
  const initSkills = {_js_json(cfg.get("skills", []))};

  const form = document.getElementById("bot-form");
  const navLinks = [...document.querySelectorAll(".nav-link")];
  const sectionPanels = [...document.querySelectorAll(".section-panel")];
  const toolsBox = document.getElementById("tools-box");
  const tagsBox = document.getElementById("tags-box");
  const featuredBox = document.getElementById("featured-box");
  const setupBox = document.getElementById("setup-box");
  const expertsBox = document.getElementById("experts-box");
  const skillsBox = document.getElementById("skills-box");
  const tagInput = document.getElementById("tag-input");
  const tagAdd = document.getElementById("tag-add");
  const tags = [...initTags];
  const allowedSections = ["core", "tools", "tags", "featured", "setup", "experts", "skills", "runtime", "prompts", "build"];

  function applyRoute() {{
    const raw = (window.location.hash || "").replace("#", "").trim();
    const section = allowedSections.includes(raw) ? raw : "core";
    for (const panel of sectionPanels) {{
      panel.classList.toggle("active", panel.dataset.section === section);
    }}
    for (const link of navLinks) {{
      link.classList.toggle("active", link.dataset.nav === section);
    }}
    if (!raw) {{
      window.location.hash = "#core";
    }}
  }}

  function make(type, cls = "") {{
    const el = document.createElement(type);
    if (cls) el.className = cls;
    return el;
  }}

  function currentExpertNames() {{
    const xs = [...document.querySelectorAll("input[name='exp_name']")].map(x => x.value.trim()).filter(Boolean);
    return xs.length ? xs : ["default"];
  }}

  function renderTools() {{
    toolsBox.innerHTML = "";
    for (const t of availableTools) {{
      const row = make("div", "line");
      const cb = make("input");
      cb.type = "checkbox";
      cb.name = "tool_check";
      cb.value = t;
      cb.checked = initTools.includes(t);
      const label = make("label");
      label.style.display = "inline";
      label.style.fontWeight = "normal";
      label.style.marginLeft = "8px";
      label.textContent = t;
      row.append(cb, label);
      toolsBox.appendChild(row);
    }}
  }}

  function renderTags() {{
    tagsBox.innerHTML = "";
    for (const tag of tags) {{
      const badge = make("span");
      badge.style.display = "inline-block";
      badge.style.padding = "4px 8px";
      badge.style.margin = "4px";
      badge.style.border = "1px solid #bbb";
      badge.style.borderRadius = "12px";
      badge.textContent = tag + " ";
      const del = make("button");
      del.type = "button";
      del.textContent = "x";
      del.onclick = () => {{
        const i = tags.indexOf(tag);
        if (i >= 0) tags.splice(i, 1);
        renderTags();
      }};
      badge.appendChild(del);
      tagsBox.appendChild(badge);
    }}
  }}

  function addFeaturedRow(item = {{ feat_question: "", feat_expert: "default" }}) {{
    const row = make("div", "card");
    const q = make("input");
    q.type = "text";
    q.name = "fa_question";
    q.placeholder = "Question";
    q.value = item.feat_question || "";
    const ex = make("select");
    ex.name = "fa_expert";
    const names = currentExpertNames();
    for (const n of names) {{
      const opt = make("option");
      opt.value = n;
      opt.textContent = n;
      ex.appendChild(opt);
    }}
    ex.value = names.includes(item.feat_expert) ? item.feat_expert : "default";
    const del = make("button");
    del.type = "button";
    del.textContent = "Delete";
    del.onclick = () => row.remove();
    row.append(q, ex, del);
    featuredBox.appendChild(row);
  }}

  function setupTypeSelect(v) {{
    const sel = make("select");
    sel.name = "ss_type";
    for (const t of bsTypes) {{
      const opt = make("option");
      opt.value = t;
      opt.textContent = t;
      sel.appendChild(opt);
    }}
    sel.value = bsTypes.includes(v) ? v : "string_short";
    return sel;
  }}

  function addSetupRow(item = {{}}) {{
    const row = make("div", "card");
    const n = make("input"); n.type = "text"; n.name = "ss_name"; n.placeholder = "bs_name"; n.value = item.bs_name || "";
    const t = setupTypeSelect(item.bs_type || "string_short");
    const d = make("input"); d.type = "text"; d.name = "ss_default"; d.placeholder = "bs_default"; d.value = item.bs_default === undefined ? "" : String(item.bs_default);
    const g = make("input"); g.type = "text"; g.name = "ss_group"; g.placeholder = "bs_group"; g.value = item.bs_group || "";
    const o = make("input"); o.type = "number"; o.name = "ss_order"; o.placeholder = "bs_order"; o.value = item.bs_order === undefined ? "1" : String(item.bs_order);
    const i = make("input"); i.type = "number"; i.name = "ss_importance"; i.placeholder = "bs_importance"; i.value = item.bs_importance === undefined ? "0" : String(item.bs_importance);
    const ds = make("input"); ds.type = "text"; ds.name = "ss_desc"; ds.placeholder = "bs_description"; ds.value = item.bs_description || "";
    const del = make("button"); del.type = "button"; del.textContent = "Delete"; del.onclick = () => row.remove();
    row.append(n, t, d, g, o, i, ds, del);
    setupBox.appendChild(row);
  }}

  function addExpertRow(item = {{}}) {{
    const row = make("div", "card");
    const n = make("input"); n.type = "text"; n.name = "exp_name"; n.placeholder = "name"; n.value = item.name || "";
    const d = make("input"); d.type = "text"; d.name = "exp_desc"; d.placeholder = "fexp_description"; d.value = item.fexp_description || "";
    const bt = make("input"); bt.type = "text"; bt.name = "exp_block"; bt.placeholder = "fexp_block_tools"; bt.value = item.fexp_block_tools || "";
    const at = make("input"); at.type = "text"; at.name = "exp_allow"; at.placeholder = "fexp_allow_tools"; at.value = item.fexp_allow_tools || "";
    const sk = make("input"); sk.type = "text"; sk.name = "exp_skills"; sk.placeholder = "skills (comma-separated)"; sk.value = (item.skills || []).join(",");
    const ps = make("textarea"); ps.name = "exp_pdoc_schemas"; ps.placeholder = "pdoc_output_schemas json array"; ps.style.minHeight = "90px"; ps.value = item.pdoc_output_schemas ? JSON.stringify(item.pdoc_output_schemas, null, 2) : "";
    const b = make("textarea"); b.name = "exp_body"; b.style.minHeight = "180px"; b.value = item.body_md || "";
    const del = make("button"); del.type = "button"; del.textContent = "Delete"; del.onclick = () => {{ row.remove(); refreshFeaturedExpertOptions(); }};
    n.addEventListener("input", refreshFeaturedExpertOptions);
    row.append(n, d, bt, at, sk, ps, b, del);
    expertsBox.appendChild(row);
  }}

  function addSkillRow(item = {{}}) {{
    const row = make("div", "card");
    const n = make("input"); n.type = "text"; n.name = "skill_name"; n.placeholder = "name"; n.value = item.name || "";
    const d = make("input"); d.type = "text"; d.name = "skill_desc"; d.placeholder = "description"; d.value = item.description || "";
    const b = make("textarea"); b.name = "skill_body"; b.style.minHeight = "160px"; b.value = item.body_md || "";
    const del = make("button"); del.type = "button"; del.textContent = "Delete"; del.onclick = () => row.remove();
    row.append(n, d, b, del);
    skillsBox.appendChild(row);
  }}

  function refreshFeaturedExpertOptions() {{
    const names = currentExpertNames();
    for (const sel of document.querySelectorAll("select[name='fa_expert']")) {{
      const prev = sel.value;
      sel.innerHTML = "";
      for (const n of names) {{
        const opt = make("option");
        opt.value = n;
        opt.textContent = n;
        sel.appendChild(opt);
      }}
      sel.value = names.includes(prev) ? prev : (names.includes("default") ? "default" : names[0]);
    }}
  }}

  function parseDefaultByType(tp, raw) {{
    const v = String(raw).trim();
    if (tp === "bool") {{
      if (["true", "1", "yes"].includes(v.toLowerCase())) return true;
      if (["false", "0", "no"].includes(v.toLowerCase())) return false;
      throw new Error("bool default must be true/false/1/0/yes/no");
    }}
    if (tp === "int") {{
      if (!/^[-]?[0-9]+$/.test(v)) throw new Error("int default must be integer");
      return Number.parseInt(v, 10);
    }}
    if (tp === "float") {{
      if (!/^[-]?[0-9]+(\\.[0-9]+)?$/.test(v)) throw new Error("float default must be numeric");
      return Number.parseFloat(v);
    }}
    return raw;
  }}

  function collectFeatured() {{
    return [...featuredBox.children].map((row) => {{
      const feat_question = row.querySelector("input[name='fa_question']").value.trim();
      const feat_expert = row.querySelector("select[name='fa_expert']").value.trim();
      return {{ feat_question, feat_expert }};
    }}).filter(x => x.feat_question);
  }}

  function collectSetup() {{
    return [...setupBox.children].map((row) => {{
      const bs_name = row.querySelector("input[name='ss_name']").value.trim();
      const bs_type = row.querySelector("select[name='ss_type']").value.trim();
      const bs_default_raw = row.querySelector("input[name='ss_default']").value;
      const bs_group = row.querySelector("input[name='ss_group']").value.trim();
      const bs_order = Number.parseInt(row.querySelector("input[name='ss_order']").value, 10);
      const bs_importance = Number.parseInt(row.querySelector("input[name='ss_importance']").value, 10);
      const bs_description = row.querySelector("input[name='ss_desc']").value.trim();
      return {{
        bs_name,
        bs_type,
        bs_default: parseDefaultByType(bs_type, bs_default_raw),
        bs_group,
        bs_order,
        bs_importance,
        bs_description,
      }};
    }}).filter(x => x.bs_name);
  }}

  function collectExperts() {{
    return [...expertsBox.children].map((row) => {{
      const name = row.querySelector("input[name='exp_name']").value.trim();
      const fexp_description = row.querySelector("input[name='exp_desc']").value.trim();
      const fexp_block_tools = row.querySelector("input[name='exp_block']").value.trim();
      const fexp_allow_tools = row.querySelector("input[name='exp_allow']").value.trim();
      const exp_skills_csv = row.querySelector("input[name='exp_skills']").value.trim();
      const exp_pdoc_schemas_raw = row.querySelector("textarea[name='exp_pdoc_schemas']").value.trim();
      const body_md = row.querySelector("textarea[name='exp_body']").value;
      const out = {{ name, fexp_description, body_md }};
      if (fexp_block_tools) out.fexp_block_tools = fexp_block_tools;
      if (fexp_allow_tools) out.fexp_allow_tools = fexp_allow_tools;
      if (exp_skills_csv) {{
        const xs = [];
        for (const x of exp_skills_csv.split(",")) {{
          const y = x.trim();
          if (y && !xs.includes(y)) xs.push(y);
        }}
        if (xs.length) out.skills = xs;
      }}
      if (exp_pdoc_schemas_raw) {{
        out.pdoc_output_schemas = JSON.parse(exp_pdoc_schemas_raw);
      }}
      return out;
    }}).filter(x => x.name);
  }}

  function collectSkills() {{
    return [...skillsBox.children].map((row) => {{
      const name = row.querySelector("input[name='skill_name']").value.trim();
      const description = row.querySelector("input[name='skill_desc']").value.trim();
      const body_md = row.querySelector("textarea[name='skill_body']").value;
      return {{ name, description, body_md }};
    }}).filter(x => x.name);
  }}

  function syncHidden() {{
    const tools = [...document.querySelectorAll("input[name='tool_check']:checked")].map(x => x.value);
    form.elements["tools_json"].value = JSON.stringify(tools);
    form.elements["tags_json"].value = JSON.stringify(tags);
    form.elements["featured_actions_json"].value = JSON.stringify(collectFeatured());
    form.elements["setup_schema_json"].value = JSON.stringify(collectSetup());
    form.elements["experts_json"].value = JSON.stringify(collectExperts());
    form.elements["skills_json"].value = JSON.stringify(collectSkills());
    const authSupported = document.getElementById("auth-supported-csv").value.split(",").map(x => x.trim()).filter(Boolean);
    form.elements["auth_supported_json"].value = JSON.stringify(authSupported);
    form.elements["auth_scopes_json"].value = JSON.stringify(JSON.parse(document.getElementById("auth-scopes-json").value || "{{}}"));
    form.elements["schedule_json"].value = JSON.stringify(JSON.parse(document.getElementById("schedule-json").value || "[]"));
    form.elements["forms_json"].value = JSON.stringify(JSON.parse(document.getElementById("forms-json").value || "{{}}"));
  }}

  tagAdd.addEventListener("click", () => {{
    const v = tagInput.value.trim();
    if (!v) return;
    if (!tags.includes(v)) tags.push(v);
    tagInput.value = "";
    renderTags();
  }});
  tagInput.addEventListener("keydown", (ev) => {{
    if (ev.key !== "Enter") return;
    ev.preventDefault();
    tagAdd.click();
  }});
  document.getElementById("featured-add").addEventListener("click", () => addFeaturedRow());
  document.getElementById("setup-add").addEventListener("click", () => addSetupRow());
  document.getElementById("experts-add").addEventListener("click", () => {{ addExpertRow(); refreshFeaturedExpertOptions(); }});
  document.getElementById("skills-add").addEventListener("click", () => addSkillRow());

  form.addEventListener("submit", (ev) => {{
    try {{
      syncHidden();
    }} catch (e) {{
      ev.preventDefault();
      alert("Validation error in dynamic fields: " + String(e.message || e));
    }}
  }});

  renderTools();
  renderTags();
  for (const x of initExperts) addExpertRow(x);
  for (const x of initSkills) addSkillRow(x);
  for (const x of initFeatured) addFeaturedRow(x);
  for (const x of initSetup) addSetupRow(x);
  refreshFeaturedExpertOptions();
  window.addEventListener("hashchange", applyRoute);
  applyRoute();
}})();
</script>
"""
    except KeyError as e:
        raise RuntimeError(f"Missing required key while rendering bot form: {e}") from e


def _parse_bot_form(post: dict) -> dict:
    try:
        cfg = {
            "bot_name": str(post["bot_name"]),
            "accent_color": str(post["accent_color"]),
            "title1": str(post["title1"]),
            "title2": str(post["title2"]),
            "author": str(post["author"]),
            "occupation": str(post["occupation"]),
            "typical_group": str(post["typical_group"]),
            "github_repo": str(post["github_repo"]),
            "tools": json.loads(str(post["tools_json"])),
            "featured_actions": json.loads(str(post["featured_actions_json"])),
            "intro_message": str(post["intro_message"]),
            "preferred_model_default": str(post["preferred_model_default"]),
            "daily_budget_default": int(str(post["daily_budget_default"])),
            "default_inbox_default": int(str(post["default_inbox_default"])),
            "tags": json.loads(str(post["tags_json"])),
            "personality_md": str(post["personality_md"]),
            "experts": json.loads(str(post["experts_json"])),
            "skills": json.loads(str(post.get("skills_json", "[]"))),
            "setup_schema": json.loads(str(post["setup_schema_json"])),
            "readme_md": str(post.get("readme_md", "")),
            "auth_supported": json.loads(str(post.get("auth_supported_json", "[]"))),
            "auth_scopes": json.loads(str(post.get("auth_scopes_json", "{}"))),
            "schedule": json.loads(str(post.get("schedule_json", "[]"))),
            "forms": json.loads(str(post.get("forms_json", "{}"))),
        }
        if not cfg["skills"]:
            cfg.pop("skills")
        if not cfg["auth_supported"]:
            cfg.pop("auth_supported")
        if not cfg["auth_scopes"]:
            cfg.pop("auth_scopes")
        if not cfg["schedule"]:
            cfg.pop("schedule")
        if not cfg["forms"]:
            cfg.pop("forms")
        return cfg
    except (ValueError, TypeError, json.JSONDecodeError, KeyError) as e:
        raise RuntimeError(f"Cannot parse form values: {e}") from e


async def index_handler(request: web.Request) -> web.Response:
    try:
        registry_path = request.app["registry_path"]
        sidebar = """
<div class="line"><strong>Home</strong></div>
<div class="line">Placeholder section.</div>
"""
        main = f"""
<div class="card">
  <h2>Home Placeholder</h2>
  <div class="line">registry: <span class="mono">{_escape(str(registry_path))}</span></div>
  <div class="line">This page is intentionally minimal for now.</div>
  <div class="line">Content will be defined later.</div>
</div>
"""
        body = _header_tabs("home") + """
<h1>Bot Registry UI</h1>
"""
        body += f"<div class='split-layout'><aside class='split-sidebar'>{sidebar}</aside><section class='split-main'>{main}</section></div>"
        return web.Response(text=_page("Bot Registry UI", body), content_type="text/html")
    except RuntimeError as e:
        return web.Response(text=_page("Bot Registry UI - Error", f'<div class="err">{_escape(str(e))}</div>'), content_type="text/html", status=500)


async def bot_page_handler(request: web.Request) -> web.Response:
    try:
        registry_path = request.app["registry_path"]
        bot_id = str(request.match_info["bot_id"])
        _, _, cfg = _resolve_bot_entry(registry_path, bot_id)
        body = _bot_editor_form(bot_id, cfg)
        return web.Response(text=_page(f"Bot {bot_id}", body), content_type="text/html")
    except RuntimeError as e:
        return web.Response(text=_page("Bot Editor - Error", f'<div class="err">{_escape(str(e))}</div>'), content_type="text/html", status=500)


async def save_bot_handler(request: web.Request) -> web.Response:
    try:
        registry_path = request.app["registry_path"]
        bot_id = str(request.match_info["bot_id"])
        post = await request.post()
        cfg = _parse_bot_form(dict(post))
        _, bot_json_path, _ = _resolve_bot_entry(registry_path, bot_id)
        bot_registry_engine._validate_bot_config(cfg, bot_json_path)
        bot_registry_engine.write_json_atomic(bot_json_path, cfg)
        body = _bot_editor_form(bot_id, cfg, message=f"Saved {bot_json_path}")
        return web.Response(text=_page(f"Bot {bot_id}", body), content_type="text/html")
    except RuntimeError as e:
        try:
            registry_path = request.app["registry_path"]
            bot_id = str(request.match_info["bot_id"])
            _, _, old_cfg = _resolve_bot_entry(registry_path, bot_id)
            body = _bot_editor_form(bot_id, old_cfg, error=str(e))
            return web.Response(text=_page(f"Bot {bot_id}", body), content_type="text/html", status=400)
        except RuntimeError as e2:
            return web.Response(text=_page("Save Bot - Error", f'<div class="err">{_escape(str(e2))}</div>'), content_type="text/html", status=500)


async def build_handler(request: web.Request) -> web.Response:
    try:
        registry_path = request.app["registry_path"]
        post = await request.post()
        mode = str(post.get("mode", "dry_run"))
        bot_id = str(post.get("bot_id", "")).strip() or None
        apply_changes = mode == "write"
        result = bot_registry_engine.build_from_registry(registry_path, apply_changes=apply_changes, bot_id=bot_id)
        body = "<h1>Build Result</h1><div class='line'><a href='/'>Back to list</a></div><div class='card'>"
        for bot in result["bots"]:
            body += f"<h2>{_escape(bot['bot_id'])}</h2>"
            for f in bot["files"]:
                body += f"<div class='line'>{_escape(f['status'])} - {_escape(f['path'])}</div>"
                if f["diff"]:
                    body += f"<details><summary>diff</summary><pre class='mono'>{_escape(f['diff'])}</pre></details>"
        body += "</div>"
        return web.Response(text=_page("Build Result", body), content_type="text/html")
    except RuntimeError as e:
        return web.Response(text=_page("Build - Error", f'<div class="err">{_escape(str(e))}</div>'), content_type="text/html", status=500)


async def control_plane_handler(request: web.Request) -> web.Response:
    try:
        registry_path = request.app["registry_path"]
        report = control_plane.build_control_plane_report(registry_path)
        s = report["summary"]
        body = _header_tabs("control-plane") + f"""
<h1>Control Plane Report</h1>
<div class="line"><a href="/">Back to bots list</a></div>
<div class="card">
  <h2>Summary</h2>
  <div class="line">registry: <span class="mono">{_escape(report["registry_path"])}</span></div>
  <div class="line">repo_root: <span class="mono">{_escape(report["repo_root"])}</span></div>
  <div class="line">bots_total: {s["bots_total"]}, bots_enabled: {s["bots_enabled"]}</div>
  <div class="line">tool_registry_total: {s["tool_registry_total"]}, integrations_total: {s["integrations_total"]}</div>
  <div class="line">generated_bot_configs_total: {s.get("generated_bot_configs_total", 0)}, unregistered_bot_configs_total: {s.get("unregistered_bot_configs_total", 0)}</div>
  <div class="line">issues_total: {s["issues_total"]}, errors_total: {s["errors_total"]}, warnings_total: {s["warnings_total"]}</div>
</div>
<div class="card">
  <h2>Bots</h2>
"""
        for b in report["bots"]:
            body += (
                f"<div class='line'><strong>{_escape(b['bot_id'])}</strong> "
                f"(enabled={_escape(str(b['enabled']))}, schema_ok={_escape(str(b['schema_ok']))}, runtime_ok={_escape(str(b['runtime_ok']))}) "
                f"tools={_escape(str(b['tools_total']))}, experts={_escape(str(b['experts_total']))}, skills={_escape(str(b['skills_total']))}</div>"
            )
        body += "</div>"
        body += """
<div class="card">
  <h2>Runtime Tool Registry</h2>
"""
        for t in report["tool_registry"]:
            body += f"<div class='line'>{_escape(t)}</div>"
        body += "</div>"
        body += """
<div class="card">
  <h2>Integration Files</h2>
"""
        for p in report["integration_files"]:
            body += f"<div class='line mono'>{_escape(p)}</div>"
        body += "</div>"
        body += """
<div class="card">
  <h2>Issues</h2>
"""
        if not report["issues"]:
            body += "<div class='line ok'>No issues found.</div>"
        else:
            for x in report["issues"]:
                color = "err" if x["severity"] == "error" else ""
                body += (
                    f"<div class='line {color}'>[{_escape(x['severity'])}] {_escape(x['scope'])} :: "
                    f"{_escape(x['code'])} :: {_escape(x['message'])}"
                    f"{' | hint: ' + _escape(x['hint']) if x.get('hint') else ''}</div>"
                )
        body += "</div>"
        return web.Response(text=_page("Control Plane Report", body), content_type="text/html")
    except RuntimeError as e:
        return web.Response(text=_page("Control Plane - Error", f'<div class="err">{_escape(str(e))}</div>'), content_type="text/html", status=500)


async def integrations_handler(request: web.Request) -> web.Response:
    try:
        registry_path = request.app["registry_path"]
        inv = control_plane.build_integrations_inventory(registry_path)
        selected = str(request.rel_url.query.get("selected", "")).strip()
        items = inv["items"]
        if items and not any(x["key"] == selected for x in items):
            selected = items[0]["key"]
        selected_item = next((x for x in items if x["key"] == selected), None)
        issue_map = {z["scope"]: z for z in inv.get("issues", [])}

        sidebar = ""
        for x in items:
            cls = "side-item active" if x["key"] == selected else "side-item"
            sidebar += f"<a class='{cls}' href='/integrations?selected={_escape(x['key'])}'>{_escape(x['name'])}</a>"

        main = """
<div class="card"><h2>Summary</h2>
"""
        main += f"<div class='line'>total integrations: {inv['integrations_total']}</div>"
        main += f"<div class='line'>inventory issues: {len(inv.get('issues', []))}</div>"
        main += "</div>"
        if selected_item:
            rel_scope = f"integration:{selected_item['path']}"
            decode_issue = issue_map.get(rel_scope)
            main += f"""
<div class="card">
  <h2>Integration: {_escape(selected_item["name"])}</h2>
  <div class="line">path: <span class="mono">{_escape(selected_item["path"])}</span></div>
  <div class="line">read_ok: {_escape(str(selected_item.get("read_ok", True)))}</div>
  <div class="line">has_describe_methods: {_escape(str(selected_item["has_describe_methods"]))}</div>
  <div class="line">has_auth_status: {_escape(str(selected_item["has_auth_status"]))}</div>
  <div class="line">has_call: {_escape(str(selected_item["has_call"]))}</div>
  <div class="line">has_base_integration: {_escape(str(selected_item["has_base_integration"]))}</div>
  <div class="line">validation_score_0_3: {_escape(str(selected_item["validation_score_0_3"]))}</div>
</div>
"""
            if decode_issue:
                main += f"<div class='card'><h2>Read Error</h2><div class='line err'>{_escape(decode_issue['message'])}</div></div>"
            main += "<div class='card'><h2>Discovered Method IDs</h2>"
            if not selected_item["method_ids"]:
                main += "<div class='line'>No method ids discovered in this file.</div>"
            for mid in selected_item["method_ids"]:
                main += f"<div class='line mono'>{_escape(mid)}</div>"
            main += "</div>"
        if inv.get("issues"):
            main += "<div class='card'><h2>Inventory Issues</h2>"
            for z in inv["issues"]:
                main += f"<div class='line err'>[{_escape(z['severity'])}] {_escape(z['scope'])} :: {_escape(z['code'])} :: {_escape(z['message'])}</div>"
            main += "</div>"
        body = _header_tabs("integrations") + """
<h1>Integrations Catalog</h1>
<div class="line"><a href="/">Back to home</a></div>
"""
        body += f"<div class='split-layout'><aside class='split-sidebar'>{sidebar}</aside><section class='split-main'>{main}</section></div>"
        return web.Response(text=_page("Integrations Catalog", body), content_type="text/html")
    except RuntimeError as e:
        return web.Response(text=_page("Integrations - Error", f'<div class="err">{_escape(str(e))}</div>'), content_type="text/html", status=500)


async def integration_detail_handler(request: web.Request) -> web.Response:
    try:
        key = str(request.match_info["integration_key"])
        raise web.HTTPFound(f"/integrations?selected={_escape(key)}")
    except RuntimeError as e:
        return web.Response(text=_page("Integration - Error", f'<div class="err">{_escape(str(e))}</div>'), content_type="text/html", status=500)


async def tools_handler(request: web.Request) -> web.Response:
    try:
        registry_path = request.app["registry_path"]
        inv = control_plane.build_tools_inventory(registry_path)
        selected = str(request.rel_url.query.get("selected", "")).strip()
        items = inv["items"]
        if items and not any(x["tool_name"] == selected for x in items):
            selected = items[0]["tool_name"]
        selected_item = next((x for x in items if x["tool_name"] == selected), None)

        sidebar = ""
        for x in items:
            cls = "side-item active" if x["tool_name"] == selected else "side-item"
            sidebar += f"<a class='{cls}' href='/tools?selected={_escape(x['tool_name'])}'>{_escape(x['tool_name'])}</a>"

        main = """
<div class="card"><h2>Summary</h2>
"""
        main += f"<div class='line'>total tools in landscape: {inv['tools_total']}</div>"
        main += f"<div class='line'>runtime registered: {inv['runtime_tools_total']}</div>"
        main += "</div>"
        if selected_item:
            x = selected_item
            main += f"""
<div class="card">
  <h2>Tool: {_escape(x["tool_name"])}</h2>
  <div class="line">runtime_registered: {_escape(str(x["registered_in_runtime"]))}</div>
  <div class="line">used_by_bots: {_escape(str(len(x["used_by_bots"])))}</div>
  <div class="line">used_by_experts_allow: {_escape(str(len(x["used_by_experts_allow"])))}</div>
  <div class="line">used_by_experts_block: {_escape(str(len(x["used_by_experts_block"])))}</div>
</div>
<div class="card"><h2>Used by Bots</h2>
"""
            if not x["used_by_bots"]:
                main += "<div class='line'>No bot uses this tool.</div>"
            for b in x["used_by_bots"]:
                main += f"<div class='line'>{_escape(b)}</div>"
            main += "</div><div class='card'><h2>Expert Allow-List Usage</h2>"
            if not x["used_by_experts_allow"]:
                main += "<div class='line'>No explicit allow-list usage found.</div>"
            for y in x["used_by_experts_allow"]:
                main += f"<div class='line'>{_escape(y)}</div>"
            main += "</div><div class='card'><h2>Tool Catalog Entries</h2>"
            if not x["tool_catalog_entries"]:
                main += "<div class='line'>No tool_catalog metadata found.</div>"
            for m in x["tool_catalog_entries"]:
                main += (
                    f"<div class='line'>{_escape(m['bot_name'])} | integration_mode={_escape(m['integration_mode'])} | "
                    f"method_ids_total={_escape(str(m['method_ids_total']))}</div>"
                )
            main += "</div>"
        body = _header_tabs("tools") + """
<h1>Tools Catalog</h1>
<div class="line"><a href="/">Back to home</a></div>
"""
        body += f"<div class='split-layout'><aside class='split-sidebar'>{sidebar}</aside><section class='split-main'>{main}</section></div>"
        return web.Response(text=_page("Tools Catalog", body), content_type="text/html")
    except RuntimeError as e:
        return web.Response(text=_page("Tools - Error", f'<div class="err">{_escape(str(e))}</div>'), content_type="text/html", status=500)


async def tool_detail_handler(request: web.Request) -> web.Response:
    try:
        tool_name = str(request.match_info["tool_name"])
        raise web.HTTPFound(f"/tools?selected={_escape(tool_name)}")
    except RuntimeError as e:
        return web.Response(text=_page("Tool - Error", f'<div class="err">{_escape(str(e))}</div>'), content_type="text/html", status=500)


async def bots_handler(request: web.Request) -> web.Response:
    try:
        registry_path = request.app["registry_path"]
        inv = control_plane.build_bots_inventory(registry_path)
        selected = str(request.rel_url.query.get("selected", "")).strip()
        items = inv["registered"]
        if items and not any(x["bot_id"] == selected for x in items):
            selected = items[0]["bot_id"]
        selected_item = next((x for x in items if x["bot_id"] == selected), None)

        sidebar = ""
        for x in items:
            cls = "side-item active" if x["bot_id"] == selected else "side-item"
            sidebar += f"<a class='{cls}' href='/bots?selected={_escape(x['bot_id'])}'>{_escape(x['bot_id'])}</a>"

        main = """
<div class="card"><h2>Summary</h2>
"""
        main += f"<div class='line'>registered: {inv['bots_registered_total']}; unregistered generated configs: {inv['bots_unregistered_total']}</div>"
        main += "</div>"
        if selected_item:
            x = selected_item
            main += f"""
<div class="card">
  <h2>Bot: {_escape(x["bot_id"])}</h2>
  <div class="line"><a href="{_escape(x["editor_path"])}">Open no-code editor</a></div>
  <div class="line">bot_json_path: <span class="mono">{_escape(x["bot_json_path"])}</span></div>
  <div class="line">output_dir: <span class="mono">{_escape(x["output_dir"])}</span></div>
  <div class="line">tools={_escape(str(x["tools_total"]))}, experts={_escape(str(x["experts_total"]))}, skills={_escape(str(x["skills_total"]))}</div>
</div>
<div class="card">
  <h2>Generator Managed Zone</h2>
  <div class="line">Generator reads/writes only these standard paths (pattern-based):</div>
"""
            for p in x["managed_path_patterns"]:
                main += f"<div class='line mono'>{_escape(p)}</div>"
            main += "</div><div class='card'><h2>Managed Files Present</h2>"
            if not x["existing_managed_files"]:
                main += "<div class='line'>No managed files detected in output dir yet.</div>"
            for p in x["existing_managed_files"]:
                main += f"<div class='line mono'>{_escape(p)}</div>"
            main += f"</div><div class='card'><h2>Custom Zone (Generator Never Touches)</h2><div class='line mono'>{_escape(x['custom_zone_rel'])}/</div>"
            if not x["custom_files"]:
                main += "<div class='line'>No custom files in custom zone.</div>"
            for p in x["custom_files"]:
                main += f"<div class='line mono'>{_escape(p)}</div>"
            main += "</div>"
        main += "<div class='card'><h2>Unregistered Generated Configs</h2>"
        if not inv["unregistered"]:
            main += "<div class='line ok'>No unregistered generated bot configs.</div>"
        for x in inv["unregistered"]:
            main += f"<div class='line'>{_escape(x['bot_name'])} - {_escape(x['bot_json_path'])}</div>"
        main += "</div>"
        body = _header_tabs("bots") + """
<h1>Bots Catalog</h1>
<div class="line"><a href="/">Back to home</a></div>
"""
        body += f"<div class='split-layout'><aside class='split-sidebar'>{sidebar}</aside><section class='split-main'>{main}</section></div>"
        return web.Response(text=_page("Bots Catalog", body), content_type="text/html")
    except RuntimeError as e:
        return web.Response(text=_page("Bots - Error", f'<div class="err">{_escape(str(e))}</div>'), content_type="text/html", status=500)


async def bot_detail_handler(request: web.Request) -> web.Response:
    try:
        bot_id = str(request.match_info["bot_id"])
        raise web.HTTPFound(f"/bots?selected={_escape(bot_id)}")
    except RuntimeError as e:
        return web.Response(text=_page("Bot Detail - Error", f'<div class="err">{_escape(str(e))}</div>'), content_type="text/html", status=500)


def main() -> None:
    try:
        parser = argparse.ArgumentParser(description="Local UI for bot registry and bot configs")
        parser.add_argument("--registry", default="flexus_simple_bots/generated/bots_registry.json", help="Path to registry json")
        parser.add_argument("--host", default="127.0.0.1", help="Host to bind")
        parser.add_argument("--port", type=int, default=8777, help="Port to bind")
        args = parser.parse_args()

        app = web.Application()
        app["registry_path"] = Path(args.registry).resolve()
        app.router.add_get("/", index_handler)
        app.router.add_get("/bot/{bot_id}", bot_page_handler)
        app.router.add_post("/bot/{bot_id}/save", save_bot_handler)
        app.router.add_post("/build", build_handler)
        app.router.add_get("/control-plane", control_plane_handler)
        app.router.add_get("/integrations", integrations_handler)
        app.router.add_get("/integrations/{integration_key}", integration_detail_handler)
        app.router.add_get("/tools", tools_handler)
        app.router.add_get("/tools/{tool_name}", tool_detail_handler)
        app.router.add_get("/bots", bots_handler)
        app.router.add_get("/bots/{bot_id}", bot_detail_handler)
        web.run_app(app, host=args.host, port=args.port)
    except RuntimeError as e:
        print(f"ERROR: {e}")
        raise SystemExit(1) from e


if __name__ == "__main__":
    main()
