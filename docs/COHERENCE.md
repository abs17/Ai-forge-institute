# Mise en cohérence des contenus

Référence : `content/curriculum.json` (sessions, titres, badges) et `content/sessions/*.md` (contenu). Les pages HTML et les médias NotebookLM en découlent.

## Ce qui a été harmonisé

### Marque et navigation
- Un seul nom : **AI Forge Institute — Formation OpenClaw 2026**. Avant, on trouvait « OpenClaw Academy », « Cours OpenClaw 2026 — Build Your First AI Agent » et le nom du dépôt. Le nom « OpenClaw Academy » pouvait aussi laisser croire à une formation officielle du projet OpenClaw.
- La landing ne menait pas au cours : ajout du lien « Cours interactif », le bouton principal ouvre le cours, et chaque session renvoie vers son onglet (`index.html#s1`…).

### Titres des sessions (landing ≠ cours)

| # | Landing (avant) | Cours (avant) | Titre unique |
|---|---|---|---|
| 1 | Architecture & Local LLM | Foundations & Architecture | Fondations & Architecture locale |
| 2 | OpenClaw Core : Ton Premier Agent | Créer ton Premier Agent | Créer ton premier agent |
| 3 | Sécurité, RAG & Sandbox | Connexions Messaging & RAG Local | RAG local, Sandbox & Notifications |
| 4 | Déploiement 24/7 & Automatisation | Skills, Multi-Agents & Déploiement 24/7 | Outils, Multi-Agents & Déploiement 24/7 |

### Commandes et code
- `curl … | bash` (landing) et `| sh` (cours) → `| sh`, comme la doc d'Ollama.
- `ollama run` (landing) et `ollama pull` (cours) → `ollama pull`.
- **Bug** : les exemples curl appelaient le modèle `llama3`, alors que seul `llama3:8b-instruct-q8_0` est téléchargé. Ollama cherche alors `llama3:latest` et renvoie une erreur. Le nom complet est désormais utilisé partout.
- Imports : `@openclaw/memory` (landing) et `@openclaw/hooks` (cours) → `@openclaw/sdk`, comme le reste du cours.
- `openclaw run --sandbox` sans fichier de config → `openclaw run agent.config.json --sandbox`.
- PM2 lance l'agent avec `--audit`, conformément à la règle « toujours démarrer avec --audit ».
- Taille du modèle q8_0 : « ~5 Go » → ~8,5 Go (q4_0 : ~4,7 Go).
- `OLLAMA_HOST` « dans /etc/ollama/config » (fichier qui n'existe pas) → override systemd `sudo systemctl edit ollama`.

### Pédagogie
- Les mini-quiz 1, 3 et 4 de la landing avaient **deux bonnes réponses** pour un QCM à réponse unique ; reformulés avec une seule bonne réponse.
- Progression : la landing et le cours utilisaient des clés `localStorage` différentes, et le compteur de la landing mélangeait jalons, quiz et sessions sur une base de 8 étapes (100 % atteint trop tôt). Les sessions validées sont désormais partagées entre les deux pages ; le dashboard compte 8 jalons, dont 2 validés automatiquement par les sessions.
- Jalon « Cloner le Repo » (aucun dépôt à cloner dans le cours) → « Modèle Llama 3 prêt ».

### RGPD
- « DPO désigné si >250 salariés » : le seuil de 250 salariés concerne le registre des traitements, pas le DPO. Remplacé par les cas réels (secteur public, suivi à grande échelle, données sensibles).
- « Conformité CNIL vérifiée » → « Recommandations CNIL sur l'IA appliquées » (la CNIL ne certifie pas).
- Llama 3 est *open-weight*, pas open source au sens strict.
- Usage de NotebookLM (service Google) explicité : supports publics uniquement, aucune donnée d'apprenant transmise.

## Points ouverts — à trancher

1. **Le SDK OpenClaw enseigné ne correspond pas à l'outil réel.** Le cours décrit un paquet `@openclaw/sdk` avec `openclaw init --template`, `defineTool`, `Orchestrator`, `LocalMemory`, `openclaw sandbox up`. Le projet OpenClaw public s'installe avec `npm install -g openclaw@latest` puis `openclaw onboard --install-daemon`, et s'étend avec des *skills* (`SKILL.md`, ClawHub). Les commandes du cours ont été rendues cohérentes entre elles, mais pas réécrites pour l'outil réel : c'est un choix éditorial. Les vidéos NotebookLM reprenant fidèlement les sources, mieux vaut trancher **avant** la première génération complète. Il suffira ensuite de corriger les fichiers `content/sessions/*.md` et de relancer `run`.
2. **Formateur.** La landing présente « Chinat Yu (Stanford LDT · MLH Top 50) ». À confirmer, ou à remplacer par l'équipe AI Forge Institute.
3. **Doublons de contenu.** Les commandes et les quiz sont encore écrits deux fois, dans `index.html` et dans `content/sessions/*.md`. Étape suivante possible : générer les onglets du cours à partir des fichiers Markdown pour n'avoir qu'une seule source.
