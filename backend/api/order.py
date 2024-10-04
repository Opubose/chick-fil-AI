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
            pass #return jsonify error that this item isnt in the order

    def remove_item(self, item):
        if item in self.items:
            del self.items[item]
        else:
            pass #return jsonify error that this item isnt in the order

    def clear_order(self):
        self.items.clear()
        #return jsonify order is cleared

    def get_total_items(self):
        return self.items
        #return jsonify current items

    def get_total_price(self, menu_table):
        total_price = 0
        for item, quantity in self.items.items():
            response = menu_table.get_item(Key={'Item': item})
            if 'Item' in response:
                price = response['Item']['Price']
                total_price += price * quantity
        return total_price