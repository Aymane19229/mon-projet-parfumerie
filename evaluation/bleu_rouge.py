"""
Module d'évaluation BLEU et ROUGE-L pour les politiques générées

Pourquoi : Évaluer la qualité des politiques générées par les LLMs
Comment : Compare les politiques générées avec des références en utilisant BLEU et ROUGE-L
"""
from typing import List, Tuple
import re


def tokenize(text: str) -> List[str]:
    """
    Tokenise un texte en mots
    
    Pourquoi : BLEU et ROUGE nécessitent des tokens (mots)
    Comment : Divise le texte en mots, supprime la ponctuation
    
    Args:
        text: Texte à tokeniser
        
    Returns:
        Liste de mots (tokens)
    """
    # Convertir en minuscules et tokeniser
    text = text.lower()
    # Supprimer la ponctuation et diviser en mots
    words = re.findall(r'\b\w+\b', text)
    return words


def ngram_generator(tokens: List[str], n: int):
    """
    Génère des n-grams à partir d'une liste de tokens
    
    Pourquoi : BLEU utilise des n-grams (1-gram, 2-gram, 3-gram, 4-gram)
    Comment : Génère toutes les séquences de n tokens consécutifs
    
    Args:
        tokens: Liste de tokens
        n: Taille du n-gram (1, 2, 3, ou 4)
        
    Yields:
        Tuples de n tokens
    """
    for i in range(len(tokens) - n + 1):
        yield tuple(tokens[i:i + n])


def calculate_bleu_score(candidate: str, references: List[str], max_n: int = 4) -> float:
    """
    Calcule le score BLEU entre un candidat et des références
    
    Pourquoi : Mesurer la similarité n-gram entre le texte généré et les références
    Comment : Utilise la formule BLEU standard (moyenne géométrique des précisions)
    
    Args:
        candidate: Politique générée (texte)
        references: Liste de politiques de référence
        max_n: Ordre maximum des n-grams (défaut: 4)
        
    Returns:
        Score BLEU entre 0 et 1 (1 = identique, 0 = complètement différent)
    """
    if not candidate or not references:
        return 0.0
    
    candidate_tokens = tokenize(candidate)
    
    # Si le candidat est vide, score = 0
    if not candidate_tokens:
        return 0.0
    
    # Tokeniser toutes les références
    reference_token_lists = [tokenize(ref) for ref in references]
    
    # Calculer les précisions pour chaque ordre de n-gram
    precisions = []
    
    for n in range(1, max_n + 1):
        # Compter les n-grams dans le candidat
        candidate_ngrams = {}
        for ngram in ngram_generator(candidate_tokens, n):
            candidate_ngrams[ngram] = candidate_ngrams.get(ngram, 0) + 1
        
        if not candidate_ngrams:
            precisions.append(0.0)
            continue
        
        # Pour chaque n-gram du candidat, trouver le maximum dans les références
        clipped_counts = 0
        total_counts = sum(candidate_ngrams.values())
        
        for ngram, count in candidate_ngrams.items():
            # Maximum de ce n-gram dans toutes les références
            max_ref_count = max(
                sum(1 for ref_ngram in ngram_generator(ref_tokens, n) if ref_ngram == ngram)
                for ref_tokens in reference_token_lists
            )
            clipped_counts += min(count, max_ref_count)
        
        precision = clipped_counts / total_counts if total_counts > 0 else 0.0
        precisions.append(precision)
    
    # Moyenne géométrique des précisions
    if any(p == 0 for p in precisions):
        return 0.0
    
    geometric_mean = (precisions[0] * precisions[1] * precisions[2] * precisions[3]) ** (1.0 / max_n)
    
    # Penalité de longueur (brevity penalty)
    candidate_length = len(candidate_tokens)
    # Longueur de référence la plus proche
    closest_ref_length = min(
        abs(len(ref_tokens) - candidate_length)
        for ref_tokens in reference_token_lists
    )
    closest_ref_length = min(
        len(ref_tokens)
        for ref_tokens in reference_token_lists
        if abs(len(ref_tokens) - candidate_length) == closest_ref_length
    )
    
    if candidate_length > closest_ref_length:
        brevity_penalty = 1.0
    else:
        brevity_penalty = (candidate_length / closest_ref_length) if closest_ref_length > 0 else 0.0
    
    bleu_score = brevity_penalty * geometric_mean
    return bleu_score


def longest_common_subsequence(seq1: List[str], seq2: List[str]) -> int:
    """
    Calcule la longueur de la plus longue sous-séquence commune (LCS)
    
    Pourquoi : ROUGE-L utilise LCS pour mesurer le recouvrement
    Comment : Algorithme dynamique classique
    
    Args:
        seq1: Première séquence de tokens
        seq2: Deuxième séquence de tokens
        
    Returns:
        Longueur de la LCS
    """
    m, n = len(seq1), len(seq2)
    
    # Tableau de programmation dynamique
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if seq1[i - 1] == seq2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    
    return dp[m][n]


def calculate_rouge_l_score(candidate: str, references: List[str]) -> Tuple[float, float, float]:
    """
    Calcule le score ROUGE-L (F-score, Precision, Recall)
    
    Pourquoi : Mesurer le recouvrement basé sur la plus longue sous-séquence commune
    Comment : Utilise LCS pour calculer precision, recall et F-score
    
    Args:
        candidate: Politique générée (texte)
        references: Liste de politiques de référence
        
    Returns:
        Tuple (F-score, Precision, Recall) entre 0 et 1
    """
    if not candidate or not references:
        return (0.0, 0.0, 0.0)
    
    candidate_tokens = tokenize(candidate)
    
    if not candidate_tokens:
        return (0.0, 0.0, 0.0)
    
    # Calculer LCS avec chaque référence et prendre le maximum
    max_lcs = 0
    best_ref_length = 0
    
    for reference in references:
        ref_tokens = tokenize(reference)
        lcs_length = longest_common_subsequence(candidate_tokens, ref_tokens)
        
        if lcs_length > max_lcs:
            max_lcs = lcs_length
            best_ref_length = len(ref_tokens)
    
    if max_lcs == 0:
        return (0.0, 0.0, 0.0)
    
    # Precision = LCS / longueur candidat
    precision = max_lcs / len(candidate_tokens) if candidate_tokens else 0.0
    
    # Recall = LCS / longueur référence
    recall = max_lcs / best_ref_length if best_ref_length > 0 else 0.0
    
    # F-score = 2 * (precision * recall) / (precision + recall)
    if precision + recall > 0:
        f_score = 2 * (precision * recall) / (precision + recall)
    else:
        f_score = 0.0
    
    return (f_score, precision, recall)


def evaluate_policy(candidate: str, references: List[str]) -> dict:
    """
    Évalue une politique générée avec BLEU et ROUGE-L
    
    Pourquoi : Fournir une évaluation complète d'une politique générée
    Comment : Calcule BLEU et ROUGE-L et retourne un dictionnaire de scores
    
    Args:
        candidate: Politique générée à évaluer
        references: Liste de politiques de référence
        
    Returns:
        Dictionnaire avec les scores :
        {
            'bleu': float,
            'rouge_l_f': float,
            'rouge_l_p': float,
            'rouge_l_r': float
        }
    """
    if not references:
        return {
            'bleu': 0.0,
            'rouge_l_f': 0.0,
            'rouge_l_p': 0.0,
            'rouge_l_r': 0.0
        }
    
    # Calculer BLEU
    bleu_score = calculate_bleu_score(candidate, references)
    
    # Calculer ROUGE-L
    rouge_f, rouge_p, rouge_r = calculate_rouge_l_score(candidate, references)
    
    return {
        'bleu': round(bleu_score, 4),
        'rouge_l_f': round(rouge_f, 4),
        'rouge_l_p': round(rouge_p, 4),
        'rouge_l_r': round(rouge_r, 4)
    }

