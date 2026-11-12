#!/usr/bin/env python3
"""
AI Forge Studio — génération des supports e-learning via NotebookLM.

Pipeline : content/curriculum.json + content/sessions/*.md
           → un notebook NotebookLM par session (source = le texte de la session)
           → vidéo, podcast audio, quiz, flashcards, slides, infographie
           → téléchargés dans media/<session>/ + media/manifest.json
           → lus par la plateforme web (assets/elearning.js).

S'appuie sur la lib non officielle notebooklm-py (>= 0.8.6), la même que
le dépôt abs17/notebooklm-ui, et sur la même session Google :
    notebooklm login --fresh --browser chrome

Commandes :
    python tools/nlm_studio.py plan                     # ce qui serait fait (aucun appel réseau)
    python tools/nlm_studio.py sync                     # crée/maj les notebooks et leurs sources
    python tools/nlm_studio.py launch [--only video,quiz] [--session s1] [--force]
    python tools/nlm_studio.py collect [--wait 1800]    # télécharge ce qui est prêt
    python tools/nlm_studio.py run                      # sync + launch + collect (attend la fin)
    python tools/nlm_studio.py status
    python tools/nlm_studio.py manifest                 # reconstruit media/manifest.json depuis le disque

Toutes les commandes acceptent --storage <chemin storage_state.json> et --session <id>.
"""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CURRICULUM = ROOT / "content" / "curriculum.json"
MEDIA = ROOT / "media"
MANIFEST = MEDIA / "manifest.json"
STATE = ROOT / "tools" / ".nlm_state.json"  # IDs de notebooks/tâches (exclu de Git)

# kind → (extension du fichier, méthode de téléchargement, kwargs de téléchargement)
KINDS: dict[str, tuple[str, str, dict]] = {
    "video":       (".mp4",  "download_video",       {}),
    "audio":       (".m4a",  "download_audio",       {}),
    "quiz":        (".json", "download_quiz",        {"output_format": "json"}),
    "flashcards":  (".json", "download_flashcards",  {"output_format": "json"}),
    "slides":      (".pdf",  "download_slide_deck",  {"output_format": "pdf"}),
    "infographic": (".png",  "download_infographic", {}),
    "study_guide": (".md",   "download_report",      {}),
}


# ─── Utilitaires ────────────────────────────────────────────────────────────

def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def say(msg: str, level: str = "info") -> None:
    icon = {"info": "·", "ok": "✓", "warn": "!", "err": "✗"}.get(level, "·")
    print(f"[{datetime.now():%H:%M:%S}] {icon} {msg}", flush=True)


def load_json(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return default


def save_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def load_curriculum() -> dict:
    return load_json(CURRICULUM, None) or sys.exit(f"Introuvable : {CURRICULUM}")


def select_sessions(cur: dict, only_session: str | None) -> list[dict]:
    sessions = cur["sessions"]
    if only_session:
        sessions = [s for s in sessions if s["id"] == only_session]
        if not sessions:
            sys.exit(f"Session inconnue : {only_session}")
    return sessions


def wanted_kinds(session: dict, only: list[str] | None) -> list[str]:
    kinds = [k for k in session.get("media", []) if k in KINDS]
    return [k for k in kinds if not only or k in only]


def media_path(sid: str, kind: str) -> Path:
    return MEDIA / sid / f"{kind}{KINDS[kind][0]}"


# ─── Client NotebookLM ──────────────────────────────────────────────────────

def _import_lib():
    try:
        import notebooklm  # noqa: F401
        return notebooklm
    except ImportError:
        sys.exit("notebooklm-py manquant : pip install -r tools/requirements.txt")


def client(storage: str | None):
    nlm = _import_lib()
    return nlm.NotebookLMClient.from_storage(path=storage)


def enum(nlm, name: str, value: str | None):
    """Convertit une valeur texte du curriculum ('WHITEBOARD') en enum notebooklm-py."""
    if not value:
        return None
    try:
        return getattr(nlm, name)[value.upper()]
    except KeyError:
        valid = ", ".join(m.name for m in getattr(nlm, name))
        sys.exit(f"Valeur invalide pour {name} : {value} (attendu : {valid})")


# ─── Étape 1 : notebooks + sources ──────────────────────────────────────────

async def sync_sources(cl, cur: dict, sessions: list[dict], state: dict) -> None:
    prefix = cur["generation"].get("notebook_prefix", "")
    for s in sessions:
        sid = s["id"]
        st = state.setdefault(sid, {})
        text = (ROOT / s["source"]).read_text(encoding="utf-8")
        h = sha(text)

        if not st.get("notebook_id"):
            nb = await cl.notebooks.create(f"{prefix}{s['title']}")
            st.update(notebook_id=nb.id, created_at=now())
            say(f"{sid} : notebook créé ({nb.id})", "ok")

        if st.get("source_hash") == h and st.get("source_id"):
            say(f"{sid} : source à jour")
            continue

        if st.get("source_id"):
            try:
                await cl.sources.delete(st["notebook_id"], st["source_id"])
            except Exception as e:  # la source a pu être supprimée à la main
                say(f"{sid} : ancienne source non supprimée ({e})", "warn")

        src = await cl.sources.add_text(
            st["notebook_id"], s["title"], text, wait=True, wait_timeout=300
        )
        st.update(source_id=src.id, source_hash=h, source_updated_at=now())
        # Le contenu a changé : les médias existants sont périmés.
        for k in st.get("artifacts", {}).values():
            k["stale"] = True
        say(f"{sid} : source publiée ({src.id})", "ok")
        save_json(STATE, state)


# ─── Étape 2 : lancement des générations ────────────────────────────────────

async def start_generation(cl, nlm, cur: dict, kind: str, nb_id: str):
    g = cur["generation"]
    lang = cur.get("language", "fr")
    instr = g.get("instructions")
    a = cl.artifacts
    if kind == "video":
        return await a.generate_video(
            nb_id, language=lang, instructions=instr,
            video_format=enum(nlm, "VideoFormat", g["video"].get("format")),
            video_style=enum(nlm, "VideoStyle", g["video"].get("style")),
        )
    if kind == "audio":
        return await a.generate_audio(
            nb_id, language=lang, instructions=instr,
            audio_format=enum(nlm, "AudioFormat", g["audio"].get("format")),
            audio_length=enum(nlm, "AudioLength", g["audio"].get("length")),
        )
    if kind in ("quiz", "flashcards"):
        fn = a.generate_quiz if kind == "quiz" else a.generate_flashcards
        return await fn(
            nb_id,
            instructions=f"{instr} Rédige en français.",
            quantity=enum(nlm, "QuizQuantity", g[kind].get("quantity")),
            difficulty=enum(nlm, "QuizDifficulty", g[kind].get("difficulty")),
        )
    if kind == "slides":
        return await a.generate_slide_deck(
            nb_id, language=lang, instructions=instr,
            slide_format=enum(nlm, "SlideDeckFormat", g["slides"].get("format")),
        )
    if kind == "infographic":
        return await a.generate_infographic(nb_id, language=lang, instructions=instr)
    if kind == "study_guide":
        return await a.generate_study_guide(nb_id, language=lang, extra_instructions=instr)
    raise ValueError(kind)


async def launch(cl, cur: dict, sessions: list[dict], state: dict,
                 only: list[str] | None, force: bool) -> None:
    nlm = _import_lib()
    for s in sessions:
        sid = s["id"]
        st = state.get(sid, {})
        if not st.get("notebook_id"):
            say(f"{sid} : pas de notebook, lance d'abord `sync`", "warn")
            continue
        arts = st.setdefault("artifacts", {})
        for kind in wanted_kinds(s, only):
            cur_art = arts.get(kind, {})
            fresh = cur_art.get("status") in ("pending", "in_progress", "scheduled") or (
                cur_art.get("status") == "completed" and not cur_art.get("stale")
                and media_path(sid, kind).exists()
            )
            if fresh and not force:
                say(f"{sid}/{kind} : déjà {cur_art['status']}, ignoré")
                continue
            try:
                gs = await start_generation(cl, nlm, cur, kind, st["notebook_id"])
            except Exception as e:
                say(f"{sid}/{kind} : échec du lancement — {e}", "err")
                arts[kind] = {"status": "failed", "error": str(e), "at": now()}
                save_json(STATE, state)
                continue
            if gs.is_failed:
                say(f"{sid}/{kind} : refusé par NotebookLM — {gs.error} ({gs.error_code})", "err")
                arts[kind] = {"status": "failed", "error": gs.error, "at": now()}
            else:
                arts[kind] = {"task_id": gs.task_id, "status": gs.status, "at": now()}
                say(f"{sid}/{kind} : lancé ({gs.task_id})", "ok")
            save_json(STATE, state)
            await asyncio.sleep(2)  # ménage les quotas


# ─── Étape 3 : suivi + téléchargement ───────────────────────────────────────

async def collect(cl, sessions: list[dict], state: dict, wait: int, poll: int = 30) -> None:
    deadline = time.monotonic() + wait
    while True:
        pending = 0
        for s in sessions:
            sid = s["id"]
            st = state.get(sid, {})
            for kind, art in st.get("artifacts", {}).items():
                if kind not in KINDS or not art.get("task_id"):
                    continue
                if art.get("status") == "completed" and art.get("file"):
                    continue
                if art.get("status") == "failed":
                    continue
                gs = await cl.artifacts.poll_status(st["notebook_id"], art["task_id"])
                art["status"] = gs.status
                if gs.is_complete:
                    out = media_path(sid, kind)
                    out.parent.mkdir(parents=True, exist_ok=True)
                    ext, method, kw = KINDS[kind]
                    await getattr(cl.artifacts, method)(
                        st["notebook_id"], str(out), artifact_id=art["task_id"], **kw
                    )
                    art.update(file=str(out.relative_to(ROOT)), stale=False, done_at=now())
                    say(f"{sid}/{kind} : téléchargé → {out.relative_to(ROOT)}", "ok")
                elif gs.is_failed:
                    art["error"] = gs.error
                    say(f"{sid}/{kind} : échec — {gs.error}", "err")
                else:
                    pending += 1
                save_json(STATE, state)
        write_manifest()
        if not pending:
            say("Tous les médias demandés sont traités.", "ok")
            return
        if time.monotonic() >= deadline:
            say(f"{pending} média(s) encore en génération. Relance `collect` plus tard.", "warn")
            return
        say(f"{pending} en cours… nouvelle vérification dans {poll}s")
        await asyncio.sleep(poll)


# ─── Manifest lu par la plateforme web ──────────────────────────────────────

def write_manifest() -> dict:
    cur = load_curriculum()
    state = load_json(STATE, {})
    base = cur.get("media_base_url", "").rstrip("/")
    out = {"generated_at": now(), "generator": "NotebookLM (notebooklm-py) via tools/nlm_studio.py",
           "sessions": {}}
    for s in cur["sessions"]:
        sid, entry = s["id"], {}
        for kind in KINDS:
            p = media_path(sid, kind)
            if p.exists() and p.stat().st_size > 0:
                rel = p.relative_to(ROOT).as_posix()
                entry[kind] = f"{base}/{rel}" if base else rel
        if entry:
            if state.get(sid, {}).get("source_hash"):
                entry["source_hash"] = state[sid]["source_hash"]
            entry["title"] = s["title"]
            out["sessions"][sid] = entry
    save_json(MANIFEST, out)
    return out


# ─── CLI ────────────────────────────────────────────────────────────────────

def cmd_plan(args, cur, sessions):
    state = load_json(STATE, {})
    for s in sessions:
        sid = s["id"]
        st = state.get(sid, {})
        text = (ROOT / s["source"]).read_text(encoding="utf-8")
        src = "à jour" if st.get("source_hash") == sha(text) else "à (re)publier"
        print(f"\n{sid} — {s['title']}\n  notebook : {st.get('notebook_id', 'à créer')}\n  source   : {src}")
        for k in wanted_kinds(s, args.only):
            a = st.get("artifacts", {}).get(k, {})
            on_disk = "sur disque" if media_path(sid, k).exists() else "absent"
            print(f"  {k:<12} {a.get('status', '—'):<12} {on_disk}{'  (périmé)' if a.get('stale') else ''}")


def cmd_status(args, cur, sessions):
    state = load_json(STATE, {})
    print(json.dumps({s["id"]: state.get(s["id"], {}) for s in sessions}, ensure_ascii=False, indent=2))


async def cmd_async(args, cur, sessions):
    state = load_json(STATE, {})
    async with client(args.storage) as cl:
        if args.cmd in ("sync", "run"):
            await sync_sources(cl, cur, sessions, state)
        if args.cmd in ("launch", "run"):
            await launch(cl, cur, sessions, state, args.only, args.force)
        if args.cmd in ("collect", "run"):
            await collect(cl, sessions, state, wait=args.wait)
    save_json(STATE, state)


def main(argv=None):
    p = argparse.ArgumentParser(description="Génère les médias e-learning via NotebookLM.")
    p.add_argument("cmd", choices=["plan", "sync", "launch", "collect", "run", "status", "manifest"])
    p.add_argument("--session", help="Limiter à une session (ex. s1)")
    p.add_argument("--only", type=lambda v: [x.strip() for x in v.split(",") if x.strip()],
                   help=f"Types de médias, séparés par des virgules : {', '.join(KINDS)}")
    p.add_argument("--force", action="store_true", help="Régénérer même si le média existe")
    p.add_argument("--wait", type=int, default=None,
                   help="Attente max en secondes (défaut : 1800 pour run, 0 pour collect = un seul passage)")
    p.add_argument("--storage", help="Chemin du storage_state.json (défaut : profil notebooklm actif)")
    args = p.parse_args(argv)

    if args.only and (bad := [k for k in args.only if k not in KINDS]):
        p.error(f"type(s) inconnu(s) : {', '.join(bad)}")
    cur = load_curriculum()
    sessions = select_sessions(cur, args.session)

    if args.cmd == "plan":
        return cmd_plan(args, cur, sessions)
    if args.cmd == "status":
        return cmd_status(args, cur, sessions)
    if args.cmd == "manifest":
        m = write_manifest()
        say(f"manifest écrit : {sum(k in KINDS for v in m['sessions'].values() for k in v)} média(s)", "ok")
        return
    if args.wait is None:
        args.wait = 1800 if args.cmd == "run" else 0
    asyncio.run(cmd_async(args, cur, sessions))


if __name__ == "__main__":
    main()
