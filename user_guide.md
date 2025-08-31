# Guide Utilisateur – CSV Analyzer

## 1. Pré-requis
- Navigateur Web moderne (Chrome / Firefox).
- Compte utilisateur créé par l’administrateur ou auto-inscription.

## 2. Lancement de l’application (local)
```bash
# clone & démarrage
$ git clone <repo>
$ cd csv_analyzer
$ docker-compose up --build
```
L’interface est accessible sur http://localhost:8000/.

## 3. Parcours fonctionnels
| Étape | Action | Capture d’écran |
|-------|--------|-----------------|
| 1 | Page d’accueil → « Upload CSV » | ![upload](images/upload.png) |
| 2 | Sélection du fichier puis « Valider » | |
| 3 | Visualisation tabulaire + statistiques qualité | |
| 4 | Choix de la cible et lancement AutoML | |
| 5 | Affichage des métriques (F1 / RMSE) | |
| 6 | Section « Predict » pour tester une ligne | |

## 4. API REST
La documentation interactive Swagger est disponible sur http://localhost:8000/api/docs/ après démarrage.

## 5. Monitoring
- Grafana : http://localhost:3000/ (admin/admin)
- Prometheus : http://localhost:9090/

## 6. Résolution d’incidents rapide
| Problème | Diagnostic | Correctif |
|----------|-----------|-----------|
| Erreur 500 après upload | Consulter logs container `web` | Vérifier format CSV, redémarrer service |
| Modèle non entraîné | Check onglet MLflow | Relancer AutoML |

---