# 🔧 Correction - Rapport ZAP Vide (32 bytes)

## 🔴 Problème Identifié

**Symptômes** :
- ✅ ZAP scanne avec succès (66 PASS, 1 WARN)
- ❌ Mais le rapport JSON est vide : `{"@version":"2.11.0","site":[]}` (32 bytes)
- ❌ Erreur : `AccessDeniedException /zap/wrk/zap-report.json.html`
- ❌ Erreur : `Unable to copy yaml file to /zap/wrk/zap.yaml [Errno 13] Permission denied`

**Cause** : ZAP n'a pas les permissions pour écrire dans le volume monté `/zap/wrk/`.

**Pourquoi** :
- Le répertoire monté appartient à `runner` (UID différent)
- ZAP s'exécute avec l'utilisateur `zap` (UID probablement 1000)
- Les permissions du répertoire sont `drwxr-xr-x` (755), donc seul le propriétaire peut écrire

---

## ✅ Solution Appliquée

### 1. Créer un Répertoire Dédié avec Permissions Ouvertes

**Ajouté** :
```bash
mkdir -p zap-output
chmod 777 zap-output
```

**Pourquoi** :
- Créer un répertoire dédié pour ZAP
- Donner les permissions 777 (lecture/écriture pour tous)
- ZAP peut maintenant écrire dans ce répertoire

### 2. Monter Seulement le Répertoire Dédié

**Avant** (❌ Problématique) :
```yaml
-v $(pwd):/zap/wrk/:rw
```

**Après** (✅ Corrigé) :
```yaml
-v $(pwd)/zap-output:/zap/wrk/:rw
```

**Pourquoi** :
- Monter seulement `zap-output/` au lieu de tout `$(pwd)`
- Ce répertoire a les permissions 777, donc ZAP peut écrire
- Plus sûr et plus propre

### 3. Recherche Améliorée du Rapport

**Améliorations** :
- ✅ Chercher d'abord dans `zap-output/zap-report.json`
- ✅ Vérifier que la taille est > 100 bytes (éviter les rapports vides)
- ✅ Fallback vers le répertoire courant si nécessaire
- ✅ Diagnostic amélioré avec `ls -lah zap-output/`

**Pourquoi** :
- Le rapport est maintenant dans `zap-output/`
- Vérifier la taille évite de copier des rapports vides
- Diagnostic amélioré pour identifier les problèmes

---

## 📋 Modifications Détailées

### 1. Création du Répertoire Dédié

```bash
mkdir -p zap-output
chmod 777 zap-output
```

**Pourquoi** : Donner les permissions nécessaires à ZAP pour écrire.

### 2. Commande Docker Modifiée

```yaml
docker run --rm \
  --network host \
  -v $(pwd)/zap-output:/zap/wrk/:rw \
  -w /zap/wrk \
  -t "$ZAP_IMAGE" \
  zap-baseline.py \
  -t "$TARGET_URL" \
  -J -a -r zap-report.json \
  -I
```

**Changements** :
- `-v $(pwd)/zap-output:/zap/wrk/:rw` au lieu de `-v $(pwd):/zap/wrk/:rw`
- ZAP écrit maintenant dans `zap-output/` qui a les permissions 777

### 3. Recherche du Rapport

```bash
# Chercher dans zap-output
if [ -f zap-output/zap-report.json ]; then
  SIZE=$(wc -c < zap-output/zap-report.json)
  if [ "$SIZE" -gt 100 ]; then
    cp zap-output/zap-report.json reports/dast/zap-report.json
    REPORT_FOUND=true
  fi
fi
```

**Pourquoi** :
- Chercher dans le bon répertoire (`zap-output/`)
- Vérifier la taille (> 100 bytes) pour éviter les rapports vides
- Copier dans `reports/dast/` pour le parser

---

## ✅ Résultat Attendu

**Maintenant** :
- ✅ ZAP peut écrire dans `zap-output/` (permissions 777)
- ✅ Le rapport JSON devrait être généré correctement
- ✅ Le rapport devrait avoir une taille > 100 bytes
- ✅ Le rapport devrait être copié dans `reports/dast/zap-report.json`

**Si ça fonctionne** :
- ✅ Rapport JSON généré avec les résultats du scan (66 PASS, 1 WARN)
- ✅ Rapport disponible pour le parser
- ✅ Plus de rapport vide (32 bytes)

---

## 🚀 Prochaine Exécution

Lors de la prochaine exécution :
- ✅ ZAP peut écrire dans `zap-output/`
- ✅ Le rapport JSON devrait être généré
- ✅ Le rapport devrait avoir une taille > 100 bytes
- ✅ Le rapport devrait être récupéré correctement

**Le pipeline devrait maintenant générer un rapport ZAP valide !** 🎉

---

## 📝 Notes Importantes

### Pourquoi Permissions 777 ?

- ZAP s'exécute avec l'utilisateur `zap` (UID différent de `runner`)
- Les permissions 777 permettent à tous les utilisateurs d'écrire
- C'est acceptable dans un environnement CI/CD isolé
- Le répertoire `zap-output/` est temporaire et nettoyé après

### Pourquoi Vérifier la Taille > 100 bytes ?

- Un rapport vide fait 32 bytes : `{"@version":"2.11.0","site":[]}`
- Un rapport valide fait plusieurs KB (au moins quelques centaines de bytes)
- Vérifier la taille évite de copier des rapports vides

### Sécurité

- Le répertoire `zap-output/` est créé dans le workspace du projet
- Il est nettoyé après l'exécution (ou peut être ajouté à `.gitignore`)
- Pas de risque de sécurité supplémentaire

---

## 🔗 Références

- Documentation ZAP : https://www.zaproxy.org/docs/docker/baseline-scan/
- Docker volumes : https://docs.docker.com/storage/volumes/

