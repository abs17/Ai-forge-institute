# Session 4 — Automatisation, Multi-agents & 24/7

*AI Forge Institute · Formation OpenClaw 2026 · Badge final : 👑 Automator Supreme*

**Objectif :** faire travailler ton agent tout seul à heures fixes, répartir les rôles entre plusieurs agents et le garder actif en continu.

## Les automatisations

Une automatisation lance l'agent selon un planning, dans une session isolée, puis t'envoie le résultat. On place le planning en premier et la consigne en second :

```bash landing
# Tous les jours à 7 h
openclaw automations create "0 7 * * *" \
  "Prépare ma revue de presse IA avec le skill revue-presse." \
  --name "Brief du matin" \
  --tz "Europe/Paris"

# Toutes les heures
openclaw automations create "every 1h" \
  "Vérifie l'espace disque et préviens-moi s'il reste moins de 10 %." \
  --name "Surveillance disque"

openclaw automations list
openclaw automations run <job-id>
```

`openclaw cron` est un alias de `openclaw automations`. Par défaut, le résultat d'une tâche isolée t'est annoncé ; `--no-deliver` le garde en interne, `--webhook <url>` l'envoie à une URL.

## Le heartbeat

Le heartbeat réveille l'agent à intervalle régulier (toutes les 30 minutes par défaut) pour qu'il vérifie s'il a quelque chose à faire.

```json5 openclaw.json
{
  agents: {
    defaults: {
      heartbeat: { every: "1h" },   // "0m" désactive
    },
  },
}
```

## Plusieurs agents

Tu peux faire tourner plusieurs agents, chacun avec son workspace, son modèle et ses canaux. Les **bindings** décident quel agent répond sur quel canal :

```json5 openclaw.json
{
  agents: {
    entries: {
      veille: { name: "Veille IA", workspace: "~/.openclaw/workspace-veille", model: "ollama/gemma4" },
      perso:  { name: "Assistant perso", workspace: "~/.openclaw/workspace-perso", model: "ollama/qwen3.5:27b" },
    },
  },
  bindings: [
    { agentId: "veille", match: { channel: "telegram", accountId: "*" } },
    { agentId: "perso",  match: { channel: "signal", accountId: "*" } },
  ],
}
```

```bash
openclaw agents list --bindings
```

Un agent peut aussi déléguer une sous-tâche à un **sous-agent** (outil `sessions_spawn`), qui travaille dans sa propre session puis rapporte son résultat. Dans la conversation, `/subagents list` les affiche.

> ℹ️ **Ancien format** — `agents.list` est l'ancien format de déclaration ; `agents.entries` le remplace. `openclaw doctor --fix` fait la migration.

## Rester actif 24 h/24

La Gateway doit tourner en permanence pour recevoir tes messages et lancer les automatisations. Installe-la comme service système (LaunchAgent sur macOS, service systemd utilisateur sur Linux, tâche planifiée sur Windows) :

```bash
openclaw gateway install
openclaw gateway status

# Linux : garder le service actif après déconnexion
sudo loginctl enable-linger $(whoami)
```

`openclaw onboard --install-daemon` fait la même chose pendant l'installation.

## Sur un serveur européen

Pour ne pas dépendre de ton ordinateur, installe OpenClaw sur un VPS européen : Hetzner (Allemagne), OVH ou Scaleway (France). Garde la Gateway sur `loopback` et accède-y à distance par un tunnel SSH ou Tailscale :

```bash
# Depuis ton ordinateur : le tableau de bord distant devient accessible sur localhost:18789
ssh -N -L 18789:127.0.0.1:18789 utilisateur@mon-serveur
```

Un modèle local sur VPS demande beaucoup de RAM (16 Go et plus) ; sur une petite machine, le modèle tourne souvent ailleurs, ce qui change le bilan de confidentialité.

## Surveiller et mettre à jour

```bash
openclaw status --all
openclaw health
openclaw logs --follow
openclaw update
```

`openclaw status --all` produit un diagnostic qui masque les secrets, à partager sans risque.

## Exercice final

Crée une automatisation quotidienne qui utilise ton skill `revue-presse` et t'envoie le résultat sur Telegram. Ton agent travaille, tu reçois le résumé.

## Checklist

- J'ai créé une automatisation et l'ai lancée à la main avec `openclaw automations run`
- J'ai réglé le heartbeat
- J'ai déclaré deux agents et vérifié les bindings avec `openclaw agents list --bindings`
- La Gateway tourne comme service (`openclaw gateway status`)
- J'ai réalisé l'exercice final de revue de presse quotidienne

## Quiz

**Quelle commande installe la Gateway comme service qui redémarre avec la machine ?**
- [ ] `pm2 start openclaw`
- [x] `openclaw gateway install`
- [ ] `openclaw run --daemon`
- [ ] `docker run openclaw`
> `openclaw gateway install` crée un LaunchAgent (macOS), un service systemd utilisateur (Linux) ou une tâche planifiée (Windows).

**Dans une automatisation, que précise `"0 7 * * *"` ?**
- [x] Le planning : tous les jours à 7 h
- [ ] Le modèle à utiliser
- [ ] Le nombre maximal d'essais
- [ ] Le canal de livraison
> C'est une expression cron : minute 0, heure 7, tous les jours.

**À quoi servent les bindings ?**
- [ ] À chiffrer la configuration
- [x] À décider quel agent répond sur quel canal ou compte
- [ ] À installer des skills
- [ ] À relier OpenClaw à Ollama
> Chaque binding associe un agent à un canal, un compte ou une conversation ; la règle la plus précise l'emporte.
