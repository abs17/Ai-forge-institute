# Générations NotebookLM à réaliser

À faire ensemble sur ta machine : il faut ta session Google. Tout le reste (supports, pages, lecteur, pipeline) est prêt et ne dépend pas de ces générations. Tant qu'un média manque, la page affiche « Supports multimédias en préparation ».

Sources : `content/sessions/*.md`, version OpenClaw de référence **2026.11.3**. Réglages : section `generation` de `content/curriculum.json` (français, tutoiement, consigne de fidélité stricte aux commandes).

## 0. Préparation (une fois, ~5 min)

```bash
cd Ai-forge-institute
pip install -r tools/requirements.txt
notebooklm login --fresh --browser chrome   # attendre « Authentication saved to »
python3 tools/nlm_studio.py plan             # doit lister 6 sessions, notebooks « à créer »
python3 tools/nlm_studio.py sync             # crée les 6 notebooks et y publie les supports
```

## Lot 1 — Pilote : session 1 complète

But : valider le ton, le style de vidéo et surtout l'exactitude des commandes avant de lancer le reste.

```bash
python3 tools/nlm_studio.py run --session s1
```

| # | Session | Média | Réglage | Fichier | Fait |
|---|---|---|---|---|---|
| 1 | s1 Fondations | vidéo | Explainer, tableau blanc | `media/s1/video.mp4` | ☐ |
| 2 | s1 Fondations | podcast | Deep Dive, durée standard | `media/s1/audio.m4a` | ☐ |
| 3 | s1 Fondations | quiz | standard, moyen | `media/s1/quiz.json` | ☐ |
| 4 | s1 Fondations | flashcards | standard, moyen | `media/s1/flashcards.json` | ☐ |
| 5 | s1 Fondations | slides | deck détaillé (PDF) | `media/s1/slides.pdf` | ☐ |

**Revue du pilote** (voir la grille plus bas). Si le style ne convient pas, on ajuste `generation` dans `curriculum.json` et on relance avec `--force`.

## Lot 2 — Vidéos et podcasts des autres sessions

Ce sont les générations les plus longues et les plus soumises aux quotas. On les lance sans attendre, puis on récupère plus tard :

```bash
python3 tools/nlm_studio.py launch --only video,audio
python3 tools/nlm_studio.py collect          # à relancer jusqu'à ce que tout soit téléchargé
```

| # | Session | Média | Fichier | Fait |
|---|---|---|---|---|
| 6 | Prérequis | vidéo | `media/prereqs/video.mp4` | ☐ |
| 7 | Prérequis | podcast | `media/prereqs/audio.m4a` | ☐ |
| 8 | s2 Premier agent | vidéo | `media/s2/video.mp4` | ☐ |
| 9 | s2 Premier agent | podcast | `media/s2/audio.m4a` | ☐ |
| 10 | s3 Skills & Sandbox | vidéo | `media/s3/video.mp4` | ☐ |
| 11 | s3 Skills & Sandbox | podcast | `media/s3/audio.m4a` | ☐ |
| 12 | s4 Automatisation | vidéo | `media/s4/video.mp4` | ☐ |
| 13 | s4 Automatisation | podcast | `media/s4/audio.m4a` | ☐ |
| 14 | Sécurité & RGPD | vidéo | `media/security/video.mp4` | ☐ |
| 15 | Sécurité & RGPD | podcast | `media/security/audio.m4a` | ☐ |

Si NotebookLM refuse pour quota (`RateLimitError` ou `USER_DISPLAYABLE_ERROR`), on reprend le lendemain : le pipeline ne relance que ce qui manque.

## Lot 3 — Quiz, flashcards, slides, infographie

Rapides à générer, on peut tout lancer d'un coup :

```bash
python3 tools/nlm_studio.py run --only quiz,flashcards,slides,infographic
```

| # | Session | Média | Fichier | Fait |
|---|---|---|---|---|
| 16 | Prérequis | flashcards | `media/prereqs/flashcards.json` | ☐ |
| 17 | s2 Premier agent | quiz | `media/s2/quiz.json` | ☐ |
| 18 | s2 Premier agent | flashcards | `media/s2/flashcards.json` | ☐ |
| 19 | s2 Premier agent | slides | `media/s2/slides.pdf` | ☐ |
| 20 | s3 Skills & Sandbox | quiz | `media/s3/quiz.json` | ☐ |
| 21 | s3 Skills & Sandbox | flashcards | `media/s3/flashcards.json` | ☐ |
| 22 | s3 Skills & Sandbox | slides | `media/s3/slides.pdf` | ☐ |
| 23 | s4 Automatisation | quiz | `media/s4/quiz.json` | ☐ |
| 24 | s4 Automatisation | flashcards | `media/s4/flashcards.json` | ☐ |
| 25 | s4 Automatisation | slides | `media/s4/slides.pdf` | ☐ |
| 26 | Sécurité & RGPD | quiz | `media/security/quiz.json` | ☐ |
| 27 | Sécurité & RGPD | flashcards | `media/security/flashcards.json` | ☐ |
| 28 | Sécurité & RGPD | infographie | `media/security/infographic.png` | ☐ |

## Grille de revue (chaque média, avant publication)

NotebookLM peut reformuler ou se tromper. On vérifie chaque média avant de le publier :

- [ ] Les commandes montrées ou citées sont **identiques** au support (ex. `openclaw dashboard`, `ollama/gemma4`, `openclaw gateway install`).
- [ ] Aucune commande de l'ancien cours : `openclaw init`, `agent.config.json`, `@openclaw/sdk`, PM2, `llama3`.
- [ ] Les ports sont justes : 18789 pour la Gateway, 11434 pour Ollama.
- [ ] Les points de sécurité sont présents : appairage, Gateway sur loopback, recherche mémoire sur Ollama et non OpenAI, skills tiers non fiables.
- [ ] Le français est correct (le podcast et la vidéo restent parfois en anglais si la langue n'est pas prise en compte).
- [ ] Quiz : une seule bonne réponse par question, réponses justes.

Média à corriger : on corrige le **support Markdown**, puis `python3 tools/nlm_studio.py run --session <id> --only <média> --force`.

## Publication

```bash
du -h media/*/video.mp4          # GitHub refuse les fichiers de plus de 100 Mo
python3 tools/nlm_studio.py manifest
git add media && git commit -m "Médias NotebookLM : <sessions>" && git push
```

Si une vidéo dépasse 100 Mo : hébergement européen (Scaleway, OVH) et `media_base_url` dans `content/curriculum.json`.
