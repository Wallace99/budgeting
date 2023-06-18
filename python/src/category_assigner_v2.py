import datetime
import math
from typing import List
from data_classes import TransactionOriginal, CategorisedTransaction, KnownPayee
from custom_category_assigner import closest_string


def date_string_is_newer_than(date_to_compare: datetime.date, latest_record_date: datetime.date) -> bool:
    return date_to_compare > latest_record_date


def transaction_not_in_list(transaction: TransactionOriginal, seen_transactions: List[KnownPayee]) -> bool:
    return not any(
            item.payee == transaction.payee and math.isclose(float(item.amount), float(transaction.amount) * -1)
            for item in seen_transactions
    )


def is_relevant_transaction(row: TransactionOriginal) -> bool:
    # ignore transfers between funds and deposits
    return row.amount < 0 and row.reference != "INTERNET XFR" and row.tran_type != "FT"


def is_transaction_from_credit_card(row: TransactionOriginal) -> bool:
    return row.tran_type == "BP" and row.reference != "" and row.payee.lower() == "elya cox"


def count_categories_per_payee(transactions: List[KnownPayee]) -> dict:
    payee_categories = {}
    for transaction in transactions:
        payee = transaction.payee
        category = transaction.category
        if payee not in payee_categories:
            payee_categories[payee] = {}
        if category not in payee_categories[payee]:
            payee_categories[payee][category] = 0
        payee_categories[payee][category] += 1
    return payee_categories


def predict_categories(categorised_dataset: List[KnownPayee], data_to_assign_categories: List[TransactionOriginal],
                       known_categories_and_counts: dict) -> List[CategorisedTransaction]:
    if len(categorised_dataset) == 0:
        return []

    most_recent_date = max(categorised_dataset, key=lambda x: x.date).date
    categorised_transactions_on_most_recent_date = [item for item in categorised_dataset if
                                                    item.date == most_recent_date]
    # TODO format this better
    filtered_transactions: List[TransactionOriginal] = [
        transaction for transaction in data_to_assign_categories
        if date_string_is_newer_than(transaction.date, most_recent_date) or (transaction.date == most_recent_date and transaction_not_in_list(transaction,
                                                                                categorised_transactions_on_most_recent_date))
    ]
    print(f"Found {len(filtered_transactions)} new transactions")

    filtered_data_to_categorise: List[TransactionOriginal] = [row for row in filtered_transactions if is_relevant_transaction(row)]

    if len(filtered_data_to_categorise) == 0:
        print("No rows found to assign categories to")
        return []

    rows: List[CategorisedTransaction] = []
    for row in filtered_data_to_categorise:
        payee = row.payee
        if is_transaction_from_credit_card(row):
            payee = row.reference
        amount = row.amount * -1
        category = closest_string(categorised_dataset, row, known_categories_and_counts)
        categorised_row = CategorisedTransaction(date=row.date,
                                                 payee=payee,
                                                 amount=amount,
                                                 category=category,
                                                 particulars=row.particulars,
                                                 code=row.code,
                                                 reference=row.reference)
        rows.append(categorised_row)
    return rows


def process(data_to_categorise: List[TransactionOriginal], categorised_data: List[KnownPayee]) -> List[CategorisedTransaction]:
    known_categories = count_categories_per_payee(categorised_data)
    predicted_data = predict_categories(categorised_data, data_to_categorise, known_categories)

    return predicted_data
