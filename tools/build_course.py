#!/usr/bin/env python3
"""
Génère les parties « contenu » des pages à partir de la source unique :
    content/curriculum.json  +  content/sessions/*.md
→ index.html                      : onglets, panneaux de sessions, liste des checklists
→ openclaw-masterclass-2026.html  : défi 15 min, cartes de sessions, checklists RGPD

Seules les zones entre <!-- BUILD:nom --> et <!-- /BUILD:nom --> sont réécrites ;
le reste des pages (design, JS, ressources) est conservé.

    python3 tools/build_course.py          # régénère les pages
    python3 tools/build_course.py --check  # échoue si les pages ne sont pas à jour (CI)

Conventions Markdown des sessions :
    # Titre / *AI Forge…* / **Objectif :** … → ignorés (titre et objectif viennent de curriculum.json)
    ## Section                 → une carte
    ### Sous-titre             → titre dans la carte
    ```bash titre landing      → bloc de code avec bouton Copier ; « landing » = repris sur la landing,
                                 « quickstart » = terminal du défi 15 min
    > 💡 **Titre** texte        → encadré (💡 orange, ⚠️ rouge, ℹ️ cyan, ✅ vert)
    ## Checklist [suffixe]     → checklist interactive (une par section)
    ## Quiz                    → questions : **Question ?** puis - [x] / - [ ] puis > explication
"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CUR = json.loads((ROOT / "content" / "curriculum.json").read_text(encoding="utf-8"))
COURSE = ROOT / "index.html"
LANDING = ROOT / "openclaw-masterclass-2026.html"

COLORS = {  # couleur d'accent par session (reprend le design existant)
    "prereqs": ("#FF6B00", "rgba(255,107,0,"), "s1": ("#FF6B00", "rgba(255,107,0,"),
    "s2": ("#00F5FF", "rgba(0,245,255,"), "s3": ("#FCA5A5", "rgba(239,68,68,"),
    "s4": ("#FCD34D", "rgba(234,179,8,"), "security": ("#86EFAC", "rgba(34,197,94,"),
}
CODE_STYLE = 'class="font-mono text-xs px-1 rounded" style="background:rgba(255,255,255,0.1)"'
CALLOUTS = {"💡": ("#FF6B00", "rgba(255,107,0,0.07)", "rgba(255,107,0,0.2)"),
            "⚠️": ("#FCA5A5", "rgba(239,68,68,0.07)", "rgba(239,68,68,0.2)"),
            "ℹ️": ("#00F5FF", "rgba(0,245,255,0.05)", "rgba(0,245,255,0.15)"),
            "✅": ("#86EFAC", "rgba(34,197,94,0.07)", "rgba(34,197,94,0.2)")}


# ─── Markdown minimal ───────────────────────────────────────────────────────

def inline(text: str) -> str:
    out, parts = [], re.split(r"(`[^`]+`)", text)
    for p in parts:
        if p.startswith("`") and p.endswith("`") and len(p) > 1:
            out.append(f"<code {CODE_STYLE}>{html.escape(p[1:-1], quote=False)}</code>")
            continue
        p = html.escape(p, quote=False)
        p = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)",
                   r'<a href="\2" target="_blank" rel="noopener" style="color:#FF6B00;text-decoration:underline">\1</a>', p)
        p = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", p)
        p = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", p)
        out.append(p)
    return "".join(out)


def highlight(code: str, lang: str) -> str:
    lines, out, cont = code.split("\n"), [], False
    for raw in lines:
        e = html.escape(raw, quote=False)
        if lang in ("bash", "sh", "shell", "powershell", "console"):
            if re.match(r"\s*#", raw):
                e = f'<span style="color:#6C757D">{e}</span>'
            elif raw.strip() and not cont:
                e = re.sub(r"^(\s*)(\S+)", r'\1<span style="color:#FF6B00">\2</span>', e, count=1)
                e = re.sub(r"(\s)(#\s.*)$", r'\1<span style="color:#6C757D">\2</span>', e)
            cont = raw.rstrip().endswith("\\")
        elif lang in ("json", "json5", "js", "javascript", "ts", "typescript", "yaml", "yml"):
            m = re.match(r"^(.*?)(\s*(?://|#)\s.*)?$", e)
            body, comment = (m.group(1), m.group(2) or "") if m else (e, "")
            if re.match(r"\s*(//|#)", e):
                body, comment = "", e
            body = re.sub(r'("(?:[^"\\]|\\.)*")(\s*:)', r'<span style="color:#86EFAC">\1</span>\2', body)
            body = re.sub(r'(:\s*|\[\s*|,\s*)("(?:[^"\\]|\\.)*")', r'\1<span style="color:#FCD34D">\2</span>', body)
            if comment:
                comment = f'<span style="color:#6C757D">{comment}</span>'
            e = body + comment
        out.append(e)
    return "\n".join(out)


class Block:
    def __init__(self, kind, **kw):
        self.kind, self.__dict__ = kind, {**kw, "kind": kind}


def parse_md(text: str):
    """Retourne une liste de sections : {title, blocks:[Block]}."""
    sections, cur = [], {"title": None, "blocks": []}
    lines = text.split("\n")
    i = 0
    para: list[str] = []

    def flush():
        if para:
            cur["blocks"].append(Block("p", text=" ".join(s.strip() for s in para)))
            para.clear()

    while i < len(lines):
        ln = lines[i]
        if ln.startswith("# ") or ln.startswith("*AI Forge") or ln.startswith("**Objectif"):
            i += 1
            continue
        if ln.startswith("## "):
            flush()
            if cur["title"] or cur["blocks"]:
                sections.append(cur)
            cur = {"title": ln[3:].strip(), "blocks": []}
        elif ln.startswith("### "):
            flush()
            cur["blocks"].append(Block("h", text=ln[4:].strip()))
        elif ln.startswith("```"):
            flush()
            info = ln[3:].strip().split()
            lang = info[0] if info else ""
            flags = {f for f in info[1:] if f in ("landing", "quickstart")}
            title = " ".join(f for f in info[1:] if f not in flags)
            body = []
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                body.append(lines[i])
                i += 1
            cur["blocks"].append(Block("code", lang=lang, title=title, flags=flags, code="\n".join(body)))
        elif ln.startswith(">"):
            flush()
            q = []
            while i < len(lines) and lines[i].startswith(">"):
                q.append(lines[i][1:].strip())
                i += 1
            cur["blocks"].append(Block("quote", text=" ".join(q)))
            continue
        elif re.match(r"\s*([-*]|\d+\.)\s", ln):
            flush()
            ordered = bool(re.match(r"\s*\d+\.", ln))
            items = []
            while i < len(lines) and re.match(r"\s*([-*]|\d+\.)\s", lines[i]):
                items.append(re.sub(r"^\s*([-*]|\d+\.)\s+", "", lines[i]))
                i += 1
                while i < len(lines) and lines[i].startswith("  ") and lines[i].strip():
                    items[-1] += " " + lines[i].strip()
                    i += 1
            cur["blocks"].append(Block("list", ordered=ordered, items=items))
            continue
        elif ln.startswith("|"):
            flush()
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-{2,}:?", c) for c in cells):
                    rows.append(cells)
                i += 1
            cur["blocks"].append(Block("table", rows=rows))
            continue
        elif not ln.strip():
            flush()
        else:
            para.append(ln)
        i += 1
    flush()
    if cur["title"] or cur["blocks"]:
        sections.append(cur)
    return sections


def parse_quiz(blocks) -> list[dict]:
    qs, q = [], None
    for b in blocks:
        if b.kind == "p" and b.text.startswith("**"):
            q = {"question": b.text.strip("* "), "options": [], "explanation": ""}
            qs.append(q)
        elif b.kind == "list" and q is not None:
            for it in b.items:
                m = re.match(r"\[( |x|X)\]\s*(.*)", it)
                if m:
                    q["options"].append({"text": m.group(2), "correct": m.group(1).lower() == "x"})
        elif b.kind == "quote" and q is not None:
            q["explanation"] = b.text
    for q in qs:
        n = sum(o["correct"] for o in q["options"])
        if n != 1:
            sys.exit(f"Quiz invalide ({n} bonnes réponses) : {q['question']}")
    return qs


def slug(s: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", s.lower().encode("ascii", "ignore").decode())
    return s.strip("-")


# ─── Rendu HTML (cours) ─────────────────────────────────────────────────────

_code_ids: dict[str, int] = {}


def code_id(sid: str) -> str:
    _code_ids[sid] = _code_ids.get(sid, 0) + 1
    return f"code-{sid}-{_code_ids[sid]}"


def render_code(b, sid: str) -> str:
    cid = code_id(sid)
    label = " · ".join(x for x in (b.lang, b.title) if x) or "code"
    return (f'<div class="code-block mb-4">\n'
            f'  <div class="flex items-center gap-2 px-4 py-2 border-b text-xs font-mono" style="background:rgba(255,255,255,0.04);border-color:rgba(255,255,255,0.07);opacity:.6">{html.escape(label)}</div>\n'
            f'  <pre class="p-4 font-mono text-sm leading-loose overflow-x-auto"><code id="{cid}">{highlight(b.code, b.lang)}</code></pre>\n'
            f'  <div class="px-4 pb-3"><button onclick="copyCodeBlock(\'{cid}\')" class="copy-btn flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold transition-all hover:scale-105" style="background:rgba(255,107,0,0.2);color:#FF6B00;border:1px solid rgba(255,107,0,0.3)">🦞 Copier</button></div>\n'
            f'</div>')


def render_block(b, sid: str) -> str:
    if b.kind == "p":
        return f'<p class="text-sm mb-4" style="opacity:.75;line-height:1.75">{inline(b.text)}</p>'
    if b.kind == "h":
        return f'<h4 class="font-bold text-base mt-5 mb-2">{inline(b.text)}</h4>'
    if b.kind == "code":
        return render_code(b, sid)
    if b.kind == "list":
        tag = "ol" if b.ordered else "ul"
        cls = "list-decimal" if b.ordered else "list-disc"
        items = "".join(f'<li class="mb-1.5">{inline(x)}</li>' for x in b.items)
        return f'<{tag} class="{cls} pl-5 text-sm mb-4" style="opacity:.8;line-height:1.7">{items}</{tag}>'
    if b.kind == "table":
        head, *rows = b.rows
        th = "".join(f'<th class="text-left p-2 font-bold">{inline(c)}</th>' for c in head)
        tr = "".join("<tr class=\"border-t\" style=\"border-color:rgba(255,255,255,0.08)\">" +
                     "".join(f'<td class="p-2 align-top">{inline(c)}</td>' for c in r) + "</tr>" for r in rows)
        return f'<div class="overflow-x-auto mb-4"><table class="w-full text-sm"><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table></div>'
    if b.kind == "quote":
        icon = next((k for k in CALLOUTS if b.text.startswith(k)), "💡")
        fg, bg, bd = CALLOUTS[icon]
        text = b.text[len(icon):].strip() if b.text.startswith(icon) else b.text
        m = re.match(r"\*\*(.+?)\*\*\s*[—:-]?\s*(.*)", text)
        title, body = (m.group(1), m.group(2)) if m else ("", text)
        t = f'<p class="font-bold mb-1" style="color:{fg}">{icon} {inline(title)}</p>' if title else ""
        return (f'<div class="p-4 rounded-xl text-sm mb-4" style="background:{bg};border:1px solid {bd}">{t}'
                f'<p style="opacity:.8;line-height:1.7">{inline(body)}</p></div>')
    raise ValueError(b.kind)


def render_checklist(sid, title, items, keys_out) -> str:
    rows = []
    for n, it in enumerate(items):
        key = f"{sid}-{slug(title) or 'c'}-{n}"
        keys_out.append(key)
        rows.append(f'      <div class="check-item flex items-start gap-3" data-key="{key}" onclick="toggleCheck(this)">'
                    f'<div class="check-box mt-0.5"></div><span class="text-sm">{inline(it)}</span></div>')
    return (f'  <div class="glass border rounded-2xl p-6 mb-6">\n'
            f'    <h3 class="font-display font-bold text-lg mb-4">✅ {inline(title)}</h3>\n'
            f'    <div class="space-y-2">\n' + "\n".join(rows) + "\n    </div>\n  </div>")


def render_quiz_course(sid, qs) -> str:
    out = []
    for n, q in enumerate(qs):
        qid = f"quiz-{sid}-{n}"
        opts = "\n".join(
            f'      <button class="quiz-opt" data-correct="{str(o["correct"]).lower()}" onclick="handleQuiz(this,\'{qid}\')">'
            f'{chr(65 + k)}. {inline(o["text"])}</button>' for k, o in enumerate(q["options"]))
        expl = (f'\n      <p class="quiz-expl text-xs mt-2" style="opacity:.7;line-height:1.6">💬 {inline(q["explanation"])}</p>'
                if q["explanation"] else "")
        out.append(f'    <div id="{qid}" class="space-y-3 mb-6">\n'
                   f'      <p class="text-sm font-semibold mb-2" style="opacity:.8">{n + 1}. {inline(q["question"])}</p>\n{opts}{expl}\n    </div>')
    return (f'  <div class="glass border rounded-2xl p-6 mb-6">\n'
            f'    <h3 class="font-bold text-base mb-4">🧠 Quiz de validation</h3>\n' + "\n".join(out) + "\n  </div>")


def load_session(s):
    secs = parse_md((ROOT / s["source"]).read_text(encoding="utf-8"))
    content, checklists, quiz = [], [], []
    for sec in secs:
        t = sec["title"] or ""
        if t.lower().startswith("checklist"):
            items = [x for b in sec["blocks"] if b.kind == "list" for x in b.items]
            checklists.append((t, items))
        elif t.lower().startswith("quiz"):
            quiz += parse_quiz(sec["blocks"])
        else:
            content.append(sec)
    return content, checklists, quiz


def label_for(s) -> str:
    if s["id"] == "prereqs":
        return "Étape 0"
    if s["id"] == "security":
        return "Module transverse"
    return f"Session {s['number']}"


def build_course(sessions_data, all_keys) -> tuple[str, str]:
    tabs, panels = [], []
    ss = CUR["sessions"]
    for idx, s in enumerate(ss):
        sid = s["id"]
        content, checklists, quiz = sessions_data[sid]
        tab_label = s.get("tab") or s["short"]
        tabs.append(f'    <button class="tab-btn{" active" if idx == 0 else ""}" data-tab="{sid}">{html.escape(tab_label)}</button>')
        fg, rgba = COLORS.get(sid, COLORS["s1"])
        body = [f'<div id="tab-{sid}" class="tab-panel{" active" if idx == 0 else ""}">',
                f'  <div class="section-label">{label_for(s)}</div>',
                f'  <h2 class="font-display font-black text-4xl mb-2">{html.escape(s["title"])}</h2>',
                f'  <p class="mb-8" style="opacity:.6;line-height:1.8">{inline(s["objective"])}</p>',
                f'  <div data-elearning="{sid}"></div>']
        for sec in content:
            # Pas d'indentation : elle s'ajouterait au contenu des <pre>.
            inner = "\n".join(render_block(b, sid) for b in sec["blocks"])
            title = f'    <h3 class="font-display font-bold text-xl mb-3">{inline(sec["title"])}</h3>\n' if sec["title"] else ""
            body.append(f'  <div class="glass border rounded-2xl p-6 mb-6">\n{title}{inner}\n  </div>')
        for t, items in checklists:
            body.append(render_checklist(sid, t, items, all_keys))
        if quiz:
            body.append(render_quiz_course(sid, quiz))
        if s.get("badge"):
            b = s["badge"]
            final = ' data-final="1"' if b.get("final") else ""
            body.append(
                f'  <div class="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 glass border rounded-2xl p-6 mb-4">\n'
                f'    <div>\n      <p class="font-bold">{"Badge final à débloquer" if b.get("final") else "Badge à débloquer"}</p>\n'
                f'      <span id="badge-{sid}" class="badge-unlock locked mt-2"{final} style="border-color:{rgba}0.4);color:{fg};">{b["icon"]} {html.escape(b["label"])}</span>\n    </div>\n'
                f'    <button onclick="completeSession(\'{sid}\',\'badge-{sid}\')" class="shimmer-btn px-6 py-3 rounded-xl font-bold text-sm transition-all hover:scale-105" style="background:{rgba}0.12);border:1px solid {rgba}0.4);color:{fg}">Valider {label_for(s)} ✅</button>\n  </div>')
        if idx + 1 < len(ss):
            nxt = ss[idx + 1]
            body.append(f'  <div class="flex justify-end"><button onclick="switchTab(\'{nxt["id"]}\')" class="shimmer-btn px-6 py-3 rounded-xl font-bold text-sm transition-all hover:scale-105" style="background:#FF6B00;color:white">{label_for(nxt)} → {html.escape(nxt["short"])} ▶</button></div>')
        body.append("</div>\n")
        panels.append("\n".join(body))
    return "\n".join(tabs) + "\n", "\n".join(panels)


# ─── Rendu HTML (landing) ───────────────────────────────────────────────────

def landing_code(b, cid) -> str:
    label = " · ".join(x for x in (b.lang, b.title) if x)
    return (f'        <div class="code-block relative rounded-xl border overflow-hidden" style="background:#080808;border-color:rgba(255,255,255,0.1)">\n'
            f'          <div class="flex items-center gap-2 px-4 py-2 border-b text-xs font-mono" style="background:rgba(255,255,255,0.04);border-color:rgba(255,255,255,0.07);opacity:.6">{html.escape(label)}</div>\n'
            f'          <pre class="p-5 font-mono text-sm overflow-x-auto leading-loose" style="color:#e0e0e0"><code id="{cid}">{highlight(b.code, b.lang)}</code></pre>\n'
            f'          <button onclick="copyCodeBlock(\'{cid}\')" class="absolute top-9 right-3 flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold transition-all hover:scale-105" style="background:rgba(255,107,0,0.2);color:#FF6B00;border:1px solid rgba(255,107,0,0.3)">🦞 Copier</button>\n'
            f'        </div>')


def build_landing_sessions(sessions_data) -> str:
    cards = []
    for s in [x for x in CUR["sessions"] if x.get("badge")]:
        sid, n = s["id"], s["number"]
        content, _, quiz = sessions_data[sid]
        fg, rgba = COLORS[sid]
        codes = [b for sec in content for b in sec["blocks"] if b.kind == "code" and "landing" in b.flags]
        code_html = "\n".join(landing_code(b, f"code-landing-{sid}-{k}") for k, b in enumerate(codes))
        mini = ""
        if quiz:
            q = quiz[0]
            opts = "\n".join(
                f'          <button class="quiz-opt w-full text-left p-4 rounded-xl text-sm border" style="background:rgba(255,255,255,0.04);border-color:rgba(255,255,255,0.09)" data-correct="{str(o["correct"]).lower()}" onclick="handleQuiz(this,\'quiz-{sid}\')">{chr(65 + k)}. {inline(o["text"])}</button>'
                for k, o in enumerate(q["options"]))
            mini = (f'      <div class="p-6 rounded-xl border" style="background:rgba(255,255,255,0.03);border-color:rgba(255,255,255,0.08)">\n'
                    f'        <p class="font-bold mb-4 text-sm">🧠 Mini-quiz — {inline(q["question"])}</p>\n'
                    f'        <div class="space-y-2" id="quiz-{sid}">\n{opts}\n        </div>\n      </div>')
        b = s["badge"]
        cards.append(f'''    <!-- SESSION {n} -->
    <div class="session-card glass-card rounded-2xl p-8 mb-6" data-session="{n}" style="border-color:rgba(255,255,255,0.07)">
      <div class="flex justify-between items-start mb-4">
        <span class="session-num font-display font-black text-8xl leading-none" style="opacity:.07;color:inherit">{n:02d}</span>
        <div class="flex items-center gap-3">
          <span class="px-3 py-1 rounded-full text-xs font-bold" style="background:{rgba}0.15);color:{fg}">{b["icon"]} {html.escape(b["label"])}</span>
          <div class="badge-completed hidden px-3 py-1 rounded-full text-xs font-bold" style="background:rgba(34,197,94,0.2);color:#86EFAC">TERMINÉ ✅</div>
        </div>
      </div>
      <h4 class="text-2xl md:text-3xl font-display font-black mb-2">Session {n} — {html.escape(s["title"])}</h4>
      <p class="mb-6 text-sm" style="opacity:.55;line-height:1.7">Objectif : {inline(s["objective"])}</p>
      <div data-elearning="{sid}" data-kinds="video,audio"></div>
      <p class="mb-6 text-xs" style="opacity:.55">Pas à pas complet, quiz, flashcards et slides : <a href="index.html#{sid}" style="color:var(--lobster);font-weight:700">ouvrir la session {n} dans le cours →</a></p>
      <div class="space-y-4 mb-6">
{code_html}
      </div>
{mini}
      <button class="session-done-btn mt-6 w-full py-3 rounded-xl font-bold text-sm transition-all duration-300 hover:scale-[1.02]" data-session="{n}" style="background:{rgba}0.12);border:1px solid {rgba}0.4);color:{fg}" onclick="markSessionDone({n})">
        Marquer la session {n} comme terminée{" — obtenir le badge final 👑" if b.get("final") else " ✅"}
      </button>
    </div>
''')
    return "".join(cards)


def build_landing_quickstart(sessions_data) -> str:
    content = sessions_data["prereqs"][0]
    qs = [b for sec in content for b in sec["blocks"] if b.kind == "code" and "quickstart" in b.flags]
    if not qs:
        sys.exit("Aucun bloc ```bash quickstart dans les prérequis")
    code = highlight(qs[0].code, qs[0].lang)
    qtext = CUR.get("quickstart", {})
    return f'''<section class="py-20 px-6 border-t" style="border-color:rgba(255,255,255,0.05)">
  <div class="max-w-5xl mx-auto flex flex-col md:flex-row gap-12 items-center">
    <div class="flex-1">
      <p class="text-xs font-bold tracking-widest uppercase mb-3" style="color:var(--lobster)">Défi rapide</p>
      <h3 class="text-4xl md:text-5xl font-display font-black mb-5 leading-tight">
        Ton premier agent en <span class="text-neon-cyan" style="color:var(--cyan-neon)">15:00</span> chrono
      </h3>
      <p class="mb-8 text-lg" style="opacity:.65;line-height:1.7">
        {inline(qtext.get("pitch", ""))}
      </p>
      <button id="start-timer" class="flex items-center gap-4 px-8 py-4 rounded-xl font-bold text-sm border transition-all duration-300 hover:scale-105" style="background:rgba(0,245,255,0.08);border-color:var(--cyan-neon);color:var(--cyan-neon)" onclick="startTimer(900)">
        <span>▶ Lancer le chrono</span>
        <span id="timer-display" class="font-mono text-2xl font-black">15:00</span>
      </button>
      <p id="timer-status" class="mt-3 text-xs" style="opacity:.45"></p>
    </div>
    <div class="flex-1 w-full">
      <div class="code-block relative rounded-2xl border overflow-hidden" style="background:#080808;border-color:rgba(255,255,255,0.12)">
        <div class="flex items-center gap-2 px-5 py-3 border-b" style="background:rgba(255,255,255,0.04);border-color:rgba(255,255,255,0.08)">
          <div class="w-3 h-3 rounded-full bg-red-500"></div>
          <div class="w-3 h-3 rounded-full bg-yellow-500"></div>
          <div class="w-3 h-3 rounded-full bg-green-500"></div>
          <span class="text-xs ml-3 font-mono" style="opacity:.4">terminal — bash</span>
          <div style="position:absolute;left:0;right:0;height:2px;background:linear-gradient(90deg,transparent,rgba(0,245,255,0.3),transparent);animation:scanline 3s linear infinite;pointer-events:none"></div>
        </div>
        <pre class="p-6 font-mono text-sm overflow-x-auto leading-relaxed" style="color:#e0e0e0"><code id="code-install">{code}<span class="terminal-cursor"></span></code></pre>
        <button onclick="copyCodeBlock('code-install')" class="absolute top-10 right-3 flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold transition-all duration-200 hover:scale-105" style="background:rgba(255,107,0,0.2);color:#FF6B00;border:1px solid rgba(255,107,0,0.3)">🦞 Copier</button>
      </div>
    </div>
  </div>
</section>

'''


def build_landing_security(sessions_data) -> str:
    _, checklists, _ = sessions_data["security"]
    cards = []
    for t, items in checklists:
        flag = "🇫🇷" if "france" in t.lower() else "🇪🇺" if "europe" in t.lower() else "✅"
        lis = "\n".join(
            f'          <li class="flex items-start gap-3 text-sm">\n'
            f'            <span class="w-5 h-5 rounded border-2 flex items-center justify-center shrink-0 mt-0.5 transition-colors" style="border-color:rgba(134,239,172,0.5)"></span>\n'
            f'            <span>{inline(it)}</span>\n          </li>' for it in items)
        cards.append(f'''      <div class="glass-card rounded-2xl p-7">
        <div class="flex items-center gap-3 mb-6">
          <span class="text-3xl">{flag}</span>
          <h4 class="font-display font-black text-xl">{inline(t)}</h4>
        </div>
        <ul class="space-y-3">
{lis}
        </ul>
      </div>''')
    return '    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">\n' + "\n".join(cards) + "\n    </div>\n"


def build_resources() -> str:
    res = CUR.get("resources", {})
    links = "\n".join(
        f'      <a href="{html.escape(l["url"])}" target="_blank" rel="noopener" class="flex items-center gap-3 p-4 rounded-xl border transition-all hover:scale-[1.02] hover:border-orange-500/40" style="border-color:rgba(255,255,255,0.08);background:rgba(255,255,255,0.03)">\n'
        f'        <span class="text-xl">{l["icon"]}</span>\n'
        f'        <div><p class="font-bold text-sm">{html.escape(l["label"])}</p><p class="text-xs" style="opacity:.5">{html.escape(re.sub(r"^https?://(www\.)?", "", l["url"]).rstrip("/"))}</p></div>\n'
        f'        <span class="ml-auto text-xs" style="opacity:.4">↗</span>\n      </a>' for l in res.get("links", []))
    gloss = "\n".join(
        f'      <div class="accordion-header flex items-center justify-between p-4 rounded-xl hover:bg-white/5 transition-all" onclick="toggleAccordion(this)">\n'
        f'        <div class="flex items-center gap-3"><span class="font-mono text-sm font-bold" style="color:#FF6B00">{html.escape(g["term"])}</span><span class="text-sm font-semibold">{html.escape(g["full"])}</span></div>\n'
        f'        <span class="accordion-arrow text-xs" style="opacity:.5">▼</span>\n      </div>\n'
        f'      <div class="accordion-body px-4 pb-4"><p class="text-sm" style="opacity:.65;line-height:1.7">{inline(g["def"])}</p></div>'
        for g in res.get("glossary", []))
    return (f'  <div class="glass border rounded-2xl p-6 mb-6">\n    <h3 class="font-display font-bold text-xl mb-4">🔗 Liens officiels</h3>\n'
            f'    <div class="grid grid-cols-1 md:grid-cols-2 gap-3">\n{links}\n    </div>\n  </div>\n'
            f'  <div class="glass border rounded-2xl p-6 mb-6">\n    <h3 class="font-display font-bold text-xl mb-4">📖 Glossaire</h3>\n'
            f'    <div class="space-y-1" id="glossaire">\n{gloss}\n    </div>\n  </div>\n')


# ─── Injection ──────────────────────────────────────────────────────────────

def inject(page: str, name: str, content: str, js: bool = False) -> str:
    if js:
        pat = re.compile(r"(/\* BUILD:%s \*/\n).*?(/\* /BUILD:%s \*/)" % (name, name), re.S)
    else:
        pat = re.compile(r"(<!-- BUILD:%s [^>]*-->\n).*?(<!-- /BUILD:%s -->)" % (name, name), re.S)
    if not pat.search(page):
        sys.exit(f"Marqueur BUILD:{name} introuvable")
    return pat.sub(lambda m: m.group(1) + content + m.group(2), page, count=1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    data = {s["id"]: load_session(s) for s in CUR["sessions"]}
    keys: list[str] = []
    tabs, panels = build_course(data, keys)

    course = COURSE.read_text(encoding="utf-8")
    new_course = inject(course, "tabs", tabs)
    new_course = inject(new_course, "panels", panels)
    new_course = inject(new_course, "resources", build_resources())
    new_course = inject(new_course, "checks", "const ALL_CHECKS = " + json.dumps(keys) + ";\n", js=True)

    landing = LANDING.read_text(encoding="utf-8")
    new_landing = inject(landing, "quickstart", build_landing_quickstart(data))
    new_landing = inject(new_landing, "sessions", build_landing_sessions(data))
    new_landing = inject(new_landing, "security", build_landing_security(data))

    changed = [p.name for p, old, new in ((COURSE, course, new_course), (LANDING, landing, new_landing)) if old != new]
    if args.check:
        if changed:
            sys.exit("Pages non à jour : " + ", ".join(changed) + " → python3 tools/build_course.py")
        print("Pages à jour.")
        return
    COURSE.write_text(new_course, encoding="utf-8")
    LANDING.write_text(new_landing, encoding="utf-8")
    nq = sum(len(d[2]) for d in data.values())
    print(f"✓ {len(CUR['sessions'])} sessions, {len(keys)} cases de checklist, {nq} questions de quiz"
          + (f" — modifié : {', '.join(changed)}" if changed else " — rien à changer"))


if __name__ == "__main__":
    main()
