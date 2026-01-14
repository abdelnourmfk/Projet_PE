Projet 19 (C) — Livrables

Ce répertoire contient tous les artefacts livrables pour le projet « Détection DDoS (SYN flood) ». Voici les fichiers fournis et leur rôle :

- models/final_model.pkl — Modèle entraîné (IsolationForest) à utiliser pour la détection.
- outputs/sample_alerts.json — Exemple d'alertes JSON (une alerte par ligne) générées par le pipeline.
- data/final_features.csv — Jeu de caractéristiques généré pour l'entraînement final.
- notebooks/demo.ipynb — Notebook de démonstration du pipeline.
- src/ — Code source (génération, extraction de features, entraînement, détection).
- tests/ — Suite de tests automatisés (pytest).
- .github/workflows/ci.yml — CI (GitHub Actions) pour tests.
- README.md — Guide d'installation et d'usage.
- REPORT.md — Rapport technique (méthodologie, métriques, limites).

Usage rapide
1) Installer dépendances: see `README.md`.
2) Pour re-générer le modèle final:
   python -m src.build_final_model
3) Pour recréer le fichier d'alertes d'exemple:
   python -m src.generate_sample_alerts
4) Pour créer l'archive de livraison:
   python scripts/package_deliverables.py

Notes
- Les données sont synthétiques; adaptez la génération si vous fournissez des pcaps réels.
- Le modèle est léger et conçu pour être exécutable sur hôtes avec ressources limitées.
