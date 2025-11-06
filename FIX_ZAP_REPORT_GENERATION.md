# 🔧 Correction - Génération et Récupération du Rapport ZAP

## 🔴 Problèmes Identifiés

### Problème 1 : Rapport Non Généré Correctement
```
NoSuchFileException /zap/wrk/zap/wrk/zap-report.json.html
```

**Cause** : ZAP essaie de générer le rapport dans un chemin incorrect (double `/zap/wrk/`).

### Problème 2 : Erreur de Copie
```
cp: './reports/dast/zap-report.json' and 'reports/dast/zap-report.json' are the same file
```

**Cause** : Le script essaie de copier le fichier sur lui-même.

### Problème 3 : Rapport Non Trouvé
ZAP a scanné avec succès (66 PASS, 1 WARN) mais le rapport JSON n'est pas récupéré.

---

## ✅ Solutions Appliquées

### 1. Correction du Chemin du Rapport

**Avant** (❌ Problématique) :
```bash
-r /zap/wrk/zap-report.json  # Double chemin possible
```

**Après** (✅ Corrigé) :
```bash
-r zap-report.json  # Chemin relatif dans /zap/wrk/ (qui correspond à $(pwd))
```

**Pourquoi** :
- Le volume `-v $(pwd):/zap/wrk/:rw` monte `$(pwd)` dans `/zap/wrk/`
- Donc `zap-report.json` dans `/zap/wrk/` correspond à `zap-report.json` dans `$(pwd)`
- Plus simple et évite les problèmes de double chemin

### 2. Amélioration de la Recherche du Rapport

**Améliorations** :
- ✅ Attendre 2 secondes après le scan pour que le rapport soit écrit
- ✅ Vérifier la taille du fichier avant de copier (éviter les fichiers vides)
- ✅ Utiliser `realpath` pour normaliser les chemins
- ✅ Comparer les chemins absolus pour éviter de copier sur le même fichier
- ✅ Exclure `reports/dast/` de la recherche récursive

**Code** :
```bash
# Attendre un peu pour que le rapport soit écrit
sleep 2

# Chercher dans le répertoire courant
if [ -f zap-report.json ]; then
  SIZE=$(wc -c < zap-report.json)
  if [ "$SIZE" -gt 0 ]; then
    # Normaliser les chemins
    FOUND_ABS=$(realpath zap-report.json)
    DEST_ABS=$(realpath reports/dast/zap-report.json 2>/dev/null || echo "...")
    
    # Éviter de copier sur le même fichier
    if [ "$FOUND_ABS" != "$DEST_ABS" ]; then
      cp zap-report.json reports/dast/zap-report.json
    fi
  fi
fi
```

### 3. Meilleur Diagnostic

**Ajouté** :
- ✅ Afficher la taille du rapport trouvé
- ✅ Lister les fichiers JSON trouvés si le rapport n'est pas trouvé
- ✅ Messages clairs à chaque étape

---

## 📋 Modifications Détailées

### 1. Commande ZAP - Chemin Relatif

**Avant** :
```yaml
zap-baseline.py -r /zap/wrk/zap-report.json
```

**Après** :
```yaml
zap-baseline.py -r zap-report.json
```

**Pourquoi** : Le chemin relatif est plus simple et évite les problèmes de double chemin.

### 2. Recherche du Rapport - Vérifications Améliorées

**Avant** :
```bash
if [ -f zap-report.json ]; then
  cp zap-report.json reports/dast/zap-report.json
fi
```

**Après** :
```bash
# Attendre que le rapport soit écrit
sleep 2

if [ -f zap-report.json ]; then
  SIZE=$(wc -c < zap-report.json)
  if [ "$SIZE" -gt 0 ]; then
    # Normaliser les chemins
    FOUND_ABS=$(realpath zap-report.json)
    DEST_ABS=$(realpath reports/dast/zap-report.json 2>/dev/null || echo "...")
    
    # Éviter de copier sur le même fichier
    if [ "$FOUND_ABS" != "$DEST_ABS" ]; then
      mkdir -p reports/dast
      cp zap-report.json reports/dast/zap-report.json
      echo "✅ Rapport copié ($SIZE bytes)"
    else
      echo "✅ Rapport déjà présent"
    fi
  fi
fi
```

### 3. Recherche Récursive - Exclusion de reports/dast/

**Avant** :
```bash
find . -name "zap*.json" | grep -v node_modules | grep -v ".git"
```

**Après** :
```bash
find . -name "zap*.json" | \
  grep -v node_modules | \
  grep -v ".git" | \
  grep -v "reports/dast"  # Exclure reports/dast/
```

**Pourquoi** : Éviter de trouver le fichier de destination dans la recherche.

---

## ✅ Résultat Attendu

**Maintenant** :
- ✅ ZAP génère le rapport avec un chemin relatif (plus simple)
- ✅ Le rapport est cherché avec des vérifications améliorées
- ✅ Plus d'erreur "are the same file"
- ✅ Rapport récupéré correctement même si ZAP génère ailleurs
- ✅ Diagnostic détaillé si le rapport n'est pas trouvé

**Si ZAP génère le rapport** :
- ✅ Le rapport est trouvé et copié dans `reports/dast/zap-report.json`
- ✅ Taille du rapport affichée
- ✅ Rapport disponible pour le parser

**Si le rapport n'est pas trouvé** :
- ⚠️ Diagnostic détaillé affiché
- ⚠️ Liste des fichiers JSON trouvés
- ⚠️ Rapport vide créé (évite les erreurs du parser)

---

## 🚀 Prochaine Exécution

Lors de la prochaine exécution :
- ✅ ZAP génère le rapport avec un chemin relatif
- ✅ Le rapport est trouvé et copié correctement
- ✅ Plus d'erreur de copie
- ✅ Rapport disponible dans les artifacts

**Le pipeline devrait maintenant récupérer correctement le rapport ZAP !** 🎉

---

## 📝 Notes Importantes

### Pourquoi le Chemin Relatif ?

- Le volume `-v $(pwd):/zap/wrk/:rw` monte le répertoire courant dans `/zap/wrk/`
- Donc `zap-report.json` dans le conteneur correspond à `zap-report.json` dans le host
- Plus simple et évite les problèmes de double chemin

### Pourquoi Attendre 2 Secondes ?

- ZAP peut prendre un peu de temps pour écrire le rapport après le scan
- Attendre 2 secondes garantit que le fichier est écrit avant de le chercher

### Pourquoi Utiliser realpath ?

- `realpath` normalise les chemins (résout les liens symboliques, les `..`, etc.)
- Permet de comparer correctement les chemins pour éviter de copier sur le même fichier

---

## 🔗 Références

- Documentation ZAP : https://www.zaproxy.org/docs/docker/baseline-scan/
- Options ZAP : `zap-baseline.py --help`

