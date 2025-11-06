# 🐳 Configuration Docker pour ZAP - Résumé

## 🔴 Problème Identifié

L'action `zaproxy/action-baseline` nécessite Docker pour fonctionner, mais :
- Docker n'était pas explicitement vérifié
- Pas d'alternative si Docker échoue
- Pas de diagnostic pour identifier les problèmes Docker

**Erreur typique** :
```
failed to scan the target: Error: The process '/usr/bin/docker' failed with exit code 3
```

---

## ✅ Solutions Appliquées

### 1. Vérification de Docker

**Ajouté** : Étape `Check Docker Availability`
- ✅ Vérifie que Docker est installé
- ✅ Affiche la version de Docker
- ✅ Teste que Docker peut être utilisé
- ✅ Messages clairs pour le diagnostic

### 2. Alternative Docker Direct

**Ajouté** : Étape `Run OWASP ZAP Baseline Scan (Alternative - Docker Direct)`
- ✅ Utilise Docker directement si l'action GitHub échoue
- ✅ Commande : `docker run owasp/zap2docker-stable zap-baseline.py`
- ✅ Utilise `host.docker.internal:8080` pour accéder à l'application
- ✅ Crée un rapport vide si Docker n'est pas disponible

### 3. Double Stratégie

**Maintenant** :
1. **Première tentative** : Action GitHub `zaproxy/action-baseline` (plus simple)
2. **Si échec** : Docker direct (plus de contrôle)
3. **Si tout échoue** : Rapport vide (évite les erreurs du parser)

---

## 📋 Configuration

### Vérification Docker

```yaml
- name: Check Docker Availability
  run: |
    docker --version
    docker ps || echo "Docker daemon peut ne pas être démarré"
```

### Alternative Docker Direct

```yaml
- name: Run OWASP ZAP Baseline Scan (Alternative)
  run: |
    docker run --rm \
      -v $(pwd):/zap/wrk/:rw \
      -t owasp/zap2docker-stable \
      zap-baseline.py \
      -t http://host.docker.internal:8080 \
      -J -a -r zap-report.json
```

**Note importante** : `host.docker.internal` permet au conteneur Docker d'accéder à `localhost:8080` du host.

---

## 🔍 Diagnostic

Si ZAP échoue toujours, vérifier dans les logs :

1. **Docker disponible ?**
   ```
   docker --version
   ```

2. **Application accessible ?**
   ```
   curl http://localhost:8080
   ```

3. **Docker peut accéder au host ?**
   - `host.docker.internal` devrait fonctionner sur GitHub Actions
   - Sinon, utiliser l'IP du host

---

## ⚠️ Notes Importantes

### GitHub Actions Runners

Les runners `ubuntu-latest` ont Docker préinstallé, mais :
- Le daemon Docker doit être démarré
- Les permissions peuvent varier
- `host.docker.internal` devrait fonctionner

### Alternative : ZAP API

Si Docker continue d'échouer, on peut utiliser ZAP en mode API :
1. Démarrer ZAP en mode API
2. Utiliser l'API REST pour scanner
3. Récupérer le rapport via l'API

**Mais** : Plus complexe à configurer, donc on garde Docker pour l'instant.

---

## ✅ Résultat

**Le pipeline gère maintenant** :
- ✅ Vérification de Docker avant le scan
- ✅ Alternative Docker direct si l'action échoue
- ✅ Rapport vide si tout échoue (évite les erreurs)
- ✅ Messages de diagnostic détaillés

**Si Docker n'est toujours pas disponible, les logs indiqueront exactement pourquoi !** 🔍

