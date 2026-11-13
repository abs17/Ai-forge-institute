# Session 8 — Comparatif : choisir le bon agent

*AI Forge Institute · Formation OpenClaw 2026 · Badge final : 👑 Agent Architect*

**Objectif :** situer OpenClaw parmi ses alternatives et savoir choisir, et justifier, l'outil adapté à un besoin.

## Ce que tu sais déjà faire, quel que soit l'outil

OpenClaw a lancé une famille d'outils qui partagent les mêmes briques. Tout ce que tu as appris s'y transpose :

- une **passerelle** qui relie l'agent à tes messageries ;
- un **modèle** interchangeable, local ou distant ;
- des fichiers de **personnalité et de règles** (`SOUL.md`, `AGENTS.md` ou équivalents) ;
- des **skills** au format `SKILL.md`, devenu un standard partagé ;
- une **mémoire** en fichiers et une recherche sémantique ;
- des **automatisations** planifiées ;
- et toujours les mêmes questions de sécurité : qui peut parler à l'agent, quels outils, quelle isolation.

## Les principaux agents personnels en novembre 2026

| | OpenClaw | Hermes Agent | NanoClaw | ZeroClaw | nanobot | IronClaw |
|---|---|---|---|---|---|---|
| Éditeur | Communauté OpenClaw | Nous Research | NanoCo | ZeroClaw Labs | HKU Data Science | NEAR AI |
| Langage | TypeScript | Python | TypeScript | Rust | Python | Rust |
| Licence | MIT | MIT | MIT | MIT ou Apache 2.0 | MIT | MIT ou Apache 2.0 |
| Étoiles GitHub | ~394 000 | ~263 000 | ~31 000 | ~33 000 | ~50 000 | ~13 000 |
| Version stable | 2026.11.3 | v2026.9.24 | v2026.10.0 | v0.9.0 | v0.4.1 | v1.4.1 |
| Modèles locaux (Ollama) | Oui | Oui | Oui (via un skill) | Oui | Oui | Oui |
| Isolation par défaut | Non (sandbox Docker à activer) | Non (exécution sur la machine) | **Oui** (conteneur par agent) | Approbation des actions risquées ; sandbox si disponible | Non | **Oui** pour les outils tiers (WASM) |
| Import depuis OpenClaw | — | Oui (`hermes import-agent openclaw`) | Oui (skill de migration) | Mémoire uniquement | Non vérifié | Non |

Chiffres relevés le 13 novembre 2026 sur GitHub. Les versions évoluent vite : vérifie-les avant de choisir.

## Les profils en bref

### OpenClaw — la référence

Le plus utilisé, le plus de canaux (une trentaine), le plus grand écosystème de skills (ClawHub) et une documentation complète. En contrepartie : une surface d'attaque large, un historique de failles en 2026 et des réglages par défaut permissifs qu'il faut durcir (session 6).

### Hermes Agent — l'agent qui apprend

Il crée et améliore ses propres skills à l'usage et modélise son utilisateur. Il importe une installation OpenClaw en une commande (personnalité, mémoire, skills, listes d'accès). Mais sa propre politique de sécurité le dit : la seule vraie frontière face à un modèle malveillant est le système d'exploitation. Par défaut, les commandes s'exécutent directement sur ta machine. Plusieurs failles ont été publiées au printemps 2026.

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
hermes import-agent openclaw --dry-run
```

### NanoClaw — l'isolation d'abord

Une base de code volontairement petite, lisible en une après-midi. Chaque agent tourne dans son propre conteneur Linux et ne voit que ce qui y est explicitement monté ; les clés API passent par une passerelle d'identifiants et ne sont jamais confiées à l'agent. Il est conçu autour de Claude et de Claude Code (d'autres modèles, dont Ollama, s'ajoutent par des skills), et on le personnalise en modifiant son code plutôt qu'une configuration.

### ZeroClaw — léger et embarqué

Un seul binaire Rust, peu gourmand, qui tourne jusque sur des cartes électroniques. Par défaut, il demande une approbation pour les actions à risque moyen et bloque les actions à haut risque. La sandbox du système (Landlock, Bubblewrap, Docker…) n'est active que si elle est disponible, et le projet est encore en version 0.x.

### nanobot — la simplicité

Un petit cœur Python facile à lire et à modifier, compatible avec les skills `SKILL.md` et ClawHub. Ses réglages par défaut sont permissifs : pas de restriction au workspace ni de sandbox tant qu'on ne les active pas.

### IronClaw — la sécurité par conception

Une réécriture en Rust inspirée d'OpenClaw : les outils non fiables tournent dans une sandbox WebAssembly avec des permissions explicites, les secrets sont chiffrés et injectés hors de portée du modèle, sans télémétrie. Moins de canaux (pas encore WhatsApp) et un développement moins actif depuis septembre 2026.

## Et les agents hébergés ?

Claude Cowork (Anthropic), Perplexity Computer ou Manus n'exigent aucune installation : l'agent tourne dans le cloud du fournisseur. C'est plus simple et souvent plus capable, mais tes fichiers et conversations sont traités sur leurs serveurs, en général hors de l'UE. On revient alors aux questions de la session 7 : contrat de sous-traitance, transferts, Cloud Act.

## Comment choisir : les six questions

1. **Quelles données l'agent touchera-t-il ?** Données personnelles ou sensibles : local ou fournisseur européen, isolation forte.
2. **Qui lui parlera ?** Toi seul, ou des collègues et des clients (contrôle d'accès, transparence AI Act).
3. **Que doit-il pouvoir faire ?** Lire, écrire, exécuter, envoyer : chaque capacité ajoutée doit être justifiée.
4. **Quelle isolation par défaut ?** Un outil isolé par conception (NanoClaw, IronClaw) pardonne plus d'erreurs de configuration.
5. **Qui maintiendra l'installation ?** Mises à jour de sécurité fréquentes : prévois le temps, ou choisis un outil plus petit.
6. **Quel écosystème te faut-il ?** Canaux, skills, documentation, communauté : l'avantage d'OpenClaw.

| Besoin | Choix raisonnable |
|---|---|
| Découvrir les agents, le plus de canaux et de skills | OpenClaw, durci selon la session 6 |
| Données sensibles, priorité à l'isolation | NanoClaw ou IronClaw, avec un modèle local |
| Un assistant qui s'améliore tout seul | Hermes Agent, dans une machine virtuelle ou un conteneur |
| Petite machine, objets connectés | ZeroClaw |
| Comprendre et modifier le code | nanobot ou NanoClaw |
| Aucune installation, données non sensibles | Agent hébergé, avec contrat et analyse des transferts |

> 💡 **Le bon réflexe** — Quel que soit l'outil, applique la même méthode : cartographie des flux, moindre privilège, isolation, journalisation, mises à jour. C'est ce qui rend un agent sûr, bien plus que le nom du logiciel.

## Exercice final

Rédige une note d'une page pour un dirigeant de PME qui veut « un assistant IA sur WhatsApp pour l'équipe commerciale » : outil recommandé, modèle (local ou Mistral), réglages de sécurité indispensables, documents RGPD et AI Act à produire, et limites à annoncer.

## Checklist

- Je sais citer les briques communes à tous les agents personnels
- Je connais les forces et faiblesses d'au moins quatre alternatives à OpenClaw
- Je sais quels outils isolent l'agent par défaut et lesquels non
- Je sais appliquer les six questions de choix à un cas réel
- J'ai rédigé la note de recommandation de l'exercice final

## Quiz

**Parmi ces outils, lequel isole chaque agent dans un conteneur dès l'installation ?**
- [ ] OpenClaw
- [ ] Hermes Agent
- [x] NanoClaw
- [ ] nanobot
> NanoClaw lance chaque agent dans son propre conteneur Linux ; OpenClaw, Hermes Agent et nanobot exécutent par défaut sur la machine.

**Tu passes d'OpenClaw à Hermes Agent. Que deviennent tes compétences ?**
- [ ] Elles sont perdues, tout est différent
- [x] Elles se transposent : passerelle, modèle, fichiers de personnalité, skills SKILL.md, mémoire et sécurité reposent sur les mêmes principes
- [ ] Il faut obligatoirement changer de modèle
- [ ] Hermes Agent n'accepte pas les skills
> Hermes Agent importe même directement une installation OpenClaw.

**Pour des données sensibles, quelle combinaison est la plus prudente ?**
- [ ] Un agent hébergé aux États-Unis
- [ ] OpenClaw avec les réglages par défaut
- [x] Un agent isolé par conception avec un modèle local
- [ ] N'importe quel agent, tant que le modèle est gros
> Isolation et modèle local réduisent à la fois le risque technique et les transferts de données.
