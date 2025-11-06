#!/bin/bash
# Script de test Docker étape par étape

echo "🐳 VÉRIFICATION DOCKER - ÉTAPE PAR ÉTAPE"
echo "=========================================="
echo ""

# Étape 1
echo "📋 ÉTAPE 1 : Vérifier si Docker est installé"
echo "Commande : docker --version"
if command -v docker &> /dev/null; then
    docker --version
    echo "✅ Docker est installé"
else
    echo "❌ Docker n'est PAS installé"
    echo "💡 Solution : Installez Docker Desktop depuis https://www.docker.com/products/docker-desktop/"
    exit 1
fi
echo ""

# Étape 2
echo "📋 ÉTAPE 2 : Vérifier que Docker Daemon est démarré"
echo "Commande : docker ps"
if docker ps &> /dev/null; then
    echo "✅ Docker Daemon est démarré"
    docker ps
else
    echo "❌ Docker Daemon n'est PAS démarré"
    echo "💡 Solution : Ouvrez Docker Desktop et attendez que l'icône soit verte"
    exit 1
fi
echo ""

# Étape 3
echo "📋 ÉTAPE 3 : Tester Docker avec hello-world"
echo "Commande : docker run hello-world"
if docker run --rm hello-world &> /dev/null; then
    echo "✅ Docker fonctionne correctement"
else
    echo "⚠️  Problème avec hello-world (peut être normal si l'image n'est pas téléchargée)"
fi
echo ""

# Étape 4
echo "📋 ÉTAPE 4 : Vérifier les informations Docker"
echo "Commande : docker info"
if docker info &> /dev/null; then
    echo "✅ Docker est accessible"
    docker info | head -10
else
    echo "❌ Impossible d'accéder à Docker"
    exit 1
fi
echo ""

# Étape 5
echo "📋 ÉTAPE 5 : Vérifier si l'image ZAP est disponible"
echo "Commande : docker images | grep zap"
if docker images | grep -q zap; then
    echo "✅ Image ZAP trouvée :"
    docker images | grep zap
else
    echo "⚠️  Image ZAP non trouvée"
    echo "💡 Vous pouvez la télécharger avec : docker pull owasp/zap2docker-stable"
fi
echo ""

echo "=========================================="
echo "✅ VÉRIFICATION TERMINÉE"
echo "=========================================="
