# 🔧 Correction - Permission Denied pour zap.yaml

## 🔴 Problème Identifié

**Erreur** :
```
PermissionError: [Errno 13] Permission denied: '/home/zap/zap.yaml'
```

**Cause** : ZAP essaie d'écrire dans `/home/zap/zap.yaml` mais n'a pas les permissions.

**Pourquoi** : L'option `--user $(id -u):$(id -g)` fait que ZAP s'exécute avec l'utilisateur du runner, mais ZAP essaie d'écrire dans `/home/zap/` qui appartient à l'utilisateur `zap` dans le conteneur.

---

## ✅ Solution Appliquée

### Suppression de `--user` et Utilisation de `-w`

**Avant** (❌ Problématique) :
```yaml
docker run --rm \
  --user $(id -u):$(id -g) \
  -v $(pwd):/zap/wrk/:rw \
  ...
```

**Après** (✅ Corrigé) :
```yaml
docker run --rm \
  -v $(pwd):/zap/wrk/:rw \
  -w /zap/wrk \
  ...
```

**Changements** :
- ✅ Suppression de `--user $(id -u):$(id -g)` (causait le problème)
- ✅ Ajout de `-w /zap/wrk` pour forcer ZAP à utiliser le répertoire monté
- ✅ ZAP s'exécute avec son utilisateur par défaut (`zap`) mais écrit dans le volume monté

**Pourquoi** :
- Le volume monté (`-v $(pwd):/zap/wrk/:rw`) a les permissions en lecture/écriture
- ZAP peut écrire dans `/zap/wrk/` (qui correspond à `$(pwd)`)
- `-w /zap/wrk` force ZAP à utiliser ce répertoire comme répertoire de travail
- ZAP n'essaie plus d'écrire dans `/home/zap/`

---

## 📋 Modifications Détailées

### 1. Suppression de `--user`

**Problème** : `--user $(id -u):$(id -g)` causait des problèmes de permissions.

**Solution** : Laisser ZAP s'exécuter avec son utilisateur par défaut (`zap`).

**Pourquoi** : Le volume monté a les permissions nécessaires, donc pas besoin de changer l'utilisateur.

### 2. Ajout de `-w /zap/wrk`

**Ajouté** : `-w /zap/wrk` pour forcer ZAP à utiliser le répertoire monté.

**Pourquoi** : 
- Force ZAP à utiliser `/zap/wrk/` comme répertoire de travail
- ZAP écrit ses fichiers (yaml, rapport) dans ce répertoire
- Ce répertoire est monté depuis `$(pwd)`, donc accessible depuis le host

### 3. Attente Augmentée

**Changé** : `sleep 2` → `sleep 3`

**Pourquoi** : Donner plus de temps à ZAP pour écrire le rapport.

---

## ✅ Résultat Attendu

**Maintenant** :
- ✅ ZAP s'exécute avec son utilisateur par défaut
- ✅ ZAP écrit dans `/zap/wrk/` (répertoire monté)
- ✅ Plus d'erreur "Permission denied: '/home/zap/zap.yaml'"
- ✅ Le rapport JSON devrait être généré correctement

**Si ça fonctionne** :
- ✅ ZAP génère le rapport dans `zap-report.json`
- ✅ Le rapport est trouvé et copié dans `reports/dast/zap-report.json`
- ✅ Rapport disponible pour le parser

---

## 🚀 Prochaine Exécution

Lors de la prochaine exécution :
- ✅ Plus d'erreur de permissions pour zap.yaml
- ✅ ZAP peut écrire dans le répertoire monté
- ✅ Le rapport JSON devrait être généré
- ✅ Le rapport devrait être récupéré correctement

**Le pipeline devrait maintenant générer le rapport ZAP correctement !** 🎉

---

## 📝 Notes Importantes

### Pourquoi Supprimer `--user` ?

- `--user $(id -u):$(id -g)` causait des problèmes car ZAP essayait d'écrire dans `/home/zap/`
- Le volume monté a les permissions nécessaires, donc pas besoin de changer l'utilisateur
- ZAP peut écrire dans le volume monté même avec son utilisateur par défaut

### Pourquoi Utiliser `-w /zap/wrk` ?

- Force ZAP à utiliser le répertoire monté comme répertoire de travail
- ZAP écrit tous ses fichiers (yaml, rapport) dans ce répertoire
- Plus simple et évite les problèmes de permissions

### Sécurité

- ZAP s'exécute toujours dans un conteneur isolé
- Le volume monté est en lecture/écriture mais seulement pour le répertoire du projet
- Pas de risque de sécurité supplémentaire

---

## 🔗 Références

- Documentation Docker : https://docs.docker.com/engine/reference/run/#workdir
- Documentation ZAP : https://www.zaproxy.org/docs/docker/baseline-scan/

