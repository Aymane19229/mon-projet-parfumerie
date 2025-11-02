# 📊 Module d'Évaluation - BLEU & ROUGE-L

## 🎯 Objectif

Évaluer la qualité des politiques générées par les LLMs en les comparant avec des politiques de référence utilisant les métriques **BLEU** et **ROUGE-L**.

## 🔍 Métriques Utilisées

### BLEU Score
- **Quoi** : Mesure la similarité n-gram entre le texte généré et les références
- **Pourquoi** : Indique si le texte généré utilise un vocabulaire et des phrases similaires aux références
- **Gamme** : 0 (complètement différent) à 1 (identique)

### ROUGE-L Score
- **Quoi** : Mesure le recouvrement basé sur la plus longue sous-séquence commune (LCS)
- **Pourquoi** : Indique si les idées principales sont présentes dans le texte généré
- **Composantes** :
  - **F-Score** : Moyenne harmonique de précision et rappel
  - **Precision** : Combien du texte généré est pertinent
  - **Recall** : Combien des références est couvert

## 📁 Structure

```
evaluation/
├── bleu_rouge.py              # Implémentation BLEU et ROUGE-L
├── evaluator.py               # Évaluateur principal
├── reference_policies/        # Politiques de référence
│   ├── nist_csf/             # Références NIST CSF
│   └── iso27001/             # Références ISO 27001
├── evaluation_report.json     # Rapport généré
└── README.md                  # Ce fichier
```

## 🚀 Utilisation

### 1. Préparer les Politiques de Référence

Créez des fichiers `.txt` dans `evaluation/reference_policies/` :

**NIST CSF** :
```
evaluation/reference_policies/nist_csf/PROTECT_1.txt
evaluation/reference_policies/nist_csf/IDENTIFY_1.txt
```

**ISO 27001** :
```
evaluation/reference_policies/iso27001/A.9.2.1.txt
evaluation/reference_policies/iso27001/A.12.6.1.txt
```

### 2. Organiser les Politiques Générées

Les politiques générées doivent être organisées par modèle LLM :

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

### 3. Exécuter l'Évaluation

```bash
cd mon-projet-parfumerie
python3 evaluation/evaluator.py
```

### 4. Consulter les Résultats

Le rapport est généré dans `evaluation/evaluation_report.json` et affiché dans le terminal.

## 📊 Interprétation des Scores

- **BLEU > 0.3** : Bonne similarité avec les références
- **BLEU > 0.5** : Très bonne similarité
- **BLEU > 0.7** : Excellent (presque identique)

- **ROUGE-L F > 0.4** : Bon recouvrement des idées
- **ROUGE-L F > 0.6** : Très bon recouvrement
- **ROUGE-L F > 0.8** : Excellent recouvrement

## 🔄 Comparaison de Modèles

L'évaluateur compare automatiquement :
- **DeepSeek R1** vs **LLaMA 3**
- Détermine le meilleur modèle basé sur les scores moyens

## 📝 Exemple de Rapport

```json
{
  "timestamp": "2024-11-02T10:30:00",
  "summary": {
    "deepseek": {
      "avg_bleu": 0.4523,
      "avg_rouge_l_f": 0.6234,
      "num_policies": 10
    },
    "llama3": {
      "avg_bleu": 0.3891,
      "avg_rouge_l_f": 0.5678,
      "num_policies": 10
    }
  }
}
```

## 💡 Notes

- Les métriques sont implémentées en Python pur (pas de dépendances externes)
- Les politiques de référence doivent être de qualité professionnelle
- Plus de références = évaluation plus robuste (recommandé: 3-5 par catégorie)

