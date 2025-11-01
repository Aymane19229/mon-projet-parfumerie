"""
Parser pour les rapports SAST (Static Application Security Testing)

Pourquoi : Extraire les vulnérabilités des rapports SpotBugs et ESLint
Comment : Parse les fichiers XML/JSON et convertit en objets Vulnerability
"""
import json
import xml.etree.ElementTree as ET
from typing import List, Optional
from pathlib import Path

from ..vulnerability_model import Vulnerability, Severity, VulnerabilityType


class SpotBugsParser:
    """
    Parser pour les rapports SpotBugs (format XML)
    
    Pourquoi : SpotBugs génère des rapports XML avec des bugs et vulnérabilités
    Comment : Parse le XML et extrait les bugs de sécurité
    """
    
    # Mapping des priorités SpotBugs vers nos niveaux de sévérité
    PRIORITY_TO_SEVERITY = {
        "CRITICAL": Severity.CRITICAL,
        "HIGH": Severity.HIGH,
        "MEDIUM": Severity.MEDIUM,
        "LOW": Severity.LOW,
    }
    
    # Mapping des catégories SpotBugs pour identifier les vulnérabilités de sécurité
    SECURITY_CATEGORIES = {
        "SQL_INJECTION": "SQL Injection",
        "XSS": "Cross-Site Scripting",
        "CRYPTOGRAPHIC": "Weak Cryptography",
        "PATH_MANIPULATION": "Path Traversal",
        "COMMAND_INJECTION": "Command Injection",
        "LDAP_INJECTION": "LDAP Injection",
        "XPATH_INJECTION": "XPath Injection",
    }
    
    @staticmethod
    def parse(file_path: str) -> List[Vulnerability]:
        """
        Parse un fichier XML SpotBugs
        
        Args:
            file_path: Chemin vers le fichier spotbugs-report.xml
            
        Returns:
            Liste de vulnérabilités détectées
        """
        vulnerabilities = []
        
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # SpotBugs stocke les bugs dans des éléments BugInstance
            for bug_instance in root.findall(".//BugInstance"):
                # Extraire les informations du bug
                bug_type = bug_instance.get("type", "UNKNOWN")
                priority = bug_instance.get("priority", "LOW")
                
                # Filtrer uniquement les bugs de sécurité
                if not SpotBugsParser._is_security_bug(bug_type):
                    continue
                
                # Extraire le message
                short_message = bug_instance.find("ShortMessage")
                message = short_message.text if short_message is not None else bug_type
                
                # Extraire la localisation (fichier, ligne)
                source_line = bug_instance.find(".//SourceLine")
                file_path = None
                line_number = None
                if source_line is not None:
                    file_path = source_line.get("sourcepath")
                    line_number = int(source_line.get("start", 0)) if source_line.get("start") else None
                
                # Extraire la méthode/fonction
                method = bug_instance.find(".//Method")
                function_name = None
                if method is not None:
                    function_name = method.get("name")
                
                # Convertir la priorité en sévérité
                severity = SpotBugsParser.PRIORITY_TO_SEVERITY.get(
                    priority, Severity.LOW
                )
                
                # Déterminer la catégorie
                category = SpotBugsParser.SECURITY_CATEGORIES.get(
                    bug_type, "Code Quality Issue"
                )
                
                # Créer l'objet Vulnerability
                vulnerability = Vulnerability(
                    id=f"SPOTBUGS-{bug_type}-{hash(bug_instance.get('instanceHash', ''))}",
                    title=f"{category}: {message}",
                    severity=severity,
                    vulnerability_type=VulnerabilityType.SAST,
                    category=category,
                    description=f"SpotBugs detected: {message}. Type: {bug_type}",
                    recommendation="Review the code and fix the security issue. Use parameterized queries for SQL, sanitize inputs for XSS, use strong cryptography.",
                    file_path=file_path,
                    line_number=line_number,
                    function_name=function_name,
                    tool_name="SpotBugs",
                    raw_data={
                        "bug_type": bug_type,
                        "priority": priority,
                        "instance_hash": bug_instance.get("instanceHash")
                    }
                )
                
                vulnerabilities.append(vulnerability)
                
        except ET.ParseError as e:
            print(f"❌ Erreur lors du parsing XML SpotBugs: {e}")
        except FileNotFoundError:
            print(f"⚠️  Fichier SpotBugs non trouvé: {file_path}")
        
        return vulnerabilities
    
    @staticmethod
    def _is_security_bug(bug_type: str) -> bool:
        """Vérifie si un bug est lié à la sécurité"""
        security_keywords = [
            "SQL", "XSS", "CRYPTO", "INJECTION", 
            "PATH", "COMMAND", "LDAP", "XPATH"
        ]
        return any(keyword in bug_type.upper() for keyword in security_keywords)


class ESLintParser:
    """
    Parser pour les rapports ESLint (format JSON)
    
    Pourquoi : ESLint génère des rapports JSON avec des problèmes de code
    Comment : Parse le JSON et extrait les problèmes de sécurité
    """
    
    # Mapping des règles ESLint de sécurité
    SECURITY_RULES = {
        "no-eval": "Code Injection",
        "no-implied-eval": "Code Injection",
        "no-new-func": "Code Injection",
        "no-script-url": "XSS",
        "react/no-danger": "XSS",
        "react/no-danger-with-children": "XSS",
    }
    
    @staticmethod
    def parse(file_path: str) -> List[Vulnerability]:
        """
        Parse un fichier JSON ESLint
        
        Args:
            file_path: Chemin vers le fichier eslint-report.json
            
        Returns:
            Liste de vulnérabilités détectées
        """
        vulnerabilities = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                # ESLint peut générer du texte brut, on essaie JSON d'abord
                content = f.read()
                try:
                    data = json.loads(content)
                except json.JSONDecodeError:
                    # Si ce n'est pas du JSON valide, c'est probablement du texte brut
                    # On parse ligne par ligne pour trouver les erreurs
                    return ESLintParser._parse_text_output(content, file_path)
                
            # Format JSON standard ESLint
            if isinstance(data, list):
                for result in data:
                    file_path_item = result.get("filePath", "")
                    messages = result.get("messages", [])
                    
                    for message in messages:
                        if ESLintParser._is_security_issue(message):
                            vulnerability = ESLintParser._create_vulnerability(
                                message, file_path_item
                            )
                            vulnerabilities.append(vulnerability)
                            
        except FileNotFoundError:
            print(f"⚠️  Fichier ESLint non trouvé: {file_path}")
        except json.JSONDecodeError as e:
            print(f"❌ Erreur lors du parsing JSON ESLint: {e}")
        
        return vulnerabilities
    
    @staticmethod
    def _parse_text_output(content: str, file_path: str) -> List[Vulnerability]:
        """Parse la sortie texte d'ESLint"""
        vulnerabilities = []
        lines = content.split('\n')
        
        for line in lines:
            # Format: /path/to/file.js:10:5 error Rule 'no-eval' was violated
            if 'error' in line.lower() or 'warning' in line.lower():
                parts = line.split(':')
                if len(parts) >= 3:
                    file_path_item = parts[0]
                    line_number = int(parts[1]) if parts[1].isdigit() else None
                    
                    # Chercher les règles de sécurité
                    for rule_name, category in ESLintParser.SECURITY_RULES.items():
                        if rule_name in line:
                            vulnerability = Vulnerability(
                                id=f"ESLINT-{rule_name}-{hash(line)}",
                                title=f"{category}: {rule_name} violation",
                                severity=Severity.MEDIUM,
                                vulnerability_type=VulnerabilityType.SAST,
                                category=category,
                                description=f"ESLint detected security issue: {line}",
                                recommendation=f"Fix ESLint rule violation: {rule_name}",
                                file_path=file_path_item,
                                line_number=line_number,
                                tool_name="ESLint",
                                raw_data={"rule": rule_name, "line": line}
                            )
                            vulnerabilities.append(vulnerability)
                            break
        
        return vulnerabilities
    
    @staticmethod
    def _is_security_issue(message: dict) -> bool:
        """Vérifie si un message ESLint est lié à la sécurité"""
        rule_id = message.get("ruleId", "")
        return any(rule in rule_id for rule in ESLintParser.SECURITY_RULES.keys())
    
    @staticmethod
    def _create_vulnerability(message: dict, file_path: str) -> Vulnerability:
        """Crée un objet Vulnerability à partir d'un message ESLint"""
        rule_id = message.get("ruleId", "UNKNOWN")
        category = ESLintParser.SECURITY_RULES.get(
            rule_id, "Code Quality Issue"
        )
        
        # Déterminer la sévérité
        severity_map = {
            2: Severity.HIGH,  # error
            1: Severity.MEDIUM,  # warning
            0: Severity.LOW     # off
        }
        severity = severity_map.get(
            message.get("severity", 1), Severity.MEDIUM
        )
        
        return Vulnerability(
            id=f"ESLINT-{rule_id}-{message.get('line', 0)}",
            title=f"{category}: {rule_id}",
            severity=severity,
            vulnerability_type=VulnerabilityType.SAST,
            category=category,
            description=message.get("message", "ESLint security issue"),
            recommendation=f"Fix ESLint rule: {rule_id}. Review the code for security best practices.",
            file_path=file_path,
            line_number=message.get("line"),
            function_name=None,
            tool_name="ESLint",
            raw_data=message
        )

