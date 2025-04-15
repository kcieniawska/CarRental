from datetime import datetime

class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get('cart', {})
        if not cart:
            cart = self.session['cart'] = {}
        self.cart = cart

    def add_item(self, car, rental_days, total_price, start_date, end_date):
        if str(car.id) not in self.cart:
            self.cart[str(car.id)] = {
                'car_id': car.id,
                'rental_days': rental_days,
                'total_price': total_price,
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d'),
            }
            self.save()

    def save(self):
        self.session.modified = True

    def save(self):
        self.session['cart'] = self.cart
        self.session.modified = True

    def __iter__(self):
        # Iterate through cart items
        for item in self.cart.values():
            yield item

    def __len__(self):
        return len(self.cart)
