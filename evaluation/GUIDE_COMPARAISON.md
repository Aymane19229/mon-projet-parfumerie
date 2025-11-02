# 🔬 Guide de Comparaison des Modèles LLM

## 🎯 Objectif

Comparer les performances de **DeepSeek R1** et **LLaMA 3** pour générer des politiques de sécurité conformes NIST CSF et ISO 27001.

## 📋 Processus de Comparaison

### Étape 1 : Génération des Politiques

Générer les mêmes politiques avec les deux modèles :

```bash
# Option 1 : Utiliser le script de comparaison automatique
python3 llm/compare_models.py parser/reports/normalized_vulnerabilities.json

# Option 2 : Générer manuellement
# DeepSeek R1
python3 llm/policy_generator.py parser/reports/normalized_vulnerabilities.json deepseek deepseek-chat

# LLaMA 3 (Hugging Face)
python3 llm/policy_generator.py parser/reports/normalized_vulnerabilities.json huggingface meta-llama/Meta-Llama-3-8B-Instruct
```

### Étape 2 : Organisation des Politiques

Les politiques doivent être organisées ainsi :

```
llm/policies/
├── deepseek/
│   ├── nist_csf/
│   │   └── PROTECT.txt
│   └── iso27001/
│       └── A.9.2.1.txt
└── llama3/
    ├── nist_csf/
    │   └── PROTECT.txt
    └── iso27001/
        └── A.9.2.1.txt
```

### Étape 3 : Évaluation

Exécuter l'évaluateur :

```bash
python3 evaluation/evaluator.py
```

### Étape 4 : Consulter les Résultats

Le rapport est généré dans `evaluation/evaluation_report.json` et affiché dans le terminal.

## 📊 Métriques Comparées

### BLEU Score
- Mesure la similarité n-gram avec les références
- Plus élevé = meilleur vocabulaire et structure

### ROUGE-L F-Score
- Mesure le recouvrement des idées principales
- Plus élevé = meilleure couverture des concepts

### ROUGE-L Precision
- Combien du texte généré est pertinent

### ROUGE-L Recall
- Combien des références est couvert

## 🏆 Détermination du Meilleur Modèle

L'évaluateur compare automatiquement et détermine le meilleur modèle basé sur :
1. **Score BLEU moyen** (principal critère)
2. **Score ROUGE-L F moyen** (critère secondaire)
3. **Nombre de politiques générées** (complétude)

## 📝 Exemple de Sortie

```
📊 COMPARAISON DES MODÈLES LLM
======================================================================

Modèle               BLEU       ROUGE-L F    ROUGE-L P    ROUGE-L R    Politiques
----------------------------------------------------------------------
DEEPSEEK             0.4523     0.6234       0.5891       0.6587       10
LLAMA3               0.3891     0.5678       0.5213       0.6156       10

======================================================================

🏆 MEILLEUR MODÈLE: DEEPSEEK
   BLEU Score: 0.4523
   ROUGE-L F-Score: 0.6234
======================================================================
```

## 💡 Interprétation

- **Différence > 0.05** : Modèle significativement meilleur
- **Différence < 0.05** : Modèles équivalents (choix selon autres critères)
- **DeepSeek généralement plus rapide** : API plus performante
- **LLaMA 3 gratuit** : Mais nécessite permissions Hugging Face

## 🔍 Analyse Approfondie

Pour une analyse plus détaillée :

1. **Lire le rapport JSON** : `evaluation/evaluation_report.json`
2. **Comparer politique par politique** : Voir les scores individuels
3. **Analyser les différences qualitatives** : Lire les politiques générées
4. **Considérer les coûts** : DeepSeek ~0.55$/1M tokens vs LLaMA gratuit

## ✅ Résultat Final

À la fin, vous aurez :
- ✅ Politiques générées par les deux modèles
- ✅ Scores d'évaluation BLEU et ROUGE-L
- ✅ Détermination du meilleur modèle
- ✅ Rapport JSON pour documentation

