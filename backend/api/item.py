class Item:
    def __init__(self, name: str, price: float, modifiers: str):
        self.name = name
        self.price = price
        self.modifiers = modifiers

    def to_string(self):
        if self.modifiers:
            return f"{self.name}, {self.modifiers.lower()} at ${self.price:.2f}"
        return f"{self.name} at ${self.price:.2f}"