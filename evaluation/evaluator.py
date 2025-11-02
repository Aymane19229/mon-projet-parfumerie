"""
Évaluateur Principal pour Comparer les Politiques Générées

Pourquoi : Comparer les politiques générées par différents LLMs (DeepSeek R1 vs LLaMA 3)
Comment : Charge les politiques, les compare avec des références, génère un rapport
"""
import json
import os
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime

from .bleu_rouge import evaluate_policy


class PolicyEvaluator:
    """
    Évaluateur pour comparer les politiques générées par différents LLMs
    
    Pourquoi : Comparer la qualité des politiques générées par DeepSeek R1 vs LLaMA 3
    Comment : Utilise BLEU et ROUGE-L pour comparer avec des références
    """
    
    def __init__(self, reference_dir: str = "evaluation/reference_policies"):
        """
        Initialise l'évaluateur
        
        Args:
            reference_dir: Dossier contenant les politiques de référence
        """
        self.reference_dir = Path(reference_dir)
        self.references: Dict[str, List[str]] = {}
        
    def load_references(self):
        """
        Charge toutes les politiques de référence depuis les fichiers
        
        Pourquoi : Avoir des références pour comparer les politiques générées
        Comment : Lit tous les fichiers .txt dans reference_policies/
        """
        print("📚 Chargement des politiques de référence...")
        
        # Charger références NIST CSF
        nist_dir = self.reference_dir / "nist_csf"
        if nist_dir.exists():
            nist_refs = []
            for ref_file in nist_dir.glob("*.txt"):
                with open(ref_file, 'r', encoding='utf-8') as f:
                    nist_refs.append(f.read())
            if nist_refs:
                self.references['nist_csf'] = nist_refs
                print(f"✅ {len(nist_refs)} références NIST CSF chargées")
        
        # Charger références ISO 27001
        iso_dir = self.reference_dir / "iso27001"
        if iso_dir.exists():
            iso_refs = []
            for ref_file in iso_dir.glob("*.txt"):
                with open(ref_file, 'r', encoding='utf-8') as f:
                    iso_refs.append(f.read())
            if iso_refs:
                self.references['iso27001'] = iso_refs
                print(f"✅ {len(iso_refs)} références ISO 27001 chargées")
        
        if not self.references:
            print("⚠️  Aucune référence trouvée. Créez des fichiers .txt dans evaluation/reference_policies/")
    
    def load_generated_policies(self, policies_dir: str) -> Dict[str, Dict[str, str]]:
        """
        Charge les politiques générées par les LLMs
        
        Pourquoi : Comparer les politiques générées par différents modèles
        Comment : Lit les fichiers dans llm/policies/ organisés par modèle
        
        Args:
            policies_dir: Dossier contenant les politiques générées
            
        Returns:
            Dictionnaire organisé par modèle LLM et type de politique
            {
                'deepseek': {
                    'nist_csf/PROTECT': 'texte politique...',
                    'iso27001/A.9.2.1': 'texte politique...'
                },
                'llama3': {
                    ...
                }
            }
        """
        policies = {}
        policies_path = Path(policies_dir)
        
        if not policies_path.exists():
            print(f"⚠️  Dossier non trouvé: {policies_dir}")
            return policies
        
        print(f"📂 Chargement des politiques générées depuis {policies_dir}...")
        
        # Chercher les politiques par modèle
        for model_dir in policies_path.iterdir():
            if not model_dir.is_dir():
                continue
            
            model_name = model_dir.name.lower()
            if model_name not in ['deepseek', 'llama3', 'huggingface']:
                continue
            
            policies[model_name] = {}
            
            # Chercher les politiques NIST CSF
            nist_dir = model_dir / "nist_csf"
            if nist_dir.exists():
                for policy_file in nist_dir.glob("*.txt"):
                    category = policy_file.stem
                    with open(policy_file, 'r', encoding='utf-8') as f:
                        policies[model_name][f"nist_csf/{category}"] = f.read()
            
            # Chercher les politiques ISO 27001
            iso_dir = model_dir / "iso27001"
            if iso_dir.exists():
                for policy_file in iso_dir.glob("*.txt"):
                    control = policy_file.stem
                    with open(policy_file, 'r', encoding='utf-8') as f:
                        policies[model_name][f"iso27001/{control}"] = f.read()
        
        print(f"✅ {sum(len(ps) for ps in policies.values())} politiques chargées")
        return policies
    
    def evaluate_all_policies(self, generated_policies: Dict[str, Dict[str, str]]) -> Dict:
        """
        Évalue toutes les politiques générées
        
        Pourquoi : Obtenir des scores pour toutes les politiques et comparer les modèles
        Comment : Compare chaque politique avec les références appropriées
        
        Args:
            generated_policies: Dictionnaire des politiques générées par modèle
            
        Returns:
            Dictionnaire des résultats d'évaluation
        """
        results = {}
        
        print("\n🔍 Évaluation des politiques...")
        
        for model_name, policies in generated_policies.items():
            print(f"\n📊 Évaluation pour {model_name.upper()}...")
            results[model_name] = {}
            
            for policy_key, policy_text in policies.items():
                # Déterminer le type de référence à utiliser
                if policy_key.startswith("nist_csf/"):
                    ref_type = 'nist_csf'
                    ref_key = policy_key.replace("nist_csf/", "")
                elif policy_key.startswith("iso27001/"):
                    ref_type = 'iso27001'
                    ref_key = policy_key.replace("iso27001/", "")
                else:
                    continue
                
                # Obtenir les références
                references = self.references.get(ref_type, [])
                
                if not references:
                    print(f"⚠️  Pas de référence pour {policy_key}")
                    continue
                
                # Évaluer
                scores = evaluate_policy(policy_text, references)
                results[model_name][policy_key] = scores
                
                print(f"  ✅ {policy_key}: BLEU={scores['bleu']:.3f}, ROUGE-L F={scores['rouge_l_f']:.3f}")
        
        return results
    
    def calculate_model_averages(self, results: Dict) -> Dict[str, Dict[str, float]]:
        """
        Calcule les moyennes pour chaque modèle
        
        Pourquoi : Comparer les modèles avec des statistiques agrégées
        Comment : Moyenne de tous les scores pour chaque modèle
        
        Args:
            results: Dictionnaire des résultats d'évaluation
            
        Returns:
            Dictionnaire des moyennes par modèle
        """
        averages = {}
        
        for model_name, model_results in results.items():
            if not model_results:
                continue
            
            total_policies = len(model_results)
            avg_bleu = sum(r['bleu'] for r in model_results.values()) / total_policies
            avg_rouge_f = sum(r['rouge_l_f'] for r in model_results.values()) / total_policies
            avg_rouge_p = sum(r['rouge_l_p'] for r in model_results.values()) / total_policies
            avg_rouge_r = sum(r['rouge_l_r'] for r in model_results.values()) / total_policies
            
            averages[model_name] = {
                'avg_bleu': round(avg_bleu, 4),
                'avg_rouge_l_f': round(avg_rouge_f, 4),
                'avg_rouge_l_p': round(avg_rouge_p, 4),
                'avg_rouge_l_r': round(avg_rouge_r, 4),
                'num_policies': total_policies
            }
        
        return averages
    
    def generate_report(self, results: Dict, averages: Dict, output_file: str = "evaluation/evaluation_report.json"):
        """
        Génère un rapport d'évaluation complet
        
        Pourquoi : Documenter les résultats de l'évaluation pour comparaison
        Comment : Sauvegarde un rapport JSON avec tous les scores
        
        Args:
            results: Résultats détaillés par politique
            averages: Moyennes par modèle
            output_file: Fichier de sortie
        """
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': averages,
            'detailed_results': results
        }
        
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Rapport sauvegardé: {output_file}")
        return report
    
    def print_comparison(self, averages: Dict):
        """
        Affiche une comparaison claire des modèles
        
        Pourquoi : Visualiser rapidement quel modèle performe le mieux
        Comment : Tableau formaté avec les scores moyens
        
        Args:
            averages: Moyennes par modèle
        """
        print("\n" + "="*70)
        print("📊 COMPARAISON DES MODÈLES LLM")
        print("="*70)
        
        if not averages:
            print("⚠️  Aucun résultat à comparer")
            return
        
        # En-têtes
        print(f"\n{'Modèle':<20} {'BLEU':<10} {'ROUGE-L F':<12} {'ROUGE-L P':<12} {'ROUGE-L R':<12} {'Politiques':<10}")
        print("-" * 70)
        
        # Tri par BLEU score décroissant
        sorted_models = sorted(
            averages.items(),
            key=lambda x: x[1]['avg_bleu'],
            reverse=True
        )
        
        for model_name, scores in sorted_models:
            print(f"{model_name.upper():<20} "
                  f"{scores['avg_bleu']:<10.4f} "
                  f"{scores['avg_rouge_l_f']:<12.4f} "
                  f"{scores['avg_rouge_l_p']:<12.4f} "
                  f"{scores['avg_rouge_l_r']:<12.4f} "
                  f"{scores['num_policies']:<10}")
        
        print("\n" + "="*70)
        
        # Déterminer le meilleur modèle
        best_model = max(averages.items(), key=lambda x: x[1]['avg_bleu'])
        print(f"\n🏆 MEILLEUR MODÈLE: {best_model[0].upper()}")
        print(f"   BLEU Score: {best_model[1]['avg_bleu']:.4f}")
        print(f"   ROUGE-L F-Score: {best_model[1]['avg_rouge_l_f']:.4f}")
        print("="*70 + "\n")


def main():
    """
    Fonction principale pour exécuter l'évaluation complète
    
    Pourquoi : Permettre d'exécuter l'évaluateur depuis la ligne de commande
    Comment : Charge références, politiques générées, évalue et génère rapport
    """
    evaluator = PolicyEvaluator()
    
    # Charger les références
    evaluator.load_references()
    
    if not evaluator.references:
        print("❌ Erreur: Aucune référence chargée. Créez des politiques de référence d'abord.")
        return
    
    # Charger les politiques générées
    generated_policies = evaluator.load_generated_policies("llm/policies")
    
    if not generated_policies:
        print("❌ Erreur: Aucune politique générée trouvée. Générez des politiques d'abord.")
        return
    
    # Évaluer toutes les politiques
    results = evaluator.evaluate_all_policies(generated_policies)
    
    # Calculer les moyennes
    averages = evaluator.calculate_model_averages(results)
    
    # Afficher la comparaison
    evaluator.print_comparison(averages)
    
    # Générer le rapport
    evaluator.generate_report(results, averages)
    
    print("\n✅ Évaluation terminée !")


if __name__ == "__main__":
    main()

