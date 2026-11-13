# AI Forge Institute — Formation OpenClaw 2026

Plateforme de formation self-paced : installer, personnaliser, sécuriser et faire tourner 24 h/24 un assistant [OpenClaw](https://github.com/openclaw/openclaw) branché sur un modèle **local** (Ollama), avec un parcours e-learning interactif (vidéos, podcasts, quiz, flashcards, slides) généré avec Google NotebookLM.

Contenu vérifié sur **OpenClaw 2026.11.3** (13 novembre 2026). Voir `docs/COHERENCE.md`.

| Page | Rôle |
|---|---|
| `openclaw-masterclass-2026.html` | Landing : présentation, défi 15 min, aperçu vidéo/podcast de chaque session, dashboard de progression |
| `index.html` | Cours complet : prérequis, sessions 1 à 4, sécurité & RGPD, ressources, avec le studio e-learning de chaque session |

Les deux pages partagent la même progression (sessions validées et badges), stockée dans le `localStorage` du navigateur. Aucun cookie, aucun tracking.

## Organisation

```
content/
  curriculum.json          ← source unique : sessions, badges, formateur, ressources, réglages NotebookLM
  sessions/*.md            ← contenu de chaque session : pages web ET source NotebookLM
assets/
  elearning.js / .css      ← lecteur e-learning (onglets Vidéo, Podcast, Quiz, Flashcards, Slides…)
media/
  manifest.json            ← liste des médias disponibles, lue par les pages
  <session>/video.mp4, audio.m4a, quiz.json, flashcards.json, slides.pdf …
tools/
  build_course.py          ← génère les pages à partir de content/
  nlm_studio.py            ← pipeline NotebookLM (notebooklm-py)
openclaw-skill/
  forge-nlm-studio/SKILL.md ← skill OpenClaw pour piloter le pipeline depuis un agent
docs/COHERENCE.md          ← version de référence, validation, points ouverts
docs/GENERATIONS.md        ← liste des 45 générations NotebookLM à faire
```

Pour ajouter un média à une session, il suffit de placer un `<div data-elearning="s2"></div>` dans une page (option `data-kinds="video,audio"` pour filtrer) : le lecteur se branche tout seul sur `media/manifest.json`. Sans média, il affiche « Supports multimédias en préparation ».

## Modifier le cours

On ne modifie pas le contenu des pages HTML à la main : on édite `content/sessions/*.md` ou `content/curriculum.json`, puis :

```bash
python3 tools/build_course.py          # régénère les zones <!-- BUILD:… --> des deux pages
python3 tools/build_course.py --check  # vérifie que les pages sont à jour
```

Conventions Markdown : `## Section` = une carte ; ```` ```bash landing ```` = bloc repris sur la landing ; ```` ```bash quickstart ```` = terminal du défi 15 min ; `> 💡 **Titre** texte` = encadré (💡 ⚠️ ℹ️ ✅) ; `## Checklist …` = checklist interactive ; `## Quiz` = questions au format `**Question ?**` puis `- [x]` / `- [ ]` puis `> explication`. Le design, le JavaScript et l'en-tête des pages restent éditables à la main hors des zones `BUILD`.

## Générer les médias avec NotebookLM

Le pipeline utilise la bibliothèque non officielle [`notebooklm-py`](https://github.com/teng-lin/notebooklm-py) (≥ 0.8.6), la même que l'app Streamlit [`abs17/notebooklm-ui`](https://github.com/abs17/notebooklm-ui), et la même session Google.

```bash
pip install -r tools/requirements.txt
notebooklm login --fresh --browser chrome     # une fois ; attendre « Authentication saved to »

python3 tools/nlm_studio.py plan              # ce qui va être fait, sans appel réseau
python3 tools/nlm_studio.py run               # notebooks + sources + génération + téléchargement
```

Pour chaque session, le pipeline :

1. crée (ou réutilise) un notebook « AI Forge — <titre> » ;
2. y publie `content/sessions/<session>.md` comme source, et la remplace si le fichier a changé ;
3. lance les générations déclarées dans `curriculum.json` (vidéo *Explainer* style tableau blanc, podcast *Deep Dive*, quiz, flashcards, slides), en français ;
4. attend, télécharge dans `media/<session>/` et réécrit `media/manifest.json`.

Il est idempotent : un média à jour n'est pas régénéré ; une source modifiée rend ses médias périmés et ils sont refaits au `run` suivant.

| Commande | Effet |
|---|---|
| `plan` | État de chaque session et média |
| `sync` | Crée les notebooks et publie les sources |
| `launch [--only video,quiz] [--session s1] [--force]` | Lance les générations sans attendre |
| `collect [--wait 1800]` | Télécharge ce qui est prêt (un passage par défaut) |
| `run` | `sync` + `launch` + `collect` (attend jusqu'à 30 min) |
| `status` / `manifest` | État brut / reconstruit le manifest depuis le disque |

Les réglages (format et style de vidéo, longueur du podcast, difficulté des quiz, consignes) sont dans la section `generation` de `content/curriculum.json`. Les identifiants de notebooks sont gardés dans `tools/.nlm_state.json`, exclu de Git.

### Piloter depuis OpenClaw

```bash
openclaw skills install ./openclaw-skill/forge-nlm-studio
```

L'agent peut alors répondre à « régénère la vidéo de la session 2 » ou faire une passe planifiée qui ne relance que les sessions dont le support a changé (voir `SKILL.md`).

### Hébergement des médias

GitHub refuse les fichiers de plus de 100 Mo. Si une vidéo dépasse cette taille, hébergez `media/` sur un stockage objet européen (Scaleway, OVH…) et indiquez son URL dans `"media_base_url"` de `content/curriculum.json`, puis lancez `python3 tools/nlm_studio.py manifest`.

### Confidentialité

NotebookLM est un service Google. Il ne reçoit que les supports de cours publics, envoyés par l'équipe pédagogique ; aucune donnée d'apprenant ne lui est transmise. Les apprenants lisent des fichiers hébergés avec le site, sans appel à un service tiers.

## Lancer en local

```bash
python3 -m http.server 8000
# http://localhost:8000/openclaw-masterclass-2026.html
```

Un serveur HTTP est nécessaire pour que le lecteur charge `media/manifest.json` ; en ouvrant le fichier directement (`file://`), les pages s'affichent mais le studio reste en mode « en préparation ».
