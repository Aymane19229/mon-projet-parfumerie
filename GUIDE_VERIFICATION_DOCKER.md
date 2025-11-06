# 🐳 Guide de Vérification Docker - Étape par Étape

## 🎯 Objectif

Vérifier que Docker est correctement installé et configuré sur votre système pour que ZAP puisse fonctionner.

---

## 📋 Étape 1 : Vérifier si Docker est Installé

### Commande à exécuter :
```bash
docker --version
```

### Ce que vous devriez voir :
```
Docker version 24.0.0, build abc123
```
(La version peut varier)

### Si vous voyez une erreur :
```
command not found: docker
```

**Cela signifie** : Docker n'est pas installé sur votre système.

**Solution** : Installez Docker Desktop pour macOS :
1. Allez sur https://www.docker.com/products/docker-desktop/
2. Téléchargez Docker Desktop pour Mac
3. Installez l'application
4. Lancez Docker Desktop
5. Attendez que l'icône Docker dans la barre de menu soit verte

---

## 📋 Étape 2 : Vérifier que Docker Daemon est Démarré

### Commande à exécuter :
```bash
docker ps
```

### Ce que vous devriez voir :
```
CONTAINER ID   IMAGE     COMMAND   CREATED   STATUS    PORTS     NAMES
```
(Peut être vide, c'est normal si aucun conteneur n'est en cours)

### Si vous voyez une erreur :
```
Cannot connect to the Docker daemon. Is the docker daemon running?
```

**Cela signifie** : Docker est installé mais le daemon n'est pas démarré.

**Solution** :
1. Ouvrez Docker Desktop
2. Attendez que l'icône dans la barre de menu soit verte
3. Vérifiez dans Docker Desktop que "Docker is running"

---

## 📋 Étape 3 : Tester Docker avec une Image Simple

### Commande à exécuter :
```bash
docker run hello-world
```

### Ce que vous devriez voir :
```
Hello from Docker!
This message shows that your installation appears to be working correctly.
...
```

### Si vous voyez une erreur :
- **"Unable to find image"** : Docker essaie de télécharger l'image, attendez
- **"Cannot connect"** : Le daemon Docker n'est pas démarré (voir Étape 2)
- **"Permission denied"** : Problème de permissions (voir Étape 4)

---

## 📋 Étape 4 : Vérifier les Permissions Docker

### Commande à exécuter :
```bash
docker info
```

### Ce que vous devriez voir :
```
Client:
 Version:    24.0.0
 ...

Server:
 Containers: 0
 Running: 0
 ...
```

### Si vous voyez une erreur :
```
permission denied while trying to connect to the Docker daemon socket
```

**Cela signifie** : Vous n'avez pas les permissions pour utiliser Docker.

**Solution** :
1. Vérifiez que vous êtes dans le groupe `docker` (sur Linux)
2. Sur macOS avec Docker Desktop, cela devrait fonctionner automatiquement
3. Si nécessaire, redémarrez Docker Desktop

---

## 📋 Étape 5 : Télécharger l'Image ZAP (Test)

### Commande à exécuter :
```bash
docker pull owasp/zap2docker-stable
```

### Ce que vous devriez voir :
```
Using default tag: latest
latest: Pulling from owasp/zap2docker-stable
...
Status: Downloaded newer image for owasp/zap2docker-stable:latest
```

### Si vous voyez une erreur :
- **"Network error"** : Problème de connexion Internet
- **"Cannot connect"** : Docker daemon n'est pas démarré

**Temps estimé** : 2-5 minutes (première fois, l'image fait ~1GB)

---

## 📋 Étape 6 : Vérifier que l'Image ZAP est Disponible

### Commande à exécuter :
```bash
docker images | grep zap
```

### Ce que vous devriez voir :
```
owasp/zap2docker-stable   latest   abc123def456   2 weeks ago   1.2GB
```

### Si vous ne voyez rien :
L'image n'est pas téléchargée. Répétez l'Étape 5.

---

## 📋 Étape 7 : Test Complet - Exécuter ZAP (Optionnel)

### Commande à exécuter :
```bash
docker run --rm owasp/zap2docker-stable zap-baseline.py --help
```

### Ce que vous devriez voir :
```
Usage: zap-baseline.py -t <target> [options]
...
```

### Si vous voyez une erreur :
- Vérifiez que l'image est téléchargée (Étape 6)
- Vérifiez que Docker fonctionne (Étapes 1-4)

---

## 🔍 Résumé des Commandes Essentielles

### Vérification Rapide (3 commandes) :
```bash
# 1. Vérifier l'installation
docker --version

# 2. Vérifier que Docker fonctionne
docker ps

# 3. Tester avec une image simple
docker run hello-world
```

Si ces 3 commandes fonctionnent, Docker est correctement configuré ! ✅

---

## ⚠️ Problèmes Courants et Solutions

### Problème 1 : "Docker n'est pas installé"

**Sur macOS** :
1. Téléchargez Docker Desktop : https://www.docker.com/products/docker-desktop/
2. Installez l'application
3. Lancez Docker Desktop
4. Attendez que l'icône soit verte

**Sur Linux** :
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install docker.io

# RedHat/CentOS
sudo yum install docker
```

### Problème 2 : "Docker daemon n'est pas démarré"

**Solution** :
1. Ouvrez Docker Desktop
2. Vérifiez dans les paramètres que Docker démarre automatiquement
3. Redémarrez Docker Desktop si nécessaire

### Problème 3 : "Permission denied"

**Sur macOS** : Normalement pas de problème avec Docker Desktop

**Sur Linux** :
```bash
# Ajouter votre utilisateur au groupe docker
sudo usermod -aG docker $USER

# Redémarrer la session (se déconnecter/reconnecter)
```

---

## ✅ Checklist de Vérification

Cochez chaque étape une fois terminée :

- [ ] Étape 1 : `docker --version` fonctionne
- [ ] Étape 2 : `docker ps` fonctionne (peut être vide)
- [ ] Étape 3 : `docker run hello-world` fonctionne
- [ ] Étape 4 : `docker info` fonctionne
- [ ] Étape 5 : `docker pull owasp/zap2docker-stable` fonctionne
- [ ] Étape 6 : `docker images | grep zap` montre l'image
- [ ] Étape 7 : `docker run --rm owasp/zap2docker-stable zap-baseline.py --help` fonctionne

**Si toutes les étapes sont cochées** : Docker est correctement configuré ! 🎉

---

## 🚀 Pour GitHub Actions

**Note importante** : Sur GitHub Actions, Docker est préinstallé sur les runners `ubuntu-latest`.

Vous n'avez **rien à configurer** côté GitHub Actions - Docker est automatiquement disponible.

Le pipeline vérifie Docker automatiquement avec l'étape `Check Docker Availability`.

---

## 📞 Besoin d'Aide ?

Si une étape échoue :
1. Notez le message d'erreur exact
2. Vérifiez les solutions dans "Problèmes Courants"
3. Consultez la documentation Docker : https://docs.docker.com/

---

## 🎯 Prochaine Étape

Une fois Docker vérifié, le pipeline GitHub Actions devrait fonctionner correctement pour ZAP !

