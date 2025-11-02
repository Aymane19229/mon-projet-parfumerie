# 🚀 Guide d'Utilisation : Générateur de Politiques avec LLM

## 🎯 Objectif

Générer automatiquement des **politiques de sécurité conformes** (NIST CSF, ISO 27001) à partir des vulnérabilités détectées par le pipeline DevSecOps.

---

## 📋 Prérequis

### 1. Installer les Dépendances

```bash
cd mon-projet-parfumerie
pip install -r llm/requirements.txt
```

### 2. Configurer les Clés API

**Option A : DeepSeek R1 - ⭐ RECOMMANDÉ (Par défaut)**

1. Créer un compte sur https://platform.deepseek.com
2. Générer une clé API (gratuite au démarrage)
3. Créer un fichier `.env` dans le dossier `llm/` :
   ```
   DEEPSEEK_API_KEY=sk-votre_cle_api_ici
   ```
   **Avantages :** Performant, économique, open-source !

**Option B : Hugging Face (LLaMA 3) - Gratuit**

1. Créer un compte sur https://huggingface.co
2. Accepter les termes pour LLaMA 3
3. Optionnel : Générer une clé API pour les modèles privés
4. Créer un fichier `.env` :
   ```
   HUGGINGFACE_API_KEY=votre_cle_ici  # Optionnel
   ```

---

## 🔄 Workflow Complet

```
1. Pipeline DevSecOps détecte des vulnérabilités
         ↓
2. Parser normalise les rapports → normalized_vulnerabilities.json
         ↓
3. LLM génère des politiques conformes
         ↓
4. Politiques sauvegardées dans llm/policies/
```

---

## 🚀 Utilisation

### Méthode 1 : Ligne de Commande

```bash
# Avec DeepSeek R1 (défaut - recommandé)
python llm/policy_generator.py

# Avec DeepSeek R1 Reasoner (raisonnement avancé)
python llm/policy_generator.py parser/reports/normalized_vulnerabilities.json deepseek deepseek-reasoner

# Avec Hugging Face (LLaMA 3)
python llm/policy_generator.py parser/reports/normalized_vulnerabilities.json huggingface
```

### Méthode 2 : Depuis Python

```python
from llm.policy_generator import PolicyGenerator

# Créer le générateur avec DeepSeek R1 (défaut - recommandé)
generator = PolicyGenerator(
    vulnerabilities_file="parser/reports/normalized_vulnerabilities.json",
    llm_provider="deepseek",  # ou "huggingface"
    model_name="deepseek-chat"  # ou "deepseek-reasoner" pour R1
)

# OU simplement (DeepSeek est le défaut maintenant)
generator = PolicyGenerator()
```

# Générer une politique NIST CSF
nist_policy = generator.generate_nist_csf_policy("PROTECT")
generator.save_policy(nist_policy, "nist_csf", "PROTECT")

# Générer une politique ISO 27001
iso_policy = generator.generate_iso27001_policy("A.14.2.5")
generator.save_policy(iso_policy, "iso27001", "A.14.2.5")

# OU générer toutes les politiques
generator.generate_all_policies()
```

---

## 📊 Résultats

Les politiques sont sauvegardées dans :
- `llm/policies/nist_csf/` - Politiques NIST CSF
- `llm/policies/iso27001/` - Politiques ISO 27001

Format des fichiers :
- Nom : `{framework}_{identifier}_{timestamp}.md`
- Contenu : Politique complète en Markdown avec métadonnées

---

## 🔧 Configuration Avancée

### Personnaliser les Prompts

Modifier les fichiers :
- `llm/prompts/nist_csf_prompt.py` - Pour NIST CSF
- `llm/prompts/iso27001_prompt.py` - Pour ISO 27001

### Choisir le Modèle LLM

**DeepSeek R1 (Recommandé) :**
- `deepseek-chat` : Modèle conversationnel standard (0.55$/1M tokens)
- `deepseek-reasoner` : R1 avec raisonnement avancé (meilleure qualité)

**Hugging Face :**
- `meta-llama/Meta-Llama-3-8B-Instruct` : LLaMA 3 (gratuit via API)
- `mistralai/Mistral-7B-Instruct-v0.2` : Mistral (gratuit via API)
- Autres modèles disponibles sur Hugging Face

---

## 📝 Exemple de Politique Générée

Chaque politique contient :
1. **Métadonnées** (YAML frontmatter)
2. **Informations de base** (ID, titre, références)
3. **Objectif et portée**
4. **Exigences détaillées** basées sur les vulnérabilités
5. **Mesures de contrôle** actionnables
6. **Responsabilités**
7. **Conformité et audit**

---

## ⚠️ Notes Importantes

1. **Coûts** : 
   - DeepSeek : Très économique (0.55$/1M tokens) - **Recommandé**
   - Hugging Face : Gratuit (selon le modèle)
   - Vérifiez vos limites d'utilisation
2. **Résultats** : Les politiques générées doivent être revues et adaptées.
3. **Conformité** : Vérifiez que les politiques respectent bien NIST/ISO.
4. **Performance** : Les LLMs peuvent prendre du temps (30 secondes à plusieurs minutes).
   - DeepSeek reasoner peut prendre plus de temps (raisonnement approfondi)

---

## 🔍 Dépannage

### Erreur : "DEEPSEEK_API_KEY non configurée"
- Vérifiez que le fichier `.env` existe dans `llm/`
- OU définissez la variable d'environnement : `export DEEPSEEK_API_KEY=votre_cle`
- Créez un compte sur https://platform.deepseek.com

### Erreur : "HUGGINGFACE_API_KEY non configurée" (pour certains modèles)
- Certains modèles Hugging Face nécessitent une clé API
- Créez un compte sur https://huggingface.co
- OU utilisez un modèle public qui ne nécessite pas de clé

### Erreur : "Fichier vulnérabilités non trouvé"
- Exécutez d'abord : `python parser/main_parser.py`

### Erreur : "Module non trouvé"
- Installez les dépendances : `pip install -r llm/requirements.txt`

---

## ✅ Prochaines Étapes

Après avoir généré les politiques :

1. **Évaluer la qualité** avec BLEU/ROUGE-L (module à venir)
2. **Comparer avec des références** NIST/ISO
3. **Réviser et adapter** les politiques générées
4. **Documenter** dans le rapport final

---

## 📚 Ressources

- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [ISO/IEC 27001](https://www.iso.org/isoiec-27001-information-security.html)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Hugging Face Models](https://huggingface.co/models)

