"""
Générateur Principal de Politiques de Sécurité avec LLM

Pourquoi : Orchestrer la génération de politiques à partir des vulnérabilités parsées
Comment : Charge les vulnérabilités, génère les prompts, appelle les LLMs, sauvegarde les résultats
"""
import json
import os
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

from .prompts.nist_csf_prompt import NISTCSFPrompt
from .prompts.iso27001_prompt import ISO27001Prompt

# Import pour la vérification de type
try:
    from .models.huggingface import HuggingFaceAPI
except ImportError:
    HuggingFaceAPI = None


class PolicyGenerator:
    """
    Générateur principal pour créer des politiques de sécurité avec LLM
    
    Pourquoi : Automatiser la génération de politiques conformes NIST/ISO à partir des vulnérabilités
    Comment : Utilise les prompts structurés et les LLMs pour générer les politiques
    """
    
    def __init__(self, vulnerabilities_file: str = "parser/reports/normalized_vulnerabilities.json",
                 llm_provider: str = "deepseek", model_name: Optional[str] = None):
        """
        Initialise le générateur de politiques
        
        Args:
            vulnerabilities_file: Chemin vers le fichier JSON des vulnérabilités normalisées
            llm_provider: "deepseek" (recommandé) ou "huggingface"
            model_name: Nom du modèle spécifique (optionnel)
                - DeepSeek: "deepseek-chat" (défaut) ou "deepseek-reasoner" (R1)
                - HuggingFace: "meta-llama/Meta-Llama-3-8B-Instruct" ou autre modèle
        """
        self.vulnerabilities_file = Path(vulnerabilities_file)
        self.llm_provider = llm_provider
        self.model_name = model_name
        self.vulnerabilities: List[Dict] = []
        self.llm = None
        
    def load_vulnerabilities(self) -> List[Dict]:
        """
        Charge les vulnérabilités depuis le fichier JSON normalisé
        
        Pourquoi : Utiliser les vulnérabilités parsées pour générer les politiques
        Comment : Lit le fichier JSON et retourne la liste des vulnérabilités
        
        Returns:
            Liste des vulnérabilités normalisées
        """
        try:
            if not self.vulnerabilities_file.exists():
                print(f"⚠️  Fichier non trouvé: {self.vulnerabilities_file}")
                print("💡 Exécutez d'abord: python parser/main_parser.py")
                return []
            
            with open(self.vulnerabilities_file, 'r', encoding='utf-8') as f:
                self.vulnerabilities = json.load(f)
            
            print(f"✅ {len(self.vulnerabilities)} vulnérabilités chargées")
            return self.vulnerabilities
            
        except json.JSONDecodeError as e:
            print(f"❌ Erreur lors du parsing JSON: {e}")
            return []
        except Exception as e:
            print(f"❌ Erreur lors du chargement: {e}")
            return []
    
    def initialize_llm(self):
        """
        Initialise le LLM selon le provider choisi
        
        Pourquoi : Charger le modèle LLM pour générer les politiques
        Comment : Importe et initialise le bon wrapper selon le provider
        """
        if self.llm_provider == "deepseek":
            # DeepSeek R1 - Recommandé : performant et économique
            from .models.deepseek import DeepSeekLLM
            model = self.model_name or "deepseek-chat"
            self.llm = DeepSeekLLM(model=model)
            print(f"✅ LLM initialisé: DeepSeek {model}")
            
        elif self.llm_provider == "huggingface":
            # Utiliser l'API plutôt que le chargement local (plus simple, pas besoin de GPU)
            from .models.huggingface import HuggingFaceAPI
            self.llm = HuggingFaceAPI()
            # Note: le modèle sera passé lors de l'appel à generate()
            print(f"✅ LLM initialisé: Hugging Face API")
            
        elif self.llm_provider == "huggingface-local":
            # Option pour charger le modèle localement (nécessite GPU)
            from .models.huggingface import HuggingFaceLLM
            model = self.model_name or "meta-llama/Meta-Llama-3-8B-Instruct"
            self.llm = HuggingFaceLLM(model_name=model)
            print(f"✅ LLM initialisé: Hugging Face Local {model}")
            print("⚠️  Note: Le chargement local nécessite un GPU et beaucoup de RAM")
            
        else:
            raise ValueError(f"Provider LLM inconnu: {self.llm_provider}. Utiliser 'deepseek' (recommandé) ou 'huggingface'")
    
    def generate_nist_csf_policy(self, framework_category: str = "PROTECT") -> str:
        """
        Génère une politique NIST CSF
        
        Pourquoi : Créer une politique conforme au NIST Cybersecurity Framework
        Comment : Utilise le prompt NIST et le LLM pour générer la politique
        
        Args:
            framework_category: Catégorie NIST (IDENTIFY, PROTECT, DETECT, RESPOND, RECOVER)
            
        Returns:
            Politique générée (texte)
        """
        if not self.vulnerabilities:
            self.load_vulnerabilities()
        
        if not self.llm:
            self.initialize_llm()
        
        print(f"\n🔄 Génération d'une politique NIST CSF ({framework_category})...")
        
        # Générer le prompt
        prompt = NISTCSFPrompt.generate_policy_prompt(self.vulnerabilities, framework_category)
        
        # Générer la politique avec le LLM
        if isinstance(self.llm, HuggingFaceAPI) and self.model_name:
            # Pour HuggingFaceAPI, passer le modèle en paramètre
            policy = self.llm.generate(prompt, model=self.model_name)
        else:
            policy = self.llm.generate(prompt)
        
        print("✅ Politique NIST CSF générée!")
        
        return policy
    
    def generate_iso27001_policy(self, iso_control: str = "A.14.2.5") -> str:
        """
        Génère une politique ISO 27001
        
        Pourquoi : Créer une politique conforme à ISO/IEC 27001
        Comment : Utilise le prompt ISO et le LLM pour générer la politique
        
        Args:
            iso_control: Contrôle ISO 27001 (ex: A.14.2.5)
            
        Returns:
            Politique générée (texte)
        """
        if not self.vulnerabilities:
            self.load_vulnerabilities()
        
        if not self.llm:
            self.initialize_llm()
        
        print(f"\n🔄 Génération d'une politique ISO 27001 ({iso_control})...")
        
        # Générer le prompt
        prompt = ISO27001Prompt.generate_policy_prompt(self.vulnerabilities, iso_control)
        
        # Générer la politique avec le LLM
        if HuggingFaceAPI and isinstance(self.llm, HuggingFaceAPI) and self.model_name:
            # Pour HuggingFaceAPI, passer le modèle en paramètre
            policy = self.llm.generate(prompt, model=self.model_name)
        else:
            policy = self.llm.generate(prompt)
        
        print("✅ Politique ISO 27001 générée!")
        
        return policy
    
    def save_policy(self, policy: str, framework: str, identifier: str, output_dir: Optional[str] = None):
        """
        Sauvegarde une politique générée
        
        Pourquoi : Stocker les politiques pour référence et évaluation
        Comment : Sauvegarde dans un fichier markdown structuré
        
        Args:
            policy: Texte de la politique
            framework: "nist_csf" ou "iso27001"
            identifier: Identifiant unique (ex: "PROTECT", "A.14.2.5")
            output_dir: Dossier de sortie (optionnel)
        """
        if output_dir is None:
            output_dir = f"llm/policies/{framework}"
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Nom du fichier
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{framework}_{identifier}_{timestamp}.md"
        filepath = output_path / filename
        
        # Ajouter les métadonnées
        metadata = f"""---
framework: {framework}
identifier: {identifier}
generated_date: {datetime.now().isoformat()}
vulnerabilities_count: {len(self.vulnerabilities)}
---

"""
        
        # Sauvegarder
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(metadata)
            f.write(policy)
        
        print(f"💾 Politique sauvegardée: {filepath}")
        
        return filepath
    
    def generate_all_policies(self, output_dir: Optional[str] = None):
        """
        Génère toutes les politiques (NIST CSF et ISO 27001)
        
        Pourquoi : Créer un ensemble complet de politiques
        Comment : Génère plusieurs politiques pour différents domaines
        
        Returns:
            Liste des fichiers générés
        """
        if not self.vulnerabilities:
            self.load_vulnerabilities()
        
        if not self.llm:
            self.initialize_llm()
        
        generated_files = []
        
        print("\n" + "="*60)
        print("🚀 GÉNÉRATION DE TOUTES LES POLITIQUES")
        print("="*60)
        
        # NIST CSF - Générer pour PROTECT (le plus important)
        print("\n📋 NIST CSF - PROTECT")
        nist_policy = self.generate_nist_csf_policy("PROTECT")
        nist_file = self.save_policy(nist_policy, "nist_csf", "PROTECT", output_dir)
        generated_files.append(nist_file)
        
        # ISO 27001 - Générer pour A.14.2.5 (Sécurité des applications)
        print("\n📋 ISO 27001 - A.14.2.5")
        iso_policy = self.generate_iso27001_policy("A.14.2.5")
        iso_file = self.save_policy(iso_policy, "iso27001", "A.14.2.5", output_dir)
        generated_files.append(iso_file)
        
        print("\n" + "="*60)
        print(f"✅ {len(generated_files)} politiques générées avec succès!")
        print("="*60)
        
        return generated_files


def main():
    """
    Point d'entrée principal
    
    Pourquoi : Permettre d'exécuter le générateur depuis la ligne de commande
    Comment : python llm/policy_generator.py
    """
    import sys
    
    # Paramètres par défaut - DeepSeek R1 est maintenant le défaut (recommandé)
    vulnerabilities_file = sys.argv[1] if len(sys.argv) > 1 else "parser/reports/normalized_vulnerabilities.json"
    llm_provider = sys.argv[2] if len(sys.argv) > 2 else "deepseek"
    model_name = sys.argv[3] if len(sys.argv) > 3 else None
    
    # Créer le générateur
    generator = PolicyGenerator(
        vulnerabilities_file=vulnerabilities_file,
        llm_provider=llm_provider,
        model_name=model_name
    )
    
    # Générer toutes les politiques
    generator.generate_all_policies()


if __name__ == "__main__":
    main()

