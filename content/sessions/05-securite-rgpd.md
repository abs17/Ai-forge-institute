# Module transverse — Sécurité & RGPD France / Europe

*AI Forge Institute · Formation OpenClaw 2026*

**Philosophie : Privacy by Design.** Chaque choix technique vise la souveraineté des données et la conformité réglementaire.

## Principes

- Aucune donnée hors du réseau local par défaut
- Chiffrement au repos (AES-256 en option)
- Audit trail de chaque décision de l'agent (`--audit`)
- Pas de télémétrie, pas d'analytics, pas de cookies tiers

## Risques à éviter

- **Exposer l'API Ollama sur `0.0.0.0`** : n'importe qui sur ton réseau, voire sur Internet, pourrait utiliser ton LLM et ta machine.
- Exécuter l'agent en `root`.
- Désactiver la sandbox en production.
- Mettre des clés ou tokens dans `agent.config.json`.

## Durcissement

```bash
# Utilisateur dédié, non-root
sudo useradd -m -s /bin/bash openclaw-agent
sudo -u openclaw-agent openclaw run agent.config.json --audit

# Ollama n'écoute que sur localhost
# (installation Linux : service systemd → sudo systemctl edit ollama)
#   [Service]
#   Environment="OLLAMA_HOST=127.0.0.1:11434"
sudo systemctl restart ollama
ss -tlnp | grep 11434        # doit afficher 127.0.0.1:11434

# Secrets dans .env, jamais dans la config
echo "TELEGRAM_BOT_TOKEN=xxx" >> .env
chmod 600 .env

# Pare-feu : tout bloquer sauf le nécessaire
sudo ufw default deny incoming
sudo ufw allow ssh
sudo ufw enable
```

## Checklist RGPD France

- Hébergement en France ou dans l'UE
- Aucune donnée personnelle transmise à des tiers
- Stockage navigateur local uniquement, aucun cookie tiers
- Recommandations de la CNIL sur l'IA consultées et appliquées
- Registre des traitements à jour (art. 30 RGPD)
- DPO désigné si le traitement l'exige (secteur public, suivi à grande échelle, données sensibles)

## Checklist Europe

- Aucun transfert hors UE (conforme à l'arrêt Schrems II)
- LLM open-weight (Llama 3) : pas de dépendance à une API propriétaire
- Sandbox Docker : exécutions isolées
- Droit à l'effacement : suppression locale immédiate
- AI Act (UE 2024) : traçabilité via `--audit`
- Chiffrement en transit (TLS) dès qu'un service est exposé sur le réseau

## Note sur les supports multimédias de la formation

Les vidéos, podcasts, quiz et flashcards de la plateforme sont générés **par l'équipe pédagogique** avec Google NotebookLM, à partir des seuls textes de cours publics. Aucune donnée d'apprenant n'est envoyée à NotebookLM. Les fichiers sont ensuite hébergés avec le site : leur lecture ne fait appel à aucun service tiers.
