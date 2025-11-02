# 🤖 Module LLM : Génération de Politiques de Sécurité

## 🎯 Objectif

Transformer les **vulnérabilités techniques détectées** (SAST, SCA, DAST) en **politiques de sécurité conformes** aux standards internationaux :
- **NIST CSF** (Cybersecurity Framework)
- **ISO/IEC 27001**

## 📊 Flux de Données

```
Rapports de Vulnérabilités (SAST/SCA/DAST)
         ↓
Parser Python (normalisation)
         ↓
normalized_vulnerabilities.json
         ↓
LLM (DeepSeek R1, Hugging Face)
         ↓
Politiques de Sécurité (NIST CSF / ISO 27001)
```

## 🏗️ Structure du Module

```
llm/
├── policy_generator.py       # Générateur principal
├── prompts/
│   ├── nist_csf_prompt.py   # Prompts pour NIST CSF
│   └── iso27001_prompt.py   # Prompts pour ISO 27001
├── models/
│   ├── deepseek.py          # Intégration DeepSeek R1
│   └── huggingface.py       # Intégration Hugging Face (LLaMA 3, Mistral, etc.)
└── policies/
    ├── nist_csf/            # Politiques générées NIST CSF
    └── iso27001/            # Politiques générées ISO 27001
```

## 🔄 Processus

1. **Lecture** : Charger `normalized_vulnerabilities.json`
2. **Prompt Engineering** : Construire des prompts structurés
3. **Génération LLM** : Appeler le modèle LLM
4. **Post-traitement** : Structurer et valider les politiques
5. **Export** : Sauvegarder les politiques générées

## 📝 Format des Politiques Générées

Chaque politique contient :
- **Identifiant** : Référence au standard (ex: NIST CSF PR.AC-1)
- **Titre** : Nom de la politique
- **Description** : Objectif et contexte
- **Exigences** : Liste des exigences basées sur les vulnérabilités
- **Mesures de contrôle** : Actions spécifiques à implémenter
- **Références** : Liens avec les vulnérabilités détectées

