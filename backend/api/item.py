class Item:
    def __init__(self, name: str, price: float, quantity: int, modifiers: str):
        self.name = name
        self.price = price
        self.quantity = quantity
        self.modifiers = modifiers

    def to_string(self):
        res = ""
        if self.modifiers:
            res = f"{self.quantity}x {self.name}, {self.modifiers.lower()} at ${self.price:.2f}"
        else:
            res = f"{self.quantity}x {self.name} at ${self.price:.2f}"
        
        return f"{res} each" if self.quantity > 1 else res