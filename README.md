# AutoML-Gr4

## Aperçu du projet

Ce projet est une application web complète basée sur le framework Django, conçue pour simplifier le processus d'analyse de données à partir de fichiers CSV et l'application de techniques d'apprentissage automatique. L'objectif est de fournir une plateforme robuste et conviviale permettant aux utilisateurs de télécharger leurs données, de les traiter, de les explorer visuellement, d'entraîner automatiquement des modèles d'apprentissage automatique et d'obtenir des prédictions précises. Le projet vise à automatiser de nombreuses étapes fastidieuses du cycle de vie de l'apprentissage automatique, le rendant accessible aux utilisateurs de tous niveaux techniques.

## Fonctionnalités clés

- **Téléchargement de fichiers CSV**: Interface utilisateur intuitive pour télécharger des fichiers CSV en toute sécurité.
- **Traitement et nettoyage des données**: Outils intégrés pour gérer les valeurs manquantes, convertir les types de données et normaliser les données.
- **Analyse exploratoire des données (EDA)**: Génération de visualisations interactives (telles que des graphiques et des diagrammes) pour comprendre la distribution des données, les relations entre les variables et découvrir des motifs.
- **Apprentissage automatique automatisé (AutoML)**: Prise en charge de l'entraînement automatique de modèles d'apprentissage automatique, y compris la sélection d'algorithmes, l'optimisation des hyperparamètres et l'évaluation des modèles.
- **Génération de prédictions**: Utilisation des modèles entraînés pour générer des prédictions sur de nouvelles données.
- **Gestion des modèles**: Un système pour suivre, stocker et gérer les modèles entraînés, permettant un accès facile et une réutilisation.
- **Interface de programmation d'applications (API)**: Exposition de points de terminaison API pour intégrer les fonctionnalités du projet avec d'autres applications.
- **Surveillance et journalisation**: Enregistrement des performances et surveillance de l'utilisation de l'application.

## Pile technologique

Le projet s'appuie sur un ensemble de technologies modernes pour garantir performance, évolutivité et maintenabilité :

- **Backend**:
  - **Django**: Un framework web Python de haut niveau pour un développement rapide et sécurisé.
  - **Django REST Framework (DRF)**: Pour la construction d'APIs robustes et flexibles.
  - **Pandas**: Pour la manipulation et l'analyse efficace des données.
  - **Scikit-learn**: La bibliothèque d'apprentissage automatique fondamentale pour l'entraînement des modèles.
  - **MLflow**: Pour le suivi des expériences, la gestion des modèles et le déploiement.
- **Frontend**:
  - **HTML/CSS/JavaScript**: Pour la construction de l'interface utilisateur interactive.
  - **Bootstrap**: Pour un design réactif et attrayant.
- **Base de données**:
  - **SQLite**: Base de données par défaut pour le développement.
  - Facilement extensible pour supporter PostgreSQL ou MySQL pour la production.
- **Environnement**:
  - **Docker**: Pour la conteneurisation et la facilité de déploiement.
  - **Gunicorn**: Serveur WSGI pour la production.
  - **Nginx**: Serveur web inverse pour la production.

## Configuration et exécution

Pour configurer et exécuter le projet localement, suivez les étapes ci-dessous :

### Prérequis

Assurez-vous d'avoir installé les éléments suivants sur votre système :

- **Python 3.x** (3.8 ou plus récent recommandé)
- **pip** (gestionnaire de paquets Python)
- **Git** (pour cloner le dépôt)
- **Docker et Docker Compose** (si vous prévoyez d'exécuter avec des conteneurs)

### Étapes d'installation

1. **Cloner le dépôt :**

   Ouvrez votre terminal et exécutez la commande suivante pour cloner le projet :

   ```bash
   git clone https://github.com/your-repo/AutoML-Gr4.git
   cd AutoML-Gr4
   ``

2. **Créer et activer un environnement virtuel :**

   Il est fortement recommandé d'utiliser un environnement virtuel pour isoler les dépendances du projet :

   ```bash
   python -m venv venv
   source venv/bin/activate  # Pour macOS/Linux
   # venv\Scripts\activate  # Pour Windows (dans l'invite de commande)
   # .\venv\Scripts\Activate.ps1  # Pour Windows (dans PowerShell)
   ```

3. **Installer les dépendances :**

   Après avoir activé l'environnement virtuel, installez toutes les bibliothèques requises :

   ```bash
   pip install -r requirements.txt
   ```

4. **Appliquer les migrations :**

   Appliquez les migrations de base de données pour créer les tables nécessaires :

   ```bash
   python manage.py migrate
   ```

5. **Créer un superutilisateur (facultatif) :**

   Pour accéder au panneau d'administration de Django, vous pouvez créer un superutilisateur :

   ```bash
   python manage.py createsuperuser
   ```
   Suivez les instructions pour entrer le nom d'utilisateur, l'e-mail et le mot de passe.

6. **Lancer le serveur de développement :**

   Vous pouvez maintenant démarrer le serveur de développement Django :

   ```bash
   python manage.py runserver
   ```

   L'application devrait maintenant être accessible dans votre navigateur web à l'adresse `http://127.0.0.1:8000/`.

### Exécution avec Docker (facultatif)

Si vous préférez exécuter le projet à l'aide de Docker, vous pouvez utiliser `docker-compose` :

```bash
docker-compose up --build
```

Cette commande construira les images Docker et démarrera tous les services définis dans le fichier `docker-compose.yml`.

## Structure du projet

Le projet est organisé en plusieurs applications Django, chacune responsable d'un ensemble spécifique de fonctionnalités :

- `csv_analyzer/`: Le répertoire principal du projet, contenant les paramètres généraux (`settings.py`), les configurations d'URL principales (`urls.py`) et les configurations WSGI/ASGI.
- `csv_processor/`: L'application principale qui contient la logique pour le traitement des fichiers CSV, l'analyse des données, les fonctions d'apprentissage automatique et les points de terminaison API associés.
  - `views.py`: Contient la logique de vue pour les pages et les points de terminaison API.
  - `models.py`: Définitions des modèles de base de données liés aux fichiers CSV et aux modèles entraînés.
  - `urls.py`: Configurations d'URL spécifiques à l'application `csv_processor`.
  - `serializers.py`: Pour la conversion des données entre les modèles Django et les formats JSON/XML pour DRF.
  - `utils.py`: Diverses fonctions utilitaires.
  - `mlflow_utils.py`: Fonctions d'intégration avec MLflow.
- `users/`: Une application pour la gestion des utilisateurs, l'inscription, la connexion et la gestion des profils.
- `templates/`: Contient les modèles HTML pour le frontend.
- `static/`: Contient les fichiers statiques comme CSS, JavaScript et les images.
- `media/`: Pour le stockage des fichiers téléchargés par les utilisateurs (par exemple, les fichiers CSV).
- `docs/` et `docsss/`: Répertoires contenant la documentation du projet.

## Tests

python -m venv venv
source venv/bin/activate  # Pour macOS/Linux
# venv\Scripts\activate  # Pour Windows

pip install -r requirements.txt

python manage.py migrate 

python manage.py runserver