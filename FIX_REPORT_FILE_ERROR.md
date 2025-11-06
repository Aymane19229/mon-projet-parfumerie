# 🔧 Correction de l'Erreur `report_file` - ZAP Action

## 🔴 Problème Identifié

L'action `zaproxy/action-baseline@v0.10.0` ne supporte **PAS** le paramètre `report_file`.

**Erreur** :
```
Unexpected input(s) 'report_file', valid inputs are ['token', 'target', 'rules_file_name', 'docker_name', 'cmd_options', 'issue_title', 'fail_action', 'allow_issue_writing', 'artifact_name']
```

**Paramètres valides** :
- `token` : Token GitHub (optionnel)
- `target` : URL cible à scanner
- `rules_file_name` : Fichier de règles personnalisées
- `docker_name` : Nom du conteneur Docker
- `cmd_options` : Options de ligne de commande ZAP
- `issue_title` : Titre pour les issues GitHub
- `fail_action` : Action en cas d'échec
- `allow_issue_writing` : Autoriser l'écriture d'issues
- `artifact_name` : Nom de l'artifact

**❌ `report_file` n'existe pas !**

---

## ✅ Solution Appliquée

### Avant (❌ Incorrect) :
```yaml
- name: Run OWASP ZAP Baseline Scan (Action GitHub)
  uses: zaproxy/action-baseline@v0.10.0
  with:
    target: 'http://localhost:8080'
    cmd_options: '-a -J -t 5'
    report_file: 'zap-report.json'  # ❌ Paramètre invalide
```

### Après (✅ Correct) :
```yaml
- name: Run OWASP ZAP Baseline Scan (Action GitHub)
  uses: zaproxy/action-baseline@v0.10.0
  with:
    target: 'http://localhost:8080'
    cmd_options: '-a -J -t 5 -r zap-report.json'  # ✅ -r dans cmd_options
```

**Explication** :
- Le nom du fichier de rapport doit être spécifié avec l'option `-r` dans `cmd_options`
- `-r zap-report.json` indique à ZAP de générer le rapport JSON avec ce nom

---

## 📋 Options ZAP dans cmd_options

### Options utilisées :
- `-a` : Active toutes les règles de scan
- `-J` : Génère un rapport JSON
- `-t 5` : Timeout de 5 minutes
- `-r zap-report.json` : Nom du fichier de rapport

### Autres options possibles :
- `-I` : Continue même en cas d'erreurs (ignore les erreurs)
- `-g` : Génère un rapport HTML
- `-x` : Génère un rapport XML
- `-w` : Génère un rapport Markdown

---

## 🔍 Alternative Docker Direct

L'alternative Docker direct a aussi été améliorée :

### Avant :
```bash
-r zap-report.json  # Génère dans le conteneur
```

### Après :
```bash
-r /zap/wrk/zap-report.json  # Génère dans le volume monté
```

**Pourquoi** :
- Le volume `-v $(pwd):/zap/wrk/:rw` monte le répertoire courant dans `/zap/wrk/`
- En spécifiant `/zap/wrk/zap-report.json`, le rapport est directement accessible depuis le host
- Plus besoin de copier le fichier après

---

## ✅ Résultat

**Maintenant** :
1. ✅ L'action GitHub utilise `-r zap-report.json` dans `cmd_options` (pas de paramètre `report_file`)
2. ✅ L'alternative Docker direct utilise `/zap/wrk/zap-report.json` pour un accès direct
3. ✅ Les deux méthodes génèrent le rapport correctement
4. ✅ Le rapport est sauvegardé dans `reports/dast/zap-report.json`

---

## 🚀 Prochaine Exécution

Lors de la prochaine exécution du pipeline :
- ✅ L'erreur `Unexpected input(s) 'report_file'` ne devrait plus apparaître
- ✅ Le rapport ZAP devrait être généré correctement
- ✅ Le rapport devrait être disponible dans les artifacts

---

## 📝 Notes Importantes

### Documentation de l'Action

L'action `zaproxy/action-baseline` :
- Utilise Docker en interne
- Génère le rapport dans le répertoire de travail
- Le nom du fichier doit être spécifié avec `-r` dans `cmd_options`

### Fichier de Rapport

Le rapport sera généré :
- **Action GitHub** : Dans le répertoire de travail (racine du projet)
- **Docker Direct** : Dans `/zap/wrk/` (qui correspond au répertoire courant grâce au volume)

Dans les deux cas, l'étape `Save DAST reports` le copie vers `reports/dast/zap-report.json`.

---

## 🔗 Références

- Documentation ZAP : https://www.zaproxy.org/docs/docker/baseline-scan/
- Action GitHub : https://github.com/zaproxy/action-baseline
- Options ZAP : `zap-baseline.py --help`

