# Outils & programmes du département de génie physique de Polytechnique [![Python application](https://github.com/ejetzer/polygphys/actions/workflows/python-app.yml/badge.svg)](https://github.com/ejetzer/polygphys/actions/workflows/python-app.yml) [![CodeQL](https://github.com/ejetzer/polygphys/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/ejetzer/polygphys/actions/workflows/codeql-analysis.yml) [![Upload Python Package](https://github.com/ejetzer/polygphys/actions/workflows/python-publish.yml/badge.svg)](https://github.com/ejetzer/polygphys/actions/workflows/python-publish.yml) [![Documentation Status](https://readthedocs.org/projects/polygphys/badge/?version=latest)](https://polygphys.readthedocs.io/en/latest/?badge=latest)

- Installation via PyPI: https://pypi.org/project/polygphys/
    ```
    pip install polygphys
    ```
- Documentation sur Read The Docs: https://polygphys.readthedocs.io/en/latest/
- Contributions via Github: https://github.com/ejetzer/polygphys



## Prérequis & conseils

La version accessible par `pip` peut être utilisée telle quelle. Les branches `beta` et `alpha` sont en développement actif, et ne devrait être utilisées que

- Si vous avez une bonne idée de la structure du programme;
- Si vous êtes capable de lire et déboguer du [Python]
- Si vous avez [Python] d'installé, avec les modules décrits dans `requirements.txt`
- Si vous pouvez utiliser [Git]

**Pour toutes questions, svp envoyez un courriel à [emile.jetzer@polymtl.ca] avec «_[gestion-inventaire]_» dans le sujet du courriel.

[Python]: https://www.python.org
[Git]: https://git-scm.com/
[emile.jetzer@polymtl.ca]: mailto:emile.jetzer@polymtl.ca?subject=[gestion-inventaire]

## Installation

L'installation de la version stable se fait via `pip`:

```
pip install polygphys
```

Le bon fonctionnement du sous-module `polygphys.outils.appareils` pourrait demander l'installation de logiciel supplémentaire, selon l'utilisation:

1. L'installation des drivers VISA officiels de National Instrument
2. L'installation de drivers supplémentaires USB pour pyUSB.
3. L'installation séparée de pylablib (selon le système d'exploitation)
4. L'installation de drivers Keysight ou Agilent pour cetains adapteurs GPIB sur Windows.

Voir la [page de référence de pyVISA] pour résoudre les problèmes causés par des drivers manquants.

[page de référence de pyVISA]: https://pyvisa.readthedocs.io/projects/pyvisa-py/en/latest/installation.html


## Développement

Le développement se fait sur les branches `alpha` et `beta` en général, parfois sur des branches spécifiques à certaines fonctionnalités. Pour s'en servir et les installer, il faut utiliser `git`:

```
git clone https://github.com/ejetzer/polygphys.git
cd polygphys
git checkout alpha
pip install -e .
```

La branche `main` est gardée à jour avec la dernière version du programme. Les branches `v0` servent à identifier les versions majeures. Si on utilise une version majeure particulière, la commande `git checkout v0` permettra d'y accéder, puis `git pull origin v0` la mettra à jour. Les versions mineures sont indiquées par des étiquettes de la forme `v0.0.0`. Le second nombre indique les passes `beta` et le troisième les passes `alpha`.

### À faire

0. [ ] Uniformiser et étoffer la documentation du module.

Dans le sous module `polygphys.outils.base_de_donnees`:

1. [ ] Filtrer par valeur dans des colonnes
2. [ ] Permettre l'ajout de colonnes de l'intérieur de l'application
5. [ ] ~~Placer la base de données dans son propre répertoire git externe, et automatiquement en faire des sauvegardes~~
0. [x] Rendre les programmes exécutables avec un argument en ligne de commande & comme application
1. [x] Définir plus adéquatement les bases de données et leurs relations
3. [x] Permettre d'ajouter des sections de configuration
4. [x] Permettre d'ajouter des champs de configuration
6. [x] Rendre le logging plus compatible avec sqlalchemy.
7. [x] Retirer les logs sql, utiliser ceux de sqlalchemy à la place.

Dans les sous modules `polygphys.laboratoires`, `polygphys.outils.appareils` et `polygphys.sst`:

8. [x] Intégrer les applications externes
    - [ ] Certificats laser
    - [ ] PHS8302

En général:

1. [ ] Compléter la suite de tests

## Guide stylistique

Pendant le code, il est important de garder en tête les principes énoncés
dans les documents suivants:

- [PEP8], le guide stylistique de base pour le développement en Python
    En fait, ces principes sont tellement importants que je recommande
    d'utiliser le programme `autopep8` qui peut formater un fichier
    automatiquement.
- [PEP20], le Zen de Python, des principes génériques de développement à favoriser quand c'est possible.
- [Sphinx] pour les chaines de documentation. Ça rend la compréhension future des programmes beaucoup plus facile. On se remerciera quand on sera vieux!
- Les noms de variables, modules, etc devraient suivre [ces conventions].
- Dans la mesure du pratique, les noms de classes, fonctions et variables devraient être en français, de même pour la documentation.

[PEP20]: https://peps.python.org/pep-0020/
[PEP8]: https://peps.python.org/pep-0008/
[Sphinx]: https://sphinx-rtd-tutorial.readthedocs.io/en/latest/docstrings.html
[ces conventions]: https://namingconvention.org/python/

Généralement, on veut aussi structurer les fichiers comme le document [`exemple.py`].

[`exemple.py`]: ./exemple.py
