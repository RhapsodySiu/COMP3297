from decimal import Decimal
from django.conf import settings
from order.models import MedicalSupply

class Cart(object):
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            # save empty cart in session
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart
        
    def add(self, supply, quantity=1, update_quantity=False):
        supply_id = str(supply.id) # stringify id for JSON
        if supply_id not in self.cart:
            self.cart[supply_id] = {'quantity': 0, 'weight': str(supply.weight)}
            
        if update_quantity:
            self.cart[supply_id]['quantity'] = quantity
        else:
            self.cart[supply_id]['quantity'] += quantity
        self.save()
    
    def save(self):
        # mark session as modified to make sure it gets saved
        self.session.modified = True
        
    def remove(self, supply):
        supply_id = str(supply.id)
        if supply_id in self.cart:
            del self.cart[supply_id]
            self.save()
    
    def __iter__(self):
        """
        Iterate over the items in the cart and get the supplies from database
        """
        
        supply_ids = self.cart.keys()
        # get supplies objects and add them to cart
        supplies = MedicalSupply.objects.filter(id__in=supply_ids)
        
        # add supply instances
        cart = self.cart.copy()
        for supply in supplies:
            cart[str(supply.id)]['supply'] = supply
            
        for item in cart.values():
            item['weight'] = Decimal(item['weight'])
            item['total_weight'] = item['weight'] * item['quantity']
            yield item
            
    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())
        
    def get_total_weight(self):
        return round(float(sum(Decimal(item['weight']) * item['quantity'] for item in self.cart.values()))+1.2, 2)
        
    def clear(self):
        del self.session[settings.CART_SESSION_ID]
        self.save()