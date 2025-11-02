"""
Script pour Comparer les Modèles LLM (DeepSeek R1 vs LLaMA 3)

Pourquoi : Générer des politiques avec les deux modèles et comparer leurs performances
Comment : Génère les mêmes politiques avec chaque modèle, puis évalue avec BLEU/ROUGE-L
"""
import sys
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from llm.policy_generator import PolicyGenerator


def generate_with_deepseek(vulnerabilities_file: str = "parser/reports/normalized_vulnerabilities.json"):
    """
    Génère des politiques avec DeepSeek R1
    
    Args:
        vulnerabilities_file: Chemin vers les vulnérabilités normalisées
    """
    print("\n" + "="*70)
    print("🤖 GÉNÉRATION AVEC DEEPSEEK R1")
    print("="*70)
    
    generator = PolicyGenerator(
        vulnerabilities_file=vulnerabilities_file,
        llm_provider="deepseek",
        model_name="deepseek-chat"
    )
    
    # Générer quelques politiques pour test
    policies = {}
    
    # NIST CSF - PROTECT
    print("\n📝 Génération politique NIST CSF - PROTECT...")
    nist_policy = generator.generate_nist_csf_policy("PROTECT")
    policies['nist_csf'] = {'PROTECT': nist_policy}
    
    # ISO 27001 - A.9.2.1
    print("\n📝 Génération politique ISO 27001 - A.9.2.1...")
    iso_policy = generator.generate_iso27001_policy("A.9.2.1")
    policies['iso27001'] = {'A.9.2.1': iso_policy}
    
    # Sauvegarder dans un dossier spécifique
    output_dir = Path("llm/policies/deepseek")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Sauvegarder NIST CSF
    nist_dir = output_dir / "nist_csf"
    nist_dir.mkdir(exist_ok=True)
    with open(nist_dir / "PROTECT.txt", 'w', encoding='utf-8') as f:
        f.write(nist_policy)
    print(f"✅ Sauvegardé: {nist_dir / 'PROTECT.txt'}")
    
    # Sauvegarder ISO 27001
    iso_dir = output_dir / "iso27001"
    iso_dir.mkdir(exist_ok=True)
    with open(iso_dir / "A.9.2.1.txt", 'w', encoding='utf-8') as f:
        f.write(iso_policy)
    print(f"✅ Sauvegardé: {iso_dir / 'A.9.2.1.txt'}")
    
    return policies


def generate_with_llama3(vulnerabilities_file: str = "parser/reports/normalized_vulnerabilities.json"):
    """
    Génère des politiques avec LLaMA 3 (Hugging Face)
    
    Args:
        vulnerabilities_file: Chemin vers les vulnérabilités normalisées
    """
    print("\n" + "="*70)
    print("🤖 GÉNÉRATION AVEC LLaMA 3 (Hugging Face)")
    print("="*70)
    
    generator = PolicyGenerator(
        vulnerabilities_file=vulnerabilities_file,
        llm_provider="huggingface",
        model_name="meta-llama/Meta-Llama-3-8B-Instruct"
    )
    
    # Générer les mêmes politiques
    policies = {}
    
    # NIST CSF - PROTECT
    print("\n📝 Génération politique NIST CSF - PROTECT...")
    nist_policy = generator.generate_nist_csf_policy("PROTECT")
    policies['nist_csf'] = {'PROTECT': nist_policy}
    
    # ISO 27001 - A.9.2.1
    print("\n📝 Génération politique ISO 27001 - A.9.2.1...")
    iso_policy = generator.generate_iso27001_policy("A.9.2.1")
    policies['iso27001'] = {'A.9.2.1': iso_policy}
    
    # Sauvegarder dans un dossier spécifique
    output_dir = Path("llm/policies/llama3")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Sauvegarder NIST CSF
    nist_dir = output_dir / "nist_csf"
    nist_dir.mkdir(exist_ok=True)
    with open(nist_dir / "PROTECT.txt", 'w', encoding='utf-8') as f:
        f.write(nist_policy)
    print(f"✅ Sauvegardé: {nist_dir / 'PROTECT.txt'}")
    
    # Sauvegarder ISO 27001
    iso_dir = output_dir / "iso27001"
    iso_dir.mkdir(exist_ok=True)
    with open(iso_dir / "A.9.2.1.txt", 'w', encoding='utf-8') as f:
        f.write(iso_policy)
    print(f"✅ Sauvegardé: {iso_dir / 'A.9.2.1.txt'}")
    
    return policies


def main():
    """
    Fonction principale : Génère avec les deux modèles puis évalue
    """
    vulnerabilities_file = sys.argv[1] if len(sys.argv) > 1 else "parser/reports/normalized_vulnerabilities.json"
    
    print("\n🚀 COMPARAISON DES MODÈLES LLM")
    print("="*70)
    print("Ce script va :")
    print("1. Générer des politiques avec DeepSeek R1")
    print("2. Générer les mêmes politiques avec LLaMA 3")
    print("3. Évaluer les deux avec BLEU/ROUGE-L")
    print("4. Déterminer le meilleur modèle")
    print("="*70)
    
    # Vérifier que les vulnérabilités existent
    if not Path(vulnerabilities_file).exists():
        print(f"\n❌ Fichier non trouvé: {vulnerabilities_file}")
        print("💡 Exécutez d'abord: python parser/main_parser.py")
        return
    
    # Générer avec DeepSeek
    try:
        deepseek_policies = generate_with_deepseek(vulnerabilities_file)
    except Exception as e:
        print(f"\n❌ Erreur lors de la génération avec DeepSeek: {e}")
        print("⚠️  Vérifiez votre clé API DeepSeek et vos crédits")
        deepseek_policies = None
    
    # Générer avec LLaMA 3
    try:
        llama3_policies = generate_with_llama3(vulnerabilities_file)
    except Exception as e:
        print(f"\n❌ Erreur lors de la génération avec LLaMA 3: {e}")
        print("⚠️  Vérifiez votre configuration Hugging Face")
        llama3_policies = None
    
    # Évaluer si au moins un modèle a fonctionné
    if deepseek_policies or llama3_policies:
        print("\n" + "="*70)
        print("📊 ÉVALUATION DES POLITIQUES GÉNÉRÉES")
        print("="*70)
        
        # Importer et exécuter l'évaluateur
        from evaluation.evaluator import PolicyEvaluator
        
        evaluator = PolicyEvaluator()
        evaluator.load_references()
        
        # Les politiques sont déjà sauvegardées, charger depuis les fichiers
        generated_policies = evaluator.load_generated_policies("llm/policies")
        
        if generated_policies:
            results = evaluator.evaluate_all_policies(generated_policies)
            averages = evaluator.calculate_model_averages(results)
            evaluator.print_comparison(averages)
            evaluator.generate_report(results, averages)
        else:
            print("⚠️  Aucune politique générée trouvée pour évaluation")
    else:
        print("\n❌ Aucune politique n'a pu être générée. Vérifiez vos configurations.")
    
    print("\n✅ Processus terminé !")


if __name__ == "__main__":
    main()

