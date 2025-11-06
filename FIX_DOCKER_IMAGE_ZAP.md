# 🔧 Correction - Image Docker ZAP Non Disponible

## 🔴 Problème Identifié

**Erreur** :
```
Error response from daemon: pull access denied for owasp/zap2docker-stable, 
repository does not exist or may require 'docker login': denied: 
requested access to the resource is denied
```

**Cause** : L'image Docker `owasp/zap2docker-stable` n'est plus disponible ou le nom a changé.

---

## ✅ Solution Appliquée

### Essayer Plusieurs Noms d'Images

**Avant** (❌ Un seul nom) :
```bash
docker pull owasp/zap2docker-stable
```

**Après** (✅ Plusieurs tentatives) :
```bash
# Essayer plusieurs noms d'images possibles
for image in "ghcr.io/zaproxy/zaproxy:stable" "owasp/zap2docker-stable" "owasp/zap2docker-weekly"; do
  if docker pull "$image"; then
    ZAP_IMAGE="$image"
    break
  fi
done
```

**Images testées** (dans l'ordre) :
1. `ghcr.io/zaproxy/zaproxy:stable` - Image officielle sur GitHub Container Registry
2. `owasp/zap2docker-stable` - Ancien nom (peut encore fonctionner)
3. `owasp/zap2docker-weekly` - Version hebdomadaire (alternative)

---

## 📋 Modifications Détailées

### 1. Téléchargement de l'Image avec Fallback

```yaml
# Essayer plusieurs noms d'images
ZAP_IMAGE=""
for image in "ghcr.io/zaproxy/zaproxy:stable" "owasp/zap2docker-stable" "owasp/zap2docker-weekly"; do
  echo "🔍 Tentative avec: $image"
  if docker pull "$image"; then
    ZAP_IMAGE="$image"
    echo "✅ Image ZAP téléchargée: $ZAP_IMAGE"
    break
  else
    echo "⚠️  Échec avec $image, essai suivant..."
  fi
done
```

### 2. Utilisation de l'Image Téléchargée

```yaml
# Utiliser l'image qui a fonctionné
docker run --rm \
  --network host \
  -v $(pwd):/zap/wrk/:rw \
  -t "$ZAP_IMAGE" \
  zap-baseline.py \
  -t "$TARGET_URL" \
  ...
```

---

## 🔍 Images ZAP Disponibles

### Image Officielle (Recommandée)

**`ghcr.io/zaproxy/zaproxy:stable`**
- ✅ Image officielle sur GitHub Container Registry
- ✅ Maintenue par l'équipe OWASP ZAP
- ✅ Version stable et à jour

### Anciennes Images (Peuvent Encore Fonctionner)

**`owasp/zap2docker-stable`**
- ⚠️ Ancien nom, peut ne plus être disponible
- ⚠️ Peut nécessiter une authentification Docker Hub

**`owasp/zap2docker-weekly`**
- ⚠️ Version hebdomadaire (moins stable)
- ⚠️ Alternative si stable ne fonctionne pas

---

## ✅ Résultat Attendu

**Maintenant** :
- ✅ Le pipeline essaie plusieurs noms d'images
- ✅ Utilise la première image qui fonctionne
- ✅ Messages clairs pour identifier quelle image est utilisée
- ✅ Rapport vide créé seulement si toutes les images échouent

**Si une image fonctionne** :
- ✅ ZAP scanne correctement
- ✅ Rapport généré (non vide)

**Si toutes les images échouent** :
- ⚠️ Diagnostic détaillé affiché
- ⚠️ Rapport vide créé
- ✅ Pipeline continue (pas d'erreur bloquante)

---

## 🚀 Prochaine Exécution

Lors de la prochaine exécution :
- ✅ Le pipeline essaiera `ghcr.io/zaproxy/zaproxy:stable` en premier (image officielle)
- ✅ Si ça échoue, essaiera `owasp/zap2docker-stable`
- ✅ Si ça échoue, essaiera `owasp/zap2docker-weekly`
- ✅ Utilisera la première image qui fonctionne

**Le pipeline devrait maintenant pouvoir télécharger l'image ZAP !** 🎉

---

## 📝 Notes Importantes

### Pourquoi Plusieurs Images ?

- Les noms d'images Docker peuvent changer
- Les images peuvent être déplacées vers d'autres registries
- GitHub Container Registry (`ghcr.io`) est maintenant le registre officiel pour ZAP

### Image Recommandée

**`ghcr.io/zaproxy/zaproxy:stable`** est maintenant l'image officielle recommandée.

---

## 🔗 Références

- GitHub Container Registry : https://github.com/orgs/zaproxy/packages
- Documentation ZAP Docker : https://www.zaproxy.org/docs/docker/

