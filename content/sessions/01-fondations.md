# Session 1 — Fondations & Architecture locale

*AI Forge Institute · Formation OpenClaw 2026 · Badge : 🛡️ Guardian of Privacy*

**Objectif :** transformer ton ordinateur en forge à IA sans dépendre du cloud, et comprendre comment Ollama, OpenClaw et ton système s'articulent.

## Pourquoi un LLM local ?

- **Confidentialité** : les données ne quittent pas ta machine, ce qui simplifie la conformité RGPD.
- **Aucune dépendance externe** : pas de clé API, pas de panne fournisseur.
- **Coût d'usage nul en tokens** : tu ne paies que ton matériel et ton électricité.
- **Latence maîtrisée** : pas d'aller-retour réseau vers un fournisseur.

## L'architecture en 3 couches

1. **Couche LLM** — Ollama + Llama 3 : l'inférence, 100 % locale.
2. **Couche agent** — OpenClaw : la boucle Perception → Réflexion → Action → Observation, les outils, la mémoire.
3. **Couche sécurité** — sandbox Docker, audit trail (`--audit`), règles RGPD.

Chaque couche est interchangeable et auditable : tu peux remplacer Llama 3 par Mistral, ou Docker par systemd, sans toucher au reste.

## La boucle de l'agent

- **Perception** : l'agent reçoit une tâche (texte, fichier, appel d'API) et en extrait l'intention.
- **Réflexion** : le LLM analyse la tâche, choisit parmi les outils autorisés et planifie les étapes.
- **Action** : l'agent exécute (appel d'outil, écriture de fichier, requête HTTP), toujours dans la sandbox.
- **Observation** : il lit le résultat, le réinjecte dans son contexte et décide de continuer ou de s'arrêter.

**Chatbot ou agent ?** Un chatbot répond à un message. Un agent peut exécuter des outils et boucler sur plusieurs étapes de façon autonome.

## Maîtriser l'API brute d'Ollama

Avant l'agent, teste l'API qu'OpenClaw utilise en interne :

```bash
# Chat simple (non-streaming)
curl http://localhost:11434/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama3:8b-instruct-q8_0",
    "messages": [
      {"role":"system","content":"Tu es un assistant expert en IA locale."},
      {"role":"user","content":"Explique le RAG en 2 phrases."}
    ],
    "stream": false
  }'

# Liste des modèles disponibles
curl http://localhost:11434/api/tags
```

## Défi sandbox

Vérifie ton modèle avec `ollama list`, puis interroge l'API locale sur le port 11434 avec curl.

## Checklist

- Je sais décrire les 3 couches de l'architecture
- Je sais expliquer la boucle Perception → Réflexion → Action → Observation
- J'ai testé l'API Ollama avec curl et reçu une réponse JSON valide
