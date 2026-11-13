# Session 7 — RGPD & AI Act : déployer en conformité

*AI Forge Institute · Formation OpenClaw 2026 · Badge : ⚖️ Compliance Officer*

**Objectif :** savoir documenter et justifier un agent IA au regard du RGPD et de l'AI Act, que ce soit pour toi ou pour une organisation.

> ℹ️ **Ce module n'est pas un conseil juridique** — Il donne une méthode et des repères à jour au 13 novembre 2026. Pour un déploiement en entreprise, fais valider ta documentation par ton DPO ou un juriste.

## Qui est qui ?

| Rôle | Texte | Dans un déploiement OpenClaw |
|---|---|---|
| **Responsable de traitement** | RGPD | Toi, ou l'organisation qui décide de déployer l'agent et pour quoi faire |
| **Sous-traitant** | RGPD, art. 28 | Tout prestataire qui traite des données pour ton compte : API de modèle (Mistral…), hébergeur du VPS |
| **Déployeur** | AI Act | Celui qui utilise un système d'IA sous sa propre autorité : l'organisation qui met l'agent à disposition |
| **Fournisseur** | AI Act | Celui qui met un modèle ou un système sur le marché (Mistral pour ses modèles). Tu peux le devenir si tu modifies substantiellement un modèle ou si tu proposes ton agent à des tiers sous ton nom. |

Un usage purement personnel et domestique échappe au RGPD. Dès que l'agent sert une activité professionnelle ou traite des données de collègues, de clients ou de prospects, le RGPD s'applique entièrement.

## Étape 1 — Cartographier les flux de données

Avant toute chose, liste où passent les données. C'est souvent là que se cachent les surprises :

| Flux | Par défaut dans OpenClaw | Réglage souverain |
|---|---|---|
| Conversations avec le modèle | Le fournisseur choisi à l'installation | Modèle local (Ollama) ou Mistral (UE) |
| Recherche dans la mémoire (embeddings) | **OpenAI** | `memory.search.provider: "ollama"` ou `"mistral"` |
| Modèle de secours | Aucun, sauf si tu en ajoutes | Pas de secours hors UE |
| Canal de messagerie | Les serveurs de la messagerie | Les messages d'un bot Telegram ne sont pas chiffrés de bout en bout et transitent par les serveurs de Telegram : préfère Signal ou le tableau de bord local pour les sujets sensibles |
| Outils web | Les sites consultés | Agent « lecteur » dédié (session 6) |
| Vérification de mise à jour | Version, système, architecture | `update: { checkOnStart: false }` si nécessaire |
| Conversations, mémoire, identifiants | Disque local (`~/.openclaw`) | Disque chiffré, machine ou VPS en UE |

`openclaw telemetry show` montre exactement ce qu'OpenClaw envoie lors de la vérification de mise à jour.

## Étape 2 — Le registre des traitements (art. 30)

Chaque usage de l'agent est une fiche du registre. Exemple pour un agent de veille interne :

| Rubrique | Exemple |
|---|---|
| Finalité | Veille documentaire et rédaction de synthèses pour l'équipe marketing |
| Base légale | Intérêt légitime de l'entreprise (mise en balance documentée) |
| Personnes concernées | Salariés utilisateurs ; auteurs cités dans les sources publiques |
| Données | Messages des utilisateurs, identifiants de messagerie, contenus publics collectés |
| Destinataires et sous-traitants | Mistral AI (API, UE) en secours ; hébergeur du VPS (France) |
| Transferts hors UE | Aucun |
| Durées de conservation | Conversations : 90 jours ; mémoire : revue trimestrielle |
| Mesures de sécurité | Gateway locale avec token, appairage, sandbox, outils restreints, audit hebdomadaire, disque chiffré |

## Étape 3 — Faut-il une AIPD ?

L'analyse d'impact relative à la protection des données (AIPD, art. 35 RGPD) est obligatoire quand le traitement présente un risque élevé. En pratique, la CNIL demande une AIPD dès que **deux critères** de cette liste sont réunis :

- usage innovant ou technologie nouvelle (un agent IA autonome en fait partie) ;
- surveillance systématique des personnes ;
- personnes vulnérables, **dont les salariés** vis-à-vis de leur employeur ;
- données sensibles ou hautement personnelles ;
- traitement à grande échelle ;
- croisement de jeux de données ;
- évaluation ou notation de personnes ;
- décision automatisée avec effet juridique ou similaire ;
- traitement qui empêche d'exercer un droit ou de bénéficier d'un service.

Un agent qui lit les e-mails et les fichiers des salariés coche presque toujours « technologie innovante » et « personnes vulnérables » : prévois une AIPD. La CNIL fournit un outil gratuit (logiciel PIA) pour la rédiger.

## Étape 4 — Appliquer les principes du RGPD à l'agent

- **Minimisation** : ne donne à l'agent que les dossiers, comptes et outils nécessaires (`fs.workspaceOnly`, `tools.deny`).
- **Conservation limitée** : fixe une durée pour les conversations et la mémoire, et applique-la (suppression régulière, éventuellement par une automatisation).
- **Transparence** : informe les personnes (salariés, clients) de l'usage de l'agent, de ses finalités et de leurs droits.
- **Droits des personnes** : sache retrouver et effacer les données d'une personne, y compris dans la mémoire.
- **Sécurité** : session 6.

```bash
# Effacer une conversation et la retirer de la mémoire
openclaw sessions delete "<clé-de-session>" --yes
openclaw memory forget --agent main --session "<clé-de-session>"
```

Pense aussi aux informations rédigées par l'agent dans `MEMORY.md` et `memory/` : relis-les et supprime ce qui concerne la personne.

## Étape 5 — Dans une entreprise : les salariés

- **Information préalable** : un dispositif qui collecte des informations sur les salariés doit leur être annoncé avant sa mise en place (Code du travail, art. L1222-4).
- **CSE** : les outils permettant de contrôler l'activité des salariés doivent être présentés au comité social et économique avant leur introduction.
- **Pas de surveillance cachée** : un agent ne doit pas servir à évaluer ou surveiller les salariés à leur insu. Un tel usage peut en outre relever du « haut risque » de l'AI Act.

## Étape 6 — Les contrats et les transferts

- **Contrat de sous-traitance** (art. 28) avec chaque fournisseur d'API de modèle : il fixe la finalité, la sécurité, la conservation et l'absence d'usage pour l'entraînement.
- **Transferts hors UE** : un fournisseur américain est encadré par le Data Privacy Framework UE–États-Unis, validé par le Tribunal de l'UE en septembre 2025 mais contesté en appel. Le Cloud Act américain permet aussi aux autorités des États-Unis d'exiger des données d'une entreprise américaine, même stockées en Europe. Un modèle local ou un fournisseur européen supprime ces deux incertitudes.

## L'AI Act pour un déployeur d'agent

### Le calendrier (état au 13 novembre 2026)

| Date | Ce qui s'applique |
|---|---|
| 1ᵉʳ août 2024 | Entrée en vigueur du règlement (UE) 2024/1689 |
| 2 février 2025 | Pratiques interdites (art. 5) et maîtrise de l'IA (art. 4) |
| 2 août 2025 | Obligations des fournisseurs de modèles à usage général (Mistral, etc.) |
| 2 août 2026 | Application générale, dont les obligations de transparence (art. 50) |
| 2 décembre 2027 | Systèmes à haut risque de l'annexe III (report décidé par le règlement « Omnibus numérique » adopté en 2026) |
| 2 août 2028 | Systèmes à haut risque intégrés à des produits réglementés (annexe I) |

### Tes obligations concrètes

- **Art. 4 — Maîtrise de l'IA** : prendre des mesures pour que les personnes qui utilisent l'agent comprennent ses capacités et ses limites. Une formation comme celle-ci, documentée, en fait partie.
- **Art. 50 — Transparence** : les personnes doivent savoir qu'elles échangent avec une IA quand ce n'est pas évident. Si ton agent répond à des clients ou à des tiers sur Telegram ou WhatsApp, dis-le clairement dans son premier message (et dans `SOUL.md`). Les contenus générés publiés pour informer le public, ou les « deepfakes », doivent être signalés comme tels.
- **Art. 5 — Pratiques interdites** : jamais de reconnaissance des émotions au travail, de manipulation, d'exploitation des vulnérabilités ou de catégorisation biométrique sensible.
- **Art. 26 — Haut risque** : si l'agent sert au recrutement, à l'évaluation ou à la surveillance de salariés, il devient un système à haut risque : contrôle humain, conservation des journaux au moins six mois, information des représentants du personnel. Le plus simple est de ne pas confier ces usages à un agent autonome.

> 💡 **Les repères de la CNIL sur l'IA agentique** — Une note exploratoire de la CNIL publiée à l'été 2026 rappelle que le RGPD s'applique entièrement aux agents et recommande : accès limités aux données et applications, mémoire propre à chaque agent avec une conservation limitée, exécution isolée, journalisation des actions, validation humaine des opérations sensibles et possibilité d'arrêt immédiat. Tous ces points se règlent dans OpenClaw (sessions 3, 4 et 6).

## Ressources officielles

- CNIL : [recommandations pour les systèmes d'IA](https://www.cnil.fr/fr/developpement-des-systemes-dia-les-recommandations-de-la-cnil-pour-respecter-le-rgpd) et [liste des traitements soumis à AIPD](https://www.cnil.fr/fr/ciblage-des-traitements-soumis-AIPD)
- Texte de l'AI Act : [règlement (UE) 2024/1689](https://eur-lex.europa.eu/eli/reg/2024/1689/oj)
- ANSSI : [recommandations de sécurité pour un système d'IA générative](https://cyber.gouv.fr/publications/recommandations-de-securite-pour-un-systeme-dia-generative)

## Checklist France

- Les flux de données de l'agent sont cartographiés, embeddings compris
- Une fiche du registre des traitements existe pour chaque usage de l'agent
- La nécessité d'une AIPD a été évaluée (et l'AIPD réalisée si deux critères sont réunis)
- Les salariés sont informés et le CSE consulté si l'agent touche à leur activité
- Une durée de conservation est fixée et appliquée pour les conversations et la mémoire
- La procédure d'effacement (sessions et mémoire) est documentée et testée

## Checklist Europe

- Aucun transfert hors UE : modèle local ou fournisseur européen, sans secours hors UE
- Un contrat de sous-traitance (art. 28) est signé avec chaque fournisseur d'API
- Les utilisateurs de l'agent ont suivi une formation documentée (AI Act, art. 4)
- Les personnes savent qu'elles échangent avec une IA (AI Act, art. 50)
- Aucun usage interdit (art. 5) ni à haut risque sans les mesures de l'art. 26
- La procédure de notification d'une violation à la CNIL sous 72 h est connue

## Quiz

**Où partent les données de la mémoire si tu ne règles pas la recherche mémoire ?**
- [ ] Nulle part
- [ ] Chez Mistral
- [x] Chez OpenAI, fournisseur par défaut des embeddings
- [ ] Chez Telegram
> C'est le flux le plus souvent oublié dans les cartographies : il faut le régler explicitement.

**Un agent qui lit les e-mails des salariés d'une entreprise nécessite-t-il une AIPD ?**
- [ ] Non, jamais pour un outil interne
- [x] Oui en règle générale : il réunit au moins « technologie innovante » et « personnes vulnérables (salariés) »
- [ ] Seulement si l'entreprise a plus de 250 salariés
- [ ] Seulement si le modèle est américain
> Deux critères de la liste suffisent en principe à rendre l'AIPD obligatoire.

**Ton agent répond à des clients sur WhatsApp. Que t'impose l'article 50 de l'AI Act ?**
- [ ] Rien, c'est un usage interne
- [ ] D'utiliser un modèle européen
- [x] D'informer clairement les personnes qu'elles échangent avec une IA
- [ ] De conserver les messages dix ans
> Depuis le 2 août 2026, les personnes doivent savoir qu'elles interagissent avec un système d'IA quand ce n'est pas évident.

**Que décale le règlement « Omnibus numérique » adopté en 2026 ?**
- [ ] L'interdiction de la reconnaissance des émotions au travail
- [x] Les obligations des systèmes à haut risque de l'annexe III, reportées au 2 décembre 2027
- [ ] L'entrée en vigueur du RGPD
- [ ] Les obligations de transparence de l'article 50, supprimées
> Les pratiques interdites et la transparence ne sont pas supprimées ; le report concerne les systèmes à haut risque.
