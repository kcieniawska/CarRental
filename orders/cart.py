from datetime import datetime

class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get('cart')
        if not cart:
            cart = self.session['cart'] = {}
        self.cart = cart

    def add_item(self, car, rental_days, total_price, start_date, end_date):
        # Convert datetime objects to strings before storing them in the session
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')

        item = {
            'car_id': car.id,
            'rental_days': rental_days,
            'total_price': total_price,  # Now total_price is float
            'start_date': start_date_str,
            'end_date': end_date_str
        }
        self.cart[car.id] = item
        self.save()

    def save(self):
        self.session['cart'] = self.cart
        self.session.modified = True

    def __iter__(self):
        # Iterate through cart items
        for item in self.cart.values():
            yield item

    def __len__(self):
        return len(self.cart)
