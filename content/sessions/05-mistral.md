# Session 5 — Personnaliser son agent avec Mistral

*AI Forge Institute · Formation OpenClaw 2026 · Badge : 🇪🇺 Sovereign Builder*

**Objectif :** faire tourner ton agent sur des modèles Mistral, en local ou via l'API européenne, et les adapter à tes besoins.

## Pourquoi Mistral ?

- **Une entreprise européenne** : Mistral AI est une société française. Son API est hébergée dans l'Union européenne par défaut.
- **Des modèles ouverts** : une grande partie de la gamme est publiée en *open-weight* sous licence Apache 2.0. Tu peux télécharger ces modèles et les faire tourner chez toi, sans aucun appel extérieur.
- **AI Act** : Mistral a signé le code de bonnes pratiques européen pour les modèles d'IA à usage général (juillet 2025) et publie pour ses modèles le résumé des données d'entraînement exigé par l'AI Act.

> ⚠️ **Fournisseur conforme ne veut pas dire déploiement conforme** — Les obligations de l'AI Act qui pèsent sur Mistral concernent le *fournisseur du modèle*. Toi, en tant que *déployeur*, tu restes responsable de la formation de tes équipes, de la transparence envers les personnes, du RGPD (base légale, AIPD, contrat de sous-traitance) et des obligations renforcées si ton usage est à haut risque. C'est l'objet de la session 7.

## Trois façons d'utiliser Mistral

| Mode | Où tournent les calculs ? | Pour qui ? |
|---|---|---|
| **100 % local** (Ollama) | Sur ta machine | Confidentialité maximale, données sensibles |
| **API Mistral** | Serveurs de Mistral (UE) | Modèles plus puissants sans matériel |
| **Hybride** | Local par défaut, API en secours | Bon compromis, à condition d'assumer que certains messages partent chez Mistral |

## Option 1 — Mistral en local avec Ollama

Les petits modèles **Ministral 3** (3B, 8B, 14B, licence Apache 2.0) savent appeler des outils et acceptent un long contexte : ils conviennent bien à un agent sur un ordinateur portable.

```bash landing
# Télécharger un modèle Mistral open-weight
ollama pull ministral-3:8b

# L'utiliser comme modèle de l'agent
openclaw models set ollama/ministral-3:8b
openclaw models list --provider ollama
```

Avec 32 Go de RAM ou un GPU confortable, `mistral-small3.2` (24B) est plus fiable sur les tâches longues.

## Option 2 — L'API Mistral

Le fournisseur Mistral est un plugin officiel à installer, puis on renseigne sa clé API (créée dans la console Mistral) :

```bash
openclaw plugins install @openclaw/mistral-provider
openclaw onboard --auth-choice mistral-api-key
openclaw models list --provider mistral
```

Range la clé dans `~/.openclaw/.env` (`MISTRAL_API_KEY=...`), jamais dans le workspace de l'agent.

Modèles disponibles dans OpenClaw 2026.11.3 :

| Identifiant | Usage |
|---|---|
| `mistral/mistral-large-latest` | Modèle par défaut, le plus capable |
| `mistral/mistral-medium-3-5` | Bon équilibre qualité/coût, raisonnement réglable |
| `mistral/mistral-small-latest` | Mistral Small 4, rapide, raisonnement réglable |
| `mistral/codestral-latest` | Code |

Les anciens modèles Magistral sont dépréciés : le raisonnement se règle désormais sur Small 4 et Medium 3.5.

## Option 3 — L'hybride : local d'abord, Mistral en secours

```json5 openclaw.json
{
  agents: {
    defaults: {
      model: {
        primary: "ollama/ministral-3:8b",
        fallbacks: ["mistral/mistral-small-latest"],
      },
    },
  },
}
```

Les modèles de secours sont essayés dans l'ordre quand le modèle principal échoue. Documente ce choix dans ton registre RGPD : quand le secours se déclenche, la conversation part chez Mistral.

## Un modèle par agent

Chaque agent peut avoir son propre modèle : un petit modèle local pour la veille, un modèle plus puissant pour l'analyse de documents.

```json5 openclaw.json
{
  agents: {
    entries: {
      veille:  { workspace: "~/.openclaw/workspace-veille", model: "ollama/ministral-3:8b" },
      analyse: {
        workspace: "~/.openclaw/workspace-analyse",
        model: { primary: "mistral/mistral-medium-3-5", fallbacks: [] },
      },
    },
  },
}
```

> 💡 **Piège des modèles par agent** — Sous forme de texte (`model: "…"`), le modèle d'un agent est strict : aucun modèle de secours n'est utilisé. Pour en ajouter, utilise la forme objet `{ primary, fallbacks: [...] }`.

## Personnaliser un modèle local avec un Modelfile

Ollama permet de créer ta propre variante d'un modèle : consignes intégrées, température, taille de contexte.

```text Modelfile
FROM ministral-3:8b
SYSTEM """Tu es un assistant professionnel francophone.
Tu réponds de façon concise, tu cites tes sources
et tu refuses de traiter des données de santé."""
PARAMETER temperature 0.3
PARAMETER num_ctx 32768
```

```bash
ollama create forge-ministral -f Modelfile
openclaw models set ollama/forge-ministral
```

La personnalité détaillée reste dans `SOUL.md` et `AGENTS.md` (session 2). Le Modelfile sert plutôt aux réglages techniques et aux garde-fous qui doivent s'appliquer quel que soit l'agent. OpenClaw fixe lui-même la taille de contexte des modèles locaux (32 768 tokens) ; une valeur plus petite dans le Modelfile peut donc être remplacée.

## La mémoire avec Mistral

Pour la recherche dans la mémoire, tu as deux options européennes :

```json5 openclaw.json
{
  memory: {
    search: { provider: "ollama", model: "nomic-embed-text" },   // 100 % local
    // ou : { provider: "mistral" }                               // API Mistral, modèle mistral-embed
  },
}
```

Rappel : sans ce réglage, la mémoire est envoyée à OpenAI pour calculer les embeddings.

## Ce qu'il faut vérifier côté Mistral

- **Entraînement** : selon Mistral, les données envoyées à l'API ne servent pas à entraîner ses modèles par défaut.
- **Conservation** : une option de conservation zéro (*zero data retention*) existe sur demande pour les comptes payants.
- **Contrat** : signe l'accord de traitement des données (DPA) de Mistral : c'est ton contrat de sous-traitance au sens de l'article 28 du RGPD.
- **Certifications** : Mistral annonce SOC 2 Type II et ISO 27001/27701 ; les rapports sont sur son portail de confiance.
- **Cloud Act** : utiliser Mistral directement ou en local évite l'exposition au droit américain ; passer par une marketplace américaine (Azure, AWS, Google Cloud) la réintroduit.

Ces conditions évoluent : vérifie-les sur le site de Mistral avant de les inscrire dans ta documentation de conformité.

## Checklist

- J'ai fait tourner `ollama/ministral-3:8b` en local
- J'ai installé le plugin Mistral et `openclaw models list --provider mistral` affiche les modèles
- J'ai configuré un modèle principal local et un modèle de secours, en documentant le flux
- J'ai créé un modèle personnalisé avec un Modelfile
- La recherche mémoire utilise Ollama ou Mistral, et non OpenAI
- J'ai identifié les documents à obtenir de Mistral : DPA, politique de conservation, certifications

## Quiz

**Mistral a signé le code de bonnes pratiques de l'AI Act. Ton agent est-il conforme pour autant ?**
- [ ] Oui, la conformité du fournisseur couvre tout
- [x] Non : en tant que déployeur, tu gardes tes propres obligations (formation, transparence, RGPD, usages à haut risque)
- [ ] Oui, à condition d'utiliser l'API et non un modèle local
- [ ] Non, car Mistral n'est pas concerné par l'AI Act
> Le code de bonnes pratiques porte sur les obligations du fournisseur de modèle ; celles du déployeur restent à ta charge.

**Quelle option garde toutes les données sur ta machine ?**
- [x] Un modèle Mistral open-weight servi par Ollama
- [ ] `mistral/mistral-large-latest`
- [ ] L'hybride avec un modèle de secours Mistral
- [ ] Mistral via une marketplace cloud
> Seul le modèle local évite tout envoi de données ; l'API, même européenne, est un sous-traitant.

**Comment ajouter un modèle de secours à un agent précis ?**
- [ ] `model: "ollama/ministral-3:8b"`
- [x] `model: { primary: "ollama/ministral-3:8b", fallbacks: ["mistral/mistral-small-latest"] }`
- [ ] En ajoutant `fallback: true`
- [ ] Ce n'est pas possible par agent
> La forme texte est stricte ; il faut la forme objet avec `fallbacks`.
