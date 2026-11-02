# Contribuer à WillProof Labs

*[English version](CONTRIBUTING.md)*

Merci de votre intérêt. Ces règles s'appliquent à tous les dépôts de l'organisation, sauf
si le `CONTRIBUTING.md` d'un projet dit autre chose. Elles se veulent légères : chacune
existe parce qu'elle protège quelque chose d'important.

## Avant de commencer

- **Toute modification part d'une issue.** Ouvrez-en une (formulaire bug, fonctionnalité
  ou expérience), ou prenez-en une sur le tableau du projet, et signalez que vous la
  prenez.
- **Réutiliser avant de construire.** Vérifiez quel outil existant fait déjà une partie
  du travail ; les formulaires d'issues le demandent.
- **Ne partagez jamais rien d'identifiant ni de secret** : noms de machine, noms
  d'utilisateur, chemins personnels, clés, vraies données personnelles.

## Commits et branches

Les branches portent le numéro de l'issue : `type/<numéro>-description-courte`.

```text
feat/12-onnx-engine
fix/31-icacls-parsing
docs/7-readme-pitch
```

Les messages de commit suivent [Conventional Commits](https://www.conventionalcommits.org/fr/)
et référencent leur issue (en anglais, comme le code) :

```text
feat(engines): add the ONNX Runtime engine

Why the change is needed, in a few lines if it is not obvious.

Refs #12
```

| Type | Pour |
|---|---|
| `test` | un test, en général écrit avant le code qu'il spécifie |
| `feat` | une nouvelle fonctionnalité |
| `fix` | une correction de bug |
| `refactor` | un changement qui ne modifie ni le comportement ni les tests |
| `docs` | de la documentation seulement |
| `ci`, `build`, `chore` | pipelines, packaging, maintenance |
| `perf` | une amélioration de performance mesurée |

`feat!:` (avec `!`) signale une rupture de compatibilité. La première ligne fait 72
caractères au plus.

## Développement piloté par les tests

On écrit d'abord le test qui échoue, on le committe (`test:`), puis on le fait passer
(`feat:` ou `fix:`). Dans une pull request, un commit `feat` ou `fix` doit venir après au
moins un commit `test`. Quand un test n'a vraiment pas de sens (une coquille dans un
message, par exemple), ajoutez une ligne qui dit pourquoi :

```text
fix: correct a typo in an error message

Refs #44

TDD-Exempt: wording only, no behaviour to specify
```

La CI vérifie les messages de commit, les noms de branches et cet ordre sur chaque pull
request. Pour vérifier les messages avant même leur création, installez le hook fourni
par chaque projet (voir sa documentation `DEVELOPMENT`).

## Pull requests

- Une pull request par issue ; sa description indique `Closes #<numéro>`.
- Les pull requests sont fusionnées par **rebase** : chaque commit arrive tel quel sur
  `main`, et l'historique « test d'abord » reste lisible. Le squash et les commits de
  fusion sont désactivés.
- `main` ne change que par des pull requests dont les vérifications sont au vert.

## Définition de « terminé »

Un changement est terminé quand :

1. ses tests ont été écrits d'abord, et tous les tests passent ;
2. le lint, le formatage et la vérification des types passent ;
3. la documentation est à jour **en anglais et en français** ;
4. rien d'identifiant ni de secret n'est committé ;
5. la pull request est relue et fusionnée.

## Documentation en deux langues

Le code, les commentaires et les messages de commit sont en anglais. La documentation
existe en anglais et en français, modifiés ensemble dans la même pull request : une
barrière de langue ne devrait jamais tenir un bon développeur à l'écart.

## Travailler avec des assistants IA

Les assistants IA sont bienvenus, utilisés ouvertement :

- déclarez leur usage dans la pull request (quel assistant, pour quoi) ;
- les commits écrits avec un assistant portent une ligne `Co-Authored-By` qui le nomme ;
- une personne relit et fusionne toujours ; les assistants ne poussent jamais sur `main` ;
- les assistants reçoivent l'accès le plus restreint possible (un dépôt, pull requests
  seulement) ;
- vous restez responsable de ce que vous soumettez : comprenez-le avant d'ouvrir la pull
  request.

## Sécurité

Ne signalez jamais une vulnérabilité dans une issue publique : voir
[SECURITY.md](SECURITY.md).
