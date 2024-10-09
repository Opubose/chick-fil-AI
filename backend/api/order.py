class Order:
    def __init__(self):
        self.items = {}

    def add_item(self, item, quantity=1):
        if item in self.items:
            self.items[item] += quantity
        else:
            self.items[item] = quantity

    def modify_item(self, item, quantity):
        if item in self.items:
            self.items[item] = quantity
        else:
            pass #throw error

    def remove_item(self, item):
        if item in self.items:
            del self.items[item]
        else:
            pass #throw error

    def clear_order(self):
        self.items.clear()

    def get_total_items(self):
        return self.items

    def get_total_price(self, menu_table):
        total_price = 0
        for item, quantity in self.items.items():
            menu_item = menu_table.get_item(Key={'Item': item})
            if 'Item' in menu_item:
                total_price += menu_item['Item']['Price'] * quantity
        return total_price