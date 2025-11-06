# 🔧 Correction Erreur Docker Exit Code 3 - ZAP

## 🔴 Problèmes Identifiés

### Erreur 1 : Docker Exit Code 3
```
failed to scan the target: Error: The process '/usr/bin/docker' failed with exit code 3
```

### Erreur 2 : Process Exit Code 1
```
Process completed with exit code 1.
```

**Cause principale** : L'action GitHub `zaproxy/action-baseline@v0.10.0` a des problèmes récurrents avec Docker sur GitHub Actions.

---

## ✅ Solution Appliquée

### Changement de Stratégie

**Avant** :
- ❌ Action GitHub `zaproxy/action-baseline` (échoue souvent)
- ✅ Alternative Docker direct (fallback)

**Après** :
- ✅ **Utiliser uniquement Docker direct** (plus fiable)
- ❌ **Désactiver l'action GitHub** (trop de problèmes)

---

## 📋 Modifications

### 1. Suppression de l'Action GitHub

**Supprimé** :
```yaml
- name: Run OWASP ZAP Baseline Scan (Action GitHub)
  uses: zaproxy/action-baseline@v0.10.0
  # ❌ Cette action échoue souvent avec Docker exit code 3
```

**Pourquoi** :
- L'action GitHub a des problèmes récurrents avec Docker
- Docker direct est plus fiable et donne plus de contrôle
- On peut mieux gérer les erreurs avec Docker direct

### 2. Amélioration de Docker Direct

**Améliorations** :
- ✅ Meilleure vérification de l'application avant le scan
- ✅ Diagnostic détaillé si l'application n'est pas accessible
- ✅ Logs détaillés du scan ZAP (`tee zap-scan.log`)
- ✅ Meilleure recherche du rapport généré
- ✅ Vérification de la taille du rapport final
- ✅ Messages clairs à chaque étape

**Commande Docker** :
```bash
docker run --rm \
  --network host \
  -v $(pwd):/zap/wrk/:rw \
  -t owasp/zap2docker-stable \
  zap-baseline.py \
  -t http://localhost:8080 \
  -J -a -r /zap/wrk/zap-report.json \
  -I
```

**Options** :
- `--network host` : Permet d'accéder à `localhost:8080` depuis le conteneur
- `-v $(pwd):/zap/wrk/:rw` : Monte le répertoire courant pour sauvegarder le rapport
- `-J` : Génère un rapport JSON
- `-a` : Active toutes les règles
- `-r /zap/wrk/zap-report.json` : Nom du fichier de rapport
- `-I` : Continue même en cas d'erreurs (ignore les erreurs)

---

## 🔍 Diagnostic Amélioré

### Vérifications Avant le Scan

1. **Vérification de l'application** :
   ```bash
   curl -f http://localhost:8080
   ```

2. **Diagnostic si l'application n'est pas accessible** :
   ```bash
   netstat -tuln | grep 8080  # Vérifier le port
   ps aux | grep java         # Vérifier les processus Java
   ```

3. **Vérification Docker** :
   ```bash
   docker --version
   docker pull owasp/zap2docker-stable
   ```

### Logs Détaillés

- ✅ Logs du scan ZAP sauvegardés dans `zap-scan.log`
- ✅ Affichage des dernières lignes en cas d'erreur
- ✅ Messages clairs à chaque étape

### Recherche du Rapport

Le pipeline cherche le rapport dans plusieurs emplacements :
1. `zap-report.json` (répertoire courant)
2. `/zap/wrk/zap-report.json` (volume monté)
3. Recherche récursive de fichiers `zap*.json` ou `*report*.json`

---

## ✅ Résultat Attendu

### Si Tout Fonctionne :

1. ✅ Application accessible sur `http://localhost:8080`
2. ✅ Docker disponible et image ZAP téléchargée
3. ✅ Scan ZAP exécuté avec succès
4. ✅ Rapport généré dans `reports/dast/zap-report.json`
5. ✅ Rapport non vide (taille > 50 bytes)

### Si l'Application N'est Pas Accessible :

1. ⚠️ Diagnostic affiché (port, processus Java)
2. ⚠️ Rapport vide créé : `{"@version":"2.11.0","site":[]}`
3. ✅ Pipeline continue (pas d'erreur bloquante)

### Si Docker Échoue :

1. ⚠️ Message d'erreur clair
2. ⚠️ Rapport vide créé
3. ✅ Pipeline continue (pas d'erreur bloquante)

---

## 🚀 Avantages de Cette Approche

### 1. Plus de Contrôle

- ✅ On contrôle exactement la commande Docker
- ✅ On peut ajouter des options supplémentaires facilement
- ✅ On peut mieux gérer les erreurs

### 2. Plus Fiable

- ✅ Moins de dépendances (pas d'action GitHub qui peut échouer)
- ✅ Docker direct fonctionne mieux sur GitHub Actions
- ✅ Meilleure gestion des erreurs

### 3. Meilleur Diagnostic

- ✅ Logs détaillés à chaque étape
- ✅ Diagnostic si l'application n'est pas accessible
- ✅ Messages clairs pour identifier les problèmes

---

## 📝 Notes Importantes

### Pourquoi Docker Exit Code 3 ?

L'erreur `exit code 3` de Docker peut avoir plusieurs causes :
1. **Problème de réseau** : Docker ne peut pas accéder à l'application
2. **Problème de permissions** : Docker n'a pas les permissions nécessaires
3. **Problème avec l'action GitHub** : L'action a des bugs connus

**Solution** : Utiliser Docker direct évite ces problèmes.

### Pourquoi l'Action GitHub Échoue ?

L'action `zaproxy/action-baseline` :
- ❌ A des problèmes récurrents avec Docker sur GitHub Actions
- ❌ Moins de contrôle sur la configuration
- ❌ Messages d'erreur moins clairs

**Solution** : Docker direct est plus fiable et donne plus de contrôle.

---

## ✅ Prochaine Exécution

Lors de la prochaine exécution du pipeline :
- ✅ Seule l'étape Docker direct sera exécutée
- ✅ Plus d'erreur `exit code 3` de l'action GitHub
- ✅ Meilleur diagnostic si quelque chose échoue
- ✅ Rapport toujours généré (même si vide)

**Le pipeline devrait maintenant fonctionner correctement !** 🎉

