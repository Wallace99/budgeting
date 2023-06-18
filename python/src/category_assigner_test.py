import pytest
from category_assigner_v2 import date_string_is_newer_than, \
    transaction_not_in_list, is_relevant_transaction, is_transaction_from_credit_card, \
    count_categories_per_payee, predict_categories
from data_classes import KnownPayee, TransactionOriginal, CategorisedTransaction
from datetime import date


def create_original_transaction(payee: str,
                                amount: float,
                                tran_date: date = date(2022, 1, 5),
                                particulars: str = "test",
                                code: str = "test",
                                reference: str = "ref",
                                tran_type: str = "tt",
                                this_party_account: str = "te",
                                other_party_account: str = "ee",
                                serial: str = "serial",
                                transaction_code: int = 1,
                                batch_number: int = 123,
                                originating_bank: str = "bank",
                                processed_date: str = "1/2/2023") -> TransactionOriginal:
    return TransactionOriginal(date=tran_date,
                               payee=payee,
                               amount=amount,
                               particulars=particulars,
                               code=code,
                               reference=reference,
                               this_party_account=this_party_account,
                               other_party_account=other_party_account,
                               serial=serial,
                               tran_type=tran_type,
                               transaction_code=transaction_code,
                               batch_number=batch_number,
                               originating_bank=originating_bank,
                               processed_date=processed_date)


def create_known_payee(payee: str, category: str, tran_date: date = date(2022, 1, 5), amount: float = 10.0) -> KnownPayee:
    return KnownPayee(date=tran_date, payee=payee, amount=amount, category=category)


def test_date_string_is_newer_than():
    assert date_string_is_newer_than(date(2022, 1, 5), date(2021, 1, 1)) is True
    assert date_string_is_newer_than(date(2020, 1, 1), date(2021, 1, 1)) is False
    assert date_string_is_newer_than(date(2021, 1, 1), date(2021, 1, 1)) is False  # Same dates


def test_transaction_not_in_list():
    seen_transactions = [
        KnownPayee(date=date(2022, 1, 5), payee="John", amount=100.0, category="Groceries"),
        KnownPayee(date=date(2022, 2, 5), payee="Alice", amount=200.0, category="Petrol"),
        KnownPayee(date=date(2022, 3, 5), payee="Bob", amount=50.0, category="Power"),
    ]

    transaction = create_original_transaction(payee="Eve", amount=-150.0)
    assert transaction_not_in_list(transaction, seen_transactions) is True

    transaction_duplicate = create_original_transaction(payee="John", amount=-100.0)
    assert transaction_not_in_list(transaction_duplicate, seen_transactions) is False

    transaction_negative_amount = create_original_transaction(payee="Alice", amount=200.0)
    assert transaction_not_in_list(transaction_negative_amount, seen_transactions) is True  # Amount mismatch

    transaction_zero_amount = create_original_transaction(payee="Bob", amount=0.0)
    assert transaction_not_in_list(transaction_zero_amount, seen_transactions) is True  # Zero amount not present

    empty_seen_transactions = []
    assert transaction_not_in_list(transaction, empty_seen_transactions) is True  # Empty seen transactions


def test_is_relevant_transaction():
    row1 = create_original_transaction(payee="John", amount=-100.0, reference="Payment", tran_type="BP")
    assert is_relevant_transaction(row1) is True

    row2 = create_original_transaction(payee="John", amount=200.0, reference="Internet XFR", tran_type="FT")
    assert is_relevant_transaction(row2) is False

    row3 = create_original_transaction(payee="John", amount=-50.0, reference="Deposit", tran_type="BP")
    assert is_relevant_transaction(row3) is True

    row4 = create_original_transaction(payee="John", amount=-75.0, reference="Payment", tran_type="SA")
    assert is_relevant_transaction(row4) is True

    row5 = create_original_transaction(payee="John", amount=150.0, reference="Payment", tran_type="BP")
    assert is_relevant_transaction(row5) is False

    row6 = create_original_transaction(payee="John", amount=-200.0, reference="Transfer", tran_type="FT")
    assert is_relevant_transaction(row6) is False


def test_is_transaction_from_credit_card():
    row1 = create_original_transaction(payee="Elya Cox", amount=200.0, reference="12345", tran_type="BP")
    assert is_transaction_from_credit_card(row1) is True

    row2 = create_original_transaction(payee="Elya Cox", amount=200.0, reference="12345", tran_type="FT")
    assert is_transaction_from_credit_card(row2) is False

    row3 = create_original_transaction(payee="Elya Cox", amount=200.0, reference="", tran_type="BP")
    assert is_transaction_from_credit_card(row3) is False

    row4 = create_original_transaction(payee="John Doe", amount=200.0, reference="12345", tran_type="BP")
    assert is_transaction_from_credit_card(row4) is False

    row5 = create_original_transaction(payee="Elya cox", amount=200.0, reference="12345", tran_type="BP")
    assert is_transaction_from_credit_card(row5) is True


def test_count_categories_per_payee():
    transactions = [
        create_known_payee(payee="John", category="Groceries"),
        create_known_payee(payee="John", category="Rent"),
        create_known_payee(payee="Alice", category="Rent"),
        create_known_payee(payee="Alice", category="Transportation"),
        create_known_payee(payee="John", category="Groceries"),
        create_known_payee(payee="Bob", category="Groceries"),
        create_known_payee(payee="Alice", category="Rent"),
    ]

    result = count_categories_per_payee(transactions)
    assert result == {
        'John': {'Groceries': 2, 'Rent': 1},
        'Alice': {'Rent': 2, 'Transportation': 1},
        'Bob': {'Groceries': 1}
    }

    empty_transactions = []
    empty_result = count_categories_per_payee(empty_transactions)
    assert empty_result == {}

    single_transaction = [create_known_payee(payee="John", category="Groceries")]
    single_result = count_categories_per_payee(single_transaction)
    assert single_result == {'John': {'Groceries': 1}}


def test_predict_categories():
    categorised_dataset = [
        create_known_payee(tran_date=date(2023, 1, 1), payee="John", amount=100.0, category="Groceries"),
        create_known_payee(tran_date=date(2023, 1, 2), payee="Alice", amount=50.0, category="Rent"),
    ]

    data_to_assign_categories = [
        create_original_transaction(tran_date=date(2023, 1, 3), payee="John", amount=-80.0, particulars="Part 3", code="Code 3", reference="Ref 3"),
        create_original_transaction(tran_date=date(2022, 1, 2), payee="Alice", amount=-150.0, particulars="Part 2", code="Code 2", reference="Ref 2"),
        create_original_transaction(tran_date=date(2023, 1, 2), payee="Alice", amount=-50.0, particulars="Part 1", code="Code 1", reference="Ref 1"),
        create_original_transaction(tran_date=date(2023, 1, 4), payee="Alice", amount=-60.0, particulars="Part 5", code="Code 5", reference="Ref 5"),
    ]

    known_categories_and_counts = {
        'John': {'Groceries': 2},
        'Alice': {'Rent': 1},
    }

    result = predict_categories(categorised_dataset, data_to_assign_categories, known_categories_and_counts)

    assert len(result) == 2

    expected_result1 = CategorisedTransaction(date=date(2023, 1, 3),
                                              payee="John",
                                              amount=80.0,
                                              particulars="Part 3",
                                              code="Code 3",
                                              reference="Ref 3",
                                              category="Groceries")
    assert result[0] == expected_result1

    expected_result2 = CategorisedTransaction(date=date(2023, 1, 4),
                                              payee="Alice",
                                              amount=60.0,
                                              particulars="Part 5",
                                              code="Code 5",
                                              reference="Ref 5",
                                              category="Rent")

    assert result[1] == expected_result2

    empty_result = predict_categories([], [], {})
    assert empty_result == []
