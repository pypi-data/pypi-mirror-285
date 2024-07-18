from abc import ABC


class Context(ABC):
    def get_context(self) -> dict:
        pass


class TransactionContext(Context):
    def __init__(self, transaction_id: str):
        self.transaction_id = transaction_id

    def get_context(self):
        return {
            'transaction_id': self.transaction_id,
        }
