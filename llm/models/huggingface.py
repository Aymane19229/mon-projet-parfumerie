"""
Intégration avec Hugging Face pour utiliser LLaMA 3 ou DeepSeek R1

Pourquoi : Hugging Face permet d'utiliser des modèles open-source gratuitement
Comment : Utilise l'API Transformers pour charger et exécuter les modèles OU l'API Inference
"""
from typing import Optional
import os
from pathlib import Path


class HuggingFaceLLM:
    """
    Wrapper pour utiliser les modèles Hugging Face (LLaMA 3, DeepSeek R1)
    
    Pourquoi : Permettre d'utiliser des LLMs open-source sans coût
    Comment : Charge le modèle et génère des réponses à partir des prompts
    """
    
    def __init__(self, model_name: str = "meta-llama/Meta-Llama-3-8B-Instruct"):
        """
        Initialise le modèle Hugging Face
        
        Args:
            model_name: Nom du modèle sur Hugging Face
                - "meta-llama/Meta-Llama-3-8B-Instruct" (LLaMA 3)
                - "deepseek-ai/DeepSeek-R1" (DeepSeek R1)
        """
        self.model_name = model_name
        self.model = None
        self.tokenizer = None
        
    def load_model(self):
        """
        Charge le modèle Hugging Face
        
        Pourquoi : Charger le modèle une seule fois pour optimiser les performances
        Comment : Utilise transformers pour charger le modèle
        """
        try:
            from transformers import AutoTokenizer, AutoModelForCausalLM
            import torch
            
            print(f"🔄 Chargement du modèle {self.model_name}...")
            
            # Charger le tokenizer et le modèle
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device_map="auto" if torch.cuda.is_available() else "cpu"
            )
            
            print("✅ Modèle chargé avec succès!")
            
        except ImportError:
            print("⚠️  transformers non installé. Installer avec: pip install transformers torch")
            raise
        except Exception as e:
            print(f"❌ Erreur lors du chargement du modèle: {e}")
            print("💡 Alternative: Utiliser OpenAI ou l'API Hugging Face Inference")
            raise
    
    def generate(self, prompt: str, max_length: int = 2000, temperature: float = 0.7) -> str:
        """
        Génère une réponse à partir d'un prompt
        
        Pourquoi : Générer les politiques de sécurité à partir des prompts structurés
        Comment : Utilise le modèle pour générer du texte conditionné par le prompt
        
        Args:
            prompt: Prompt d'entrée pour le LLM
            max_length: Longueur maximale de la réponse
            temperature: Contrôle la créativité (0.0 = déterministe, 1.0 = créatif)
            
        Returns:
            Texte généré par le LLM
        """
        if self.model is None or self.tokenizer is None:
            self.load_model()
        
        try:
            # Préparer le prompt
            inputs = self.tokenizer(prompt, return_tensors="pt")
            
            # Générer
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs.input_ids,
                    max_length=max_length,
                    temperature=temperature,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                    eos_token_id=self.tokenizer.eos_token_id,
                )
            
            # Décoder la réponse
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Retirer le prompt de la réponse
            if prompt in response:
                response = response.replace(prompt, "").strip()
            
            return response
            
        except Exception as e:
            print(f"❌ Erreur lors de la génération: {e}")
            return f"Erreur: {str(e)}"


class HuggingFaceAPI:
    """
    Alternative : Utiliser l'API Hugging Face Inference (plus simple, recommandé)
    
    Pourquoi : Éviter de télécharger les gros modèles localement (nécessite GPU)
    Comment : Utilise l'API HTTP de Hugging Face
    
    Note : Cette méthode est recommandée car elle ne nécessite pas de GPU local
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialise l'API Hugging Face
        
        Args:
            api_key: Clé API Hugging Face (optionnel pour certains modèles publics)
        """
        # Charger depuis .env si disponible
        self._load_env_file()
        
        self.api_key = api_key or os.getenv("HUGGINGFACE_API_KEY")
        self.api_url = "https://api-inference.huggingface.co/models"
        
        if not self.api_key:
            print("⚠️  HUGGINGFACE_API_KEY non définie.")
            print("💡 Certains modèles nécessitent une clé API. Créer un compte sur huggingface.co")
    
    def _load_env_file(self):
        """
        Charge les variables d'environnement depuis .env
        
        Pourquoi : Permettre de stocker la clé API dans un fichier .env local
        Comment : Utilise python-dotenv si disponible, sinon lit le fichier manuellement
        """
        env_paths = [
            Path(__file__).parent.parent / ".env",
            Path(__file__).parent.parent.parent / ".env",
        ]
        
        for env_path in env_paths:
            if env_path.exists():
                # Essayer avec python-dotenv d'abord
                try:
                    from dotenv import load_dotenv
                    load_dotenv(env_path)
                    break
                except ImportError:
                    # Fallback : lire le fichier manuellement
                    self._load_env_manual(env_path)
                    break
    
    def _load_env_manual(self, env_path: Path):
        """
        Charge les variables depuis .env manuellement (si dotenv n'est pas disponible)
        """
        try:
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")
                        
                        if key and value and key not in os.environ:
                            os.environ[key] = value
        except Exception as e:
            pass  # Ignorer les erreurs silencieusement
        
    def generate(self, prompt: str, model: str = "meta-llama/Meta-Llama-3-8B-Instruct", 
                 max_length: int = 2000, temperature: float = 0.7) -> str:
        """
        Génère une réponse via l'API Hugging Face
        
        Pourquoi : Utiliser les LLMs sans télécharger les modèles localement
        Comment : Appelle l'API REST de Hugging Face Inference
        
        Args:
            prompt: Prompt d'entrée
            model: Nom du modèle sur Hugging Face
                - "meta-llama/Meta-Llama-3-8B-Instruct" (nécessite clé API)
                - "gpt2" (public, pas de clé nécessaire)
                - "mistralai/Mistral-7B-Instruct-v0.2"
            max_length: Nombre maximum de tokens à générer
            temperature: Contrôle la créativité (0.0-1.0)
            
        Returns:
            Texte généré
        """
        try:
            import requests
            
            headers = {"Content-Type": "application/json"}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            
            print(f"🔄 Appel API Hugging Face ({model})...")
            
            response = requests.post(
                f"{self.api_url}/{model}",
                headers=headers,
                json={
                    "inputs": prompt,
                    "parameters": {
                        "max_new_tokens": max_length,
                        "temperature": temperature,
                        "return_full_text": False
                    }
                },
                timeout=180  # 3 minutes pour les gros modèles
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Gérer différents formats de réponse
                if isinstance(result, list) and len(result) > 0:
                    generated_text = result[0].get("generated_text", "")
                elif isinstance(result, dict):
                    generated_text = result.get("generated_text", str(result))
                else:
                    generated_text = str(result)
                
                print(f"✅ Réponse reçue ({len(generated_text)} caractères)")
                return generated_text
                
            elif response.status_code == 503:
                # Modèle en cours de chargement
                return f"Erreur: Modèle {model} est en cours de chargement. Attendez 30 secondes et réessayez."
            elif response.status_code == 401:
                return f"Erreur d'authentification: Vérifiez votre clé API Hugging Face"
            else:
                return f"Erreur API ({response.status_code}): {response.text[:200]}"
                
        except ImportError:
            return "Erreur: requests non installé. Installer avec: pip install requests"
        except requests.exceptions.Timeout:
            return "Erreur: Timeout - Le modèle prend trop de temps à répondre. Essayez un modèle plus petit."
        except Exception as e:
            return f"Erreur: {str(e)}"

