# Cohérence et validation des contenus

Source unique : `content/curriculum.json` (programme, badges, ressources, formateur) et `content/sessions/*.md` (contenu). `tools/build_course.py` génère les deux pages ; `tools/nlm_studio.py` génère les médias à partir des mêmes fichiers.

## Version de référence

Contenu vérifié le **13 novembre 2026** sur **OpenClaw 2026.11.3** (version stable du 10 novembre 2026, Node.js 24.16+ ou 26.1+), à partir de la documentation officielle livrée avec le paquet npm `openclaw@2026.11.3`. Pour revalider sur une nouvelle version :

```bash
npm view openclaw version          # dernière version stable
# relire les commandes des content/sessions/*.md, mettre à jour openclaw_version
# et verified_on dans curriculum.json, puis :
python3 tools/build_course.py
```

## Réécriture pour le vrai OpenClaw (13/11/2026)

L'ancien cours enseignait un SDK qui n'existe pas. Correspondance avec l'outil réel :

| Ancien cours | OpenClaw 2026.11.3 |
|---|---|
| `npm install -g @openclaw/sdk` | `curl -fsSL https://openclaw.ai/install.sh \| bash`, puis l'assistant (`openclaw onboard`) |
| Node.js 20 | Node.js 24.16+ ou 26.1+ |
| `openclaw init --template …` + `agent.config.json` | Workspace `~/.openclaw/workspace` (`AGENTS.md`, `SOUL.md`, `USER.md`…) + `~/.openclaw/openclaw.json` (JSON5) |
| Modèle `llama3:8b-instruct-q8_0` | `ollama/gemma4` (modèle proposé par l'assistant ; un modèle doit gérer les outils et 16 000 tokens de contexte) |
| `openclaw run --verbose / --audit` | `openclaw agent --message …`, `openclaw logs --follow`, `openclaw security audit` |
| `LocalMemory` + RAG | `MEMORY.md`, `memory/AAAA-MM-JJ.md`, recherche via `memory.search.provider: "ollama"` |
| Hook Telegram maison | Canal Telegram natif : `openclaw channels add`, appairage `openclaw pairing approve` |
| `defineTool` | Skills (`SKILL.md`, ClawHub, `openclaw skills …`) |
| `openclaw sandbox up --isolated` | `agents.defaults.sandbox` (Docker), `openclaw sandbox explain` |
| `Orchestrator` | `agents.entries` + `bindings`, sous-agents `sessions_spawn` |
| PM2 | `openclaw gateway install` (service système), `openclaw automations` pour les tâches planifiées |

Points de vigilance ajoutés au cours parce que la doc officielle les signale :
- l'agent créé par le Quick start a un **accès complet** à la machine ;
- la recherche mémoire utilise **OpenAI par défaut** : à basculer sur Ollama pour rester local ;
- l'URL `/v1` d'Ollama casse les appels d'outils ;
- les petits modèles locaux résistent moins bien à l'injection de prompt ;
- `TOOLS.md` et `HEARTBEAT.md` ne sont plus lus ; `agents.list` devient `agents.entries`.

## Harmonisation précédente (12/11/2026)

Nom unique « AI Forge Institute — Formation OpenClaw 2026 » ; titres de sessions identiques entre landing et cours ; mini-quiz à une seule bonne réponse ; progression partagée entre les deux pages ; corrections RGPD (DPO, CNIL, open-weight) ; usage de NotebookLM explicité.

## Formateur

Le nom n'est plus écrit en dur. La landing affiche « l'équipe AI Forge Institute » tant que `instructor.name` est vide dans `content/curriculum.json`. Pour afficher un formateur :

```json
"instructor": { "name": "Prénom Nom", "initials": "PN", "title": "Ingénieur IA · Formateur" }
```

## Points ouverts

1. **Test réel du parcours.** Toutes les commandes viennent de la documentation officielle de la version 2026.11.3, mais le parcours n'a pas été exécuté de bout en bout sur une machine avec Ollama et Telegram. À faire une fois avant l'ouverture : suivre les sessions 0 à 4 sur une machine vierge.
2. **Médias NotebookLM.** 28 générations à faire et à relire : voir `docs/GENERATIONS.md`.
