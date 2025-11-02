# Guide : Quand et Pourquoi Utiliser SAST, SCA, DAST ?

## 🎯 Vue d'ensemble : Les 3 types d'analyse

```
┌─────────────────────────────────────────────────────────────┐
│                    CYCLES DE VIE                            │
│                                                              │
│  Code Source → Dépendances → Application Déployée          │
│      │              │                  │                     │
│      ▼              ▼                  ▼                     │
│    SAST           SCA                DAST                    │
│  (Statique)    (Dépendances)      (Dynamique)               │
└─────────────────────────────────────────────────────────────┘
```

## 1. 🔍 SAST - Static Application Security Testing

### QUAND l'utiliser ?
- ✅ **Pendant le développement** : À chaque commit/push
- ✅ **Avant la mise en production** : Dans le pipeline CI/CD
- ✅ **Code Review** : Quand vous recevez une pull request
- ✅ **Intégration continue** : Automatiquement dans GitHub Actions

### POURQUOI l'utiliser ?

**SAST analyse votre CODE SOURCE** sans l'exécuter.

#### Exemples CONCRETS dans votre projet parfumerie :

**Exemple 1 : Injection SQL**
```java
// ❌ MAUVAIS - Détecté par SAST
@GetMapping("/product/{id}")
public ProductEntity getProduct(@PathVariable String id) {
    String query = "SELECT * FROM products WHERE id = " + id;  // DANGEREUX !
    // SAST détecte : "Possible SQL Injection vulnerability"
    return productService.executeQuery(query);
}

// ✅ BON - SAST ne signale rien
@GetMapping("/product/{id}")
public ProductEntity getProduct(@PathVariable Long id) {
    return productService.findById(id);  // Utilise JPA, sécurisé
}
```

**Exemple 2 : Faible chiffrement**
```java
// ❌ MAUVAIS - Détecté par SAST
String password = encrypt(password, "DES");  // DES est faible
// SAST détecte : "Use of weak cryptographic algorithm"

// ✅ BON
String password = BCrypt.hashpw(password, BCrypt.gensalt());  // BCrypt est fort
```

**Exemple 3 : Null Pointer Exception**
```java
// ❌ MAUVAIS - Détecté par SAST
@GetMapping("/client/{id}")
public ClientEntity getClient(@PathVariable Long id) {
    ClientEntity client = clientRepository.findById(id);
    return client.getName();  // client peut être null !
    // SAST détecte : "Possible null pointer dereference"
}

// ✅ BON
@GetMapping("/client/{id}")
public Optional<ClientEntity> getClient(@PathVariable Long id) {
    return clientRepository.findById(id);  // Retourne Optional
}
```

#### Avantages de SAST :
- ⚡ **Rapide** : Analyse en quelques secondes
- 💰 **Gratuit** : SpotBugs, ESLint sont gratuits
- 🔍 **Trouve beaucoup de bugs** : Avant même d'exécuter le code
- 📝 **Suggestions de correction** : Les outils proposent des correctifs

#### Limitations de SAST :
- ❌ **Faux positifs** : Signale parfois des problèmes qui n'en sont pas
- ❌ **Ne trouve pas tout** : Certaines vulnérabilités nécessitent l'exécution
- ❌ **Pas de contexte runtime** : Ne sait pas comment l'app est utilisée

---

## 2. 📦 SCA - Software Composition Analysis

### QUAND l'utiliser ?
- ✅ **Après chaque modification de `pom.xml` ou `package.json`**
- ✅ **Avant chaque release** : Vérifier les nouvelles dépendances
- ✅ **Hebdomadairement** : Les bases de données CVE sont mises à jour
- ✅ **Quand une CVE est publiée** : Scans d'urgence

### POURQUOI l'utiliser ?

**SCA analyse vos DÉPENDANCES** (bibliothèques externes).

#### Exemple CONCRET dans votre projet :

Votre `pom.xml` utilise :
```xml
<dependency>
    <groupId>com.fasterxml.jackson.core</groupId>
    <artifactId>jackson-databind</artifactId>
    <version>2.13.0</version>
</dependency>
```

**SCA détecte :**
```json
{
  "vulnerabilities": [
    {
      "cve": "CVE-2022-42003",
      "severity": "HIGH",
      "description": "Remote code execution in Jackson Databind",
      "dependency": "jackson-databind:2.13.0",
      "fixedIn": "2.13.4.1",
      "recommendation": "Update to version 2.13.4.1"
    }
  ]
}
```

**Solution :**
```xml
<!-- ❌ AVANT - Vulnérable -->
<version>2.13.0</version>

<!-- ✅ APRÈS - Sécurisé -->
<version>2.13.4.1</version>
```

#### Pourquoi c'est CRITIQUE ?

- 🚨 **Vous n'écrivez pas tout le code** : 80% du code vient de dépendances
- 🚨 **Vulnérabilités connues** : Les CVE sont publiques, les attaquants les exploitent
- 🚨 **Mise à jour simple** : Souvent, il suffit de mettre à jour la version

#### Exemple réel dans votre projet parfumerie :

Si votre frontend utilise une version vulnérable de `axios` :
```json
{
  "package": "axios",
  "version": "0.21.0",
  "vulnerability": "CVE-2021-3749",
  "severity": "CRITICAL",
  "impact": "Server-Side Request Forgery (SSRF)"
}
```

Un attaquant peut forcer votre application à faire des requêtes vers des serveurs internes !

#### Avantages de SCA :
- ✅ **Facile à corriger** : Souvent juste mettre à jour la version
- ✅ **Détecte des vulnérabilités critiques** : CVE connues et exploitées
- ✅ **Automatisable** : Peut bloquer le déploiement si vulnérable

#### Limitations de SCA :
- ❌ **Beaucoup d'alertes** : Parfois des centaines de vulnérabilités mineures
- ❌ **Faux positifs** : Certaines CVE ne s'appliquent pas à votre usage
- ❌ **Mises à jour cassantes** : Parfois une mise à jour peut casser votre code

---

## 3. 🎯 DAST - Dynamic Application Security Testing

### QUAND l'utiliser ?
- ✅ **Avant chaque déploiement en production**
- ✅ **Après chaque changement d'API** : Nouveaux endpoints
- ✅ **Tests d'intégration** : Quand l'application est déployée
- ✅ **Scans réguliers** : Hebdomadairement ou mensuellement

### POURQUOI l'utiliser ?

**DAST teste votre APPLICATION EN EXÉCUTION**.

#### Exemple CONCRET dans votre projet parfumerie :

Votre endpoint :
```java
@PostMapping("/order")
public OrderEntity createOrder(@RequestBody OrderEntity order) {
    // Pas de validation !
    return orderService.save(order);
}
```

**DAST (OWASP ZAP) teste :**
```
1. Envoie une requête POST avec du JavaScript malveillant :
   POST /order
   {
     "productId": "<script>alert('XSS')</script>",
     "quantity": "'; DROP TABLE orders; --"
   }

2. Analyse la réponse HTTP :
   - Si le script est exécuté → XSS détecté
   - Si la requête SQL est exécutée → SQL Injection détecté
   - Si les headers de sécurité manquent → Vulnérabilité détectée
```

**DAST détecte :**
```json
{
  "vulnerability": "Cross-Site Scripting (XSS)",
  "endpoint": "POST /order",
  "severity": "HIGH",
  "evidence": "JavaScript executed in response",
  "solution": "Sanitize user input, use Content-Security-Policy header"
}
```

#### Exemple réel : Test de votre API

Votre endpoint :
```java
@GetMapping("/product/{id}")
public ProductEntity getProduct(@PathVariable String id) {
    return productService.findById(id);
}
```

**DAST teste :**
- `GET /product/1` → Normal
- `GET /product/1' OR '1'='1` → Teste SQL Injection
- `GET /product/<script>alert(1)</script>` → Teste XSS
- `GET /product/../../etc/passwd` → Teste Path Traversal

**Si votre API ne filtre pas correctement :**
```java
// ❌ MAUVAIS - DAST détecte la vulnérabilité
@GetMapping("/product/{id}")
public ProductEntity getProduct(@PathVariable String id) {
    // Si vous faites une requête SQL directe avec 'id'
    // DAST trouve : SQL Injection
}

// ✅ BON - DAST ne trouve rien
@GetMapping("/product/{id}")
public ProductEntity getProduct(@PathVariable Long id) {  // Validation automatique
    return productService.findById(id);  // JPA échappe automatiquement
}
```

#### Avantages de DAST :
- ✅ **Détecte les vulnérabilités runtime** : Celles que SAST ne trouve pas
- ✅ **Teste l'application réelle** : Comme un vrai attaquant
- ✅ **Détecte les problèmes de configuration** : Headers manquants, CORS mal configuré
- ✅ **Détecte les problèmes de déploiement** : Sécurité au niveau infrastructure

#### Limitations de DAST :
- ❌ **Plus lent** : Doit démarrer l'application et tester
- ❌ **Nécessite l'application déployée** : Plus complexe à mettre en place
- ❌ **Couverture limitée** : Ne teste que les endpoints accessibles
- ❌ **Peut être bruyant** : Génère beaucoup de logs

---

## 🤔 Est-on OBLIGÉ de tous les faire ?

### Réponse courte : **OUI, les 3 sont complémentaires !**

### Pourquoi les 3 sont nécessaires :

```
SAST trouve :          SCA trouve :           DAST trouve :
┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│ Bugs dans   │       │ Dépendances │       │ Runtime      │
│ votre code  │       │ vulnérables │       │ vulnérabilités│
│             │       │             │       │              │
│ • SQL Inj   │   +   │ • CVE connues│  +   │ • XSS        │
│ • XSS       │       │ • Versions  │       │ • Config err │
│ • Null ptr  │       │ • Licences  │       │ • Headers     │
└─────────────┘       └─────────────┘       └─────────────┘
      │                     │                     │
      └─────────────────────┴─────────────────────┘
                    │
          🎯 COUVERTURE COMPLÈTE
```

### Exemple concret : Pourquoi les 3 ?

**Scénario : Votre application parfumerie a une faille de sécurité**

#### 1. SAST trouve :
```java
// Dans votre code
String query = "SELECT * FROM products WHERE name = '" + productName + "'";
```
✅ SAST détecte : "Possible SQL Injection"

#### 2. Mais vous corrigez :
```java
// Vous utilisez JPA
return productRepository.findByName(productName);
```
✅ SAST ne trouve plus rien

#### 3. Mais SCA trouve :
```json
{
  "vulnerability": "CVE-2023-XXXX",
  "dependency": "spring-data-jpa:2.7.0",
  "description": "SQL Injection in JPA queries"
}
```
⚠️ Même avec du code propre, une dépendance vulnérable peut introduire une faille !

#### 4. Vous mettez à jour la dépendance :
```xml
<version>2.7.5</version>  <!-- Version corrigée -->
```
✅ SCA ne trouve plus rien

#### 5. Mais DAST trouve :
```
POST /api/order
Body: {"productId": "<img src=x onerror=alert('XSS')>"}

Réponse: Le script est exécuté côté client
```
⚠️ Même avec du code propre et des dépendances à jour, la configuration peut être vulnérable !

### Conclusion : Les 3 couches sont nécessaires

- **SAST** : Protège contre les erreurs de développement
- **SCA** : Protège contre les vulnérabilités des dépendances
- **DAST** : Protège contre les problèmes de configuration et runtime

## 📊 Comparaison rapide

| Critère | SAST | SCA | DAST |
|---------|------|-----|------|
| **Quand** | Développement | Après modif dépendances | Avant déploiement |
| **Vitesse** | ⚡⚡⚡ Rapide (secondes) | ⚡⚡ Moyen (minutes) | ⚡ Lent (10-30 min) |
| **Coût** | 💰 Gratuit | 💰 Gratuit | 💰 Gratuit |
| **Complexité** | 🟢 Facile | 🟢 Facile | 🟡 Moyenne |
| **Ce qu'il trouve** | Bugs dans votre code | CVE dans dépendances | Vulnérabilités runtime |
| **Faux positifs** | 🟡 Moyen | 🟢 Faible | 🟡 Moyen |
| **Obligatoire ?** | ✅ OUI | ✅ OUI | ✅ OUI |

## 🎯 Recommandation pour votre projet

### Pipeline optimal :

```
1. SAST (à chaque commit)
   ↓ Rapide, détecte les bugs rapidement
   
2. SCA (à chaque push)
   ↓ Important, dépendances peuvent être critiques
   
3. DAST (avant déploiement en production)
   ↓ Complète la couverture, détecte les problèmes de config
```

### Priorisation :

1. **SAST** : Le plus important, rapide, trouve beaucoup de problèmes
2. **SCA** : Critique, une seule CVE peut compromettre tout le système
3. **DAST** : Important mais peut être fait moins fréquemment (avant release)

## 💡 Analogie simple

Imaginez que vous construisez une maison :

- **SAST** = Inspection des matériaux avant construction (votre code)
- **SCA** = Vérification que les matériaux achetés ne sont pas défectueux (dépendances)
- **DAST** = Test de résistance de la maison construite (application déployée)

Vous avez besoin des 3 pour être sûr que votre maison est solide ! 🏠

