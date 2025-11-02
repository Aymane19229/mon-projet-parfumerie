"""
Prompts pour générer des politiques de sécurité conformes à ISO/IEC 27001

Pourquoi : ISO 27001 est un standard international pour la gestion de la sécurité de l'information
Comment : Créer des prompts structurés qui guident le LLM pour générer des politiques conformes
"""

from typing import List, Dict


class ISO27001Prompt:
    """
    Générateur de prompts pour politiques ISO 27001
    
    Pourquoi : Structurer les prompts de manière cohérente pour obtenir des résultats conformes ISO 27001
    Comment : Combine les vulnérabilités avec les contrôles ISO 27001 appropriés
    """
    
    # Mapping des contrôles ISO 27001 (Annexe A)
    ISO_CONTROLS = {
        "SQL Injection": "A.14.2.5",  # Gestion sécurisée des applications
        "Cross-Site Scripting (XSS)": "A.14.2.5",
        "CVE": "A.12.6.1",  # Gestion des vulnérabilités techniques
        "Weak Cryptography": "A.10.1.1",  # Politique de cryptage
        "Path Traversal": "A.14.2.5",
        "Command Injection": "A.14.2.5",
        "Missing Security Headers": "A.14.2.5",
        "Information Disclosure": "A.9.4.2",  # Contrôle d'accès
        "Code Injection": "A.14.2.5",
        "Authentication": "A.9.2.1",  # Gestion des utilisateurs
    }
    
    # Domaines ISO 27001 (Annexe A)
    ISO_DOMAINS = {
        "A.9": "Contrôle d'accès",
        "A.10": "Cryptographie",
        "A.12": "Sécurité opérationnelle",
        "A.14": "Sécurité des systèmes d'acquisition, développement et maintenance",
    }
    
    @staticmethod
    def generate_policy_prompt(vulnerabilities: List[Dict], iso_control: str = "A.14.2.5") -> str:
        """
        Génère un prompt pour créer une politique ISO 27001
        
        Pourquoi : Transformer les vulnérabilités techniques en prompt structuré pour le LLM
        Comment : Combine les informations des vulnérabilités avec les contrôles ISO 27001
        
        Args:
            vulnerabilities: Liste des vulnérabilités normalisées
            iso_control: Contrôle ISO 27001 (ex: A.14.2.5)
            
        Returns:
            Prompt structuré pour le LLM
        """
        
        # Grouper les vulnérabilités par catégorie
        by_category = {}
        for vuln in vulnerabilities:
            category = vuln.get("category", "Security Vulnerability")
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(vuln)
        
        # Construire le prompt
        prompt = f"""Tu es un expert en cybersécurité et conformité. Ta tâche est de générer une politique de sécurité conforme à la norme ISO/IEC 27001:2022.

# Contexte du Projet
L'organisation développe un système e-commerce (parfumerie) avec :
- Backend : Spring Boot (Java)
- Frontend : React (JavaScript)
- Base de données : MySQL

# Vulnérabilités Détectées

"""
        
        # Ajouter les détails des vulnérabilités
        for category, vulns in by_category.items():
            prompt += f"## {category}\n\n"
            for vuln in vulns[:5]:  # Limiter à 5 par catégorie
                prompt += f"- **{vuln.get('title', 'Vulnérabilité')}** (Sévérité: {vuln.get('severity', 'UNKNOWN')})\n"
                prompt += f"  - Description: {vuln.get('description', 'N/A')}\n"
                if vuln.get('recommendation'):
                    prompt += f"  - Recommandation: {vuln.get('recommendation')}\n"
                if vuln.get('file_path'):
                    prompt += f"  - Localisation: {vuln.get('file_path')}\n"
                if vuln.get('dependency_name'):
                    prompt += f"  - Dépendance: {vuln.get('dependency_name')} (version: {vuln.get('dependency_version')})\n"
                prompt += "\n"
        
        # Récupérer le domaine ISO correspondant
        iso_domain = iso_control.split(".")[0] + "." + iso_control.split(".")[1]
        domain_name = ISO27001Prompt.ISO_DOMAINS.get(iso_domain, "Sécurité de l'information")
        
        # Ajouter les instructions
        prompt += f"""
# Instructions

Génère une politique de sécurité conforme à l'ISO/IEC 27001:2022, spécifiquement pour le contrôle **{iso_control}** ({domain_name}).

La politique doit :
1. **Être conforme à ISO 27001** : Référencer le contrôle et les exigences ISO appropriées
2. **Suivre la structure ISO** : Objectif, portée, responsabilités, contrôles
3. **Être actionnable** : Fournir des mesures concrètes à implémenter
4. **Être liée aux vulnérabilités** : Montrer comment la politique répond aux vulnérabilités détectées
5. **Respecter le cycle PDCA** : Plan-Do-Check-Act (Planifier-Implémenter-Vérifier-Agir)

# Format Requis

Structure la politique comme suit :

## 1. Informations de Base
- **ID Politique** : ISO27001-{iso_control}
- **Titre** : [Titre clair et descriptif]
- **Référence ISO** : ISO/IEC 27001:2022 - {iso_control}
- **Domaine** : {domain_name}
- **Version** : 1.0
- **Date** : [Date actuelle]

## 2. Objectif
[Décrire l'objectif de la politique et son alignement avec ISO 27001]

## 3. Portée
[Systèmes d'information, processus et actifs couverts par cette politique]

## 4. Références Normatives
- ISO/IEC 27001:2022
- ISO/IEC 27002:2022 (Guide des contrôles)
- [Autres références pertinentes]

## 5. Définitions
[Définir les termes techniques utilisés dans la politique]

## 6. Contrôles ISO 27001

Pour le contrôle {iso_control}, détailler :

### 6.1 Exigences
[Liste des exigences spécifiques du contrôle ISO]

### 6.2 Mesures de Contrôle
Pour chaque mesure :
- **Description** : [Description de la mesure]
- **Implémentation** : [Comment implémenter concrètement]
- **Vulnérabilités adressées** : [Références aux vulnérabilités détectées]
- **Indicateurs** : [Comment mesurer l'efficacité]

### 6.3 Responsabilités
- **Responsable de la sécurité** : [Rôle]
- **Équipe de développement** : [Rôles]
- **Équipe DevOps** : [Rôles]

## 7. Conformité et Audit
[Comment vérifier la conformité et auditer la mise en œuvre]

## 8. Révision et Maintenance
[Fréquence de révision et processus de mise à jour]

## 9. Approbation
[Qui approuve cette politique]

Génère maintenant la politique de sécurité ISO 27001 complète et structurée, en français.
"""
        
        return prompt
    
    @staticmethod
    def generate_category_prompt(vulnerabilities: List[Dict], iso_control: str) -> str:
        """
        Génère un prompt pour un contrôle ISO 27001 spécifique
        
        Pourquoi : Créer des politiques plus spécifiques pour chaque contrôle ISO
        Comment : Filtre les vulnérabilités pertinentes et génère un prompt ciblé
        """
        
        # Filtrer les vulnérabilités pertinentes
        relevant_vulns = [
            v for v in vulnerabilities 
            if ISO27001Prompt.ISO_CONTROLS.get(v.get("category", ""), "").startswith(iso_control.split(".")[0] + "." + iso_control.split(".")[1])
        ]
        
        if not relevant_vulns:
            relevant_vulns = vulnerabilities[:10]
        
        return ISO27001Prompt.generate_policy_prompt(relevant_vulns, iso_control)
    
    @staticmethod
    def get_iso_mapping(vulnerability_category: str) -> str:
        """
        Retourne le contrôle ISO 27001 approprié pour une vulnérabilité
        
        Pourquoi : Mapper les types de vulnérabilités aux contrôles ISO appropriés
        Comment : Utilise un mapping prédéfini
        """
        return ISO27001Prompt.ISO_CONTROLS.get(
            vulnerability_category,
            "A.14.2.5"  # Par défaut : Gestion sécurisée des applications
        )

