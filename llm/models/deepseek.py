"""
Intégration avec DeepSeek R1 API

Pourquoi : DeepSeek R1 est un modèle performant, open-source, et beaucoup moins cher qu'OpenAI
Comment : Utilise l'API DeepSeek (similaire à OpenAI) pour générer les politiques
"""
from typing import Optional
import os
from pathlib import Path


class DeepSeekLLM:
    """
    Wrapper pour utiliser l'API DeepSeek R1
    
    Pourquoi : DeepSeek R1 offre d'excellentes performances pour un coût beaucoup plus faible
    Comment : Appelle l'API DeepSeek avec les prompts structurés
    
    Avantages vs OpenAI :
    - ✅ 40x moins cher (0.55$ vs 15$ par million tokens)
    - ✅ Performance comparable
    - ✅ Open-source
    - ✅ API similaire à OpenAI (facile à intégrer)
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "deepseek-chat"):
        """
        Initialise l'API DeepSeek
        
        Args:
            api_key: Clé API DeepSeek (peut être dans .env ou variable d'environnement)
            model: Modèle à utiliser
                - "deepseek-chat" : Modèle conversationnel standard
                - "deepseek-reasoner" : Modèle avec raisonnement (R1, plus puissant)
        """
        # Charger depuis le fichier .env si disponible
        self._load_env_file()
        
        # Priorité : paramètre > variable d'environnement
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        self.model = model
        
        # URL de l'API DeepSeek
        self.api_base = "https://api.deepseek.com/v1"
        
        if not self.api_key:
            print("⚠️  DEEPSEEK_API_KEY non définie.")
            print("💡 Options:")
            print("   1. Créer un compte sur https://platform.deepseek.com")
            print("   2. Créer un fichier .env dans llm/ avec: DEEPSEEK_API_KEY=votre_cle")
            print("   3. Définir la variable d'environnement: export DEEPSEEK_API_KEY=votre_cle")
            print("   4. Passer api_key directement au constructeur")
    
    def _load_env_file(self):
        """
        Charge les variables d'environnement depuis un fichier .env
        
        Pourquoi : Permettre de stocker la clé API dans un fichier .env local
        Comment : Utilise python-dotenv si disponible, sinon lit le fichier manuellement
        """
        # Chercher .env dans le dossier llm/ puis à la racine
        env_paths = [
            Path(__file__).parent.parent / ".env",  # llm/.env
            Path(__file__).parent.parent.parent / ".env",  # racine/.env
        ]
        
        for env_path in env_paths:
            if env_path.exists():
                # Essayer avec python-dotenv d'abord (méthode recommandée)
                try:
                    from dotenv import load_dotenv
                    load_dotenv(env_path)
                    print(f"✅ Fichier .env chargé: {env_path}")
                    break
                except ImportError:
                    # Fallback : lire le fichier manuellement
                    self._load_env_manual(env_path)
                    break
    
    def _load_env_manual(self, env_path: Path):
        """
        Charge les variables depuis .env manuellement (si dotenv n'est pas disponible)
        
        Pourquoi : Permettre de fonctionner même sans python-dotenv installé
        Comment : Parse le fichier ligne par ligne
        """
        try:
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # Ignorer les commentaires et lignes vides
                    if not line or line.startswith('#'):
                        continue
                    
                    # Format: KEY=VALUE
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")
                        
                        # Ne pas écraser les variables déjà définies
                        if key and value and key not in os.environ:
                            os.environ[key] = value
            
            print(f"✅ Fichier .env chargé manuellement: {env_path}")
        except Exception as e:
            print(f"⚠️  Erreur lors du chargement manuel de .env: {e}")
    
    def generate(self, prompt: str, max_tokens: int = 2000, temperature: float = 0.7) -> str:
        """
        Génère une réponse à partir d'un prompt avec DeepSeek
        
        Pourquoi : Générer les politiques de sécurité avec DeepSeek R1
        Comment : Appelle l'API DeepSeek ChatCompletion (compatible OpenAI)
        
        Args:
            prompt: Prompt d'entrée pour le LLM
            max_tokens: Nombre maximum de tokens à générer
            temperature: Contrôle la créativité (0.0-1.0)
                Note : DeepSeek R1 recommande temperature=0 pour le raisonnement
            
        Returns:
            Texte généré par DeepSeek
        """
        if not self.api_key:
            return "Erreur: DEEPSEEK_API_KEY non configurée. Définir dans .env ou variable d'environnement"
        
        try:
            # DeepSeek utilise une API compatible OpenAI
            from openai import OpenAI
            
            # Utiliser l'API DeepSeek avec le client OpenAI (compatible)
            client = OpenAI(
                api_key=self.api_key,
                base_url=self.api_base
            )
            
            print(f"🔄 Appel API DeepSeek ({self.model})...")
            
            # Pour DeepSeek R1 (reasoner), utiliser temperature=0 pour le raisonnement
            if "reasoner" in self.model.lower():
                temperature = 0.0
            
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Tu es un expert en cybersécurité et conformité. Tu génères des politiques de sécurité professionnelles et conformes aux standards internationaux (NIST CSF, ISO 27001). Réponds toujours en français."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=max_tokens,
                temperature=temperature,
                timeout=180  # Timeout de 3 minutes (DeepSeek peut prendre plus de temps pour le raisonnement)
            )
            
            generated_text = response.choices[0].message.content.strip()
            print(f"✅ Réponse reçue ({len(generated_text)} caractères)")
            
            return generated_text
            
        except ImportError:
            return "Erreur: openai non installé. Installer avec: pip install openai"
        except Exception as e:
            error_msg = str(e)
            if "api_key" in error_msg.lower() or "authentication" in error_msg.lower():
                return f"Erreur d'authentification: Vérifiez votre clé API DeepSeek. {error_msg}"
            elif "rate limit" in error_msg.lower():
                return f"Erreur: Limite de taux atteinte. Attendez un moment avant de réessayer. {error_msg}"
            elif "model" in error_msg.lower():
                return f"Erreur: Modèle {self.model} non disponible. Vérifiez le nom du modèle. {error_msg}"
            else:
                return f"Erreur DeepSeek: {error_msg}"

