import json


class HuffmanNode:
    def __init__(self, node_id, symbol=None, frequency=0, left=None, right=None, label=None,
                 left_child_node_id=None, right_child_node_id=None):
        self.node_id = node_id
        self.symbol = symbol
        self.frequency = frequency
        self.left = left
        self.right = right
        # label is a string. "['symbol', frequency]"
        self.label = f"['{symbol}', {frequency}]" if symbol is not None else f"['NaN', {frequency}]"
        self.left_child_node_id = left_child_node_id
        self.right_child_node_id = right_child_node_id
        self.left_child_node_id = self.left.node_id if self.left is not None else left_child_node_id
        self.right_child_node_id = self.right.node_id if self.right is not None else right_child_node_id

    def __lt__(self, other):
        return self.frequency < other.frequency

    def to_dict(self):
        # Convert the HuffmanNode object to a dictionary
        return {
            'node_id': self.node_id,
            'symbol': self.symbol,
            'frequency': self.frequency,
            'label': self.label,
            'left_child_node_id': self.left.node_id if self.left is not None else None,
            'right_child_node_id': self.right.node_id if self.right is not None else None
        }

    def to_json(self):
        # Convert the HuffmanNode object to a JSON string
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data):
        # Create a HuffmanNode object from a dictionary
        return cls(
            node_id=data['id'],
            symbol=data['symbol'],
            frequency=data['frequency'],
            label=data['label'],
            left_child_node_id=data['left_child_node_id'],
            right_child_node_id=data['right_child_node_id']
        )

    @classmethod
    def from_json(cls, json_str):
        # Create a HuffmanNode object from a JSON string
        data = json.loads(json_str)
        return cls.from_dict(data)
