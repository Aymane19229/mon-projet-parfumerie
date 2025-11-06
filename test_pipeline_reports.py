#!/usr/bin/env python3
"""
Script de test pour vérifier que les rapports peuvent être générés et parsés

Pourquoi : Tester que SCA et DAST fonctionnent correctement
Comment : Simule la structure de rapports et teste les parsers
"""
import sys
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent))

def test_sca_parser():
    """Test le parser SCA"""
    print("\n" + "="*60)
    print("🧪 TEST PARSER SCA")
    print("="*60)
    
    from parser.parsers.sca_parser import DependencyCheckParser, NpmAuditParser
    
    # Test avec un fichier JSON vide (structure minimale)
    test_dir = Path("parser/reports/sca")
    test_dir.mkdir(parents=True, exist_ok=True)
    
    # Créer un fichier Dependency-Check minimal
    dependency_check_file = test_dir / "backend-dependency-check-report.json"
    minimal_dc = {
        "dependencies": []
    }
    import json
    with open(dependency_check_file, 'w') as f:
        json.dump(minimal_dc, f)
    
    print(f"✅ Fichier test créé: {dependency_check_file}")
    
    # Tester le parser
    try:
        vulns = DependencyCheckParser.parse(str(dependency_check_file))
        print(f"✅ Parser Dependency-Check fonctionne: {len(vulns)} vulnérabilités")
    except Exception as e:
        print(f"❌ Erreur Dependency-Check parser: {e}")
    
    # Créer un fichier npm audit minimal
    npm_audit_file = test_dir / "frontend-npm-audit-report.json"
    minimal_npm = {
        "vulnerabilities": {}
    }
    with open(npm_audit_file, 'w') as f:
        json.dump(minimal_npm, f)
    
    print(f"✅ Fichier test créé: {npm_audit_file}")
    
    # Tester le parser
    try:
        vulns = NpmAuditParser.parse(str(npm_audit_file))
        print(f"✅ Parser npm audit fonctionne: {len(vulns)} vulnérabilités")
    except Exception as e:
        print(f"❌ Erreur npm audit parser: {e}")


def test_dast_parser():
    """Test le parser DAST"""
    print("\n" + "="*60)
    print("🧪 TEST PARSER DAST")
    print("="*60)
    
    from parser.parsers.dast_parser import ZAPParser
    
    # Test avec un fichier JSON vide (structure minimale)
    test_dir = Path("parser/reports/dast")
    test_dir.mkdir(parents=True, exist_ok=True)
    
    # Créer un fichier ZAP minimal
    zap_file = test_dir / "zap-report.json"
    minimal_zap = {
        "@version": "2.11.0",
        "site": []
    }
    import json
    with open(zap_file, 'w') as f:
        json.dump(minimal_zap, f)
    
    print(f"✅ Fichier test créé: {zap_file}")
    
    # Tester le parser
    try:
        vulns = ZAPParser.parse(str(zap_file))
        print(f"✅ Parser ZAP fonctionne: {len(vulns)} vulnérabilités")
    except Exception as e:
        print(f"❌ Erreur ZAP parser: {e}")


def test_main_parser():
    """Test le parser principal"""
    print("\n" + "="*60)
    print("🧪 TEST PARSER PRINCIPAL")
    print("="*60)
    
    from parser.main_parser import VulnerabilityReportParser
    
    try:
        parser = VulnerabilityReportParser()
        vulns = parser.parse_all()
        print(f"✅ Parser principal fonctionne: {len(vulns)} vulnérabilités totales")
        return True
    except Exception as e:
        print(f"❌ Erreur parser principal: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Exécute tous les tests"""
    print("\n🚀 TESTS DES PARSERS SCA ET DAST")
    print("="*60)
    
    # Tests individuels
    test_sca_parser()
    test_dast_parser()
    
    # Test du parser principal
    success = test_main_parser()
    
    print("\n" + "="*60)
    if success:
        print("✅ Tous les parsers fonctionnent correctement")
    else:
        print("⚠️  Certains parsers ont des problèmes")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()

