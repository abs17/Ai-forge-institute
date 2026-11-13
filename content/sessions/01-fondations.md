# Session 1 — Fondations & Architecture

*AI Forge Institute · Formation OpenClaw 2026 · Badge : 🛡️ Guardian of Privacy*

**Objectif :** comprendre comment fonctionne OpenClaw et brancher ton assistant sur un modèle 100 % local.

## OpenClaw en une phrase

OpenClaw est un assistant IA personnel open source qui tourne **sur ta machine**. Tu lui écris depuis ta messagerie (Telegram, WhatsApp, Signal, Discord…), et il répond, se souvient et agit : il lit et écrit des fichiers, lance des commandes, navigue sur le web, programme des tâches.

## Les briques de l'architecture

| Brique | Rôle | Où ? |
|---|---|---|
| **Gateway** | Le serveur central : il reçoit les messages des canaux, les route vers l'agent et garde les sessions | `127.0.0.1:18789` |
| **Agent** | L'assistant lui-même (par défaut `main`), avec sa personnalité, ses règles et sa mémoire | `~/.openclaw/workspace` |
| **Modèle** | Le « cerveau » : un LLM local (Ollama) ou dans le cloud | ex. `ollama/gemma4` |
| **Canaux** | Les messageries par lesquelles tu lui parles | Telegram, WhatsApp, Signal… |
| **Outils & skills** | Ce que l'agent sait faire : fichiers, commandes, web, automatisations | Outils intégrés + `skills/` |

La configuration est dans `~/.openclaw/openclaw.json` (format JSON5). La Gateway la recharge automatiquement quand tu la modifies.

## La boucle de l'agent

- **Perception** : un message arrive par un canal ; la Gateway l'associe à une session.
- **Réflexion** : le modèle lit le message avec le contexte de l'agent (ses fichiers d'instructions, sa mémoire, l'historique) et choisit la suite.
- **Action** : il appelle un outil — lire un fichier, lancer une commande, chercher sur le web.
- **Observation** : le résultat de l'outil revient au modèle, qui continue ou répond.

**Chatbot ou agent ?** Un chatbot répond à un message. Un agent enchaîne plusieurs actions avec des outils jusqu'à atteindre un objectif.

## Brancher le modèle local

L'assistant de configuration l'a normalement fait. Pour le régler à la main :

```bash landing
# Le modèle doit être téléchargé dans Ollama
ollama pull gemma4

# Ollama local : n'importe quelle valeur de clé convient
export OLLAMA_API_KEY="ollama-local"

# Choisir le modèle par défaut de l'agent
openclaw models list
openclaw models set ollama/gemma4
```

Ce que cela écrit dans `~/.openclaw/openclaw.json` :

```json5 openclaw.json
{
  agents: {
    defaults: {
      model: { primary: "ollama/gemma4" },
    },
  },
}
```

> ⚠️ **Pas de /v1** — Si tu indiques une adresse Ollama à la main, utilise l'API native `http://127.0.0.1:11434`, jamais l'URL compatible OpenAI `/v1` : elle casse les appels d'outils.

## Premier échange

```bash
# Envoyer un message à l'agent depuis le terminal
openclaw agent --agent main --message "Présente-toi en deux phrases."

# Ou discuter dans le terminal
openclaw
```

## Local ou cloud : être lucide

Un modèle local garde tes conversations chez toi et ne coûte rien à l'usage. La documentation d'OpenClaw rappelle aussi ses limites : les petits modèles suivent moins bien les instructions et résistent moins bien à l'injection de prompt. Avec un modèle local, on garde donc des outils limités et une sandbox (sessions 3 et Sécurité). Tu peux définir un modèle cloud en secours avec `agents.defaults.model.fallbacks`, en sachant que les messages concernés partiront alors chez ce fournisseur.

## Checklist

- Je sais décrire le rôle de la Gateway, de l'agent, du modèle et des canaux
- Je sais expliquer la boucle Perception → Réflexion → Action → Observation
- Mon agent utilise `ollama/gemma4` (vérifié avec `openclaw models list`)
- J'ai reçu une réponse avec `openclaw agent --message`

## Quiz

**Sur quel port la Gateway OpenClaw écoute-t-elle par défaut ?**
- [ ] 11434
- [x] 18789
- [ ] 8080
- [ ] 443
> 18789 est le port de la Gateway ; 11434 est celui d'Ollama.

**Quelle différence entre un chatbot et un agent OpenClaw ?**
- [ ] Aucune, c'est du marketing
- [x] L'agent enchaîne plusieurs actions avec des outils pour atteindre un objectif
- [ ] Le chatbot est plus intelligent parce qu'il est dans le cloud
- [ ] L'agent ne fonctionne qu'avec un modèle payant
> L'agent boucle : il agit avec des outils, observe le résultat et décide de la suite.

**Pourquoi ne pas utiliser l'URL `/v1` d'Ollama avec OpenClaw ?**
- [ ] Elle est plus lente
- [x] Elle casse les appels d'outils
- [ ] Elle envoie les données dans le cloud
- [ ] Elle n'existe plus
> OpenClaw utilise l'API native d'Ollama ; via `/v1`, le modèle peut renvoyer les appels d'outils sous forme de texte brut.
