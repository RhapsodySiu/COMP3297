from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from order.models import MedicalSupply
from .cart import Cart
from .forms import CartAddSupplyForm
@require_POST
def cart_add(request, supply_id):
    cart = Cart(request)
    supply = get_object_or_404(MedicalSupply, id=supply_id)
    form = CartAddSupplyForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        cart.add(supply=supply, quantity=cd['quantity'], update_quantity=cd['update'])
    return redirect('cart:cart_detail')

def cart_remove(request, supply_id):
    cart = Cart(request)
    supply = get_object_or_404(MedicalSupply, id=supply_id)
    cart.remove(supply)
    return redirect('cart:cart_detail')

@login_required
def cart_detail(request):
    cart = Cart(request)
    for item in cart:
        item['update_quantity_form'] = CartAddSupplyForm(initial={'quantity': item['quantity'], 'update': True})
    return render(request, 'cart/detail.html', {'cart': cart, 'role': str(request.user.groups.all()[0].name)})
