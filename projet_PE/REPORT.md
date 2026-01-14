# Rapport technique — Projet 19 (C) (version française détaillée)

## 1. Contexte & objectif
L'objectif du projet est de démontrer une chaîne de détection légère d'attaques SYN flood (DDoS) en temps proche du temps réel en se basant sur des features simples extraites de trafic réseau agrégé par fenêtres temporelles (par défaut 1s). Le système doit être reproductible, testable et documenté pour permettre des expérimentations supplémentaires.

## 2. Données & génération
- Les jeux de données sont synthétiques, générés par `src/traffic_gen.py`.
- Scénarios : trafic normal et fenêtres d'attaque (exemple `syn_single_src`, `syn_many_src`).
- Les données brutes sont transformées en features par `src/features.py` (débit, entropie, ratio SYN, etc.).

## 3. Features
Features calculées par fenêtre (exemples):
- `packets_per_sec` — paquets par seconde
- `bytes_per_sec` — octets par seconde
- `entropy_src_ip` / `entropy_dst_ip` — entropie des adresses IP
- `syn_ratio` — proportion de paquets SYN
- `ts_start` — timestamp de début de la fenêtre (en epoch seconds)

## 4. Modèle & entraînement
- Modèle utilisé : `IsolationForest` (sklearn) — rapide et léger pour la détection d’anomalies.
- Entraînement sur données « normales » simulées.
- Sauvegarde du modèle : `models/model.pkl` (et `models/final_model.pkl` pour la version finale).
- Commande : `python -m src.train_model` ou `python -m src.build_final_model` pour construire le modèle final.

## 5. Détection & sorties
- Détection : `src/detect.py` charge le modèle, prédit sur features et écrit les alertes en JSON lines (une alerte par fenêtre anormale détectée).
- Format d'une alerte :
  - `timestamp` (ISO RFC3339 Z), `alert_id`, `score`, `verdict`, `features`, `explanation`.
- Exemples de fichiers de sortie : `outputs/alerts.json`, `outputs/sample_alerts.json`.

## 6. Évaluation
- Tests unitaires fournis dans `projet_PE/tests/` couvrent:
  - génération de trafic, extraction de features, entraînement, détection
  - smoke tests pour l'UI Streamlit
- Mesures reportées (sur données synthétiques) : TPR élevé pour les scénarios testés (ex: TPR=100% sur `syn_single_src` dans le test unitaire). Ces résultats restent indicatifs et spécifiques aux traces générées.

## 7. Limitations
- Données synthétiques : performances réelles peuvent varier
- Pas de normalisation robuste inter-traces (StandardScaler recommandé)
- Hyperparamètres (notamment `contamination`) à ajuster pour équilibre TPR/FPR
- UI basique (auth, validation d'input et E2E tests manquants)

## 8. Reproductibilité & commandes utiles
1. Installer dépendances : `python -m pip install -r projet_PE/requirements.txt`
2. Lancer la démo complète : `python run_demo.py`
3. Lancer l'UI Streamlit : `streamlit run projet_PE/ui/streamlit_app.py` ou `python scripts/run_streamlit.py`
4. Exécuter les tests : `python -m pytest projet_PE/tests -q`

## 9. Améliorations futures recommandées
- Normalisation et pipeline `scikit-learn` (Pipeline + GridSearchCV)
- Évaluation sur traces réelles et scénarios variés
- Ajout d’alertes enrichies (contexte, corrélation multi-fenêtres)
- Tests E2E et packaging pour distribution

## 10. Conclusion
Ce projet fournit une base reproductible pour expérimenter la détection de SYN flood en utilisant des techniques d’anomalie non supervisée. Le code est modulaire et documenté pour faciliter extensions et évaluations plus poussées.
