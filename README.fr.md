# WillProof Labs : fichiers communs de l'organisation

*[English version](README.md)*

Ce dépôt spécial contient ce que partagent tous les dépôts de WillProof Labs. GitHub le lit
automatiquement ; il doit rester **public** pour cela, et ne contient rien de sensible.

## Ce que GitHub en fait

| Ici | Effet sur tous les dépôts de l'organisation |
|---|---|
| `profile/README.md` | la page d'accueil de l'organisation sur GitHub |
| `CONTRIBUTING.md`, `SECURITY.md`, `pull_request_template.md`, `ISSUE_TEMPLATE/` | utilisés par défaut par tout dépôt qui n'a pas son propre fichier (dépôts privés compris) |
| `workflow-templates/` | proposés dans l'onglet *Actions > New workflow* |
| `.github/workflows/commit-conventions.yml`, `gitleaks.yml` | workflows réutilisables que chaque dépôt appelle en une ligne |

Un dépôt qui a besoin de règles différentes ajoute simplement son propre fichier, qui
prend le dessus.

Les workflows partagés épinglent chaque action par SHA de commit et l'image gitleaks par
digest : un dépôt exécute exactement le code relu. Dependabot propose les mises à jour des
actions ; l'image gitleaks se met à jour à la main, car Dependabot ne surveille pas les images
lancées par `docker run`.

## Outils

Les outils n'utilisent que la bibliothèque standard de Python.

| Outil | Rôle |
|---|---|
| `tools/commit_conventions.py` | vérifie les messages de commit, les noms de branches et l'ordre « test d'abord » ; utilisé par la CI et comme hook local `commit-msg` (les projets copient ce seul fichier) |
| `tools/setup_repository.py` | applique la politique de fusion (rebase seulement), les étiquettes communes de `labels.toml` et, pour les produits, le sujet `willproof-product` |
| `tools/bootstrap_project.py` | crée un tableau, ses jalons et ses issues à partir d'un fichier de backlog ; idempotent |

Chaque outil affiche son plan et ne change rien sans `--apply`. `gh` doit être connecté,
avec le droit `project` pour les tableaux :

```bash
gh auth login
gh auth refresh -s project
```

## Démarrer un nouveau produit

1. Créer le dépôt à partir du modèle **willproof-template-python** (*Use this template*),
   privé jusqu'à une première version qui marche.
2. Renommer le paquet du modèle (voir son README), puis committer.
3. Appliquer les réglages et les étiquettes standard :

```bash
python -m tools.setup_repository --repo willproof-labs/my-product --product
python -m tools.setup_repository --repo willproof-labs/my-product --product --apply
```

4. Créer le tableau du produit à partir de sa graine de backlog, puis supprimer ce fichier
   dans un commit qui référence l'issue d'amorçage : à partir de là, le backlog, ce sont
   les issues.

```bash
python -m tools.bootstrap_project --repo willproof-labs/my-product --title my-product --backlog ../my-product/.github/project/backlog.toml --apply
```

## Le tableau du laboratoire

Chaque produit a son propre tableau. Le tableau **WillProof Lab** ne contient que ce qui
relie les projets ou concerne le laboratoire lui-même : dépendances, expériences
transverses, décisions communes. Sa graine est `project/lab-backlog.toml` :

```bash
python -m tools.bootstrap_project --repo willproof-labs/willproof --title "WillProof Lab" --backlog project/lab-backlog.toml --apply
```

## Rendre un produit public

Quand un produit devient public :

- [ ] ajouter le fichier `LICENSE` (GitHub propose les modèles : *Add file > Create new
  file*, nommé `LICENSE`)
- [ ] protéger `main` : pull requests seulement, vérifications obligatoires (gratuit pour
  les dépôts publics)
- [ ] décommenter le bloc de badges de son README
- [ ] l'ajouter à la liste *Projects* de `profile/README.md`, dans les deux langues

## Développement

```bash
poetry install
poetry run pytest
```
