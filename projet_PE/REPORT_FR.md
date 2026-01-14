# Rapport d'utilisation & reproduction (FR)

Ce document complète le `README.md` et donne pas à pas comment reproduire les étapes principales : génération, entraînement, détection et visualisation.

## 1. Pré-requis
- Python 3.10+ (recommandé)
- Environnement virtuel (venv)

## 2. Installation
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r projet_PE/requirements.txt
```

## 3. Générer une trace d'exemple et extraire des features
```powershell
python -m src.generate_sample_alerts
# écrit dans data/sample_test.csv et outputs/sample_alerts.json
```

## 4. Entraîner un modèle
```powershell
python -m src.build_final_model
# écrit models/final_model.pkl
```

## 5. Lancer l'UI pour tester manuellement
```powershell
streamlit run projet_PE/ui/streamlit_app.py
# ou python scripts/run_streamlit.py
```

## 6. Exécuter les tests automatisés
```powershell
python -m pytest projet_PE/tests -q
```

## 7. Notes pour les évaluations
- Comparez TPR/FPR en variant : type d'attaque, durée, débit, contamination param.
- Utilisez `notebooks/demo.ipynb` pour visualisations et analyses interactives.

---

*Fin du rapport FR — modifiez selon vos besoins projet.*