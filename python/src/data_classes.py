from datetime import datetime
from dataclasses import dataclass


@dataclass
class KnownPayee:
    date: datetime.date
    payee: str
    amount: float
    category: str

    @classmethod
    def create_from_bq(cls, row: dict):
        return KnownPayee(date=row["Date"],
                          payee=row["Payee"],
                          amount=row["Amount"],
                          category=row["Category"])


@dataclass
class TransactionOriginal:
    date: datetime.date
    payee: str
    amount: float
    particulars: str
    code: str
    reference: str
    tran_type: str
    this_party_account: str
    other_party_account: str
    serial: str
    transaction_code: int
    batch_number: int
    originating_bank: str
    processed_date: str

    @classmethod
    def create_from_dict(cls, row: dict) -> 'TransactionOriginal':
        return TransactionOriginal(date=datetime.strptime(row["Date"], "%d/%m/%y").date(),
                                   payee=row["Payee"],
                                   amount=float(row["Amount"]),
                                   particulars=row["Particulars"],
                                   code=row["Code"],
                                   reference=row["Reference"],
                                   tran_type=row["Tran Type"],
                                   this_party_account=row["This Party Account"],
                                   other_party_account=row["Other Party Account"],
                                   serial=row["Serial"],
                                   transaction_code=row["Transaction Code"],
                                   batch_number=row["Batch Number"],
                                   originating_bank=row["Originating Bank/Branch"],
                                   processed_date=row["Processed Date"])


@dataclass
class CategorisedTransaction:
    date: datetime.date
    payee: str
    amount: float
    category: str
    particulars: str
    code: str
    reference: str
