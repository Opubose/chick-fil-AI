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

    def modify_item(self, item, quantity):
        if item in self.items:
            self.items[item] = quantity
        else:
            pass #throw error

    def remove_item(self, item, price):
        if item in self.items:
            del self.items[item]
            self.total_price -= price
        else:
            pass #throw error

    def clear_order(self):
        self.items.clear()
        self.total_price = 0.0
        self.modifiers = {}

    def get_total_items(self):
        return self.items

    def get_total_price(self, menu_table):
        # total_price = 0
        # for item, quantity in self.items.items():
        #     response = menu_table.get_item(Key={'Item': item})
        #     if 'Item' in response:
        #         price = response['Item']['Price']
        #         total_price += price * quantity
        # return total_price
        return self.total_price