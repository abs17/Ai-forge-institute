# Session 2 — Créer ton premier agent

*AI Forge Institute · Formation OpenClaw 2026 · Badge : 🧠 Neural Architect*

**Objectif :** passer d'un simple chatbot à un agent qui exécute des tâches. Tu vas initialiser l'agent **Lobster-01**, lui donner des outils et le regarder exécuter sa première tâche autonome.

## Initialiser le projet

Le template `autonomous-researcher` est le point de départ idéal.

```bash
mkdir lobster-01 && cd lobster-01
openclaw init --template autonomous-researcher
```

Structure créée :

```
lobster-01/
├── agent.config.json   ← configuration de l'agent
├── tools/              ← tes outils custom
├── memory/             ← stockage local pour le RAG
└── logs/               ← audit trail complet
```

## Configurer agent.config.json

Ce fichier est le cerveau de l'agent.

```json
{
  "name": "Lobster-01",
  "version": "1.0.0",
  "model": "llama3:8b-instruct-q8_0",
  "role": "Agent de recherche autonome spécialisé IA",
  "goal": "Extraire, synthétiser et livrer les news IA toutes les 6h",
  "tools": ["web-search", "file-writer", "markdown-formatter"],
  "constraints": "Strictement local. Jamais de clé API externe. Format Markdown uniquement.",
  "memory": { "type": "local", "path": "./memory" },
  "sandbox": { "enabled": true, "driver": "docker" },
  "maxIterations": 10,
  "timeout": 120000
}
```

- `model` : le nom exact du modèle Ollama.
- `tools` : la liste blanche des outils. L'agent ne peut pas en utiliser d'autres.
- `sandbox.driver` : `docker` isole l'exécution. `none` la désactive (déconseillé).
- `maxIterations` : borne la boucle et évite les boucles infinies. Toujours la définir.
- `timeout` : durée maximale d'une tâche, en millisecondes.

## Lancer et tester l'agent

```bash
# Mode développement (logs verbeux)
openclaw run agent.config.json --verbose

# Mode production avec audit trail
openclaw run agent.config.json --audit

# Avec une tâche précise
openclaw run agent.config.json --task "Résume les 5 dernières avancées en LLM"

# En sandbox isolée
openclaw run agent.config.json --sandbox

# Suivre les logs
tail -f logs/agent.log
```

**Bonne pratique : démarre toujours avec `--audit`.** Le journal trace chaque décision de l'agent (outil, entrée, sortie). Il sert au débogage et à la conformité.

## Checklist

- Projet initialisé avec `openclaw init`
- `agent.config.json` personnalisé avec mon rôle et mon objectif
- Agent lancé en `--verbose` sans erreur
- Logs lus et boucle d'exécution comprise
- Test en sandbox Docker réussi (`--sandbox`)
