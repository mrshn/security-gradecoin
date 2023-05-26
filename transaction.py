import json

class Transaction:
    def __init__(self, source, target, amount, timestamp):
        self.source = source
        self.target = target
        self.amount = amount
        self.timestamp = timestamp

    @classmethod
    def from_dict(cls, transaction_dict):
        return cls(
            source=transaction_dict['source'],
            target=transaction_dict['target'],
            amount=transaction_dict['amount'],
            timestamp=transaction_dict['timestamp']
        )

    def to_dict(self):
        return {
            'source': self.source,
            'target': self.target,
            'amount': self.amount,
            'timestamp': self.timestamp
        }

    def to_json(self):
        return json.dumps(self.to_dict())