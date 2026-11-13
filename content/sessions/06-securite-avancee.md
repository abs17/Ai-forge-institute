# Session 6 — Sécurité avancée des agents

*AI Forge Institute · Formation OpenClaw 2026 · Badge : 🔒 Hardening Expert*

**Objectif :** comprendre comment un agent se fait attaquer, appliquer une défense en profondeur sur OpenClaw et savoir réagir à un incident.

## Pourquoi un agent est une cible à part

Un chatbot ne fait que répondre. Un agent agit : il lit tes fichiers, exécute des commandes, envoie des messages. Le risque devient maximal quand trois éléments sont réunis dans le même agent :

1. **l'accès à des données privées** (fichiers, e-mails, mémoire) ;
2. **l'exposition à du contenu non fiable** (pages web, documents, messages de tiers) ;
3. **un moyen de faire sortir des données** (requêtes web, envoi de messages, commandes shell).

Un texte piégé dans une page web peut alors pousser l'agent à lire tes secrets puis à les envoyer ailleurs. Toute la suite de cette session consiste à **casser ce triangle** : retirer au moins un des trois éléments à chaque agent, et limiter les deux autres.

## Ce qui est arrivé à OpenClaw en 2026

Ces incidents réels montrent pourquoi les réglages par défaut ne suffisent pas :

| Date | Incident | Leçon |
|---|---|---|
| Janvier 2026 | **CVE-2026-25253** (CVSS 8,8) : un lien piégé pouvait voler le token de la Gateway et prendre le contrôle de l'agent. Corrigé en 2026.1.29. | Mettre à jour vite, ne pas cliquer sur des liens de configuration reçus |
| Février 2026 | **ClawHavoc** : 341 skills malveillants découverts sur ClawHub (824 quelques semaines plus tard), qui installaient un voleur de mots de passe via de fausses « étapes d'installation » | Un skill tiers est du code non fiable |
| Janvier–mars 2026 | Plusieurs études recensent des **dizaines de milliers d'instances OpenClaw exposées** sur Internet, dont une partie exploitable à distance | Ne jamais exposer la Gateway |
| Février 2026 | Gartner qualifie OpenClaw d'« insecure by default » et conseille aux entreprises de le bloquer hors environnement isolé | En entreprise : isoler, piloter, documenter |
| Avril 2026 | Le centre belge de cybersécurité (CCB) alerte sur trois vulnérabilités d'exécution de code à distance, dont un contournement du consentement corrigé en 2026.3.28 | Suivre les avis de sécurité et appliquer les correctifs |

Sources : [The Hacker News](https://thehackernews.com/2026/02/openclaw-bug-enables-one-click-remote.html), [Koi Security](https://koi.ai/blog/clawhavoc-341-malicious-clawedbot-skills-found-by-the-bot-they-were-targeting), [CCB](https://ccb.belgium.be/advisories/warning-3-high-severity-vulnerabilities-openclaw-can-lead-rce-patch-immediately), [CSO Online](https://www.csoonline.com/article/4129867/what-cisos-need-to-know-about-clawdbot-i-mean-moltbot-i-mean-openclaw.html).

> 💡 **Garde ton installation à jour** — Ce cours est vérifié sur la 2026.11.3. `openclaw update` installe la dernière version stable, `openclaw update status` montre où tu en es.

## Les référentiels à connaître

L'**OWASP** publie deux listes de référence. Voici les risques qui concernent directement un agent OpenClaw, et la parade correspondante :

| Risque OWASP | Ce que cela donne avec un agent | Parade OpenClaw |
|---|---|---|
| LLM01 Injection de prompt / ASI01 Détournement d'objectif | Une page web ou un e-mail donne des ordres à l'agent | Outils web limités, agent « lecteur » sans outils dangereux |
| LLM06 Excès d'autonomie / ASI02 Mauvais usage d'outils | L'agent supprime, envoie ou exécute sans contrôle | `tools.deny`, `exec-policy`, demande de confirmation |
| LLM03 / ASI04 Chaîne d'approvisionnement | Skill ou plugin piégé | `openclaw skills verify`, lecture du SKILL.md, liste blanche |
| ASI03 Abus d'identité et de privilèges | L'agent agit avec tes droits complets | Utilisateur système dédié, `fs.workspaceOnly` |
| ASI05 Exécution de code inattendue | Commande shell injectée | Sandbox Docker, `exec.security: "deny"` ou `allowlist` |
| ASI06 Empoisonnement de mémoire | Une fausse « consigne » s'inscrit dans `MEMORY.md` | Relire la mémoire, `openclaw memory forget` |
| LLM02 Divulgation d'informations sensibles | Secrets ou données personnelles dans une réponse | Secrets hors workspace, `dmScope` par interlocuteur |
| ASI10 Agent incontrôlé | L'agent continue à agir de travers | Arrêt d'urgence (`openclaw gateway stop`), journaux |

Références : [OWASP Top 10 for LLM Applications 2025](https://genai.owasp.org/llm-top-10/) et OWASP Top 10 for Agentic Applications 2026. L'ANSSI a aussi publié des [recommandations de sécurité pour un système d'IA générative](https://cyber.gouv.fr/publications/recommandations-de-securite-pour-un-systeme-dia-generative) (avril 2024).

## Défense en profondeur : sept couches

### 1. Le système

```bash
# Un utilisateur dédié, sans droits d'administration
sudo useradd -m -s /bin/bash openclaw
sudo -iu openclaw
# Puis installer OpenClaw avec cet utilisateur
```

Active le chiffrement du disque (FileVault, BitLocker, LUKS) : tout ce qui est dans `~/.openclaw` peut contenir des secrets.

### 2. Le réseau

- Gateway sur `loopback` avec authentification par token (réglage par défaut : le garder).
- Accès distant uniquement par tunnel SSH ou Tailscale en mode `serve`, jamais `funnel`.
- Pare-feu de la machine : tout refuser en entrée sauf SSH.

### 3. Qui peut parler à l'agent

```json5 openclaw.json
{
  session: { dmScope: "per-channel-peer" },
  channels: {
    telegram: {
      dmPolicy: "allowlist",
      allowFrom: ["123456789"],
      groupPolicy: "allowlist",
      groups: { "*": { requireMention: true } },
    },
  },
}
```

`allowlist` n'accepte que les identifiants listés ; `dmScope: "per-channel-peer"` donne une session séparée à chaque interlocuteur, pour que personne ne voie l'historique d'un autre.

### 4. Les outils

Commence par la base durcie de la documentation, puis réactive au cas par cas :

```json5 openclaw.json
{
  tools: {
    profile: "messaging",
    deny: ["group:automation", "group:runtime", "group:fs", "sessions_spawn", "sessions_send"],
    fs: { workspaceOnly: true },
    exec: { security: "deny", ask: "always" },
    elevated: { enabled: false },
    agentToAgent: { enabled: false },
  },
}
```

Pour un agent qui doit lancer des commandes, préfère une liste blanche avec confirmation :

```bash
openclaw exec-policy preset cautious
```

Une interdiction l'emporte toujours sur une autorisation. Attention : interdire `write` et `edit` ne rend pas `exec` inoffensif ; il faut restreindre `exec` lui-même.

### 5. La sandbox

Pour les conversations de groupe et tout ce qui touche à du contenu extérieur, isole toutes les sessions et monte le workspace en lecture seule :

```json5 openclaw.json
{
  agents: {
    defaults: {
      sandbox: { mode: "all", scope: "session", workspaceAccess: "ro" },
    },
  },
}
```

Par défaut, le conteneur n'a pas de réseau, son système est en lecture seule et il n'a aucun privilège : ne change ces réglages qu'en connaissance de cause.

### 6. Les skills et plugins

- `openclaw skills verify @auteur/skill --card` avant toute installation, et lecture du SKILL.md : méfie-toi de toute « étape d'installation » qui demande de lancer une commande téléchargée.
- N'installe des plugins que de sources de confiance : ils tournent dans le processus de la Gateway.
- `openclaw security audit --deep` analyse aussi les plugins installés.

### 7. Les secrets

- Clés dans `~/.openclaw/.env` ou dans l'environnement du service, jamais dans le workspace : l'agent peut lire son workspace.
- `openclaw secrets audit --check` repère les secrets en clair.
- Bot de messagerie sur un numéro ou un compte dédié.

## L'agent « lecteur » pour le contenu non fiable

Plutôt que de laisser ton agent principal lire le web, confie cette tâche à un agent séparé, sans accès aux fichiers ni aux commandes : il ne peut ni lire tes secrets ni agir, même s'il se fait piéger.

```json5 openclaw.json
{
  agents: {
    entries: {
      main:    { name: "Assistant", workspace: "~/.openclaw/workspace" },
      lecteur: {
        name: "Lecteur web",
        workspace: "~/.openclaw/workspace-lecteur",
        tools: { profile: "minimal", alsoAllow: ["web_fetch", "web_search"] },
        sandbox: { mode: "all", workspaceAccess: "none" },
      },
    },
  },
}
```

## Surveiller en continu

```bash
openclaw security audit --deep
openclaw secrets audit --check
openclaw status --all
openclaw logs --follow
```

Automatise l'audit chaque semaine et fais-toi envoyer le résultat :

```bash
openclaw automations create "0 8 * * 1" \
  "Lance openclaw security audit --deep et résume les alertes critiques." \
  --name "Audit hebdo" --tz "Europe/Paris"
```

## Réagir à un incident

Si l'agent a fait quelque chose d'anormal, ou si une faille touche ta version :

1. **Couper** : `openclaw gateway stop`.
2. **Révoquer** : nouveau token de Gateway (`openclaw doctor --generate-gateway-token`), révocation du token du bot dans @BotFather, rotation de toutes les clés API présentes sur la machine.
3. **Comprendre** : relire les journaux et les sessions concernées, et ce que l'agent a écrit dans sa mémoire.
4. **Nettoyer** : supprimer les skills suspects, `openclaw memory forget` sur les sessions compromises, mise à jour (`openclaw update`).
5. **Notifier** : si des données personnelles ont pu fuir, la violation doit être notifiée à la CNIL dans les **72 heures** (art. 33 RGPD), et aux personnes concernées si le risque est élevé (session 7).

## Checklist

- L'agent tourne sous un utilisateur système dédié, sur un disque chiffré
- `dmPolicy` est en `allowlist` ou `pairing`, avec `dmScope: "per-channel-peer"`
- Les outils partent de la base durcie, avec `exec-policy` en `cautious` ou plus strict
- La sandbox couvre toutes les sessions exposées à du contenu extérieur
- Un agent « lecteur » sans outils dangereux traite les contenus web
- L'audit de sécurité tourne chaque semaine et je connais la procédure d'incident

## Quiz

**Quels sont les trois éléments qui, réunis dans un même agent, rendent une fuite de données possible ?**
- [ ] Un modèle local, Docker et Telegram
- [x] L'accès à des données privées, l'exposition à du contenu non fiable et un moyen de faire sortir des données
- [ ] Une Gateway, un workspace et une mémoire
- [ ] Un token, un mot de passe et une clé API
> Il suffit de retirer l'un des trois pour qu'une injection de prompt ne puisse plus exfiltrer de données.

**Que retenir de la campagne ClawHavoc de février 2026 ?**
- [ ] Que ClawHub est désormais sûr
- [x] Que des centaines de skills malveillants y installaient un voleur de mots de passe : un skill tiers doit être vérifié avant installation
- [ ] Qu'il faut désactiver Ollama
- [ ] Que la sandbox suffit à tout bloquer
> Les skills piégés passaient par de fausses étapes d'installation ; vérification et lecture du SKILL.md sont indispensables.

**Tu as interdit `write` et `edit` à ton agent. Peut-il encore modifier des fichiers ?**
- [ ] Non, c'est impossible
- [x] Oui, avec l'outil `exec` s'il n'est pas restreint
- [ ] Oui, mais seulement dans le cloud
- [ ] Non, la Gateway l'en empêche
> La documentation le rappelle : bloquer write/edit ne rend pas exec inoffensif. Il faut aussi restreindre exec.

**Une faille de sécurité a peut-être exposé des données personnelles. Quel délai pour prévenir la CNIL ?**
- [ ] 24 heures
- [x] 72 heures
- [ ] 30 jours
- [ ] Aucun, ce n'est pas obligatoire
> L'article 33 du RGPD impose une notification dans les 72 heures après la découverte de la violation.
