"""
Parser pour les rapports DAST (Dynamic Application Security Testing)

Pourquoi : Extraire les vulnérabilités détectées lors des tests dynamiques
Comment : Parse les rapports OWASP ZAP
"""
import json
from typing import List
from pathlib import Path

from ..vulnerability_model import Vulnerability, Severity, VulnerabilityType


class ZAPParser:
    """
    Parser pour les rapports OWASP ZAP (format JSON)
    
    Pourquoi : ZAP teste l'application en cours d'exécution et détecte des vulnérabilités runtime
    Comment : Parse le JSON et extrait les alertes ZAP
    """
    
    # Mapping des niveaux de risque ZAP vers nos sévérités
    RISK_SEVERITY_MAP = {
        "Informational": Severity.INFO,
        "Low": Severity.LOW,
        "Medium": Severity.MEDIUM,
        "High": Severity.HIGH,
        "Critical": Severity.CRITICAL,
    }
    
    # Mapping des alertes ZAP vers des catégories de vulnérabilités
    ALERT_CATEGORIES = {
        "XSS": "Cross-Site Scripting (XSS)",
        "SQL Injection": "SQL Injection",
        "CSRF": "Cross-Site Request Forgery",
        "Path Traversal": "Path Traversal",
        "Command Injection": "Command Injection",
        "XXE": "XML External Entity",
        "SSRF": "Server-Side Request Forgery",
        "Open Redirect": "Open Redirect",
        "Missing Security Headers": "Missing Security Headers",
        "Information Disclosure": "Information Disclosure",
    }
    
    @staticmethod
    def parse(file_path: str) -> List[Vulnerability]:
        """
        Parse un fichier JSON OWASP ZAP
        
        Args:
            file_path: Chemin vers le fichier zap-report.json
            
        Returns:
            Liste de vulnérabilités détectées
        """
        vulnerabilities = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Structure ZAP JSON peut varier
            # Format 1: avec "site" (rapport complet)
            if "site" in data:
                sites = data["site"] if isinstance(data["site"], list) else [data["site"]]
                for site in sites:
                    alerts = site.get("alerts", [])
                    for alert in alerts:
                        vulnerability = ZAPParser._parse_alert(alert, site.get("@name", "Unknown"))
                        if vulnerability:
                            vulnerabilities.append(vulnerability)
            
            # Format 2: directement une liste d'alertes
            elif isinstance(data, list):
                for alert in data:
                    vulnerability = ZAPParser._parse_alert(alert, "Unknown")
                    if vulnerability:
                        vulnerabilities.append(vulnerability)
            
            # Format 3: avec "@name" et "alerts" (rapport simplifié)
            elif "alerts" in data:
                alerts = data["alerts"]
                for alert in alerts:
                    vulnerability = ZAPParser._parse_alert(alert, data.get("@name", "Unknown"))
                    if vulnerability:
                        vulnerabilities.append(vulnerability)
                        
        except FileNotFoundError:
            print(f"⚠️  Fichier ZAP non trouvé: {file_path}")
        except json.JSONDecodeError as e:
            print(f"❌ Erreur lors du parsing JSON ZAP: {e}")
        except KeyError as e:
            print(f"⚠️  Format ZAP inattendu, clé manquante: {e}")
        
        return vulnerabilities
    
    @staticmethod
    def _parse_alert(alert: dict, site_name: str) -> Vulnerability:
        """
        Parse une alerte ZAP en objet Vulnerability
        
        Pourquoi : Normaliser les alertes ZAP en notre format standard
        Comment : Extrait les informations pertinentes de l'alerte
        """
        # Extraire les informations de base
        alert_name = alert.get("name", alert.get("@name", "Unknown Alert"))
        risk_code = alert.get("riskcode", alert.get("@riskcode", "0"))
        confidence = alert.get("confidence", alert.get("@confidence", "0"))
        
        # Convertir le code de risque en sévérité
        risk_levels = {
            "0": Severity.INFO,
            "1": Severity.LOW,
            "2": Severity.MEDIUM,
            "3": Severity.HIGH,
            "4": Severity.CRITICAL,
        }
        severity = risk_levels.get(str(risk_code), Severity.MEDIUM)
        
        # Si le format utilise "riskdesc" (description du risque)
        if "riskdesc" in alert:
            risk_str = alert["riskdesc"].split()[0]  # Prendre le premier mot
            severity = ZAPParser.RISK_SEVERITY_MAP.get(risk_str, severity)
        
        # Extraire la description
        description = alert.get("desc", alert.get("description", "No description"))
        
        # Extraire la solution
        solution = alert.get("solution", alert.get("recommendation", "Review and fix the vulnerability"))
        
        # Extraire la catégorie
        category = ZAPParser._determine_category(alert_name)
        
        # Extraire l'URL/endpoint
        instances = alert.get("instances", [])
        endpoint = None
        http_method = None
        
        if instances:
            first_instance = instances[0] if isinstance(instances, list) else instances
            uri = first_instance.get("uri", first_instance.get("@uri", ""))
            endpoint = uri
            
            # Extraire la méthode HTTP si disponible
            method = first_instance.get("method", first_instance.get("@method", ""))
            http_method = method if method else "GET"  # Par défaut GET
        
        # Créer un ID unique pour la vulnérabilité
        alert_id = alert.get("pluginid", alert.get("@pluginid", hash(alert_name)))
        vuln_id = f"ZAP-{alert_id}-{hash(str(instances))}"
        
        return Vulnerability(
            id=vuln_id,
            title=f"{category}: {alert_name}",
            severity=severity,
            vulnerability_type=VulnerabilityType.DAST,
            category=category,
            description=description,
            recommendation=solution,
            endpoint=endpoint,
            http_method=http_method,
            tool_name="OWASP ZAP",
            raw_data=alert
        )
    
    @staticmethod
    def _determine_category(alert_name: str) -> str:
        """
        Détermine la catégorie de vulnérabilité à partir du nom de l'alerte
        
        Pourquoi : Classifier les vulnérabilités ZAP en catégories standardisées
        Comment : Cherche des mots-clés dans le nom de l'alerte
        """
        alert_name_upper = alert_name.upper()
        
        # Chercher les mots-clés pour déterminer la catégorie
        if "XSS" in alert_name_upper or "CROSS-SITE SCRIPTING" in alert_name_upper:
            return "Cross-Site Scripting (XSS)"
        elif "SQL" in alert_name_upper and "INJECTION" in alert_name_upper:
            return "SQL Injection"
        elif "CSRF" in alert_name_upper or "CROSS-SITE REQUEST FORGERY" in alert_name_upper:
            return "Cross-Site Request Forgery"
        elif "PATH" in alert_name_upper and "TRAVERSAL" in alert_name_upper:
            return "Path Traversal"
        elif "COMMAND" in alert_name_upper and "INJECTION" in alert_name_upper:
            return "Command Injection"
        elif "XXE" in alert_name_upper or "XML EXTERNAL ENTITY" in alert_name_upper:
            return "XML External Entity"
        elif "SSRF" in alert_name_upper:
            return "Server-Side Request Forgery"
        elif "REDIRECT" in alert_name_upper:
            return "Open Redirect"
        elif "HEADER" in alert_name_upper or "SECURITY" in alert_name_upper:
            return "Missing Security Headers"
        elif "INFORMATION" in alert_name_upper or "DISCLOSURE" in alert_name_upper:
            return "Information Disclosure"
        else:
            return "Security Vulnerability"

