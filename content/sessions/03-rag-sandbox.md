# Session 3 — RAG local, Sandbox & Notifications

*AI Forge Institute · Formation OpenClaw 2026 · Badge : 🔐 Security Specialist*

**Objectif :** connecter l'agent à tes documents privés en toute sécurité, isoler ses exécutions et recevoir ses résumés sur ton téléphone.

## Le RAG local

Le RAG (Retrieval-Augmented Generation) permet à l'agent d'interroger tes PDF, fichiers Markdown ou CSV avant de répondre. En local, **rien ne quitte ton réseau**. Le module `LocalMemory` gère l'indexation et la recherche sémantique.

### Le modèle d'embedding

Un modèle d'embedding convertit le texte en vecteurs numériques (768 dimensions pour `nomic-embed-text`). Deux textes proches en sens ont des vecteurs proches : c'est ce qui permet la recherche sémantique. Il ne génère pas la réponse finale ; c'est le rôle du LLM.

```bash
ollama pull nomic-embed-text   # ~275 Mo
curl http://localhost:11434/api/embeddings \
  -d '{"model":"nomic-embed-text","prompt":"RGPD compliance France"}'
```

### Brancher la mémoire sur l'agent

```javascript
import { LocalMemory, Agent } from '@openclaw/sdk';

const memory = new LocalMemory({
  path: './my-private-docs',
  embedModel: 'nomic-embed-text',
  chunkSize: 512,
  overlap: 64
});
await memory.index();               // première fois, puis incrémental

const agent = new Agent('./agent.config.json');
await agent.attach(memory);

const result = await agent.run("Que dit notre politique RGPD sur la rétention ?");
console.log(result.answer);         // réponse fondée sur TES documents
```

## La sandbox Docker

La sandbox est un conteneur isolé : l'agent ne peut ni lire les fichiers hors du dossier autorisé, ni sortir sur Internet sans règle explicite.

```bash
openclaw sandbox up --isolated
openclaw sandbox status
openclaw run agent.config.json --sandbox
openclaw run agent.config.json --audit --sandbox   # voir les appels de l'agent
openclaw sandbox down
```

**Astuce :** le flag `--audit` montre exactement quelles commandes l'IA tente d'exécuter dans sa sandbox.

## Notifications Telegram via un serveur local

Un hook s'exécute après chaque tâche et envoie le résumé à ton bot Telegram auto-hébergé. Utilise Tailscale pour un tunnel privé plutôt que d'exposer un port public.

```javascript
import { createHook } from '@openclaw/sdk';

const notify = createHook('on-task-complete', async (result) => {
  await fetch('http://localhost:8080/notify', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message: `🦞 Lobster-01\n\n${result.summary}` })
  });
});

agent.use(notify);
```

Le token du bot reste dans un fichier `.env` (`chmod 600`), jamais dans `agent.config.json`.

## Checklist

- `nomic-embed-text` installé
- `LocalMemory` configuré et indexation réussie
- L'agent répond à des questions sur mes documents
- Sandbox `--isolated` opérationnelle
- Hook de notification configuré
