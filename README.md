# SoftDesk Support
Projet Openclassrooms : P10_Creer_api_restful_django dans le cadre de la formation Développeur d'application Python - OpenClassrooms.

## Présentation du projet
SoftDesk support est une API RESTful sécurisée développée avec Django REST Framework pour gérer des projets, tâches et commentaires dans un environnement collaboratif.

L’API doit couvrir tout le cycle de vie collaboratif d’un projet (projet → contributeurs → issues → commentaires), avec une gestion fine des permissions et une pagination pour limiter la charge des requêtes.


## Installation du projet en local
### Prérequis

- Python 3.10+
- [Pipenv](https://pipenv.pypa.io/en/latest/) installé (`pip install --user pipenv`)
- Git

> Les dépendances incluent Django et Django REST Framework (DRF).

---

### Installation

Clonez ce dépôt et placez-vous dans le dossier :
```
git clone https://github.com/MagNott/P10_Creer_api_restful_django.git
cd softdesk-api
```

Installez les dépendances dans un environnement virtuel :
```
pipenv install
```

### Lancement du projet
Activez l’environnement virtuel :
```
pipenv shell
```

Lancez le serveur Django :
```
python manage.py runserver
```

Accédez ensuite à l’application à l’adresse suivante :
http://127.0.0.1:8000

## Structure du projet

- `softdesk_api/` : configuration principale Django
- `project_core/` : logique métier (projets, issues, commentaires)
  - `project_core/tests` : Tests automatisés du projet
- `authentication/` : gestion des utilisateurs et authentification
- `manage.py` : commande de gestion du projet


## Méthodes HTTP prises en charge

L’API prend en charge les opérations suivantes sur les ressources :
- GET : récupération des informations
- POST : création d’une nouvelle ressource
- PUT : mise à jour complète d’une ressource existante
- PATCH : mise à jour partielle d'une ressource existante
- DELETE : suppression d’une ressource


## Endpoints et Exigences fonctionnelles

### Token JWT

- `POST /api/token/` : obtenir un JWT (access)
- `POST /api/token/refresh` : renouveler l’access token via refresh

### Authentification

- `GET /api/users/` : liste de tous les utilisateurs (authentification requise).
- `POST /api/auth/` : inscription d’un nouvel utilisateur
- `GET /api/users/{id}/` : récupérer un utilisateur spécifique
- `PUT /api/users/{id}/` : mise à jour complète d’un utilisateur
- `PATCH /api/users/{id}/` : mise à jour partielle d’un utilisateur
- `DELETE /api/users/{id}/` : suppression d’un utilisateur

**Exigences fonctionnelles**
- Authentification requise pour toutes les ressources métier (hors signup/token).
- Âge minimum ≥ 15 ans (contrôle à la création).
- Données sensibles protégées (mot de passe hashé, email non exposé inutilement).
- L’inscription (POST) est ouverte à tous.
- La liste des utilisateurs (GET) est réservée aux utilisateurs connectés.


### Projets

- `GET /api/projects/` : liste paginée des projets de l’utilisateur  
- `POST /api/projects/` : créer un projet  
- `GET /api/projects/{id}/` : détail d’un projet  
- `PUT /api/projects/{id}/` : modifier complètement un projet 
- `PATCH /api/projects/{id}/` : modifier partiellement un projet  
- `DELETE /api/projects/{id}/` : supprimer un projet 

**Exigences fonctionnelles**
- Lister les projets dont l’utilisateur est contributeur.
- Créer un projet (l’utilisateur devient automatiquement auteur et contributeur).
- Modifier un projet (réservé à l’auteur).
- Supprimer un projet (réservé à l’auteur).
- Pagination des listes de projets.

### Contributeurs
- `GET /api/projects/{id}/contributors/` : liste des contributeurs d'un projet
- `POST /api/projects/{id}/contributors/` : ajouter un contributeur sur un projet
- `DELETE /api/projects/{id}/contributors/{id}/` : retirer un contributeur d'un projet

**Exigences fonctionnelles**
- Ajouter un utilisateur comme contributeur d’un projet (réservé à l’auteur).
- Lister les contributeurs d’un projet (réservé aux contributeurs du projet).
- Supprimer un contributeur (interdit pour l’auteur lui-même).

### Issues
- `GET /api/projects/{id}/issues/` : liste paginée des issues
- `POST /api/projects/{id}/issues/` : créer une issue
- `GET /api/projects/{id}/issues/{id}` : voir le détail d'une issue
- `PUT /api/projects/{id}/issues/{id}` : modifier complètement une issue
- `PATCH /api/projects/{id}/issues/{id}` : modifier partiellement une issue
- `DELETE /api/projects/{id}/issues/{id}` : supprimer une issue

**Exigences fonctionnelles**
- Lister toutes les issues d’un projet (si l’utilisateur est contributeur) avec une pagination.
- Créer une nouvelle issue dans un projet.
- Modifier ou supprimer une issue (réservé à l’auteur de l’issue).
- Attribuer une issue à un contributeur du projet.

### Commentaires
- `GET /api/projects/{id}/issues/{id}/comments/` : liste paginée des commentaires
- `POST /api/projects/{id}/issues/{id}/comments/` : ajouter un commentaire
- `GET /api/projects/{id}/issues/{id}/comments/{uuid}` : voir le détail d'une issue
- `PUT /api/projects/{id}/issues/{id}/comments/{uuid}` : modifier complètement une issue
- `PATCH /api/projects/{id}/issues/{id}/comments/{uuid}` : modifier partiellement une issue
- `DELETE /api/projects/{id}/issues/{id}/comments/{uuid}` : supprimer une issue

**Exigences fonctionnelles**
- Lister les commentaires liés à une issue avec une pagination.
- Créer un commentaire associé à une issue.
- Modifier ou supprimer un commentaire (réservé à l’auteur du commentaire).


### Choices
Endpoint servant à documenter les choix possible pour valoriser les issues et les projets. Il se base sur les modèles issue project et se met à jour avec l'application
- `GET /api/choices/issues/` : Liste des choix possibles pour issue
  - status
  - priority
  - tag
- `GET /api/choices/projects/` : Liste des choix possibles pour project
  - type


## Sécurité
- L’authentification est assurée via des **JSON Web Tokens (JWT)** avec `djangorestframework-simplejwt`.
- Les **UUID** (une clé alphanumérique très longue) sont utilisés comme identifiants pour les commentaires.  
Cela évite d’exposer des identifiants séquentiels faciles à deviner (1, 2, 3, …) et réduit les risques
  d’attaques par énumération



## Tests

Les tests sont écrits avec `Django APITestCase` et couvrent l'essentiel des endpoints :
- CRUD (création/lecture/mise à jour/suppression)
- Permissions (auteur, contributeur, anonyme → 200/401/403 attendus)
- Pagination (format count/next/previous/results, navigation ?page=)
- Endpoints read-only (choices → GET OK, POST/PUT/DELETE = 405)

Pour lancer les tests : 
```
python manage.py test project_core
```

**Notes**
Les tests utilisent une base de données éphémère (créée/détruite automatiquement).
L’auth se fait via force_authenticate (pas de logout serveur, JWT géré côté client).


## Comptes de test
Une base de données peuplée avec des données de test est intégrée afin de manipuler l'API.

L'admin est :
Magali - Mdp : motpasseadmin1

Les utilisateurs sont :
- Magali
- MagNott
- Claire
- Lucas
- Sophie
- Bernard
Ils ont tous le même mot de passe : motpasse456



## Auteur
Projet réalisé par MagNott en août 2025 dans le cadre du parcours développeur d'application Python chez OpenClassrooms.