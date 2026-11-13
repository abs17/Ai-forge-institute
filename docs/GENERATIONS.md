# Générations NotebookLM à réaliser

À faire ensemble sur ta machine : il faut ta session Google. Tout le reste (supports, pages, lecteur, pipeline) est prêt et ne dépend pas de ces générations. Tant qu'un média manque, la page affiche « Supports multimédias en préparation ».

Sources : `content/sessions/*.md` (9 sessions, 45 générations), version OpenClaw de référence **2026.11.3**. Réglages : section `generation` de `content/curriculum.json` (français, tutoiement, consigne de fidélité stricte aux commandes).

## 0. Préparation (une fois, ~5 min)

```bash
cd Ai-forge-institute
pip install -r tools/requirements.txt
notebooklm login --fresh --browser chrome   # attendre « Authentication saved to »
python3 tools/nlm_studio.py plan             # doit lister 9 sessions, notebooks « à créer »
python3 tools/nlm_studio.py sync             # crée les 9 notebooks et y publie les supports
```

## Lot 1 — Pilote : session 1 complète

But : valider le ton, le style de vidéo et surtout l'exactitude des commandes avant de lancer le reste.

```bash
python3 tools/nlm_studio.py run --session s1
```

| # | Session | Média | Fichier | Fait |
|---|---|---|---|---|
| 1 | s1 Fondations | vidéo | `media/s1/video.mp4` | ☐ |
| 2 | s1 Fondations | podcast | `media/s1/audio.m4a` | ☐ |
| 3 | s1 Fondations | quiz | `media/s1/quiz.json` | ☐ |
| 4 | s1 Fondations | flashcards | `media/s1/flashcards.json` | ☐ |
| 5 | s1 Fondations | slides | `media/s1/slides.pdf` | ☐ |
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
| 12 | s4 Automatisation & 24/7 | vidéo | `media/s4/video.mp4` | ☐ |
| 13 | s4 Automatisation & 24/7 | podcast | `media/s4/audio.m4a` | ☐ |
| 14 | s5 Mistral | vidéo | `media/s5/video.mp4` | ☐ |
| 15 | s5 Mistral | podcast | `media/s5/audio.m4a` | ☐ |
| 16 | s6 Sécurité avancée | vidéo | `media/s6/video.mp4` | ☐ |
| 17 | s6 Sécurité avancée | podcast | `media/s6/audio.m4a` | ☐ |
| 18 | s7 RGPD & AI Act | vidéo | `media/s7/video.mp4` | ☐ |
| 19 | s7 RGPD & AI Act | podcast | `media/s7/audio.m4a` | ☐ |
| 20 | s8 Comparatif | vidéo | `media/s8/video.mp4` | ☐ |
| 21 | s8 Comparatif | podcast | `media/s8/audio.m4a` | ☐ |
## Lot 3 — Quiz, flashcards, slides, infographie

Rapides à générer, on peut tout lancer d'un coup :

```bash
python3 tools/nlm_studio.py run --only quiz,flashcards,slides,infographic
```

| # | Session | Média | Fichier | Fait |
|---|---|---|---|---|
| 22 | Prérequis | flashcards | `media/prereqs/flashcards.json` | ☐ |
| 23 | s2 Premier agent | quiz | `media/s2/quiz.json` | ☐ |
| 24 | s2 Premier agent | flashcards | `media/s2/flashcards.json` | ☐ |
| 25 | s2 Premier agent | slides | `media/s2/slides.pdf` | ☐ |
| 26 | s3 Skills & Sandbox | quiz | `media/s3/quiz.json` | ☐ |
| 27 | s3 Skills & Sandbox | flashcards | `media/s3/flashcards.json` | ☐ |
| 28 | s3 Skills & Sandbox | slides | `media/s3/slides.pdf` | ☐ |
| 29 | s4 Automatisation & 24/7 | quiz | `media/s4/quiz.json` | ☐ |
| 30 | s4 Automatisation & 24/7 | flashcards | `media/s4/flashcards.json` | ☐ |
| 31 | s4 Automatisation & 24/7 | slides | `media/s4/slides.pdf` | ☐ |
| 32 | s5 Mistral | quiz | `media/s5/quiz.json` | ☐ |
| 33 | s5 Mistral | flashcards | `media/s5/flashcards.json` | ☐ |
| 34 | s5 Mistral | slides | `media/s5/slides.pdf` | ☐ |
| 35 | s6 Sécurité avancée | quiz | `media/s6/quiz.json` | ☐ |
| 36 | s6 Sécurité avancée | flashcards | `media/s6/flashcards.json` | ☐ |
| 37 | s6 Sécurité avancée | slides | `media/s6/slides.pdf` | ☐ |
| 38 | s6 Sécurité avancée | infographie | `media/s6/infographic.png` | ☐ |
| 39 | s7 RGPD & AI Act | quiz | `media/s7/quiz.json` | ☐ |
| 40 | s7 RGPD & AI Act | flashcards | `media/s7/flashcards.json` | ☐ |
| 41 | s7 RGPD & AI Act | slides | `media/s7/slides.pdf` | ☐ |
| 42 | s7 RGPD & AI Act | infographie | `media/s7/infographic.png` | ☐ |
| 43 | s8 Comparatif | quiz | `media/s8/quiz.json` | ☐ |
| 44 | s8 Comparatif | flashcards | `media/s8/flashcards.json` | ☐ |
| 45 | s8 Comparatif | slides | `media/s8/slides.pdf` | ☐ |
## Grille de revue (chaque média, avant publication)

NotebookLM peut reformuler ou se tromper. On vérifie chaque média avant de le publier :

- [ ] Les commandes montrées ou citées sont **identiques** au support (ex. `openclaw dashboard`, `ollama/gemma4`, `openclaw gateway install`).
- [ ] Aucune commande de l'ancien cours : `openclaw init`, `agent.config.json`, `@openclaw/sdk`, PM2, `llama3`.
- [ ] Sessions 5 à 8 : les dates de l'AI Act, les articles cités (AI Act 4, 5, 26, 50 ; RGPD 28, 30, 33, 35) et les noms d'outils du comparatif sont exacts.
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
