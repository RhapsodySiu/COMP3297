from django.shortcuts import render, get_object_or_404
from .models import MedicalSupplies
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group

# Can use userId and User filter to find which group does the current user belong to
def test_view(request):
    userId = request.user.id
    if User.objects.filter(pk=userId, groups__name='ClinicManager').exists():
        context = {'value': "You are a clinic manager"}
    else:
        context = {'value': "You are not a clinic manager"}
    return render(request, 'test.html', context)

# Handle display of medical supplies
class ShowSuppliesView(ListView):
    queryset = MedicalSupplies.objects.all()
    context_object_name = 'supplies'
    paginate_by = 15
    template_name = 'content/supplies/browse.html'  
    