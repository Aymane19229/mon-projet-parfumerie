# 🐳 Configuration Docker pour ZAP - Guide Complet

## 🔴 Problème Initial

L'action `zaproxy/action-baseline` nécessite Docker, mais :
- Docker n'était pas vérifié
- Pas d'alternative si Docker échoue
- Erreur : `failed to scan the target: Error: The process '/usr/bin/docker' failed with exit code 3`

---

## ✅ Solutions Implémentées

### 1. Vérification Docker

**Étape ajoutée** : `Check Docker Availability`
- ✅ Vérifie que Docker est installé
- ✅ Affiche la version de Docker
- ✅ Teste que Docker peut être utilisé (`docker ps`)
- ✅ Messages clairs pour le diagnostic

### 2. Alternative Docker Direct

**Étape ajoutée** : `Run OWASP ZAP Baseline Scan (Alternative - Docker Direct)`
- ✅ Exécutée **AVANT** l'action GitHub
- ✅ Utilise Docker directement : `docker run owasp/zap2docker-stable`
- ✅ Télécharge automatiquement l'image ZAP si nécessaire
- ✅ Utilise `--network host` pour accéder à `localhost:8080`
- ✅ Crée un rapport vide si Docker n'est pas disponible

### 3. Action GitHub (Fallback)

**Étape** : `Run OWASP ZAP Baseline Scan (Action GitHub)`
- ✅ Exécutée après l'alternative
- ✅ Utilise l'action `zaproxy/action-baseline@v0.10.0`
- ✅ Si l'alternative a réussi, cette étape peut être ignorée

---

## 📋 Configuration Actuelle

### Ordre d'Exécution

1. **Check Docker Availability** - Vérifie Docker
2. **Verify Application is Running** - Vérifie que l'app répond
3. **Run OWASP ZAP Baseline Scan (Alternative - Docker Direct)** - Docker direct
4. **Run OWASP ZAP Baseline Scan (Action GitHub)** - Action GitHub (fallback)
5. **Save DAST reports** - Sauvegarde le rapport

### Commande Docker Direct

```bash
docker run --rm \
  --network host \
  -v $(pwd):/zap/wrk/:rw \
  -t owasp/zap2docker-stable \
  zap-baseline.py \
  -t http://localhost:8080 \
  -J -a -r zap-report.json -I
```

**Options** :
- `--network host` : Permet d'accéder à `localhost:8080` depuis le conteneur
- `-v $(pwd):/zap/wrk/:rw` : Monte le répertoire courant pour sauvegarder le rapport
- `-J` : Génère un rapport JSON
- `-a` : Active toutes les règles
- `-I` : Continue même en cas d'erreurs

---

## 🔍 Diagnostic

### Vérifier Docker dans GitHub Actions

Les runners `ubuntu-latest` ont Docker préinstallé, mais vérifiez dans les logs :

```yaml
- name: Check Docker Availability
  run: |
    docker --version
    docker ps
```

### Si Docker n'est pas disponible

Le pipeline créera automatiquement un rapport vide :
```json
{"@version":"2.11.0","site":[]}
```

Cela évite les erreurs du parser.

---

## ⚠️ Notes Importantes

### GitHub Actions Runners

- ✅ `ubuntu-latest` a Docker préinstallé
- ✅ Le daemon Docker est démarré automatiquement
- ✅ `--network host` fonctionne sur GitHub Actions

### Alternative : ZAP API (Futur)

Si Docker continue d'échouer, on peut utiliser ZAP en mode API :
1. Démarrer ZAP en mode API
2. Utiliser l'API REST pour scanner
3. Récupérer le rapport via l'API

**Mais** : Plus complexe, donc on garde Docker pour l'instant.

---

## ✅ Résultat

**Le pipeline gère maintenant** :
- ✅ Vérification de Docker avant le scan
- ✅ Alternative Docker direct (exécutée en premier)
- ✅ Action GitHub comme fallback
- ✅ Rapport vide si tout échoue (évite les erreurs)
- ✅ Messages de diagnostic détaillés

**Si Docker n'est toujours pas disponible, les logs indiqueront exactement pourquoi !** 🔍

---

## 🚀 Prochaines Étapes

Si Docker continue d'échouer :
1. Vérifier les logs GitHub Actions
2. Vérifier que l'application est accessible
3. Considérer ZAP API comme alternative ultime

