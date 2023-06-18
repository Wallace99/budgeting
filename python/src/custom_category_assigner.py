from collections import Counter
from data_classes import TransactionOriginal, KnownPayee
from typing import List


def levenshtein_distance(source_string: str, target_string: str) -> int:
    """
    Computes the Levenshtein distance between two strings (written by ChatGPT).
    """
    source_len = len(source_string)
    target_len = len(target_string)

    # Create a matrix to store the distances between all possible pairs of substrings
    distance_matrix = [[0] * (target_len + 1) for _ in range(source_len + 1)]

    # Initialize the first row and column of the matrix
    for i in range(source_len + 1):
        distance_matrix[i][0] = i
    for j in range(target_len + 1):
        distance_matrix[0][j] = j

    # Fill in the matrix
    for j in range(1, target_len + 1):
        for i in range(1, source_len + 1):
            if source_string[i - 1] == target_string[j - 1]:
                substitution_cost = 0
            else:
                substitution_cost = 1
            distance_matrix[i][j] = min(distance_matrix[i - 1][j] + 1,  # Deletion
                                        distance_matrix[i][j - 1] + 1,  # Insertion
                                        distance_matrix[i - 1][j - 1] + substitution_cost)  # Substitution

    # The final element of the matrix is the Levenshtein distance between the strings
    return distance_matrix[source_len][target_len]


def closest_string(transactions: List[KnownPayee], target_transaction: TransactionOriginal, known_categories: dict, threshold: int=100) -> str:
    """
    Returns the value associated with the "Category" key in the dictionary from `strings` that has the smallest
    Levenshtein distance to the value associated with the "Payee" key in `target_dict`.
    If the closest distance is greater than `threshold`, returns "Unknown" (written by ChatGPT).
    """
    target_payee = target_transaction.payee

    known_categories_for_target = known_categories.get(target_payee)
    if known_categories_for_target is not None:
        highest_category = max(known_categories_for_target, key=known_categories_for_target.get)
        return highest_category

    closest_distance = float('inf')
    closest_rows = []
    for row in transactions:
        payee = row.payee
        distance = levenshtein_distance(payee, target_payee)
        if distance < closest_distance:
            closest_rows = [row.category]
            closest_distance = distance
        elif distance == closest_distance:
            closest_rows.append(row.category)
    if closest_distance <= threshold:
        # Pick the category of the most frequently occurring of the most similar payees
        return Counter(closest_rows).most_common(1)[0][0]
    else:
        return "Unknown"
