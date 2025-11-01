"""
Parser pour les rapports SCA (Software Composition Analysis)

Pourquoi : Extraire les vulnérabilités des dépendances (CVE)
Comment : Parse les rapports OWASP Dependency-Check et npm audit
"""
import json
from typing import List
from pathlib import Path

from ..vulnerability_model import Vulnerability, Severity, VulnerabilityType


class DependencyCheckParser:
    """
    Parser pour les rapports OWASP Dependency-Check (format JSON)
    
    Pourquoi : Dependency-Check analyse les dépendances Maven/npm pour trouver des CVE
    Comment : Parse le JSON et extrait les vulnérabilités avec leur CVE
    """
    
    # Mapping des scores CVSS vers nos niveaux de sévérité
    CVSS_SEVERITY_MAP = {
        (9.0, 10.0): Severity.CRITICAL,
        (7.0, 9.0): Severity.HIGH,
        (4.0, 7.0): Severity.MEDIUM,
        (0.1, 4.0): Severity.LOW,
        (0.0, 0.1): Severity.INFO,
    }
    
    @staticmethod
    def parse(file_path: str) -> List[Vulnerability]:
        """
        Parse un fichier JSON OWASP Dependency-Check
        
        Args:
            file_path: Chemin vers le fichier dependency-check-report.json
            
        Returns:
            Liste de vulnérabilités détectées (CVE)
        """
        vulnerabilities = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Structure Dependency-Check JSON
            dependencies = data.get("dependencies", [])
            
            for dependency in dependencies:
                # Extraire les informations de la dépendance
                package_name = dependency.get("fileName", "Unknown")
                package_path = dependency.get("filePath", "")
                
                # Extraire les vulnérabilités
                vulnerabilities_list = dependency.get("vulnerabilities", [])
                
                for vuln in vulnerabilities_list:
                    # Extraire les informations de la CVE
                    cve_id = vuln.get("name", "UNKNOWN-CVE")
                    description = vuln.get("description", "No description available")
                    
                    # Extraire le score CVSS
                    cvss_v3 = vuln.get("cvssv3", {})
                    base_score = cvss_v3.get("baseScore", 0.0)
                    
                    # Convertir le score CVSS en sévérité
                    severity = DependencyCheckParser._cvss_to_severity(base_score)
                    
                    # Informations additionnelles
                    cwe = vuln.get("cwe", "Unknown")
                    
                    # Recommandation
                    fixed_version = dependency.get("evidenceCollected", {}).get(
                        "versionEvidence", [{}]
                    )[0].get("value", "Unknown")
                    
                    vulnerability = Vulnerability(
                        id=cve_id,
                        title=f"CVE: {cve_id}",
                        severity=severity,
                        vulnerability_type=VulnerabilityType.SCA,
                        category="CVE",
                        description=description,
                        recommendation=f"Update dependency {package_name} to a fixed version. CWE: {cwe}",
                        file_path=package_path,
                        dependency_name=package_name,
                        dependency_version=dependency.get("packages", [{}])[0].get("version", "Unknown"),
                        fixed_version=fixed_version,
                        tool_name="OWASP Dependency-Check",
                        raw_data=vuln
                    )
                    
                    vulnerabilities.append(vulnerability)
                    
        except FileNotFoundError:
            print(f"⚠️  Fichier Dependency-Check non trouvé: {file_path}")
        except json.JSONDecodeError as e:
            print(f"❌ Erreur lors du parsing JSON Dependency-Check: {e}")
        except KeyError as e:
            print(f"⚠️  Format Dependency-Check inattendu, clé manquante: {e}")
        
        return vulnerabilities
    
    @staticmethod
    def _cvss_to_severity(score: float) -> Severity:
        """Convertit un score CVSS en niveau de sévérité"""
        for (min_score, max_score), severity in DependencyCheckParser.CVSS_SEVERITY_MAP.items():
            if min_score <= score <= max_score:
                return severity
        return Severity.LOW


class NpmAuditParser:
    """
    Parser pour les rapports npm audit (format JSON)
    
    Pourquoi : npm audit scanne les packages npm pour trouver des vulnérabilités
    Comment : Parse le JSON et extrait les vulnérabilités avec leur CVE
    """
    
    # Mapping des niveaux npm audit vers nos sévérités
    SEVERITY_MAP = {
        "critical": Severity.CRITICAL,
        "high": Severity.HIGH,
        "moderate": Severity.MEDIUM,
        "low": Severity.LOW,
        "info": Severity.INFO,
    }
    
    @staticmethod
    def parse(file_path: str) -> List[Vulnerability]:
        """
        Parse un fichier JSON npm audit
        
        Args:
            file_path: Chemin vers le fichier npm-audit-report.json
            
        Returns:
            Liste de vulnérabilités détectées
        """
        vulnerabilities = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # npm audit peut avoir deux structures différentes
            # Structure 1: avec "vulnerabilities"
            if "vulnerabilities" in data:
                vulns = data["vulnerabilities"]
                for package_name, vuln_info in vulns.items():
                    vulnerability = NpmAuditParser._parse_vulnerability(
                        package_name, vuln_info, file_path
                    )
                    if vulnerability:
                        vulnerabilities.append(vulnerability)
            
            # Structure 2: avec "advisories" (ancien format)
            elif "advisories" in data:
                advisories = data["advisories"]
                for advisory_id, advisory in advisories.items():
                    vulnerability = NpmAuditParser._parse_advisory(
                        advisory, file_path
                    )
                    if vulnerability:
                        vulnerabilities.append(vulnerability)
                        
        except FileNotFoundError:
            print(f"⚠️  Fichier npm audit non trouvé: {file_path}")
        except json.JSONDecodeError as e:
            print(f"❌ Erreur lors du parsing JSON npm audit: {e}")
        
        return vulnerabilities
    
    @staticmethod
    def _parse_vulnerability(package_name: str, vuln_info: dict, file_path: str) -> Vulnerability:
        """Parse une vulnérabilité du format npm audit moderne"""
        severity_str = vuln_info.get("severity", "moderate").lower()
        severity = NpmAuditParser.SEVERITY_MAP.get(severity_str, Severity.MEDIUM)
        
        # Extraire la CVE si disponible
        cve_ids = vuln_info.get("cves", [])
        cve_id = cve_ids[0] if cve_ids else f"NPM-AUDIT-{package_name}"
        
        # Extraire la version
        version = vuln_info.get("range", "Unknown")
        
        # Trouver une version fixée
        fix_available = vuln_info.get("fixAvailable", False)
        fixed_version = None
        if isinstance(fix_available, dict) and fix_available.get("version"):
            fixed_version = fix_available.get("version")
        
        return Vulnerability(
            id=cve_id,
            title=f"npm package vulnerability: {package_name}",
            severity=severity,
            vulnerability_type=VulnerabilityType.SCA,
            category="CVE",
            description=vuln_info.get("title", f"Vulnerability in {package_name}"),
            recommendation=f"Update {package_name} to version {fixed_version or 'latest secure version'}. Run: npm audit fix",
            dependency_name=package_name,
            dependency_version=version,
            fixed_version=fixed_version,
            file_path=file_path,
            tool_name="npm audit",
            raw_data=vuln_info
        )
    
    @staticmethod
    def _parse_advisory(advisory: dict, file_path: str) -> Vulnerability:
        """Parse un advisory du format npm audit ancien"""
        severity_str = advisory.get("severity", "moderate").lower()
        severity = NpmAuditParser.SEVERITY_MAP.get(severity_str, Severity.MEDIUM)
        
        cve_id = advisory.get("cve", f"NPM-ADVISORY-{advisory.get('id', 'UNKNOWN')}")
        title = advisory.get("title", "npm package vulnerability")
        
        return Vulnerability(
            id=cve_id,
            title=title,
            severity=severity,
            vulnerability_type=VulnerabilityType.SCA,
            category="CVE",
            description=advisory.get("overview", "No description"),
            recommendation=advisory.get("recommendation", "Update the package to a secure version"),
            dependency_name=advisory.get("module_name", "Unknown"),
            dependency_version=advisory.get("vulnerable_versions", "Unknown"),
            fixed_version=advisory.get("patched_versions", None),
            file_path=file_path,
            tool_name="npm audit",
            raw_data=advisory
        )

