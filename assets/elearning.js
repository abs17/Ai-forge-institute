/*
 * AI Forge Institute — lecteur e-learning partagé (cours + landing).
 *
 * Usage : <div data-elearning="s1"></div>  puis  <script src="assets/elearning.js" defer></script>
 * Les médias (vidéo, podcast, quiz, flashcards, slides…) sont générés avec NotebookLM par
 * tools/nlm_studio.py et listés dans media/manifest.json. Aucun appel à un service tiers
 * n'est fait à la lecture ; la progression reste dans le localStorage du navigateur.
 */
(function () {
  'use strict';

  const KEYS = {
    sessions: 'openclaw_sessions_done',   // partagé avec index.html (badges)
    quiz: 'forge_quiz_scores',
    cards: 'forge_flashcards_known',
    media: 'forge_media_watched',
  };
  const TABS = [
    ['video', '🎬', 'Vidéo'],
    ['audio', '🎧', 'Podcast'],
    ['quiz', '🧠', 'Quiz'],
    ['flashcards', '🃏', 'Flashcards'],
    ['slides', '📑', 'Slides'],
    ['infographic', '🖼️', 'Infographie'],
    ['study_guide', '📘', 'Fiche'],
  ];

  const script = document.currentScript;
  const BASE = new URL('..', script ? script.src : location.href);

  // ─── Stockage local tolérant (mode privé, stockage bloqué…) ───
  const store = {
    get(k, d) { try { const v = JSON.parse(localStorage.getItem(k)); return v == null ? d : v; } catch (e) { return d; } },
    set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) { /* ignoré */ } },
  };

  // ─── Construction DOM sans innerHTML (le contenu généré n'est jamais interprété) ───
  function h(tag, attrs, ...kids) {
    const el = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs || {})) {
      if (v == null || v === false) continue;
      if (k === 'class') el.className = v;
      else if (k.startsWith('on')) el.addEventListener(k.slice(2), v);
      else el.setAttribute(k, v === true ? '' : v);
    }
    for (const kid of kids.flat()) if (kid != null && kid !== false) el.append(kid);
    return el;
  }

  function toast(msg) {
    if (typeof window.showToast === 'function') window.showToast(msg);
  }

  const url = (p) => new URL(p, BASE).href;

  let manifestPromise = null;
  function manifest() {
    if (!manifestPromise) {
      manifestPromise = fetch(url('media/manifest.json'), { cache: 'no-cache' })
        .then((r) => (r.ok ? r.json() : { sessions: {} }))
        .catch(() => ({ sessions: {} }));
    }
    return manifestPromise;
  }

  const jsonCache = {};
  function getJSON(p) {
    if (!jsonCache[p]) jsonCache[p] = fetch(url(p)).then((r) => { if (!r.ok) throw new Error(r.status); return r.json(); });
    return jsonCache[p];
  }

  function markWatched(sid, kind) {
    const all = store.get(KEYS.media, {});
    all[sid] = all[sid] || {};
    if (all[sid][kind]) return;
    all[sid][kind] = new Date().toISOString();
    store.set(KEYS.media, all);
    toast(kind === 'video' ? '🎬 Vidéo terminée !' : '🎧 Podcast écouté !');
  }

  // ─── Renderers ───
  function renderMedia(sid, kind, src) {
    const isVideo = kind === 'video';
    const el = h(isVideo ? 'video' : 'audio', {
      class: isVideo ? 'fe-video' : 'fe-audio', src: url(src), controls: true, preload: 'metadata', playsinline: true,
    });
    el.addEventListener('timeupdate', () => {
      if (el.duration && el.currentTime / el.duration > 0.9) markWatched(sid, kind);
    });
    const wrap = h('div', { class: 'fe-media' }, el);
    const speeds = h('div', { class: 'fe-row fe-speeds' }, h('span', { class: 'fe-muted' }, 'Vitesse'));
    [1, 1.25, 1.5, 2].forEach((r) => {
      const b = h('button', { class: 'fe-chip' + (r === 1 ? ' is-on' : ''), type: 'button', onclick: () => {
        el.playbackRate = r;
        speeds.querySelectorAll('.fe-chip').forEach((c) => c.classList.toggle('is-on', c === b));
      } }, r + '×');
      speeds.append(b);
    });
    wrap.append(speeds);
    if (!isVideo) wrap.prepend(h('p', { class: 'fe-muted' }, 'Podcast généré par NotebookLM à partir du support de la session. Idéal en transport ou en révision.'));
    return wrap;
  }

  function renderQuiz(sid, src) {
    const box = h('div', { class: 'fe-quiz' }, h('p', { class: 'fe-muted' }, 'Chargement du quiz…'));
    getJSON(src).then((data) => {
      const qs = (data.questions || []).filter((q) => q && q.question && (q.answerOptions || []).length);
      if (!qs.length) { box.replaceChildren(h('p', { class: 'fe-muted' }, 'Quiz vide.')); return; }
      let i = 0, score = 0;
      const draw = () => {
        if (i >= qs.length) return finish();
        const q = qs[i];
        let answered = false;
        const feedback = h('div', { class: 'fe-feedback' });
        const next = h('button', { class: 'fe-btn', type: 'button', hidden: true, onclick: () => { i++; draw(); } },
          i + 1 < qs.length ? 'Question suivante →' : 'Voir mon score');
        const opts = q.answerOptions.map((o, idx) => h('button', {
          class: 'fe-opt', type: 'button',
          onclick: (ev) => {
            if (answered) return;
            answered = true;
            const btn = ev.currentTarget;
            btn.classList.add(o.isCorrect ? 'is-correct' : 'is-wrong');
            if (o.isCorrect) score++;
            optEls.forEach((b, j) => { b.disabled = true; if (q.answerOptions[j].isCorrect) b.classList.add('is-correct'); });
            feedback.replaceChildren(
              h('strong', {}, o.isCorrect ? '✅ Bonne réponse. ' : '❌ Pas tout à fait. '),
              o.rationale || (q.answerOptions.find((a) => a.isCorrect) || {}).rationale || ''
            );
            next.hidden = false;
          },
        }, String.fromCharCode(65 + idx) + '. ' + (o.text || '')));
        const optEls = opts;
        const hint = q.hint ? h('details', { class: 'fe-hint' }, h('summary', {}, '💡 Indice'), h('p', {}, q.hint)) : null;
        box.replaceChildren(
          h('div', { class: 'fe-row fe-between' },
            h('span', { class: 'fe-muted' }, `Question ${i + 1} / ${qs.length}`),
            h('span', { class: 'fe-muted' }, `Score : ${score}`)),
          h('div', { class: 'fe-bar' }, h('div', { style: `width:${Math.round((i / qs.length) * 100)}%` })),
          h('p', { class: 'fe-q' }, q.question),
          h('div', { class: 'fe-opts' }, opts),
          hint, feedback, next
        );
      };
      const finish = () => {
        const all = store.get(KEYS.quiz, {});
        const best = Math.max(score, (all[sid] && all[sid].best) || 0);
        all[sid] = { last: score, best, total: qs.length, at: new Date().toISOString() };
        store.set(KEYS.quiz, all);
        const pct = Math.round((score / qs.length) * 100);
        if (pct >= 80) { toast('🏆 Quiz réussi : ' + pct + ' %'); if (typeof window.triggerConfetti === 'function') window.triggerConfetti(); }
        box.replaceChildren(
          h('p', { class: 'fe-score' }, `${score} / ${qs.length}`),
          h('p', { class: 'fe-muted' }, pct >= 80 ? 'Excellent, la session est maîtrisée.' : 'Revois la vidéo ou les flashcards, puis retente ta chance.'),
          h('p', { class: 'fe-muted' }, `Meilleur score : ${best} / ${qs.length}`),
          h('button', { class: 'fe-btn', type: 'button', onclick: () => { i = 0; score = 0; draw(); } }, '↻ Recommencer')
        );
      };
      draw();
    }).catch(() => box.replaceChildren(h('p', { class: 'fe-muted' }, 'Quiz indisponible pour le moment.')));
    return box;
  }

  function renderCards(sid, src) {
    const box = h('div', { class: 'fe-cards' }, h('p', { class: 'fe-muted' }, 'Chargement des flashcards…'));
    getJSON(src).then((data) => {
      let cards = (data.cards || []).filter((c) => c && (c.front || c.back));
      if (!cards.length) { box.replaceChildren(h('p', { class: 'fe-muted' }, 'Aucune flashcard.')); return; }
      const known = new Set((store.get(KEYS.cards, {})[sid]) || []);
      const save = () => { const all = store.get(KEYS.cards, {}); all[sid] = [...known]; store.set(KEYS.cards, all); };
      let i = 0, flipped = false;
      const draw = () => {
        const c = cards[i];
        const card = h('button', {
          class: 'fe-card' + (flipped ? ' is-flipped' : ''), type: 'button', 'aria-live': 'polite',
          onclick: () => { flipped = !flipped; draw(); },
        },
          h('span', { class: 'fe-card-side' }, flipped ? 'Réponse' : 'Question'),
          h('span', { class: 'fe-card-text' }, flipped ? c.back : c.front),
          h('span', { class: 'fe-card-tip' }, flipped ? '' : 'Clique pour retourner'));
        const go = (d) => { i = (i + d + cards.length) % cards.length; flipped = false; draw(); };
        box.replaceChildren(
          h('div', { class: 'fe-row fe-between' },
            h('span', { class: 'fe-muted' }, `Carte ${i + 1} / ${cards.length}`),
            h('span', { class: 'fe-muted' }, `✓ ${known.size} maîtrisée(s)`)),
          card,
          h('div', { class: 'fe-row fe-center' },
            h('button', { class: 'fe-chip', type: 'button', onclick: () => go(-1), 'aria-label': 'Carte précédente' }, '◀'),
            h('button', { class: 'fe-chip', type: 'button', onclick: () => { known.delete(c.front); save(); go(1); } }, '↺ À revoir'),
            h('button', { class: 'fe-chip is-on', type: 'button', onclick: () => { known.add(c.front); save(); go(1); } }, '✓ Je savais'),
            h('button', { class: 'fe-chip', type: 'button', onclick: () => go(1), 'aria-label': 'Carte suivante' }, '▶'),
            h('button', { class: 'fe-chip', type: 'button', onclick: () => {
              cards = cards.map((x) => [Math.random(), x]).sort((a, b) => a[0] - b[0]).map((x) => x[1]); i = 0; flipped = false; draw();
            } }, '🔀 Mélanger'))
        );
      };
      draw();
    }).catch(() => box.replaceChildren(h('p', { class: 'fe-muted' }, 'Flashcards indisponibles pour le moment.')));
    return box;
  }

  function renderDoc(kind, src) {
    const link = h('a', { class: 'fe-btn', href: url(src), target: '_blank', rel: 'noopener' },
      kind === 'slides' ? '↗ Ouvrir les slides (PDF)' : kind === 'infographic' ? '↗ Ouvrir en grand' : '↗ Ouvrir la fiche');
    if (kind === 'slides') return h('div', { class: 'fe-doc' }, h('iframe', { src: url(src), title: 'Slides de la session', loading: 'lazy' }), link);
    if (kind === 'infographic') return h('div', { class: 'fe-doc' }, h('img', { src: url(src), alt: 'Infographie de la session', loading: 'lazy' }), link);
    return h('div', { class: 'fe-doc' }, h('p', { class: 'fe-muted' }, 'Fiche de révision générée à partir du support de cours.'), link);
  }

  function empty(title) {
    return h('div', { class: 'fe-empty' },
      h('div', { class: 'fe-empty-icon' }, '🎬'),
      h('p', { class: 'fe-empty-title' }, 'Supports multimédias en préparation'),
      h('p', { class: 'fe-muted' },
        (title ? title + ' : v' : 'V') + 'idéo, podcast, quiz et flashcards seront générés avec NotebookLM et apparaîtront ici automatiquement.'));
  }

  // ─── Montage d'un lecteur ───
  async function mount(root) {
    const sid = root.dataset.elearning;
    const only = (root.dataset.kinds || '').split(',').map((s) => s.trim()).filter(Boolean);
    root.classList.add('fe-root');
    root.replaceChildren(h('p', { class: 'fe-muted' }, 'Chargement des supports…'));
    const m = await manifest();
    const entry = (m.sessions || {})[sid] || {};
    const tabs = TABS.filter(([k]) => entry[k] && (!only.length || only.includes(k)));
    if (!tabs.length) { root.replaceChildren(empty(entry.title)); return; }

    const panel = h('div', { class: 'fe-panel' });
    const nav = h('div', { class: 'fe-tabs', role: 'tablist' });
    const show = (k) => {
      nav.querySelectorAll('.fe-tab').forEach((t) => t.setAttribute('aria-selected', String(t.dataset.k === k)));
      panel.querySelectorAll('video,audio').forEach((m) => m.pause());
      const src = entry[k];
      panel.replaceChildren(
        k === 'video' || k === 'audio' ? renderMedia(sid, k, src)
          : k === 'quiz' ? renderQuiz(sid, src)
          : k === 'flashcards' ? renderCards(sid, src)
          : renderDoc(k, src));
    };
    tabs.forEach(([k, icon, label]) => nav.append(
      h('button', { class: 'fe-tab', type: 'button', role: 'tab', 'data-k': k, onclick: () => show(k) }, icon + ' ' + label)));
    root.replaceChildren(
      h('div', { class: 'fe-head' },
        h('span', { class: 'fe-kicker' }, 'Studio e-learning'),
        h('span', { class: 'fe-muted' }, 'Généré avec NotebookLM')),
      nav, panel);
    show(tabs[0][0]);
  }

  function stats() {
    return {
      sessionsDone: store.get(KEYS.sessions, []),
      quiz: store.get(KEYS.quiz, {}),
      watched: store.get(KEYS.media, {}),
    };
  }

  window.ForgeElearning = { mount, stats, manifest, KEYS };
  const boot = () => document.querySelectorAll('[data-elearning]').forEach(mount);
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot); else boot();
})();
