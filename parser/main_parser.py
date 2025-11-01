"""
Parser principal qui orchestre tous les parsers de vulnérabilités

Pourquoi : Centraliser la logique de parsing de tous les rapports
Comment : Détecte automatiquement les fichiers de rapports et les parse
"""
import json
import sys
from pathlib import Path
from typing import List, Dict, Optional

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, str(Path(__file__).parent))

from vulnerability_model import Vulnerability, VulnerabilityType
from parsers.sast_parser import SpotBugsParser, ESLintParser
from parsers.sca_parser import DependencyCheckParser, NpmAuditParser
from parsers.dast_parser import ZAPParser


class VulnerabilityReportParser:
    """
    Parser principal pour tous les rapports de vulnérabilités
    
    Pourquoi : Unifier l'extraction de vulnérabilités depuis différents formats
    Comment : Détecte et parse automatiquement les rapports SAST, SCA, DAST
    """
    
    def __init__(self, reports_directory: str = "reports"):
        """
        Initialise le parser avec le répertoire des rapports
        
        Args:
            reports_directory: Chemin vers le dossier contenant les rapports
        """
        self.reports_dir = Path(reports_directory)
        self.vulnerabilities: List[Vulnerability] = []
        
    def parse_all(self) -> List[Vulnerability]:
        """
        Parse tous les rapports disponibles dans le répertoire
        
        Pourquoi : Extraire toutes les vulnérabilités de tous les outils
        Comment : Cherche automatiquement les fichiers de rapports et les parse
        
        Returns:
            Liste complète de toutes les vulnérabilités détectées
        """
        print("🔍 Début du parsing des rapports de vulnérabilités...\n")
        
        # Parse SAST
        sast_vulns = self._parse_sast()
        print(f"✅ SAST: {len(sast_vulns)} vulnérabilités détectées")
        
        # Parse SCA
        sca_vulns = self._parse_sca()
        print(f"✅ SCA: {len(sca_vulns)} vulnérabilités détectées")
        
        # Parse DAST
        dast_vulns = self._parse_dast()
        print(f"✅ DAST: {len(dast_vulns)} vulnérabilités détectées")
        
        # Combiner toutes les vulnérabilités
        self.vulnerabilities = sast_vulns + sca_vulns + dast_vulns
        
        print(f"\n📊 Total: {len(self.vulnerabilities)} vulnérabilités détectées")
        
        return self.vulnerabilities
    
    def _parse_sast(self) -> List[Vulnerability]:
        """
        Parse les rapports SAST (SpotBugs, ESLint)
        
        Pourquoi : Extraire les vulnérabilités de l'analyse statique
        Comment : Cherche les fichiers spotbugs-report.xml et eslint-report.json
        """
        vulnerabilities = []
        sast_dir = self.reports_dir / "sast"
        
        if not sast_dir.exists():
            print("⚠️  Dossier SAST non trouvé")
            return vulnerabilities
        
        # Parse SpotBugs (XML)
        spotbugs_file = sast_dir / "spotbugs-report.xml"
        if spotbugs_file.exists():
            print(f"📄 Parsing SpotBugs: {spotbugs_file}")
            vulns = SpotBugsParser.parse(str(spotbugs_file))
            vulnerabilities.extend(vulns)
            print(f"   → {len(vulns)} vulnérabilités trouvées")
        else:
            print(f"⚠️  SpotBugs report non trouvé: {spotbugs_file}")
        
        # Parse ESLint (JSON)
        eslint_file = sast_dir / "eslint-report.json"
        if eslint_file.exists():
            print(f"📄 Parsing ESLint: {eslint_file}")
            vulns = ESLintParser.parse(str(eslint_file))
            vulnerabilities.extend(vulns)
            print(f"   → {len(vulns)} vulnérabilités trouvées")
        else:
            print(f"⚠️  ESLint report non trouvé: {eslint_file}")
        
        return vulnerabilities
    
    def _parse_sca(self) -> List[Vulnerability]:
        """
        Parse les rapports SCA (OWASP Dependency-Check, npm audit)
        
        Pourquoi : Extraire les vulnérabilités des dépendances
        Comment : Cherche les fichiers dependency-check-report.json et npm-audit-report.json
        """
        vulnerabilities = []
        sca_dir = self.reports_dir / "sca"
        
        if not sca_dir.exists():
            print("⚠️  Dossier SCA non trouvé")
            return vulnerabilities
        
        # Parse OWASP Dependency-Check (JSON)
        depcheck_file = sca_dir / "backend-dependency-check-report.json"
        if depcheck_file.exists():
            print(f"📄 Parsing OWASP Dependency-Check: {depcheck_file}")
            vulns = DependencyCheckParser.parse(str(depcheck_file))
            vulnerabilities.extend(vulns)
            print(f"   → {len(vulns)} vulnérabilités trouvées")
        else:
            print(f"⚠️  Dependency-Check report non trouvé: {depcheck_file}")
        
        # Parse npm audit (JSON)
        npm_audit_file = sca_dir / "frontend-npm-audit-report.json"
        if npm_audit_file.exists():
            print(f"📄 Parsing npm audit: {npm_audit_file}")
            vulns = NpmAuditParser.parse(str(npm_audit_file))
            vulnerabilities.extend(vulns)
            print(f"   → {len(vulns)} vulnérabilités trouvées")
        else:
            print(f"⚠️  npm audit report non trouvé: {npm_audit_file}")
        
        return vulnerabilities
    
    def _parse_dast(self) -> List[Vulnerability]:
        """
        Parse les rapports DAST (OWASP ZAP)
        
        Pourquoi : Extraire les vulnérabilités détectées lors des tests dynamiques
        Comment : Cherche le fichier zap-report.json
        """
        vulnerabilities = []
        dast_dir = self.reports_dir / "dast"
        
        if not dast_dir.exists():
            print("⚠️  Dossier DAST non trouvé")
            return vulnerabilities
        
        # Parse OWASP ZAP (JSON)
        zap_file = dast_dir / "zap-report.json"
        if zap_file.exists():
            print(f"📄 Parsing OWASP ZAP: {zap_file}")
            vulns = ZAPParser.parse(str(zap_file))
            vulnerabilities.extend(vulns)
            print(f"   → {len(vulns)} vulnérabilités trouvées")
        else:
            print(f"⚠️  ZAP report non trouvé: {zap_file}")
        
        return vulnerabilities
    
    def save_normalized_report(self, output_file: str = "parser/reports/normalized_vulnerabilities.json"):
        """
        Sauvegarde toutes les vulnérabilités dans un format normalisé JSON
        
        Pourquoi : Créer un fichier unique avec toutes les vulnérabilités pour l'étape LLM
        Comment : Convertit tous les objets Vulnerability en JSON
        
        Args:
            output_file: Chemin du fichier de sortie
        """
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convertir en dictionnaires
        vulns_dict = [vuln.to_dict() for vuln in self.vulnerabilities]
        
        # Sauvegarder en JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(vulns_dict, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Rapport normalisé sauvegardé: {output_path}")
        print(f"   {len(self.vulnerabilities)} vulnérabilités exportées")
        
        return output_path
    
    def get_statistics(self) -> Dict:
        """
        Génère des statistiques sur les vulnérabilités détectées
        
        Pourquoi : Avoir une vue d'ensemble des vulnérabilités
        Comment : Compte les vulnérabilités par type, sévérité, etc.
        
        Returns:
            Dictionnaire avec les statistiques
        """
        stats = {
            "total": len(self.vulnerabilities),
            "by_type": {},
            "by_severity": {},
            "by_category": {},
        }
        
        # Compter par type
        for vuln_type in VulnerabilityType:
            count = sum(1 for v in self.vulnerabilities if v.vulnerability_type == vuln_type)
            stats["by_type"][vuln_type.value] = count
        
        # Compter par sévérité
        from vulnerability_model import Severity
        for severity in Severity:
            count = sum(1 for v in self.vulnerabilities if v.severity == severity)
            stats["by_severity"][severity.value] = count
        
        # Compter par catégorie
        categories = {}
        for vuln in self.vulnerabilities:
            cat = vuln.category
            categories[cat] = categories.get(cat, 0) + 1
        stats["by_category"] = categories
        
        return stats
    
    def print_statistics(self):
        """Affiche les statistiques de manière lisible"""
        stats = self.get_statistics()
        
        print("\n" + "="*60)
        print("📊 STATISTIQUES DES VULNÉRABILITÉS")
        print("="*60)
        print(f"\n🔢 Total: {stats['total']} vulnérabilités")
        
        print("\n📋 Par type d'analyse:")
        for vuln_type, count in stats["by_type"].items():
            print(f"   • {vuln_type}: {count}")
        
        print("\n⚠️  Par niveau de sévérité:")
        for severity, count in sorted(stats["by_severity"].items(), 
                                      key=lambda x: ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"].index(x[0]) if x[0] in ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"] else 999):
            print(f"   • {severity}: {count}")
        
        print("\n🏷️  Top 5 catégories:")
        top_categories = sorted(stats["by_category"].items(), 
                               key=lambda x: x[1], reverse=True)[:5]
        for category, count in top_categories:
            print(f"   • {category}: {count}")
        
        print("\n" + "="*60)


def main():
    """
    Point d'entrée principal du parser
    
    Pourquoi : Permettre d'exécuter le parser depuis la ligne de commande
    Comment : python parser/main_parser.py
    """
    # Déterminer le répertoire des rapports
    reports_dir = sys.argv[1] if len(sys.argv) > 1 else "reports"
    
    # Créer et exécuter le parser
    parser = VulnerabilityReportParser(reports_directory=reports_dir)
    vulnerabilities = parser.parse_all()
    
    # Afficher les statistiques
    parser.print_statistics()
    
    # Sauvegarder le rapport normalisé
    parser.save_normalized_report()
    
    print(f"\n✅ Parsing terminé avec succès!")


if __name__ == "__main__":
    main()

