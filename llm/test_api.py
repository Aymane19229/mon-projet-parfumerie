#!/usr/bin/env python3
"""
Script de test pour vérifier que les API LLM fonctionnent

Pourquoi : Tester la configuration avant de générer des politiques complètes
Comment : Fait un appel simple à chaque API pour vérifier l'authentification
"""

import sys
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent))

def test_deepseek():
    """Test DeepSeek R1 API"""
    print("\n" + "="*60)
    print("🧪 TEST 1 : DeepSeek R1 API")
    print("="*60)
    
    try:
        from models.deepseek import DeepSeekLLM
        
        llm = DeepSeekLLM()
        
        if not llm.api_key:
            print("❌ DEEPSEEK_API_KEY non configurée")
            return False
        
        print(f"✅ Clé API chargée: {llm.api_key[:15]}...")
        print("🔄 Test d'un appel simple...")
        
        result = llm.generate("Explique la cybersécurité en une phrase.", max_tokens=100)
        
        if "Erreur" in result:
            print(f"❌ Erreur: {result}")
            return False
        
        print(f"✅ Réponse reçue ({len(result)} caractères):")
        print(f"   {result[:200]}...")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        return False


def test_huggingface():
    """Test Hugging Face API"""
    print("\n" + "="*60)
    print("🧪 TEST 2 : Hugging Face API")
    print("="*60)
    
    try:
        from models.huggingface import HuggingFaceAPI
        
        llm = HuggingFaceAPI()
        
        print("🔄 Test avec un modèle public (gpt2)...")
        
        result = llm.generate("Hello, how are you?", model="gpt2", max_length=50)
        
        if "Erreur" in result:
            print(f"⚠️  Erreur: {result}")
            print("   (Normal si le modèle est en cours de chargement)")
            return False
        
        print(f"✅ Réponse reçue ({len(result)} caractères):")
        print(f"   {result[:200]}...")
        return True
        
    except Exception as e:
        print(f"⚠️  Erreur lors du test: {e}")
        return False


def main():
    """Exécute tous les tests"""
    print("\n🚀 DÉMARRAGE DES TESTS API")
    print("="*60)
    
    results = {
        "DeepSeek": test_deepseek(),
        "HuggingFace": test_huggingface(),
    }
    
    print("\n" + "="*60)
    print("📊 RÉSULTATS DES TESTS")
    print("="*60)
    
    for provider, success in results.items():
        status = "✅ OK" if success else "❌ ÉCHEC"
        print(f"{provider}: {status}")
    
    print("\n" + "="*60)
    
    if results["DeepSeek"]:
        print("✅ DeepSeek R1 est prêt ! Vous pouvez générer des politiques.")
    else:
        print("⚠️  Vérifiez la configuration de DeepSeek R1")
    
    print("="*60 + "\n")


if __name__ == "__main__":
    main()

