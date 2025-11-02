# 🚀 Configuration DeepSeek R1

## ✅ Excellente Choix !

**DeepSeek R1 est maintenant le modèle par défaut** car :
- ✅ **Très économique** (0.55$ par million tokens)
- ✅ **Haute performance** avec raisonnement avancé
- ✅ **Open-source** (licence MIT)
- ✅ **API simple** (compatible OpenAI)
- ✅ **Raisonnement avancé** avec le modèle "deepseek-reasoner"

---

## 🔑 Configuration de la Clé API

### Étape 1 : Créer un Compte DeepSeek

1. Aller sur : https://platform.deepseek.com
2. Créer un compte (gratuit)
3. Aller dans "API Keys" ou "Settings"
4. Générer une nouvelle clé API
5. **Copier la clé** (elle commence par `sk-...`)

### Étape 2 : Configurer la Clé

**Méthode 1 : Fichier .env (Recommandé)**

1. Créer un fichier `llm/.env` :
```bash
cd mon-projet-parfumerie/llm
touch .env
```

2. Ajouter votre clé :
```
DEEPSEEK_API_KEY=sk-votre_cle_ici
```

**Méthode 2 : Variable d'environnement**
```bash
export DEEPSEEK_API_KEY=sk-votre_cle_ici
```

**Méthode 3 : Dans le code**
```python
from llm.models.deepseek import DeepSeekLLM

llm = DeepSeekLLM(api_key="sk-votre_cle_ici")
```

---

## 🎯 Utilisation

### Méthode 1 : Par Défaut (DeepSeek Chat)

```python
from llm.policy_generator import PolicyGenerator

# DeepSeek est maintenant le défaut !
generator = PolicyGenerator()
generator.generate_all_policies()
```

### Méthode 2 : DeepSeek R1 (Reasoner - Plus Puissant)

```python
generator = PolicyGenerator(
    llm_provider="deepseek",
    model_name="deepseek-reasoner"  # Modèle avec raisonnement avancé
)
```

### Méthode 3 : Ligne de Commande

```bash
# DeepSeek Chat (défaut)
python llm/policy_generator.py

# DeepSeek R1 (reasoner)
python llm/policy_generator.py parser/reports/normalized_vulnerabilities.json deepseek deepseek-reasoner
```

---

## 📊 Modèles DeepSeek Disponibles

| Modèle | Description | Quand l'utiliser |
|--------|-------------|------------------|
| **deepseek-chat** | Modèle conversationnel standard | Général, rapide, économique |
| **deepseek-reasoner** | R1 avec raisonnement avancé | Politiques complexes, meilleure qualité |

**Recommandation :** Commencer avec `deepseek-chat`, puis tester `deepseek-reasoner` si besoin de plus de qualité.

---

## 💰 Coûts

**DeepSeek R1 :**
- Entrée : **0.55$ par million de tokens**
- Sortie : **2.19$ par million de tokens**

**Exemple pour générer une politique :**
- Environ 2000 tokens → **~0.001$** 🎉
- Très économique pour un projet académique !

---

## 🔧 Test Rapide

Pour vérifier que tout fonctionne :

```python
from llm.models.deepseek import DeepSeekLLM

llm = DeepSeekLLM()
result = llm.generate("Explique brièvement la cybersécurité en 2 phrases.")
print(result)
```

Si vous voyez une réponse → ✅ Tout fonctionne !

Si vous voyez une erreur d'authentification → Vérifiez votre clé API.

---

## ✅ Avantages de DeepSeek R1

1. **Coût**
   - Très économique (0.55$/1M tokens)
   - Parfait pour générer plusieurs politiques

2. **Performance**
   - Raisonnement mathématique : 79.8%
   - Codage : 96.3%
   - Excellent pour les politiques de sécurité

3. **Open-source**
   - Licence MIT
   - Transparence et contrôle

4. **API Simple**
   - Utilise la librairie `openai` Python (API compatible)
   - Intégration facile

---

## 🔄 Utilisation Simple

DeepSeek est le défaut, donc très simple :

```python
# DeepSeek est le défaut - rien à spécifier !
generator = PolicyGenerator()
generator.generate_all_policies()
```

**C'est tout !** ✅

---

## 📝 Exemple Complet

```python
from llm.policy_generator import PolicyGenerator

# Initialiser avec DeepSeek R1
generator = PolicyGenerator(
    vulnerabilities_file="parser/reports/normalized_vulnerabilities.json",
    llm_provider="deepseek",
    model_name="deepseek-reasoner"  # Optionnel : raisonnement avancé
)

# Générer toutes les politiques
policies = generator.generate_all_policies()

# Les politiques sont sauvegardées dans llm/policies/
```

---

## 🎉 Résultat

Une fois configuré, vous pouvez générer des politiques de haute qualité avec DeepSeek R1 à un coût très faible !

**Le modèle par défaut est maintenant DeepSeek** - Plus économique et performant ! 🚀

