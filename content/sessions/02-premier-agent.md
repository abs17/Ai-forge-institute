# Session 2 — Ton premier agent

*AI Forge Institute · Formation OpenClaw 2026 · Badge : 🧠 Neural Architect*

**Objectif :** donner une identité à ton agent, le connecter à Telegram et contrôler qui peut lui parler.

## Le workspace : la mémoire et le caractère de l'agent

Chaque agent a un dossier de travail, par défaut `~/.openclaw/workspace`. Les fichiers Markdown qu'il contient sont lus à chaque session :

| Fichier | Contenu |
|---|---|
| `AGENTS.md` | Les règles de travail et les consignes, y compris la section `## Tools` sur l'usage des outils |
| `SOUL.md` | La personnalité : ton, valeurs, limites |
| `USER.md` | Ce que l'agent sait de toi (facultatif) |
| `IDENTITY.md` | Son nom et sa présentation |
| `MEMORY.md` et `memory/` | Sa mémoire à long terme et ses notes du jour (session 3) |

> ℹ️ **Changements récents** — `TOOLS.md` n'est plus utilisé : son contenu va dans `AGENTS.md`. `HEARTBEAT.md` n'est plus lu non plus. `openclaw doctor --fix` migre automatiquement un ancien workspace.

## Personnaliser Lobster-01

Ouvre `~/.openclaw/workspace/SOUL.md` et remplace son contenu :

```markdown SOUL.md
# Lobster-01

Tu es Lobster-01, l'assistant de veille IA de ton utilisateur.
- Tu réponds en français, de façon concise et concrète.
- Tu cites toujours tes sources quand tu résumes une information.
- Tu demandes confirmation avant toute action irréversible (suppression, envoi, achat).
```

Puis ajoute tes règles dans `AGENTS.md` :

```markdown AGENTS.md
## Veille
- Chaque résumé tient en 5 points maximum.
- Enregistre les sujets suivis dans memory/.

## Tools
- N'utilise pas exec pour supprimer des fichiers.
```

Pas besoin de redémarrer : ces fichiers sont relus à chaque nouvelle session. Tape `/new` dans la conversation pour en ouvrir une.

## Connecter Telegram

1. Dans Telegram, ouvre **@BotFather**, envoie `/newbot` et copie le token du bot.
2. Déclare le canal et vérifie la connexion :

```bash landing
openclaw channels add --channel telegram --token <token-du-bot>
openclaw channels status --probe
```

3. Envoie un premier message privé à ton bot. Il te répond par un **code d'appairage**.
4. Approuve ce code depuis ton terminal :

```bash
openclaw pairing list telegram
openclaw pairing approve telegram <CODE>
```

Les codes expirent au bout d'une heure. Une fois approuvé, tu peux discuter avec ton agent depuis ton téléphone.

## Qui a le droit de parler à ton agent ?

Le réglage `dmPolicy` décide qui peut écrire à l'agent en privé :

| Valeur | Effet |
|---|---|
| `pairing` (défaut) | Un inconnu reçoit un code ; rien ne passe tant que tu ne l'as pas approuvé |
| `allowlist` | Seuls les identifiants listés dans `allowFrom` sont acceptés |
| `open` | Tout le monde (exige `allowFrom: ["*"]`) — à éviter |
| `disabled` | Messages privés désactivés |

```json5 openclaw.json
{
  channels: {
    telegram: {
      enabled: true,
      dmPolicy: "pairing",
      groups: { "*": { requireMention: true } },
    },
  },
}
```

Dans un groupe, `requireMention: true` oblige à mentionner le bot pour qu'il réagisse.

## Suivre ce que fait l'agent

```bash
openclaw status
openclaw logs --follow
```

## Checklist

- J'ai personnalisé `SOUL.md` et `AGENTS.md`
- Mon bot Telegram est créé et `openclaw channels status --probe` est au vert
- J'ai approuvé mon code d'appairage
- J'ai échangé avec mon agent depuis Telegram
- J'ai suivi une réponse dans `openclaw logs --follow`

## Quiz

**Un inconnu écrit à ton bot. Avec `dmPolicy: "pairing"`, que se passe-t-il ?**
- [ ] L'agent lui répond normalement
- [x] Il reçoit un code, et rien ne passe tant que tu ne l'as pas approuvé
- [ ] Son message est transféré à OpenAI
- [ ] Le bot se désactive
> C'est le réglage par défaut : chaque nouvel interlocuteur doit être approuvé avec `openclaw pairing approve`.

**Quel fichier du workspace définit la personnalité de l'agent ?**
- [ ] `agent.config.json`
- [ ] `TOOLS.md`
- [x] `SOUL.md`
- [ ] `openclaw.json`
> `SOUL.md` porte la personnalité ; `AGENTS.md` les règles de travail ; `openclaw.json` la configuration technique.
