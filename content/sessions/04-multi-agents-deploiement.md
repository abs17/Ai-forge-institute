# Session 4 — Outils, Multi-Agents & Déploiement 24/7

*AI Forge Institute · Formation OpenClaw 2026 · Badge final : 👑 Automator Supreme*

**Objectif :** créer des outils custom, faire collaborer plusieurs agents, puis déployer l'ensemble pour qu'il tourne en continu, même quand tu dors.

## Créer un outil custom

Un outil = une fonction TypeScript accompagnée d'un schéma JSON, pour que le LLM sache quand et comment l'appeler (tool calling).

```typescript
import { defineTool } from '@openclaw/sdk';

export const newsScraper = defineTool({
  name: 'fetch-ai-news',
  description: 'Récupère les dernières news IA depuis des flux RSS locaux',
  schema: {
    type: 'object',
    properties: {
      source: { type: 'string', enum: ['arxiv', 'hn', 'local-rss'] },
      limit:  { type: 'number', default: 5 }
    },
    required: ['source']
  },
  async execute({ source, limit }) {
    const items = await fetchLocalRSS(source, limit);
    return items.map(i => ({ title: i.title, summary: i.snippet }));
  }
});
```

Pense à ajouter `fetch-ai-news` à la liste `tools` de `agent.config.json` : un outil non listé n'est pas utilisable.

## Architecture multi-agents

Un orchestrateur délègue des sous-tâches à des agents spécialisés, chacun dans sa propre sandbox.

```typescript
import { Orchestrator, Agent } from '@openclaw/sdk';

const orchestrator = new Orchestrator();
const collector = new Agent({ name: 'data-collector', tools: ['web-search'] });
const analyzer  = new Agent({ name: 'analyzer',       tools: ['file-reader', 'summarizer'] });
const writer    = new Agent({ name: 'writer',         tools: ['file-writer'] });

orchestrator.pipeline([collector, analyzer, writer]);
await orchestrator.run("Rapport hebdomadaire IA");
```

## Déploiement 24/7 avec PM2

```bash
npm install -g pm2

pm2 start "openclaw run agent.config.json --audit" \
  --name my-247-agent \
  --restart-delay 3000 \
  --max-restarts 10

pm2 save      # mémorise la liste des processus
pm2 startup   # génère le service système qui relance PM2 au démarrage

pm2 monit
pm2 logs my-247-agent --lines 50
```

`pm2 save` enregistre les processus en cours ; `pm2 startup` installe le service qui les relance automatiquement après un redémarrage de la machine. Les deux sont nécessaires.

## Monitoring

| Métrique | Seuil d'alerte | Action |
|---|---|---|
| CPU | > 80 % | Mise en pause automatique |
| Taux de succès des tâches | < 95 % | Re-prompting automatique |
| Coût en tokens | 0 € (local) | Seuls le matériel et l'électricité coûtent |

## Hébergement européen

Pour faire tourner l'agent hors de ta machine, choisis un VPS européen : Hetzner (Allemagne), OVH ou Scaleway (France). Les données restent sur le sol de l'UE. Compte quelques euros par mois pour un agent léger sur CPU ; un modèle 8B confortable demande au moins 16 Go de RAM.

## Exercice final

Configure un hook pour que ton agent t'envoie un résumé de son travail sur Telegram ou Signal via ton serveur local. L'agent travaille, tu reçois les résultats.

## Checklist

- Outil custom créé, déclaré et testé
- Pipeline multi-agents fonctionnel
- Agent lancé en daemon avec PM2
- `pm2 save` et `pm2 startup` exécutés
- Monitoring PM2 opérationnel
