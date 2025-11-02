# 🔒 DevSecOps - Génération Automatique de Politiques de Sécurité avec IA

## 🎯 Objectif

Transformer automatiquement les rapports techniques de vulnérabilités (SAST, SCA, DAST) en **politiques de sécurité conformes** aux standards internationaux (NIST CSF, ISO/IEC 27001) en utilisant des **Large Language Models (LLMs)**.

## 🏗️ Architecture

```
Pipeline CI/CD → Rapports Vulnérabilités → Parser → LLM → Politiques Conformes → Évaluation
```

### Composants

1. **Pipeline CI/CD** (`.github/workflows/devsecops-pipeline.yml`)
   - SAST : SpotBugs (Java) + ESLint (JavaScript)
   - SCA : OWASP Dependency-Check + npm audit
   - DAST : OWASP ZAP

2. **Parser** (`parser/`)
   - Normalisation des rapports XML/JSON en format standardisé
   - Support SAST, SCA, DAST

3. **Génération LLM** (`llm/`)
   - DeepSeek R1 (recommandé) ou LLaMA 3
   - Génération de politiques NIST CSF et ISO 27001

4. **Évaluation** (`evaluation/`)
   - Métriques BLEU et ROUGE-L
   - Comparaison des modèles LLM

## 🚀 Démarrage Rapide

### 1. Configuration

```bash
# Installer les dépendances
pip3 install --user --break-system-packages openai requests python-dotenv

# Configurer les clés API (llm/.env)
DEEPSEEK_API_KEY=sk-...
HUGGINGFACE_API_KEY=hf_...
```

### 2. Exécution

```bash
# 1. Parser les vulnérabilités
python3 parser/main_parser.py

# 2. Générer des politiques
python3 llm/policy_generator.py

# 3. Comparer les modèles (optionnel)
python3 llm/compare_models.py parser/reports/normalized_vulnerabilities.json

# 4. Évaluer les politiques
python3 evaluation/evaluator.py
```

## 📁 Structure du Projet

```
mon-projet-parfumerie/
├── .github/workflows/
│   └── devsecops-pipeline.yml    # Pipeline CI/CD
├── parser/                        # Parser de vulnérabilités
│   ├── main_parser.py
│   └── parsers/
├── llm/                          # Génération de politiques
│   ├── policy_generator.py
│   ├── models/                   # DeepSeek, HuggingFace
│   └── prompts/                   # Prompts NIST/ISO
├── evaluation/                    # Évaluation BLEU/ROUGE-L
│   ├── evaluator.py
│   └── reference_policies/
└── backend/ & frontend/           # Application e-commerce
```

## 📚 Documentation

- **Pipeline** : `DEVSECOPS.md`
- **SAST/SCA/DAST** : `GUIDE_SAST_SCA_DAST.md`
- **LLM** : `llm/README.md`, `llm/USAGE.md`, `llm/DEEPSEEK_SETUP.md`
- **Évaluation** : `evaluation/README.md`, `evaluation/GUIDE_COMPARAISON.md`

## 🔧 Configuration LLM

### DeepSeek R1 (Recommandé)
- Modèle par défaut
- Économique (0.55$/1M tokens)
- Configuration : `llm/DEEPSEEK_SETUP.md`

### LLaMA 3 (Hugging Face)
- Gratuit via API
- Configuration : `llm/USAGE.md`

## 📊 Évaluation

Les politiques générées sont évaluées avec :
- **BLEU Score** : Similarité avec les références
- **ROUGE-L** : Recouvrement des idées principales

Rapport généré : `evaluation/evaluation_report.json`

## 🎓 Technologies

- **CI/CD** : GitHub Actions
- **SAST** : SpotBugs, ESLint
- **SCA** : OWASP Dependency-Check, npm audit
- **DAST** : OWASP ZAP
- **LLM** : DeepSeek R1, LLaMA 3 (Hugging Face)
- **Évaluation** : BLEU, ROUGE-L (implémentation Python)

## 📝 Licence

Ce projet est développé dans le cadre d'un projet académique DevSecOps.

## 👥 Auteurs

Équipe DevSecOps - Intégration de l'IA Générative dans DevSecOps

