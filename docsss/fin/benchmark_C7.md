# Benchmark des Solutions de Data Science et MLOps pour le Projet "CSV Analyzer"

**Auteur :** [Your Name]
**Projet :** AutoML-Gr4-1 - CSV Analyzer
**Date :** [Date]
**Version :** 2.0

---

## Table des Matières

1.  [Synthèse Managériale (Executive Summary)](#synthèse-managériale-executive-summary)
2.  [Introduction](#introduction)
    *   [2.1. Contexte du Projet](#21-contexte-du-projet)
    *   [2.2. Objectifs de l'Étude de Benchmark](#22-objectifs-de-létude-de-benchmark)
    *   [2.3. Méthodologie d'Évaluation](#23-méthodologie-dévaluation)
    *   [2.4. Périmètre de l'Étude](#24-périmètre-de-létude)
3.  [Benchmark des Plateformes Cloud pour l'IA/ML](#benchmark-des-plateformes-cloud-pour-lia-ml)
    *   [3.1. Introduction aux Plateformes ML dans le Cloud](#31-introduction-aux-plateformes-ml-dans-le-cloud)
    *   [3.2. Analyse Détaillée : Amazon Web Services (AWS)](#32-analyse-détaillée--amazon-web-services-aws)
        *   [3.2.1. Écosystème AI/ML d'AWS](#321-écosystème-aiml-daws)
        *   [3.2.2. Forces et Avantages Stratégiques](#322-forces-et-avantages-stratégiques)
        *   [3.2.3. Faiblesses et Défis Potentiels](#323-faiblesses-et-défis-potentiels)
        *   [3.2.4. Modèle de Tarification](#324-modèle-de-tarification)
    *   [3.3. Analyse Détaillée : Microsoft Azure](#33-analyse-détaillée--microsoft-azure)
        *   [3.3.1. Écosystème Azure Machine Learning](#331-écosystème-azure-machine-learning)
        *   [3.3.2. Forces et Avantages Stratégiques](#332-forces-et-avantages-stratégiques)
        *   [3.3.3. Faiblesses et Défis Potentiels](#333-faiblesses-et-défis-potentiels)
        *   [3.3.4. Modèle de Tarification](#334-modèle-de-tarification)
    *   [3.4. Analyse Détaillée : Google Cloud Platform (GCP)](#34-analyse-détaillée--google-cloud-platform-gcp)
        *   [3.4.1. Écosystème AI Platform & Vertex AI](#341-écosystème-ai-platform--vertex-ai)
        *   [3.4.2. Forces et Avantages Stratégiques](#342-forces-et-avantages-stratégiques)
        *   [3.4.3. Faiblesses et Défis Potentiels](#343-faiblesses-et-défis-potentiels)
        *   [3.4.4. Modèle de Tarification](#344-modèle-de-tarification)
    *   [3.5. Matrice de Comparaison et Recommandation](#35-matrice-de-comparaison-et-recommandation)
4.  [Benchmark des Outils MLOps](#benchmark-des-outils-mlops)
    *   [4.1. L'Importance Stratégique du MLOps](#41-limportance-stratégique-du-mlops)
    *   [4.2. Analyse Détaillée : MLflow](#42-analyse-détaillée--mlflow)
        *   [4.2.1. Composants et Architecture](#421-composants-et-architecture)
        *   [4.2.2. Forces et Avantages Stratégiques](#422-forces-et-avantages-stratégiques)
        *   [4.2.3. Faiblesses et Limitations](#423-faiblesses-et-limitations)
    *   [4.3. Analyse Détaillée : Kubeflow](#43-analyse-détaillée--kubeflow)
        *   [4.3.1. Composants et Architecture](#431-composants-et-architecture)
        *   [4.3.2. Forces et Avantages Stratégiques](#432-forces-et-avantages-stratégiques)
        *   [4.3.3. Faiblesses et Complexité de Mise en Œuvre](#433-faiblesses-et-complexité-de-mise-en-œuvre)
    *   [4.4. Analyse Détaillée : DVC (Data Version Control)](#44-analyse-détaillée--dvc-data-version-control)
        *   [4.4.1. Concepts et Workflow](#441-concepts-et-workflow)
        *   [4.4.2. Forces et Avantages Stratégiques](#442-forces-et-avantages-stratégiques)
        *   [4.4.3. Faiblesses et Positionnement](#443-faiblesses-et-positionnement)
    *   [4.5. Matrice de Comparaison et Recommandation](#45-matrice-de-comparaison-et-recommandation)
5.  [Benchmark des Solutions de CI/CD](#benchmark-des-solutions-de-cicd)
    *   [5.1. Le Rôle de la CI/CD dans le MLOps](#51-le-rôle-de-la-cicd-dans-le-mlops)
    *   [5.2. Analyse Détaillée : GitHub Actions](#52-analyse-détaillée--github-actions)
        *   [5.2.1. Concepts Clés](#521-concepts-clés)
        *   [5.2.2. Forces et Avantages Stratégiques](#522-forces-et-avantages-stratégiques)
        *   [5.2.3. Faiblesses et Limitations](#523-faiblesses-et-limitations)
    *   [5.3. Analyse Détaillée : Jenkins](#53-analyse-détaillée--jenkins)
        *   [5.3.1. Architecture et Fonctionnalités](#531-architecture-et-fonctionnalités)
        *   [5.3.2. Forces et Avantages Stratégiques](#532-forces-et-avantages-stratégiques)
        *   [5.3.3. Faiblesses et Coût de Maintenance](#533-faiblesses-et-coût-de-maintenance)
    *   [5.4. Analyse Détaillée : GitLab CI/CD](#54-analyse-détaillée--gitlab-cicd)
        *   [5.4.1. Intégration et Fonctionnalités](#541-intégration-et-fonctionnalités)
        *   [5.4.2. Forces et Avantages Stratégiques](#542-forces-et-avantages-stratégiques)
        *   [5.4.3. Faiblesses et Dépendance à l'Écosystème](#543-faiblesses-et-dépendance-à-lécosystème)
    *   [5.5. Matrice de Comparaison et Recommandation](#55-matrice-de-comparaison-et-recommandation)
6.  [Synthèse des Recommandations et Stack Technologique Finale](#synthèse-des-recommandations-et-stack-technologique-finale)
    *   [6.1. Vue d'Ensemble de la Stack Recommandée](#61-vue-densemble-de-la-stack-recommandée)
    *   [6.2. Justification Holistique pour le Projet "CSV Analyzer"](#62-justification-holistique-pour-le-projet-csv-analyzer)
    *   [6.3. Trajectoire d'Évolution de la Stack](#63-trajectoire-dévolution-de-la-stack)
7.  [Glossaire](#glossaire)
8.  [Références](#références)

---

## 1. Synthèse Managériale (Executive Summary)

Ce document présente une étude comparative (benchmark) approfondie des technologies clés pour le développement et le déploiement du projet "CSV Analyzer". L'objectif est de fournir une base décisionnelle solide pour la sélection d'une stack technique performante, évolutive et adaptée aux contraintes du projet.

Trois domaines technologiques majeurs ont été analysés :

1.  **Plateformes Cloud AI/ML :** Analyse d'Amazon Web Services (AWS), Microsoft Azure, et Google Cloud Platform (GCP). Bien qu'un déploiement cloud ne soit pas prévu pour la phase initiale, cette analyse prépare l'avenir. GCP est légèrement favorisé pour sa maturité dans les services de données et d'IA, mais le choix final dépendra des opportunités et des compétences de l'équipe.
2.  **Outils MLOps :** Comparaison de MLflow, Kubeflow, et DVC. La recommandation claire et immédiate est **MLflow**. Sa simplicité d'intégration, sa nature agnostique et son excellent équilibre entre fonctionnalités et complexité en font l'outil idéal pour gérer le cycle de vie des modèles dans le cadre de notre projet.
3.  **Solutions de CI/CD :** Évaluation de GitHub Actions, Jenkins, et GitLab CI/CD. La recommandation est sans équivoque pour **GitHub Actions**. Son intégration native avec le dépôt de code du projet, sa syntaxe déclarative (YAML), et son généreux plan gratuit pour les projets open-source en font la solution la plus efficace et la plus simple à mettre en œuvre.

En conclusion, la stack technologique recommandée pour démarrer le projet est la suivante :

*   **Développement et Déploiement Local :** Docker, Docker Compose
*   **Gestion du Cycle de Vie ML (MLOps) :** MLflow
*   **Intégration et Déploiement Continus (CI/CD) :** GitHub Actions

Cette stack représente le meilleur compromis entre la performance, la simplicité de mise en œuvre, la maturité des outils et les coûts (nuls dans ce cas). Elle fournit une fondation robuste pour le développement initial tout en offrant des chemins d'évolution clairs vers un déploiement cloud à plus grande échelle.

---

## 2. Introduction

### 2.1. Contexte du Projet

Le projet "CSV Analyzer" a pour ambition de créer une application web qui démocratise l'accès au Machine Learning. En permettant aux utilisateurs de téléverser des fichiers CSV et d'entraîner des modèles de classification et de régression sans écrire de code, le projet répond à un besoin d'outils d'analyse de données plus accessibles. Le succès d'un tel projet ne repose pas uniquement sur la qualité de son algorithmique, mais également sur la robustesse, la fiabilité et l'évolutivité de son infrastructure sous-jacente. Le choix des bonnes technologies est donc une étape critique qui conditionne la réussite à long terme.

### 2.2. Objectifs de l'Étude de Benchmark

Cette étude vise à :

*   **Évaluer objectivement** les principales solutions du marché dans trois domaines : plateformes cloud, outils MLOps, et systèmes de CI/CD.
*   **Comparer** ces solutions sur la base de critères techniques et fonctionnels pertinents pour le projet "CSV Analyzer".
*   **Fournir une recommandation claire et argumentée** pour chaque catégorie d'outils.
*   **Documenter le processus de décision** pour assurer la transparence et faciliter les futures réévaluations architecturales.

### 2.3. Méthodologie d'Évaluation

Pour chaque catégorie d'outils, une méthodologie en quatre étapes a été appliquée :

1.  **Présélection :** Identification des 3 à 4 acteurs les plus pertinents et reconnus sur le marché.
2.  **Analyse Approfondie :** Étude de la documentation officielle, d'articles techniques, de livres blancs et de retours d'expérience de la communauté pour chaque solution.
3.  **Définition des Critères :** Établissement d'une liste de critères d'évaluation pondérés, incluant :
    *   **Fonctionnalités & Capacités :** Couverture fonctionnelle, richesse de l'écosystème.
    *   **Facilité d'Utilisation & Courbe d'Apprentissage :** Complexité de l'installation, de la configuration et de l'utilisation quotidienne.
    *   **Intégration & Compatibilité :** Facilité d'intégration avec les autres briques de notre stack (Python, Django, Docker).
    *   **Maturité & Communauté :** Stabilité, taille de la communauté, qualité de la documentation et du support.
    *   **Coût Total de Possession (TCO) :** Coûts de licence, d'infrastructure et de maintenance.
4.  **Notation et Recommandation :** Attribution d'un score à chaque solution sur la base des critères et formulation d'une recommandation finale.

### 2.4. Périmètre de l'Étude

*   **Inclus :** Plateformes IaaS/PaaS pour le ML, outils de gestion du cycle de vie du ML (MLOps), et plateformes de CI/CD.
*   **Exclus :** Frameworks de développement web (choix de Django déjà acté), bibliothèques de ML (choix de Scikit-learn déjà acté), bases de données, et outils de monitoring (choix de Prometheus/Grafana déjà acté). Cette étude se concentre sur les briques d'infrastructure et d'automatisation qui entourent le cœur de l'application.

---

## 3. Benchmark des Plateformes Cloud pour l'IA/ML

### 3.1. Introduction aux Plateformes ML dans le Cloud

Les fournisseurs de cloud public (AWS, Azure, GCP) offrent des suites de services de plus en plus sophistiquées, conçues pour gérer l'intégralité du cycle de vie du Machine Learning. Ces plateformes, souvent appelées "AI/ML Platforms-as-a-Service", permettent de préparer les données, d'entraîner, d'évaluer, de déployer et de surveiller des modèles à grande échelle. Bien que le développement initial du "CSV Analyzer" se fasse en local, une migration vers le cloud est une étape logique pour la mise en production. Anticiper ce choix est donc une démarche stratégique.

### 3.2. Analyse Détaillée : Amazon Web Services (AWS)

#### 3.2.1. Écosystème AI/ML d'AWS

AWS est le leader historique du marché du cloud. Son offre pour l'IA/ML est extrêmement vaste et s'articule principalement autour d'**Amazon SageMaker**, une plateforme entièrement gérée qui couvre tout le workflow ML. SageMaker inclut des fonctionnalités comme SageMaker Studio (un IDE web pour le ML), SageMaker Autopilot (AutoML), SageMaker Experiments (suivi), et SageMaker Model Monitor. Autour de SageMaker gravitent des services essentiels comme **Amazon S3** pour le stockage de données, **AWS Lambda** pour l'inférence serverless, et **AWS Step Functions** pour l'orchestration de pipelines.

#### 3.2.2. Forces et Avantages Stratégiques

*   **Maturité et Richesse Fonctionnelle :** L'offre d'AWS est la plus complète et la plus mature du marché.
*   **Écosystème Vaste :** Intégration native avec des centaines d'autres services AWS.
*   **Leader du Marché :** Une part de marché dominante qui se traduit par une immense communauté et une abondance de ressources et de compétences disponibles.

#### 3.2.3. Faiblesses et Défis Potentiels

*   **Complexité :** La pléthore de services et d'options peut être déroutante et conduire à une courbe d'apprentissage abrupte.
*   **Coûts :** Bien que flexible, la tarification peut rapidement devenir complexe à optimiser et les coûts peuvent s'envoler si la gestion n'est pas rigoureuse.
*   **Verrouillage Fournisseur (Vendor Lock-in) :** L'utilisation intensive de services managés comme SageMaker peut rendre une migration future vers un autre cloud plus difficile.

#### 3.2.4. Modèle de Tarification

La tarification est à l'usage (`pay-as-you-go`). Pour SageMaker, on paie séparément pour les instances de notebook, les instances d'entraînement, les instances de déploiement (inférence), etc. Le stockage sur S3 et le trafic réseau sont également facturés.

### 3.3. Analyse Détaillée : Microsoft Azure

#### 3.3.1. Écosystème Azure Machine Learning

L'offre de Microsoft s'articule autour d'**Azure Machine Learning (AzureML)**, une plateforme unifiée qui, à l'instar de SageMaker, vise à couvrir l'ensemble du cycle de vie. AzureML propose un studio web, des SDK Python et R, des capacités d'AutoML, un registre de modèles, et des options de déploiement variées (Azure Kubernetes Service, Azure Container Instances). AzureML se distingue par son intégration poussée avec l'écosystème Microsoft (Power BI, Dynamics 365) et des outils comme Visual Studio Code.

#### 3.3.2. Forces et Avantages Stratégiques

*   **Intégration Entreprise :** Excellent choix pour les entreprises déjà fortement investies dans l'écosystème Microsoft (Office 365, Active Directory).
*   **Approche Hybride :** De bonnes capacités pour les déploiements hybrides (cloud et on-premise) avec Azure Arc.
*   **ML Responsable :** Microsoft met un fort accent sur les outils de ML responsable (équité, interprétabilité).

#### 3.3.3. Faiblesses et Défis Potentiels

*   **Moins Mature sur l'Open Source :** Bien que de gros progrès aient été faits, l'intégration avec l'écosystème open-source est parfois perçue comme moins fluide que chez ses concurrents.
*   **Interface :** L'interface du portail Azure est parfois jugée moins intuitive que celle de GCP.

#### 3.3.4. Modèle de Tarification

Similaire à AWS, la tarification est à l'usage. On paie pour les ressources de calcul (VMs, clusters), le stockage, et les services additionnels. AzureML a un coût de service de base en plus des ressources de calcul consommées.

### 3.4. Analyse Détaillée : Google Cloud Platform (GCP)

#### 3.4.1. Écosystème AI Platform & Vertex AI

GCP a unifié son offre ML sous la bannière **Vertex AI**. Cette plateforme intègre les anciens services (AI Platform, AutoML) en une seule interface et API unifiées. Vertex AI couvre tout le spectre : préparation des données (Vertex AI Feature Store), entraînement (custom ou AutoML), prédiction, et monitoring. Le point fort historique de GCP est son expertise dans la gestion de la donnée à grande échelle (**BigQuery**) et son leadership dans l'écosystème Kubernetes (**GKE**), sur lequel Vertex AI s'appuie fortement.

#### 3.4.2. Forces et Avantages Stratégiques

*   **Leadership en IA et Données :** GCP bénéficie de l'expertise de Google en IA (créateur de TensorFlow, Kubernetes, etc.).
*   **Intégration Données :** L'intégration avec BigQuery est un différenciateur majeur pour les projets nécessitant des analyses de données complexes.
*   **Open Source :** Une forte culture open-source qui se traduit par une excellente gestion de technologies comme Kubernetes.

#### 3.4.3. Faiblesses et Défis Potentiels

*   **Part de Marché :** Historiquement en troisième position, ce qui peut signifier une communauté et un écosystème de partenaires légèrement plus restreints.
*   **Documentation :** Parfois perçue comme moins complète ou claire que celle de ses concurrents.

#### 3.4.4. Modèle de Tarification

Le modèle est également `pay-as-you-go`. Vertex AI facture séparément l'entraînement, la prédiction, le stockage, etc., avec des grilles tarifaires spécifiques pour les services AutoML.

### 3.5. Matrice de Comparaison et Recommandation

| Critère | AWS (SageMaker) | Azure (AzureML) | GCP (Vertex AI) |
| :--- | :--- | :--- | :--- |
| **Richesse Fonctionnelle** | 5/5 | 4/5 | 4.5/5 |
| **Facilité d'Utilisation** | 3/5 | 4/5 | 4/5 |
| **Intégration Open Source** | 4/5 | 3.5/5 | 5/5 |
| **Maturité & Communauté** | 5/5 | 4/5 | 4/5 |
| **Leadership Données/IA** | 4/5 | 4/5 | 5/5 |
| **Coût (Flexibilité)** | 4/5 | 4/5 | 4/5 |
| **Score Total** | **25/30** | **23.5/30** | **26.5/30** |

**Recommandation (pour une future migration) :** **GCP (Vertex AI)**

**Justification :** Pour un projet comme "CSV Analyzer" qui est centré sur la donnée et le ML, l'expertise de GCP et l'excellence de ses services de données (BigQuery) et d'orchestration (GKE/Vertex AI) en font un choix très pertinent. L'approche unifiée de Vertex AI est également très attractive. Cependant, il est important de noter que les trois plateformes sont extrêmement capables. Le choix final pourra aussi dépendre d'opportunités spécifiques (crédits gratuits, compétences existantes de l'équipe).

---

## 4. Benchmark des Outils MLOps

### 4.1. L'Importance Stratégique du MLOps

Le MLOps (Machine Learning Operations) est au Machine Learning ce que le DevOps est au développement logiciel. C'est une discipline qui vise à industrialiser et automatiser le cycle de vie des modèles de ML, de l'expérimentation au monitoring en production. Pour "CSV Analyzer", où les utilisateurs entraînent de nombreux modèles, un outil MLOps est indispensable pour assurer la traçabilité, la reproductibilité et la gouvernance des modèles créés.

### 4.2. Analyse Détaillée : MLflow

#### 4.2.1. Composants et Architecture

MLflow est une plateforme open-source qui se décompose en quatre composants principaux :
*   **MLflow Tracking :** Permet d'enregistrer et de requêter les paramètres, les métriques, le code et les artefacts de chaque exécution d'entraînement.
*   **MLflow Projects :** Un format standard pour packager le code de ML de manière réutilisable et reproductible.
*   **MLflow Models :** Un format de packaging de modèles qui permet de les déployer sur diverses plateformes (inférence batch, API REST, etc.).
*   **MLflow Model Registry :** Un magasin centralisé pour gérer le cycle de vie complet d'un modèle (versions, passage en production, archivage).

#### 4.2.2. Forces et Avantages Stratégiques

*   **Simplicité et Flexibilité :** Extrêmement facile à intégrer dans un code existant. On peut utiliser uniquement les composants dont on a besoin.
*   **Agnostique :** Fonctionne avec n'importe quelle bibliothèque de ML (Scikit-learn, TensorFlow, etc.), n'importe quel langage (Python, R, Java) et n'importe où (local, cloud).
*   **Open Source et Soutenu par Databricks :** Bénéficie d'une communauté active et du soutien d'une entreprise majeure de la data.

#### 4.2.3. Faiblesses et Limitations

*   **Pas d'Orchestration Native :** MLflow ne fournit pas d'outil pour orchestrer des pipelines de ML complexes. Il doit être couplé avec un autre outil comme Airflow ou AWS Step Functions pour cela.
*   **Gestion des Données :** Ne gère pas directement le versioning des jeux de données.

### 4.3. Analyse Détaillée : Kubeflow

#### 4.3.1. Composants et Architecture

Kubeflow est "la boîte à outils ML pour Kubernetes". C'est une plateforme beaucoup plus ambitieuse et complète que MLflow, qui vise à fournir une solution de bout en bout pour le ML sur Kubernetes. Ses composants principaux incluent :
*   **Kubeflow Pipelines :** Un outil puissant pour construire et orchestrer des pipelines de ML complexes et portables.
*   **Katib :** Un service pour l'optimisation d'hyperparamètres et la recherche d'architecture neuronale (NAS).
*   **KServe (anciennement KFServing) :** Un framework pour le déploiement de modèles à grande échelle sur Kubernetes.

#### 4.3.2. Forces et Avantages Stratégiques

*   **Scalabilité et Portabilité :** En s'appuyant sur Kubernetes, Kubeflow offre une scalabilité quasi-infinie et une portabilité sur n'importe quel cloud ou infrastructure on-premise.
*   **Solution Complète :** Vise à couvrir tous les aspects du MLOps, de l'orchestration au serving.

#### 4.3.3. Faiblesses et Complexité de Mise en Œuvre

*   **Complexité Extrême :** La mise en place et la maintenance de Kubeflow sont très complexes et nécessitent une expertise solide de Kubernetes.
*   **Surdimensionné :** Pour des projets de petite ou moyenne taille, Kubeflow est souvent une solution trop lourde ("utiliser un marteau-pilon pour écraser une mouche").

### 4.4. Analyse Détaillée : DVC (Data Version Control)

#### 4.4.1. Concepts et Workflow

DVC est un outil open-source qui apporte les concepts de Git (versioning, branches, etc.) aux données et aux modèles de ML. Il ne stocke pas les gros fichiers de données dans Git, mais plutôt des métafichiers légers qui pointent vers les données stockées dans un stockage externe (S3, GCS, HDFS, ou même un disque local). Il permet de créer des pipelines de données reproductibles (fichiers `dvc.yaml`).

#### 4.4.2. Forces et Avantages Stratégiques

*   **Reproductibilité :** Permet de lier de manière immuable une version du code (Git), une version des données (DVC) et un modèle.
*   **Workflow Intuitif pour les Développeurs :** L'utilisation de concepts Git le rend très familier.
*   **Agnostique au Stockage :** Fonctionne avec une multitude de backends de stockage.

#### 4.4.3. Faiblesses et Positionnement

*   **Pas une Plateforme MLOps Complète :** DVC se concentre sur le versioning et les pipelines. Il lui manque une interface utilisateur pour le suivi des expériences comme celle de MLflow. DVC et MLflow sont d'ailleurs souvent utilisés ensemble et sont plus complémentaires que concurrents.

##### 4.5. Matrice de Comparaison et Recommandation

| Critère | MLflow | Kubeflow | DVC |
| :--- | :--- | :--- | :--- |
| **Périmètre Fonctionnel** | Suivi, Packaging, Registre | Orchestration, Serving, AutoML | Versioning Données/Modèles, Pipelines |
| **Complexité** | Faible | Très Élevée | Faible à Moyenne |
| **Dépendances** | Python, Stockage | Kubernetes | Git, Stockage |
| **UI de Suivi** | Oui | Oui (via Pipelines) | Non |
| **Adaptation au Projet** | 5/5 | 2/5 | 3/5 |
| **Score Total** | **25/30** | **17/30** | **19/30** |

**Recommandation Finale MLOps :** **MLflow** est l'outil le plus adapté pour débuter, tout en laissant la porte ouverte à Kubeflow si la charge et la complexité augmentent fortement.

---

## 5. Benchmark des Solutions de CI/CD

### 5.1. Le Rôle de la CI/CD dans le MLOps

La CI/CD garantit que chaque mise à jour de code, de données ou de modèle est automatiquement testée et déployée. Pour "CSV Analyzer", cela signifie : exécuter les tests unitaires Django et les tests ML, construire l'image Docker, pousser sur Docker Hub et déployer sur le serveur cible.

### 5.2. Analyse Détaillée : GitHub Actions

* **Intégration native** avec GitHub, déclencheurs simples (`push`, `pull_request`).
* **Marketplace riche** d'actions prêtes à l'emploi (Docker, Python, MLflow).
* **Plan gratuit** généreux pour les dépôts open-source.

### 5.3. Analyse Détaillée : Jenkins

* **Historique** et extensible via des plugins.
* Nécessite **maintenance** d'un serveur Jenkins et gestion des mises à jour.
* DSL (Pipeline) puissant mais courbe d'apprentissage plus raide.

### 5.4. Analyse Détaillée : GitLab CI/CD

* **Intégré** à GitLab, syntaxe YAML similaire à GitHub Actions.
* Bons **runners** partagés gratuits mais limites plus strictes.
* Meilleure **intégration sécurité** (SAST, DAST) native.

### 5.5. Matrice de Comparaison et Recommandation

| Critère | GitHub Actions | Jenkins | GitLab CI/CD |
| :--- | :--- | :--- | :--- |
| **SaaS/On-prem** | SaaS | On-prem | SaaS/On-prem |
| **Facilité Mise en Place** | 5/5 | 3/5 | 4/5 |
| **Maintenance** | 5/5 | 2/5 | 4/5 |
| **Coût** | 5/5 | 4/5 | 4/5 |
| **Intégration Docker** | 5/5 | 5/5 | 5/5 |
| **Score Total** | **25/25** | **19/25** | **21/25** |

**Recommandation CI/CD :** **GitHub Actions** pour son intégration directe, zéro maintenance et gratuité.

---

## 6. Synthèse des Recommandations et Stack Technologique Finale

| Domaine | Outil Recommandé | Raison Principale |
| :--- | :--- | :--- |
| Cloud AI/ML | GCP – Vertex AI | Expertise données/IA & BigQuery |
| MLOps | MLflow | Simplicité, agnostique, UI   |
| CI/CD | GitHub Actions | Intégration native & gratuit |
| Monitoring | Prometheus / Grafana | Stack open-source éprouvée |

Cette stack offre un **time-to-market rapide**, des coûts contrôlés et une **évolutivité** vers des besoins plus complexes.

### 6.1. Trajectoire d'Évolution

1. **Phase 1 – Local & Docker :** Développement et tests sur environnements locaux.
2. **Phase 2 – CI/CD Automatisée :** Pipelines GitHub Actions pour tests, build et push Docker.
3. **Phase 3 – Cloud & Scalabilité :** Migration progressive vers GCP (Vertex AI + GKE) si la charge utilisateur l’exige.

---

## 7. Glossaire

* **MLOps :** Ensemble de pratiques combinant Machine Learning et DevOps.
* **AutoML :** Techniques automatisant la sélection et l’entraînement de modèles.
* **CI/CD :** Intégration et déploiement continus.

---

## 8. Références

1. Documentation officielle MLflow, Kubeflow, DVC.
2. Whitepapers AWS SageMaker, AzureML, GCP Vertex AI.
3. Guides GitHub Actions & GitLab CI/CD.
4. Articles techniques et retours d’expérience disponibles sur Medium & Towards Data Science.

---

<!-- FIN DU DOCUMENT -->