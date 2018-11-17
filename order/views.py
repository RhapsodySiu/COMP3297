import uuid
from django.shortcuts import render, get_object_or_404, redirect
from .models import MedicalSupply, OrderContent, Order
from account.models import ClinicManager
from django.http import HttpResponse, JsonResponse
# Pagination
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# For class-based view
from django.views.generic import ListView
# Login authentication
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from .forms import OrderCreateForm
from cart.forms import CartAddSupplyForm
from cart.cart import Cart
from datetime import datetime
from random import randint

# Can use userId and User filter to find which group does the current user belong to
def test_view(request):
    userId = request.user.id
    if User.objects.filter(pk=userId, groups__name='ClinicManager').exists():
        context = {'value': "You are a clinic manager"}
    else:
        context = {'value': "You are not a clinic manager"}
    return render(request, 'test.html', context)

# Handle display of medical supplies
"""class ShowSuppliesView(ListView):
    queryset = MedicalSupply.objects.all()
    context_object_name = 'supplies'
    paginate_by = 15
    template_name = 'content/supplies/browse.html'
"""

@login_required
def supply_list(request):
    object_list = MedicalSupply.objects.all()
    paginator = Paginator(object_list, 15)
    page = request.GET.get('page')
    cart_supply_form = CartAddSupplyForm()
    try:
        supplies = paginator.page(page)
    except PageNotAnInteger:
        supplies = paginator.page(1)
    except EmptyPage:
        supplies = paginator.page(paginator.num_pages)
    return render(request,'order/supplies/browse.html', {'page': page, 'supplies': supplies, 'cart_supply_form': cart_supply_form, 'role': str(request.user.groups.all()[0].name)})

@login_required
def search_view(request):
    query = request.GET.get('q')
    object_list = MedicalSupply.objects.filter(description__icontains=query)
    paginator = Paginator(object_list, 15)
    page = request.GET.get('page')
    cart_supply_form = CartAddSupplyForm()
    try:
        supplies = paginator.page(page)
    except PageNotAnInteger:
        supplies = paginator.page(1)
    except EmptyPage:
        supplies = paginator.page(paginator.num_pages)
    return render(request,'order/supplies/browse.html', {'page': page, 'supplies': supplies, 'cart_supply_form': cart_supply_form, 'role': str(request.user.groups.all()[0].name)})

@login_required
def category_view(request, category):
    object_list = MedicalSupply.objects.filter(type__id=category)
    paginator = Paginator(object_list, 15)
    page = request.GET.get('page')
    cart_supply_form = CartAddSupplyForm()
    try:
        supplies = paginator.page(page)
    except PageNotAnInteger:
        supplies = paginator.page(1)
    except EmptyPage:
        supplies = paginator.page(paginator.num_pages)
    return render(request,'order/supplies/browse.html', {'page': page, 'supplies': supplies, 'cart_supply_form': cart_supply_form, 'role': str(request.user.groups.all()[0].name)})

@login_required
def order_create(request):
    cart = Cart(request)
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.order_by = request.user
            served = ClinicManager.objects.get(user=request.user)
            order.clinic = served.clinic
            acronym = "".join(e[0] for e in served.clinic.name.split())
            order.id = acronym + datetime.now().strftime("%Y%m%d-%f")
            order.save()
            for item in cart:
                OrderContent.objects.create(order=order, medical_supply=item['supply'],weight=item['weight'], quantity=item['quantity'])
            cart.clear()
            return render(request, 'order/confirm.html',{'order': order, 'role': str(request.user.groups.all()[0].name)})
    else:
        form = OrderCreateForm()
    return render(request, 'order/make.html', {'cart': cart, 'form':form, 'role': str(request.user.groups.all()[0].name)})

@login_required
def order_history(request):
    role = str(request.user.groups.all()[0].name)
    if role != 'Admin' or role != 'Hospital Authority':
        order_list = Order.objects.filter(order_by=request.user).order_by('-order_time')
    else:
        order_list = Order.objects.all().order_by('-order_time')
    return render(request, 'order/history.html', {'orders': order_list, 'role': role})

@login_required
def order_detail(request, order_id):
    overview = get_object_or_404(Order, id=order_id)
    order_detail = OrderContent.objects.filter(order=overview)
    weight = overview.get_total_weight()
    return render(request, 'order/order_detail.html', {'order': overview, 'content': order_detail, 'weight': weight, 'role': str(request.user.groups.all()[0].name)})

@login_required
def cancel_order(request, order_id):
    Order.objects.filter(id=order_id).delete()
    return redirect("order:order_history")

@login_required
def mark_delivered(request, order_id):
    order = Order.objects.get(id=order_id)
    order.status=5
    order.delivered_time = datetime.now()
    order.save()
    return redirect("order:order_history")




@login_required
def order_dispatch(request):
    # order_list = Order.objects.filter(order_by=request.user)
    order_list = list(Order.objects.filter(order_by=request.user))
    for_dispatch = []
    in_queue = []
    med = []
    low = []
    total_weight = 0
    for order in order_list:
        in_queue.append(order)
        if total_weight > 25:
            break
        else:
            if str(order.priority.label) == "Low":
                low.append(order)
            elif str(order.priority.label) == "Medium":
                med.append(order)
            else:
                if total_weight + order.get_total_weight() < 25:
                    in_queue.remove(order)
                    for_dispatch.append(order)
                    total_weight = total_weight + order.get_total_weight()

    if total_weight < 25:
        for order in med:
            if total_weight > 25:
                break
            else:
                if total_weight + order.get_total_weight() < 25:
                    in_queue.remove(order)
                    for_dispatch.append(order)
                    total_weight = total_weight + order.get_total_weight()

    if total_weight < 25:
        for order in low:
            if total_weight > 25:
                break
            else:
                if total_weight + order.get_total_weight() < 25:
                    in_queue.remove(order)
                    for_dispatch.append(order)
                    total_weight = total_weight + order.get_total_weight()

    return render(request, 'order/dispatch.html', {'for_dispatch': for_dispatch, 'in_queue': in_queue, 'total_loc': len(for_dispatch), 'total_weight': total_weight, 'role': str(request.user.groups.all()[0].name)})
