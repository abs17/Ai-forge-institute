---
name: forge-nlm-studio
description: Génère ou met à jour les vidéos, podcasts, quiz, flashcards et slides de la formation AI Forge Institute via NotebookLM (notebooklm-py), puis publie les fichiers dans media/ du dépôt Ai-forge-institute. À utiliser quand on demande de « régénérer les médias du cours », « créer la vidéo de la session X » ou « vérifier l'état des générations NotebookLM ».
---

# Forge NLM Studio

Tu pilotes le pipeline `tools/nlm_studio.py` du dépôt **Ai-forge-institute**. Il transforme les supports écrits du cours en médias e-learning avec Google NotebookLM, puis les dépose dans `media/<session>/` et met à jour `media/manifest.json`, que la plateforme web lit.

## Avant de commencer

1. Place-toi à la racine du dépôt (le dossier qui contient `content/curriculum.json`).
2. Vérifie la session Google : `python3 -c "import notebooklm"` doit réussir, et le fichier `~/.notebooklm/profiles/default/storage_state.json` doit exister.
   - S'il manque, **arrête-toi** et demande à l'humain de lancer `notebooklm login --fresh --browser chrome` sur sa machine. Ne tente jamais de te connecter toi-même ni de manipuler des cookies.
3. Lance `python3 tools/nlm_studio.py plan` et résume le résultat : sessions dont la source a changé, médias absents ou périmés.

## Générer

- Tout le programme, en attendant la fin (jusqu'à 30 min) :
  `python3 tools/nlm_studio.py run`
- Une seule session ou certains médias :
  `python3 tools/nlm_studio.py run --session s2 --only video,quiz`
- Lancer sans attendre (les vidéos peuvent prendre longtemps), puis récupérer plus tard :
  `python3 tools/nlm_studio.py sync && python3 tools/nlm_studio.py launch`
  puis, plus tard : `python3 tools/nlm_studio.py collect`
- Forcer une régénération : ajouter `--force`.

Médias possibles : `video`, `audio`, `quiz`, `flashcards`, `slides`, `infographic`, `study_guide`. Ceux de chaque session sont déclarés dans `content/curriculum.json` (champ `media`).

## Règles

- Ne modifie jamais les supports `content/sessions/*.md` de ta propre initiative : ils sont la source de vérité pédagogique. Si un média contient une erreur, signale-la ; la correction se fait dans le Markdown, puis on régénère.
- Respecte les quotas NotebookLM : pas plus d'un `run` complet par jour. Si une génération échoue avec une erreur de quota (`RateLimitError` ou `USER_DISPLAYABLE_ERROR`), arrête-toi et préviens l'humain au lieu de réessayer en boucle.
- Ne committe jamais `tools/.nlm_state.json`, `storage_state.json` ni aucun cookie.
- Avant de publier, vérifie la taille des vidéos (`du -h media/*/video.mp4`) : GitHub refuse les fichiers de plus de 100 Mo. Au-delà, propose un hébergement européen (Scaleway, OVH) et le champ `media_base_url` de `content/curriculum.json`.

## Rendre compte

Termine par un tableau session × média avec le statut (`téléchargé`, `en cours`, `échec : <raison>`), puis la commande à relancer pour ce qui reste en cours. Si l'humain a configuré un canal (Telegram, Signal…), envoie-y ce résumé.

## Planification (optionnel)

Pour régénérer automatiquement la nuit après une mise à jour des supports, l'humain peut programmer une tâche OpenClaw qui exécute : « Utilise forge-nlm-studio : lance `plan`, et seulement si une source a changé, lance `run` puis rends compte. »
