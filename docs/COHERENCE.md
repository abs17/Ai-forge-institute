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

## Modules 5 à 8 : Mistral, sécurité avancée, RGPD & AI Act, comparatif (13/11/2026)

Positionnement : se différencier par la souveraineté (modèles Mistral, local d'abord) et par une partie sécurité et conformité plus poussée que les formations OpenClaw existantes.

**Ce qui est vérifié à la source**
- Configuration Mistral dans OpenClaw (plugin `@openclaw/mistral-provider`, `--auth-choice mistral-api-key`, identifiants de modèles, `memory.search.provider: "mistral"`, comportement strict des modèles par agent) : documentation officielle OpenClaw 2026.11.3.
- Comparatif : dépôts GitHub de Hermes Agent, NanoClaw, ZeroClaw, nanobot et IronClaw (README, SECURITY.md, docs, tags, étoiles au 13/11/2026).
- Incidents OpenClaw : CVE-2026-25253 (corrigée en 2026.1.29), campagne ClawHavoc (341 puis 824 skills malveillants, Koi Security), avis du CCB belge d'avril 2026.

**Repris de sources secondaires, à confirmer sur les textes officiels avant publication**
- Règlement « Omnibus numérique » de 2026 : report de l'annexe III au 2 décembre 2027 et de l'annexe I au 2 août 2028 (plusieurs cabinets d'avocats concordent ; le cours ne cite pas de numéro de règlement).
- Note exploratoire CNIL sur l'IA agentique (été 2026) : contenu résumé d'après la presse spécialisée.
- Mistral : signature du code de bonnes pratiques GPAI, absence d'entraînement sur les données API par défaut, conservation zéro sur demande, certifications SOC 2 / ISO 27001 / 27701, hébergement UE par défaut. À vérifier sur le portail de confiance de Mistral au moment de signer.
- Tags Ollama `ministral-3:8b` et `mistral-small3.2` : confirmés par le registre Ollama via des résultats de recherche, pas par un téléchargement.

**Volontairement non repris** : une alerte ANSSI référencée « CERTFR-2026-ACT-016 » citée par certains sites (introuvable à la source), et les chiffres d'instances exposées, trop variables selon les études (le cours parle de « dizaines de milliers »).

## Harmonisation précédente (12/11/2026)

Nom unique « AI Forge Institute — Formation OpenClaw 2026 » ; titres de sessions identiques entre landing et cours ; mini-quiz à une seule bonne réponse ; progression partagée entre les deux pages ; corrections RGPD (DPO, CNIL, open-weight) ; usage de NotebookLM explicité.

## Formateur

Le nom n'est plus écrit en dur. La landing affiche « l'équipe AI Forge Institute » tant que `instructor.name` est vide dans `content/curriculum.json`. Pour afficher un formateur :

```json
"instructor": { "name": "Prénom Nom", "initials": "PN", "title": "Ingénieur IA · Formateur" }
```

## Points ouverts

1. **Test réel du parcours.** Toutes les commandes viennent de la documentation officielle de la version 2026.11.3, mais le parcours n'a pas été exécuté de bout en bout sur une machine avec Ollama et Telegram. À faire une fois avant l'ouverture : suivre les sessions 0 à 6 sur une machine vierge, y compris les réglages Mistral (local et API) et la configuration durcie.
2. **Médias NotebookLM.** 45 générations à faire et à relire : voir `docs/GENERATIONS.md`.
