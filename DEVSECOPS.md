# Pipeline DevSecOps - Documentation

## 📋 Vue d'ensemble

Ce projet intègre un pipeline DevSecOps complet qui automatise la détection de vulnérabilités à chaque push ou pull request. Le pipeline combine **SAST**, **SCA**, et **DAST** pour une analyse de sécurité multi-couches.

## 🔄 Architecture du Pipeline

```
┌─────────────┐
│   Build     │ ← Compile le code (Backend + Frontend)
└──────┬──────┘
       │
       ├─────────────────┬─────────────────┐
       │                 │                 │
┌──────▼──────┐   ┌──────▼──────┐   ┌──────▼──────┐
│    SAST     │   │    SCA      │   │    DAST     │
│ (Statique)  │   │ (Dépendances)│  │ (Dynamique)  │
└──────┬──────┘   └──────┬──────┘   └──────┬──────┘
       │                 │                 │
       └─────────────────┴─────────────────┘
                    │
            ┌───────▼────────┐
            │ Collect Reports│ ← Centralise tous les rapports
            └────────────────┘
```

## 🛠️ Outils Intégrés

### 1. SAST - Static Application Security Testing

**Pourquoi :** Analyse le code source sans l'exécuter pour détecter les vulnérabilités.

**Outils utilisés :**
- **SpotBugs** (Backend Java)
  - Détecte les bugs et vulnérabilités dans le bytecode Java
  - Identifie les problèmes de sécurité (weak cryptography, SQL injection, etc.)
  - Génère un rapport XML : `reports/sast/spotbugs-report.xml`

- **SonarQube** (Optionnel - Backend Java)
  - Analyse plus complète mais nécessite un compte SonarCloud
  - Pour l'activer : ajouter `SONAR_TOKEN` et `SONAR_HOST_URL` dans les secrets GitHub

- **ESLint** (Frontend JavaScript/React)
  - Analyse le code JavaScript/JSX
  - Détecte les problèmes de sécurité (dangerouslySetInnerHTML, etc.)
  - Génère un rapport JSON : `reports/sast/eslint-report.json`

**Comment ça marche :**
1. Le code est compilé
2. Les outils analysent le code source/bytecode
3. Les rapports sont générés au format XML/JSON
4. Les rapports sont sauvegardés comme artifacts GitHub

### 2. SCA - Software Composition Analysis

**Pourquoi :** Analyse les dépendances (packages, bibliothèques) pour détecter les vulnérabilités connues.

**Outils utilisés :**
- **OWASP Dependency-Check** (Backend Maven)
  - Compare les dépendances Maven avec la base de données NVD (National Vulnerability Database)
  - Identifie les CVE (Common Vulnerabilities and Exposures)
  - Génère un rapport JSON : `reports/sca/backend-dependency-check-report.json`

- **npm audit** (Frontend npm)
  - Scanne les packages npm pour les vulnérabilités connues
  - Utilise la base de données de sécurité npm
  - Génère un rapport JSON : `reports/sca/frontend-npm-audit-report.json`

**Comment ça marche :**
1. Les outils analysent les fichiers de dépendances (`pom.xml`, `package.json`)
2. Ils consultent les bases de données de vulnérabilités (NVD, npm advisory)
3. Les rapports listent les vulnérabilités trouvées avec leur niveau de criticité

### 3. DAST - Dynamic Application Security Testing

**Pourquoi :** Teste l'application en cours d'exécution pour détecter les vulnérabilités runtime.

**Outils utilisés :**
- **OWASP ZAP** (Application complète)
  - Envoie des requêtes HTTP malveillantes à l'application
  - Analyse les réponses pour détecter :
    - Cross-Site Scripting (XSS)
    - SQL Injection
    - CSRF (Cross-Site Request Forgery)
    - Et autres vulnérabilités OWASP Top 10
  - Génère un rapport JSON : `reports/dast/zap-report.json`

**Comment ça marche :**
1. L'application Spring Boot est démarrée
2. ZAP envoie des attaques simulées sur les endpoints
3. Les réponses sont analysées pour détecter les failles
4. Un rapport détaillé est généré

## 📊 Structure des Rapports

Tous les rapports sont organisés dans le dossier `reports/` :

```
reports/
├── sast/
│   ├── spotbugs-report.xml      # Rapports SAST (Backend)
│   └── eslint-report.json       # Rapports SAST (Frontend)
├── sca/
│   ├── backend-dependency-check-report.json
│   └── frontend-npm-audit-report.json
└── dast/
    └── zap-report.json
```

## 🚀 Exécution du Pipeline

### Déclenchement Automatique

Le pipeline s'exécute automatiquement sur :
- **Push** vers les branches `main` ou `SecOps`
- **Pull Request** vers `main`

### Déclenchement Manuel

1. Allez dans l'onglet **Actions** de GitHub
2. Sélectionnez **DevSecOps Pipeline**
3. Cliquez sur **Run workflow**

## 📥 Récupération des Rapports

### Via GitHub Actions

1. Allez dans l'onglet **Actions**
2. Sélectionnez le workflow exécuté
3. Cliquez sur le job **Collect Security Reports**
4. Téléchargez l'artifact **security-reports**

### Structure Locale

Si vous exécutez le pipeline en local, les rapports seront dans `reports/`.

## 🔧 Configuration

### Secrets GitHub (Optionnel)

Pour activer SonarQube, ajoutez dans **Settings > Secrets and variables > Actions** :

- `SONAR_TOKEN` : Token d'authentification SonarCloud
- `SONAR_HOST_URL` : URL de votre instance SonarQube (ex: `https://sonarcloud.io`)

### Variables d'Environnement

Le pipeline utilise des variables d'environnement par défaut :
- Java version : 17
- Port backend : 8080
- Port frontend : 5201

## 📝 Prochaines Étapes

1. **Parser les rapports** : Créer un script pour parser les rapports JSON/XML
2. **Génération de politiques** : Utiliser les LLMs pour générer des politiques de sécurité
3. **Évaluation** : Calculer les métriques BLEU/ROUGE-L pour évaluer les politiques générées

## 🔍 Exemple de Vulnérabilités Détectées

### SAST (Exemple SpotBugs)
- **SQL Injection** : Requêtes SQL construites avec concaténation de strings
- **Weak Cryptography** : Utilisation d'algorithmes de chiffrement faibles
- **Null Pointer** : Accès à des objets potentiellement null

### SCA (Exemple Dependency-Check)
- **CVE-2024-XXXX** : Vulnérabilité critique dans une dépendance
- **Licence problématique** : Dépendance avec licence incompatible

### DAST (Exemple ZAP)
- **XSS Reflection** : Injection de script malveillant via paramètre URL
- **Missing Security Headers** : Absence de headers de sécurité (CSP, HSTS, etc.)
- **SQL Injection** : Injection SQL détectée via endpoint API

## 📚 Ressources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [SpotBugs Documentation](https://spotbugs.github.io/)
- [OWASP Dependency-Check](https://owasp.org/www-project-dependency-check/)
- [OWASP ZAP](https://www.zaproxy.org/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)

