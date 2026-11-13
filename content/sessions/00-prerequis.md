# Étape 0 — Prérequis & Installation

*AI Forge Institute · Formation OpenClaw 2026 · vérifié sur OpenClaw 2026.11.3*

**Objectif :** installer Ollama, un modèle local et OpenClaw, puis vérifier que ton assistant répond.

## Ce qu'il te faut

- **Système** : macOS, Linux, ou Windows avec WSL2.
- **Node.js** : 24.16 ou plus récent dans la série 24, ou 26.1 et plus (26 recommandé). Vérifie avec `node --version`.
- **Mémoire** : 8 Go de RAM au minimum pour un petit modèle local, 16 Go ou plus pour être à l'aise.
- **Docker** : facultatif ici, nécessaire pour la sandbox de la session 3.
- **Un compte Telegram** pour la session 2.

> ℹ️ **Version de référence** — Ce cours est vérifié sur OpenClaw **2026.11.3** (10 novembre 2026). OpenClaw évolue vite : `openclaw update` met ton installation à jour, et `openclaw doctor --fix` migre une ancienne configuration.

## 1. Installer Ollama et un modèle local

Ollama fait tourner le modèle de langage sur ta machine. Ses données ne quittent pas ton ordinateur.

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull gemma4
ollama list
```

Sur Windows, installe Ollama dans WSL2 avec la même commande, ou utilise l'installeur de [ollama.com/download](https://ollama.com/download).

> 💡 **Quel modèle ?** — OpenClaw a besoin d'un modèle qui sait appeler des outils et dispose d'au moins 16 000 tokens de contexte. `gemma4` est le modèle que l'assistant d'OpenClaw propose par défaut. Avec plus de mémoire, `qwen3.5:27b` ou `gpt-oss:20b` sont plus fiables.

## 2. Installer OpenClaw

macOS, Linux et WSL2 :

```bash
curl -fsSL https://openclaw.ai/install.sh | bash
```

Windows (PowerShell) :

```powershell
iwr -useb https://openclaw.ai/install.ps1 | iex
```

Alternative avec npm :

```bash
npm install -g openclaw@latest --allow-scripts=openclaw
```

## 3. L'assistant de configuration

Le script d'installation lance l'assistant automatiquement. Choisis **Quick start** : il détecte ton modèle Ollama, le teste avec une vraie requête et enregistre la configuration. Si tu as installé avec npm, lance-le toi-même :

```bash
openclaw onboard --install-daemon
```

Cette variante ouvre l'assistant complet (modèle, canaux, skills) et installe en plus le service d'arrière-plan. Pour le modèle, choisis **Ollama**, puis **Local only**.

> ⚠️ **Accès complet par défaut** — Le Quick start crée un agent `main` avec un accès complet à ta machine : il peut lire, écrire et exécuter des commandes. C'est pratique pour apprendre, mais nous resserrerons ces droits dans le module Sécurité.

## 4. Vérifier l'installation

```bash
openclaw --version
openclaw doctor
openclaw status
openclaw dashboard
```

`openclaw doctor` diagnostique et répare la configuration. `openclaw dashboard` ouvre l'interface web locale de contrôle (Control UI), et `openclaw` tout seul ouvre une interface dans le terminal.

## Le défi 15 minutes

```bash quickstart
# 1. Moteur IA local + modèle
curl -fsSL https://ollama.com/install.sh | sh
ollama pull gemma4

# 2. OpenClaw + assistant (Quick start → Ollama)
curl -fsSL https://openclaw.ai/install.sh | bash

# 3. Vérifier et ouvrir le tableau de bord
openclaw status
openclaw dashboard
```

## Checklist

- `node --version` affiche 24.16+ ou 26.1+
- Ollama est installé et `ollama list` affiche `gemma4`
- OpenClaw est installé (`openclaw --version`)
- L'assistant de configuration est terminé avec Ollama comme modèle
- `openclaw status` et `openclaw doctor` ne signalent pas d'erreur
- Le tableau de bord s'ouvre avec `openclaw dashboard`

## Quiz

**Quelle commande ouvre l'interface web de contrôle d'OpenClaw ?**
- [ ] `openclaw serve`
- [x] `openclaw dashboard`
- [ ] `ollama run`
- [ ] `openclaw init`
> `openclaw dashboard` ouvre la Control UI locale grâce à un lien d'appairage à usage unique.

**De quoi un modèle local a-t-il besoin pour piloter OpenClaw ?**
- [ ] D'une carte graphique NVIDIA obligatoire
- [ ] D'une connexion à l'API OpenAI
- [x] De savoir appeler des outils et d'au moins 16 000 tokens de contexte
- [ ] D'être téléchargé depuis ClawHub
> L'assistant ne retient que les modèles Ollama capables d'appeler des outils, avec au moins 16 000 tokens de contexte.
