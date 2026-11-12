# Étape 0 — Prérequis & Installation

*AI Forge Institute · Formation OpenClaw 2026*

**Objectif :** préparer un environnement propre avant de lancer ton premier agent : Ollama, le modèle Llama 3 et la CLI OpenClaw doivent être opérationnels.

## Prérequis système

**Requis**
- OS : macOS 12+, Ubuntu 22.04+, ou Windows 11 avec WSL2
- RAM : 8 Go minimum (16 Go recommandés pour Llama 3 8B en q8_0)
- Disque : 20 Go libres (les modèles LLM sont volumineux)
- Node.js v20+ LTS et npm v10+
- curl

**Recommandé**
- GPU NVIDIA (CUDA) ou Apple Silicon (Metal) pour une inférence rapide
- Docker v24+ pour la sandbox isolée
- Git, VS Code, PM2 (déploiement 24/7, session 4)

## 1. Installer Ollama

Ollama est le moteur d'inférence local qui fait tourner les LLM. Il expose une API REST sur `localhost:11434`. Aucune donnée ne quitte ta machine.

Linux & macOS :

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama --version
ollama serve &
```

Windows : activer WSL2 (`wsl --install -d Ubuntu-22.04`) puis lancer la même commande dans Ubuntu, ou utiliser l'installeur natif `OllamaSetup.exe`.

## 2. Télécharger le modèle

OpenClaw est configuré dans ce cours pour Llama 3 8B. La version `q8_0` donne la meilleure qualité (~8,5 Go) ; la version `q4_0` est plus légère si ta machine manque de RAM.

```bash
ollama pull llama3:8b-instruct-q8_0
ollama pull llama3:8b-instruct-q4_0   # alternative légère
ollama list
```

Test rapide de l'API (toujours utiliser le nom exact du modèle téléchargé) :

```bash
curl http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{"model":"llama3:8b-instruct-q8_0","prompt":"Bonjour, es-tu opérationnel ?","stream":false}'
```

La réponse JSON contient `response` (le texte généré), `done: true` et des métriques. Avec `stream: true`, les tokens arrivent au fil de l'eau.

## 3. Installer la CLI OpenClaw

La CLI ajoute la couche « agent » au-dessus d'Ollama : outils, mémoire, boucle d'action, sandbox.

```bash
npm install -g @openclaw/sdk
openclaw --version
openclaw doctor
```

`openclaw doctor` vérifie Ollama, la présence du modèle et la version de Node.js.

## Checklist

- `ollama --version` fonctionne
- Le modèle `llama3:8b-instruct-q8_0` est téléchargé
- L'API Ollama répond sur `localhost:11434`
- `openclaw doctor` est au vert
- Node.js v20+ et npm v10+ sont installés

## À retenir

- Le port par défaut de l'API Ollama est **11434**.
- Il faut appeler le modèle avec son **nom exact** (`llama3:8b-instruct-q8_0`), sinon Ollama cherche `llama3:latest`, qui n'est pas installé.
