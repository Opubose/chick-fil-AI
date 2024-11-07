class Order:
    def __init__(self):
        self.items = {}
        self.total_price = 0.0
        self.modifiers = {}

    def add_item(self, item, price, quantity=1):
        if item in self.items:
            self.items[item] += quantity
        else:
            self.items[item] = quantity
        self.total_price += quantity * price

    def modify_item(self, item, quantity): # huh?
        if item in self.items:
            self.items[item] -= quantity
            if self.items[item] == 0:
                del self.items
        else:
            pass  # throw error
    
    def add_modifier(self, item, discriminator, modifier):
        self.modifiers[item] = discriminator + modifier

    def remove_item(self, item, price, quantity=1):
        if item in self.items:
            if self.items[item] > quantity:
                self.items[item] -= quantity
                self.total_price -= quantity * price
            else:
                self.total_price -= self.items[item] * price
                del self.items[item]
                if item in self.modifiers:
                    del self.modifiers[item]
        else:
            pass  # throw error

    def clear_order(self):
        self.items.clear()
        self.total_price = 0.0
        self.modifiers = {}

    def get_total_items(self):
        return self.items

    def get_total_price(self):
        return self.total_price
