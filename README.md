[![CI](https://github.com/<OWNER>/<REPO>/actions/workflows/ci.yml/badge.svg)](https://github.com/<OWNER>/<REPO>/actions)

# Projet 19 (C) — Détection DDoS (SYN flood) via IA légère 🇫🇷

**Résumé (français)**

Ce dépôt contient une démonstration complète d'un pipeline léger de détection de SYN flood (attaque DDoS) basé sur un modèle IsolationForest. Le projet fournit des outils pour générer du trafic synthétique, extraire des features, entraîner un modèle, exécuter la détection et visualiser les alertes via une interface web minimaliste (Streamlit).

---

## 🔍 Fonctionnalités principales
- Génération de traces synthétiques (trafic normal + attaques) — `src/traffic_gen.py` 🧪
- Extraction de features par fenêtre temporelle (1s) — `src/features.py` 📊
- Entraînement d'un modèle IsolationForest et sauvegarde (`models/model.pkl`) — `src/train_model.py` 🤖
- Détection d'anomalies et écriture d'alertes (JSON lignes) — `src/detect.py` ⚠️
- Interface web interactive (Streamlit) pour charger des features, lancer la détection et visualiser/télécharger les alertes — `projet_PE/ui/streamlit_app.py` 🌐

---

## 🚀 Installation rapide
1. Créez un environnement virtuel et activez‑le :

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1   # PowerShell
# ou .\.venv\Scripts\activate.bat pour CMD
```

2. Installez les dépendances :

```powershell
python -m pip install -r projet_PE/requirements.txt
```

> Note : `requirements.txt` inclut `streamlit` et (optionnel) `altair` pour des graphiques interactifs.

---

## ▶️ Exemples d'utilisation (quickstart)
- Lancer la démo complète (génère trafic, entraîne un modèle, exécute la détection) :

```powershell
python run_demo.py
```

- Lancer l'UI Streamlit :

```powershell
streamlit run projet_PE/ui/streamlit_app.py
# ou: python scripts/run_streamlit.py
# ou (Windows) double-cliquer: run_streamlit.bat
```

> L'interface est accessible par défaut sur `http://localhost:8501`.

**Validation automatique des entrées** : l'UI vérifie que le fichier contient les colonnes obligatoires (`packets_per_sec`, `bytes_per_sec`, `entropy_src_ip`, `entropy_dst_ip`, `syn_ratio`, `ts_start`), que les types sont numériques quand attendu et qu'il y a au moins une ligne. En cas d'erreur, des messages clairs sont affichés pour vous guider.

**Authentification simple** : vous pouvez définir la variable d'environnement `STREAMLIT_UI_PASSWORD` pour protéger l'accès à l'UI. Si la variable n'est pas définie, l'UI reste accessible localement sans mot de passe (pratique pour développement). Exemple (PowerShell): `setx STREAMLIT_UI_PASSWORD "mon_mdp"`.

**Exécution en arrière-plan** : pour traitement long, l'UI permet de lancer la détection en arrière-plan (bouton "Start detection in background") et d'afficher le statut d'exécution. Le mécanisme est simple (threading) et destiné aux usages locaux; pour charge production, envisagez un worker/queue (celery, RQ, etc.).

---

## 📁 Structure & fichiers clés
- `data/` : jeux de données d'exemple (CSV)
- `projet_PE/ui/streamlit_app.py` : interface utilisateur pour la détection et visualisation
- `src/traffic_gen.py` : génération de trafic synthétique
- `src/features.py` : extraction d’attributs par fenêtre
- `src/train_model.py` : entraînement (IsolationForest)
- `src/detect.py` : détection et écriture d'alertes (JSON lines)
- `models/` : modèles sauvegardés (`model.pkl`, `final_model.pkl`)
- `outputs/` : alertes produites (`alerts.json`, `sample_alerts.json`)
- `scripts/run_streamlit.py` et `run_streamlit.bat` : helpers pour lancer l'UI
- `projet_PE/tests/` : tests unitaires et smoke tests

---

## ℹ️ Détails techniques (comment ça marche)
- Features utilisées : `packets_per_sec`, `bytes_per_sec`, `entropy_src_ip`, `entropy_dst_ip`, `syn_ratio` (calculées par fenêtre) 🔢
- Modèle : `IsolationForest` (sklearn) entraîné sur trafic normal. Prédictions : `-1` = anomalie, `1` = normal.
- Alertes : sorties en JSON lines avec `timestamp` (format RFC3339 Z), `alert_id`, `score`, `verdict`, `features`, `explanation`.

---

## ✅ Résultats & tests
- Objectif de démonstration : atteindre TPR >= 85% sur tests synthétiques.
- Tests automatisés : `python -m pytest projet_PE/tests -q` (contient des tests sur la pipeline et imports UI).

---

## 📦 Packaging & livrables
- `scripts/package_deliverables.py` crée `deliverables.zip` contenant le modèle et les exemples.

---

## 🛠️ Bonnes pratiques et améliorations possibles
- Ajouter normalisation (`StandardScaler`) pour robustesse multi‑environnements
- Évaluer sur traces réelles (pcap) et différentes variantes d'attaques
- Ajouter authentification sur l'UI pour usage partagé
- Ajouter tests E2E pour l'UI

---

## Contact
Pour toute question, ouvrez une issue ou contactez le mainteneur du projet.

---

*(Version française détaillée ajoutée automatiquement — le README original en anglais est conservé dans le commit historique.)*
