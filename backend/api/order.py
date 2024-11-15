from item import Item

class Order:
    def __init__(self):
        # self.items = {}  # Map of item name -> Item objects
        self.items = []
        self.total_price = 0.0

    def add_item(self, name, price, quantity=1, modifiers=None):
        ''' if name in self.items:
            self.items[name].quantity += quantity
        else:
            self.items[name] = Item(name=name, price=price, quantity=quantity, modifiers=modifiers)
        
        self.total_price += price * quantity '''
        for _ in range(quantity):
            self.items.append(Item(name=name, price=price, modifiers=modifiers))
            self.total_price += price

    def remove_item(self, name, quantity=1):
        ''' if name in self.items:
            item = self.items[name]
            if item.quantity > quantity: # reduce quantity
                item.quantity -= quantity
                self.total_price -= item.price * quantity
            else: # remove item completely
                self.total_price -= item.price * item.quantity
                del self.items[name] '''
        for _ in range(quantity):
            found = False
            for item in self.items:
                if item.name == name:
                    found = True
                    self.items.remove(item)
                    self.total_price -= item.price
                    break
            if not found:
                break

    def clear_order(self):
        self.items.clear()
        self.total_price = 0.0

    def get_total_items(self):
        # return [(item.name, item.quantity) for item in self.items.values()]
        return [(item.name, item.quantity) for item in self.items]
        pass

    def get_total_price(self):
        return self.total_price
    
    def to_string(self):
        if not self.items:
            return "Your order is empty."
        
        item_descriptions = [item.to_string() for item in self.items]
        items_str = "\n".join(item_descriptions)
        total_str = f"Total Price: ${self.total_price:.2f}"
        
        return f"Order Summary:\n{items_str}\n\n{total_str}"
        
        ''' item_descriptions = [item.to_string() for item in self.items.values()]
        items_str = "\n".join(item_descriptions)
        total_str = f"Total Price: ${self.total_price:.2f}"
        
        return f"Order Summary:\n{items_str}\n\n{total_str}" '''
