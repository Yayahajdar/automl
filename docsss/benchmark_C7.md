# Étude de Benchmark pour la compétence C7 – Identification de services d’IA prêts à l’emploi

## 1. Reformulation du besoin
Le projet doit **identifier un service d’intelligence artificielle pré-entraîné** capable d’être intégré rapidement afin de classer ou d’extraire des informations depuis des fichiers CSV, en respectant les contraintes suivantes :
- Intégration simple via REST ou SDK Python.
- Conformité aux exigences de **protection des données** (RGPD) et à la politique interne de l’entreprise.
- Coût d’exploitation contenu, avec possibilité de déploiement on-premise si nécessaire.
- Impact environnemental maîtrisé ; priorité aux fournisseurs engagés dans la réduction des émissions carbone.

## 2. Méthodologie de sélection
1. Constitution d’une liste initiale de services IA (cloud et open source).
2. Définition de critères d’évaluation (pertinence technique, coût, performance, confidentialité, impact environnemental).
3. Classement des services en « étudiés » et « non étudiés » selon leur adéquation aux critères essentiels (API claire, documentation à jour, modèle adapté).
4. Analyse approfondie des services retenus et élaboration de recommandations.

## 3. Services étudiés
| Service | Fonction principale | Points forts | Points faibles | Pertinence | Considérations environnementales |
|---------|--------------------|-------------|---------------|------------|----------------------------------|
| **Google Cloud AutoML Tables** | Création automatique de modèles tabulaires. | Intégration BigQuery, bonnes performances. | Données hors UE par défaut, coût d’entraînement élevé. | **Moyenne** – nécessite paramétrage RGPD. | Data centers Google >90 % énergie renouvelable. |
| **Amazon SageMaker JumpStart** | Modèles prêts au déploiement. | Support Docker & MLflow, scalabilité. | Facturation complexe, transfert de données vers AWS. | **Moyenne** – pertinent si l’infra est déjà sur AWS. | Engagement carbone net 0 d’ici 2030. |
| **Microsoft Azure AutoML** | Exploration automatisée de modèles tabulaires. | GUI + SDK complet, intégration Power BI. | Abonnement requis, prix variables. | **Élevée** – si le client utilise Azure. | Azure vise la neutralité carbone 2025. |
| **Hugging Face Inference API** | Hébergement de modèles Transformers. | Communauté large, coûts réduits, open source. | Principalement NLP ; nécessite adaptation tabulaire. | **Faible** – pas ciblé CSV. | Possible auto-hébergement sur serveurs verts. |
| **OpenAI API** | GPT-x pour analyse de texte. | Grande précision, flexibilité. | Coût au token, données envoyées aux serveurs OpenAI. | **Faible** – non orienté données tabulaires. | Source énergétique des data centers non détaillée. |
| **MLflow Models (auto-hébergé)** | Gestion et déploiement local de modèles. | Contrôle total des données, open source. | Besoin d’une infra DevOps. | **Élevée** – compatible avec l’architecture existante. | Impact dépend du serveur ; choisir hébergement bas carbone. |

## 4. Services non étudiés et justification
| Service | Motif d’exclusion |
|---------|------------------|
| **IBM Watson Studio** | Tarification complexe, disponibilité régionale limitée. |
| **DataRobot AutoML** | Licence propriétaire coûteuse, dépasse le budget. |
| **RapidMiner** | Ciblé enseignement, intégration API limitée. |

## 5. Analyse de pertinence détaillée
- **Pertinence technique** : Azure AutoML et MLflow auto-hébergé sont les plus alignés avec l’écosystème Django / MLflow actuel.
- **Coût** : MLflow auto-hébergé est le moins onéreux si un serveur est déjà disponible.
- **Confidentialité** : MLflow > Azure (zone UE) > Google / Amazon.
- **Impact environnemental** : privilégier un serveur local alimenté en énergie renouvelable ou des régions cloud à faible intensité carbone.

## 6. Approche environnementale (Green IT)
- Déployer dans des régions alimentées par de l’énergie renouvelable (ex. : `europe-west1-B` sur GCP).
- Mettre en place l’arrêt automatique des ressources inactives.
- Surveiller l’utilisation CPU/GPU afin de réduire le gaspillage énergétique.

## 7. Recommandations
1. **Tester Azure AutoML** en sandbox sur un échantillon de données.
2. Monter un **PoC** MLflow auto-hébergé sous Docker sur un serveur bas carbone.
3. Comparer précision, coût et émissions CO₂ avant décision d’intégration.

## 8. Références
- Rapports de durabilité Google, AWS, Azure.
- Documentation MLflow 1.30.
- Articles Hugging Face sur l’hébergement de modèles.