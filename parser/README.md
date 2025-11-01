# Parser de Rapports de Vulnérabilités

## 📋 Vue d'ensemble

Ce parser extrait et normalise les vulnérabilités depuis les rapports générés par les outils de sécurité (SAST, SCA, DAST) en un format unique pour la génération de politiques avec LLM.

## 🏗️ Architecture

```
parser/
├── vulnerability_model.py      # Modèle de données standardisé
├── main_parser.py               # Parser principal
├── parsers/
│   ├── sast_parser.py          # Parsers SAST (SpotBugs, ESLint)
│   ├── sca_parser.py           # Parsers SCA (Dependency-Check, npm audit)
│   └── dast_parser.py          # Parsers DAST (OWASP ZAP)
└── reports/
    └── normalized_vulnerabilities.json  # Rapport normalisé (généré)
```

## 🔄 Fonctionnement

### Étape 1 : Extraction
- Parse les rapports XML/JSON de chaque outil
- Extrait les informations pertinentes (CVE, sévérité, description, etc.)

### Étape 2 : Normalisation
- Convertit tous les formats en objets `Vulnerability` standardisés
- Unifie les niveaux de sévérité (CRITICAL, HIGH, MEDIUM, LOW, INFO)
- Standardise les catégories (SQL Injection, XSS, CVE, etc.)

### Étape 3 : Export
- Génère un fichier JSON unique avec toutes les vulnérabilités
- Prêt pour l'étape de génération de politiques avec LLM

## 📊 Format Normalisé

Chaque vulnérabilité est représentée ainsi :

```json
{
  "id": "CVE-2024-XXXX",
  "title": "SQL Injection vulnerability",
  "severity": "HIGH",
  "type": "SAST",
  "category": "SQL Injection",
  "description": "Detailed description...",
  "recommendation": "Use parameterized queries",
  "file_path": "src/main/java/Controller.java",
  "line_number": 42,
  "dependency_name": null,
  "dependency_version": null,
  "fixed_version": null,
  "endpoint": "/api/product",
  "http_method": "GET"
}
```

## 🚀 Utilisation

### Méthode 1 : Ligne de commande

```bash
cd mon-projet-parfumerie
python parser/main_parser.py reports/
```

### Méthode 2 : Depuis Python

```python
from parser.main_parser import VulnerabilityReportParser

# Créer le parser
parser = VulnerabilityReportParser(reports_directory="reports")

# Parser tous les rapports
vulnerabilities = parser.parse_all()

# Afficher les statistiques
parser.print_statistics()

# Sauvegarder le rapport normalisé
parser.save_normalized_report("normalized_vulnerabilities.json")
```

## 📁 Structure des Rapports Attendus

Le parser cherche automatiquement les fichiers suivants :

```
reports/
├── sast/
│   ├── spotbugs-report.xml        # Rapport SpotBugs
│   └── eslint-report.json         # Rapport ESLint
├── sca/
│   ├── backend-dependency-check-report.json  # OWASP Dependency-Check
│   └── frontend-npm-audit-report.json      # npm audit
└── dast/
    └── zap-report.json             # OWASP ZAP
```

## 🔍 Formats Supportés

### SAST
- ✅ **SpotBugs** : Format XML
- ✅ **ESLint** : Format JSON ou texte

### SCA
- ✅ **OWASP Dependency-Check** : Format JSON
- ✅ **npm audit** : Format JSON (ancien et nouveau format)

### DAST
- ✅ **OWASP ZAP** : Format JSON (plusieurs variantes)

## 📈 Statistiques Générées

Le parser génère automatiquement des statistiques :

- Nombre total de vulnérabilités
- Répartition par type (SAST/SCA/DAST)
- Répartition par sévérité (CRITICAL/HIGH/MEDIUM/LOW/INFO)
- Top 5 des catégories les plus fréquentes

## 💡 Prochaines Étapes

Le rapport normalisé (`normalized_vulnerabilities.json`) sera utilisé pour :

1. **Génération de politiques** : Les LLMs utiliseront ces vulnérabilités pour générer des politiques de sécurité
2. **Évaluation** : Comparaison avec des politiques de référence (NIST CSF, ISO 27001)
3. **Métriques** : Calcul de BLEU, ROUGE-L pour évaluer la qualité des politiques générées

## 🐛 Dépannage

### Erreur : "Fichier non trouvé"
- Vérifiez que les rapports sont dans le bon répertoire
- Vérifiez les noms de fichiers (sensibles à la casse)

### Erreur : "Format inattendu"
- Les formats de rapports peuvent varier selon les versions des outils
- Le parser supporte plusieurs variantes, mais certaines peuvent nécessiter des ajustements

### Aucune vulnérabilité détectée
- Vérifiez que les fichiers de rapports ne sont pas vides
- Vérifiez que les outils ont bien généré les rapports

