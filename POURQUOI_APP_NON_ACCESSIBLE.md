# 🔍 Pourquoi l'Application n'est pas Accessible via curl ?

## 🔴 Problème Identifié

**Symptômes** :
- ✅ L'application démarre correctement (Spring Boot)
- ✅ Le port 8080 écoute (`tcp6 0 0 :::8080 :::* LISTEN`)
- ✅ Le processus Java est en cours d'exécution
- ❌ Mais `curl http://localhost:8080` retourne **404 Not Found**

---

## 📋 Analyse des Routes Disponibles

D'après le code, l'application Spring Boot a **4 contrôleurs** :

1. **ProductController** : `/product`
   - `GET /product` - Liste tous les produits
   - `GET /product/{id}` - Récupère un produit par ID
   - etc.

2. **OrderController** : `/order`
   - `GET /order` - Liste toutes les commandes
   - `GET /order/{id}` - Récupère une commande par ID
   - etc.

3. **ClientController** : `/client`
   - `GET /client` - Liste tous les clients
   - `GET /client/{id}` - Récupère un client par ID
   - etc.

4. **OrderLineController** : `/orderline`
   - `GET /orderline` - Liste toutes les lignes de commande
   - etc.

**❌ Problème** : Il n'y a **PAS de route racine (`/`)** !

---

## 🔍 Causes du Problème

### 1. Pas de Route Racine

L'application n'a pas de route pour `/`, donc :
- `curl http://localhost:8080` → **404 Not Found**
- `curl http://localhost:8080/product` → ✅ Devrait fonctionner

### 2. Spring Boot Actuator Non Activé

L'application n'a probablement pas Spring Boot Actuator activé, donc :
- `curl http://localhost:8080/actuator/health` → **404 Not Found**

**Pourquoi Actuator est utile** :
- Fournit des endpoints de santé (`/actuator/health`)
- Facilite le monitoring et les tests
- Standard dans les applications Spring Boot

---

## ✅ Solutions

### Solution 1 : Tester une Route Existante (Rapide)

**Modifier le pipeline pour tester `/product` au lieu de `/`** :

```yaml
# Au lieu de :
curl -f http://localhost:8080

# Utiliser :
curl -f http://localhost:8080/product
```

**Avantages** :
- ✅ Solution rapide (pas de modification du code)
- ✅ Teste une route qui existe vraiment
- ✅ Confirme que l'application fonctionne

**Inconvénients** :
- ⚠️ Nécessite que la base de données ait des données
- ⚠️ Peut retourner une liste vide (mais pas 404)

---

### Solution 2 : Ajouter Spring Boot Actuator (Recommandé)

**Étape 1 : Ajouter la dépendance dans `pom.xml`**

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-actuator</artifactId>
</dependency>
```

**Étape 2 : Configurer dans `application.properties`**

```properties
# Activer Actuator
management.endpoints.web.exposure.include=health,info
management.endpoint.health.show-details=always
```

**Étape 3 : Tester**

```bash
curl http://localhost:8080/actuator/health
# Devrait retourner : {"status":"UP"}
```

**Avantages** :
- ✅ Standard Spring Boot
- ✅ Endpoint de santé fiable
- ✅ Utile pour le monitoring
- ✅ Ne dépend pas des données de la base

**Inconvénients** :
- ⚠️ Nécessite de modifier le code et de rebuild

---

### Solution 3 : Créer une Route Racine Simple

**Créer un contrôleur simple** :

```java
@RestController
public class RootController {
    
    @GetMapping("/")
    public Map<String, String> root() {
        return Map.of("status", "UP", "message", "API is running");
    }
}
```

**Avantages** :
- ✅ Route racine disponible
- ✅ Simple et direct

**Inconvénients** :
- ⚠️ Nécessite de modifier le code et de rebuild

---

## 🎯 Solution Recommandée

**Pour le pipeline CI/CD** : **Solution 1 (Tester `/product`)** + **Solution 2 (Actuator)**

**Pourquoi** :
1. **Solution 1** : Permet de tester rapidement sans modifier le code
2. **Solution 2** : Ajoute Actuator pour un endpoint de santé fiable à long terme

---

## 📝 Modifications à Apporter

### 1. Modifier le Pipeline (Solution 1)

**Dans `.github/workflows/devsecops-pipeline.yml`** :

```yaml
# Remplacer :
curl -f http://localhost:8080

# Par :
curl -f http://localhost:8080/product || \
curl -f http://localhost:8080/actuator/health
```

### 2. Ajouter Actuator (Solution 2)

**Dans `backend/pom.xml`** :

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-actuator</artifactId>
</dependency>
```

**Dans `backend/src/main/resources/application.properties`** :

```properties
# Activer Actuator
management.endpoints.web.exposure.include=health,info
management.endpoint.health.show-details=always
```

---

## ✅ Résultat Attendu

**Après les modifications** :
- ✅ `curl http://localhost:8080/product` → Devrait fonctionner
- ✅ `curl http://localhost:8080/actuator/health` → Devrait retourner `{"status":"UP"}`
- ✅ ZAP peut scanner l'application correctement
- ✅ Le pipeline peut vérifier que l'application est accessible

---

## 🔗 Références

- Spring Boot Actuator : https://docs.spring.io/spring-boot/docs/current/reference/html/actuator.html
- Spring Boot Controllers : https://spring.io/guides/gs/rest-service/

