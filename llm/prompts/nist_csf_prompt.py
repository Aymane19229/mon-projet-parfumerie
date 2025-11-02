"""
Prompts pour générer des politiques de sécurité conformes à NIST CSF

Pourquoi : NIST CSF (Cybersecurity Framework) est un standard reconnu pour la gestion de la cybersécurité
Comment : Créer des prompts structurés qui guident le LLM pour générer des politiques conformes
"""

from typing import List, Dict


class NISTCSFPrompt:
    """
    Générateur de prompts pour politiques NIST CSF
    
    Pourquoi : Structurer les prompts de manière cohérente pour obtenir des résultats conformes
    Comment : Combine les vulnérabilités avec les catégories NIST CSF appropriées
    """
    
    # Mapping des catégories NIST CSF
    NIST_CATEGORIES = {
        "SQL Injection": "PR.DS-5",  # Protections contre injection
        "Cross-Site Scripting (XSS)": "PR.DS-5",
        "CVE": "PR.DS-2",  # Gestion des vulnérabilités
        "Weak Cryptography": "PR.DS-1",  # Protection des données
        "Path Traversal": "PR.DS-5",
        "Command Injection": "PR.DS-5",
        "Missing Security Headers": "PR.DS-6",  # Configuration sécurisée
        "Information Disclosure": "PR.DS-4",  # Protection des informations
    }
    
    # Fonctions NIST CSF principales
    NIST_FUNCTIONS = {
        "IDENTIFY": "Identifier les systèmes, actifs, données et capacités",
        "PROTECT": "Développer et implémenter des protections",
        "DETECT": "Développer et implémenter des activités de détection",
        "RESPOND": "Développer et implémenter des activités de réponse",
        "RECOVER": "Développer et implémenter des activités de récupération"
    }
    
    @staticmethod
    def generate_policy_prompt(vulnerabilities: List[Dict], framework_category: str = "PROTECT") -> str:
        """
        Génère un prompt pour créer une politique NIST CSF
        
        Pourquoi : Transformer les vulnérabilités techniques en prompt structuré pour le LLM
        Comment : Combine les informations des vulnérabilités avec les exigences NIST CSF
        
        Args:
            vulnerabilities: Liste des vulnérabilités normalisées
            framework_category: Catégorie NIST CSF (IDENTIFY, PROTECT, DETECT, RESPOND, RECOVER)
            
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
        prompt = f"""Tu es un expert en cybersécurité et conformité. Ta tâche est de générer une politique de sécurité conforme au NIST Cybersecurity Framework (NIST CSF).

# Contexte du Projet
L'application est un système e-commerce (parfumerie) avec :
- Backend : Spring Boot (Java)
- Frontend : React (JavaScript)
- Base de données : MySQL

# Vulnérabilités Détectées

"""
        
        # Ajouter les détails des vulnérabilités
        for category, vulns in by_category.items():
            prompt += f"## {category}\n\n"
            for vuln in vulns[:5]:  # Limiter à 5 par catégorie pour éviter les prompts trop longs
                prompt += f"- **{vuln.get('title', 'Vulnérabilité')}** (Sévérité: {vuln.get('severity', 'UNKNOWN')})\n"
                prompt += f"  - Description: {vuln.get('description', 'N/A')}\n"
                if vuln.get('recommendation'):
                    prompt += f"  - Recommandation: {vuln.get('recommendation')}\n"
                if vuln.get('file_path'):
                    prompt += f"  - Localisation: {vuln.get('file_path')}\n"
                prompt += "\n"
        
        # Ajouter les instructions pour la génération
        prompt += f"""
# Instructions

Génère une politique de sécurité conforme au NIST CSF dans la fonction **{framework_category}**.

La politique doit :
1. **Être conforme au NIST CSF** : Référencer les catégories et sous-catégories NIST appropriées
2. **Être actionnable** : Fournir des mesures concrètes à implémenter
3. **Être liée aux vulnérabilités** : Montrer comment la politique répond aux vulnérabilités détectées
4. **Être structurée** : Utiliser un format professionnel et clair

# Format Requis

Structure la politique comme suit :

## 1. Informations de Base
- **ID Politique** : NIST-CSF-{framework_category}-[NUMERO]
- **Titre** : [Titre clair et descriptif]
- **Catégorie NIST CSF** : {framework_category}
- **Sous-catégories** : [Référencer les sous-catégories NIST appropriées]

## 2. Objectif
[Description de l'objectif de la politique et de son contexte]

## 3. Portée
[Systèmes, applications et actifs couverts par cette politique]

## 4. Exigences (Basées sur NIST CSF)
Pour chaque exigence :
- **Référence NIST** : [Ex: PR.DS-5]
- **Description** : [Description de l'exigence]
- **Mesures de contrôle** : [Actions spécifiques à implémenter]
- **Vulnérabilités adressées** : [Références aux vulnérabilités détectées]

## 5. Responsabilités
[Qui est responsable de l'implémentation et de la maintenance]

## 6. Conformité
[Comment vérifier la conformité et la conformité continue]

## 7. Références
- NIST Cybersecurity Framework v1.1
- [Autres références pertinentes]

Génère maintenant la politique de sécurité NIST CSF complète et structurée.
"""
        
        return prompt
    
    @staticmethod
    def generate_category_prompt(vulnerabilities: List[Dict], nist_category: str) -> str:
        """
        Génère un prompt pour une sous-catégorie spécifique NIST CSF
        
        Pourquoi : Créer des politiques plus spécifiques pour chaque domaine NIST
        Comment : Filtre les vulnérabilités pertinentes et génère un prompt ciblé
        """
        
        # Filtrer les vulnérabilités pertinentes
        relevant_vulns = [
            v for v in vulnerabilities 
            if NISTCSFPrompt.NIST_CATEGORIES.get(v.get("category", ""), "").startswith(nist_category.split(".")[0])
        ]
        
        if not relevant_vulns:
            relevant_vulns = vulnerabilities[:10]  # Prendre les 10 premières si pas de correspondance
        
        return NISTCSFPrompt.generate_policy_prompt(relevant_vulns, nist_category)
    
    @staticmethod
    def get_nist_mapping(vulnerability_category: str) -> str:
        """
        Retourne la catégorie NIST CSF appropriée pour une vulnérabilité
        
        Pourquoi : Mapper les types de vulnérabilités aux catégories NIST appropriées
        Comment : Utilise un mapping prédéfini
        """
        return NISTCSFPrompt.NIST_CATEGORIES.get(
            vulnerability_category,
            "PR.DS-5"  # Par défaut : Protections contre les menaces
        )

