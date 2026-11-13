# Session 3 — Skills, Mémoire & Sandbox

*AI Forge Institute · Formation OpenClaw 2026 · Badge : 🔐 Security Specialist*

**Objectif :** étendre ton agent avec des skills, lui donner une mémoire qui reste chez toi, et isoler ses actions dans une sandbox Docker.

## Les skills : apprendre de nouveaux savoir-faire

Un skill est un dossier contenant un fichier `SKILL.md` : un mode d'emploi que l'agent lit quand la tâche s'y prête. OpenClaw en fournit déjà (météo, PDF, GitHub, Notion…), et le registre public **ClawHub** en propose des milliers.

```bash landing
# Skills disponibles et utilisables
openclaw skills list --eligible

# Chercher sur ClawHub
openclaw skills search "calendar"

# Vérifier puis installer un skill
openclaw skills verify @auteur/nom-du-skill --card
openclaw skills install @auteur/nom-du-skill
```

> ⚠️ **Un skill tiers est du code non fiable** — La documentation d'OpenClaw est claire : lis le `SKILL.md` avant de l'activer, consulte le résultat de l'analyse de sécurité affiché sur ClawHub, et préfère la sandbox pour les tâches risquées.

## Créer ton propre skill

Crée `~/.openclaw/workspace/skills/revue-presse/SKILL.md` :

```markdown SKILL.md
---
name: revue-presse
description: Prépare une revue de presse IA en français à partir de sources fiables.
metadata: { "openclaw": { "emoji": "📰" } }
---

# Revue de presse IA

Quand l'utilisateur demande une revue de presse :
1. Cherche les actualités IA des dernières 24 h avec web_search.
2. Garde 5 sujets maximum, en privilégiant les sources primaires.
3. Pour chacun : un titre, deux phrases de résumé, le lien.
4. Enregistre la liste des sujets dans memory/ pour éviter les doublons.
```

Les champs `name` et `description` sont obligatoires ; la description sert à l'agent pour savoir quand utiliser le skill. Vérifie qu'il est reconnu :

```bash
openclaw skills info revue-presse
```

## La mémoire

La mémoire de l'agent est faite de simples fichiers Markdown dans son workspace :

- `MEMORY.md` : la mémoire à long terme, chargée au début de chaque session ;
- `memory/AAAA-MM-JJ.md` : les notes du jour ; celles d'aujourd'hui et d'hier sont rechargées automatiquement.

Pour retrouver une information plus ancienne, l'agent fait une recherche sémantique dans ces fichiers (outils `memory_search` et `memory_get`).

> ⚠️ **Piège RGPD** — Par défaut, cette recherche calcule ses embeddings avec l'API **OpenAI** : des extraits de ta mémoire partent alors chez OpenAI. Pour rester 100 % local, passe sur Ollama.

```bash
ollama pull nomic-embed-text
```

```json5 openclaw.json
{
  memory: {
    search: { provider: "ollama", model: "nomic-embed-text" },
  },
}
```

```bash
openclaw memory index --force
openclaw memory status
openclaw memory search "politique de rétention"
```

`openclaw configure --section memory` fait le même réglage de façon guidée.

## La sandbox Docker

Par défaut, l'agent exécute ses outils directement sur ta machine. La sandbox les fait tourner dans un conteneur Docker isolé : sans réseau, système en lecture seule, sans privilèges.

Construis d'abord l'image (installation npm) :

```bash
docker build -t openclaw-sandbox:bookworm-slim - <<'DOCKERFILE'
FROM debian:bookworm-slim
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
  bash ca-certificates curl git jq python3 ripgrep \
  && rm -rf /var/lib/apt/lists/*
RUN useradd --create-home --shell /bin/bash sandbox
USER sandbox
WORKDIR /home/sandbox
CMD ["sleep", "infinity"]
DOCKERFILE
```

Puis active la sandbox :

```json5 openclaw.json
{
  agents: {
    defaults: {
      sandbox: { mode: "non-main", scope: "session", workspaceAccess: "none" },
    },
  },
}
```

| Réglage | Valeurs |
|---|---|
| `mode` | `off` (défaut) · `non-main` : tout sauf ta session principale, donc tous les groupes et canaux · `all` : toutes les sessions |
| `scope` | `agent` (défaut) · `session` · `shared` |
| `workspaceAccess` | `none` (défaut, espace isolé) · `ro` (lecture seule) · `rw` (lecture-écriture) |

```bash
openclaw sandbox explain
openclaw sandbox list
```

> 💡 **Ce que la sandbox ne fait pas** — La Gateway reste sur ta machine : seule l'exécution des outils est isolée. La documentation précise que ce n'est « pas une frontière de sécurité parfaite ». On la combine avec des restrictions d'outils (session 6).

## Checklist

- J'ai listé les skills éligibles et cherché un skill sur ClawHub
- J'ai créé mon skill `revue-presse` et `openclaw skills info` le reconnaît
- La recherche mémoire utilise Ollama (`nomic-embed-text`) et non OpenAI
- J'ai construit l'image `openclaw-sandbox:bookworm-slim`
- La sandbox est active en mode `non-main` (vérifié avec `openclaw sandbox explain`)

## Quiz

**Où partent les extraits de mémoire si tu ne règles pas `memory.search.provider` ?**
- [ ] Nulle part, tout reste local
- [x] Vers l'API d'OpenAI, qui calcule les embeddings par défaut
- [ ] Vers ClawHub
- [ ] Vers Ollama
> Le fournisseur d'embeddings par défaut est OpenAI ; il faut choisir `ollama` explicitement pour rester local.

**Que fait le mode sandbox `non-main` ?**
- [ ] Il désactive la sandbox
- [ ] Il isole uniquement ta session principale
- [x] Il isole toutes les sessions sauf ta session principale, dont tous les groupes et canaux
- [ ] Il isole la Gateway entière
> Les conversations de groupe et de canal comptent toujours comme « non-main » : elles sont donc isolées.

**Quelle attitude adopter face à un skill trouvé sur ClawHub ?**
- [ ] L'installer : ClawHub garantit qu'il est sûr
- [x] Le vérifier et lire son SKILL.md avant de l'activer, comme du code non fiable
- [ ] Le lancer en root pour qu'il fonctionne bien
- [ ] Le copier dans la configuration Gateway
> Les skills tiers sont du code non fiable : `openclaw skills verify`, lecture du SKILL.md et sandbox.
