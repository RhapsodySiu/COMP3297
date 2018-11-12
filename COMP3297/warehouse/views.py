from django.shortcuts import render, get_object_or_404, redirect
from order.models import Order, DistanceClinicHospital, DistanceClinic
from django.http import HttpResponse, JsonResponse, FileResponse
# Pagination
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# For class-based view
from django.views.generic import ListView
# Login authentication
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.conf.urls import url
#datetime
from datetime import datetime

#for shipping label (pdf) generation
import reportlab
import io
from django.http import FileResponse
from reportlab.pdfgen import canvas

# import the logging library for debugging
import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)

@login_required
def order_warehouse(request):
    order_list = Order.objects.filter(order_by=request.user)
    for_processing = []
    for_dispatch = []
    for order in order_list:
        logger.error(order.status)
        if str(order.status) == "Ordered":
            for_processing.append(order)
        elif str(order.status) == "Processed":
            for_dispatch.append(order)
    return render(request, 'warehouse/warehouse.html', {'for_processing': for_processing, 'for_dispatch': for_dispatch})

@login_required
def processOrder(request):
    orders = request.GET.getlist('order')
    for orderUUID in orders:
        order = Order.objects.get(id=orderUUID)
        order.status = 2
        order.dispatched_time = datetime.now()
        order.save()
    return redirect('warehouse:order_warehouse', permanent=True)

@login_required
def queueForDispatch(request):
    orders = request.GET.getlist('order')
    for orderUUID in orders:
        order = Order.objects.get(id=orderUUID)
        order.status = 3
        order.dispatched_time = datetime.now()
        order.save()
    return redirect('warehouse:order_warehouse', permanent=True)
    
@login_required
def getShippingLabel(request):
    # Create a file-like buffer to receive PDF data.
    buffer = io.BytesIO()

    # logger.error(buffer)

    # Create the PDF object, using the buffer as its "file."
    p = canvas.Canvas(buffer)

    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.
    p.drawString(100, 100, "Hello world.")

    # Close the PDF object cleanly, and we're done.
    p.showPage()
    p.save()

    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    return FileResponse(buffer, as_attachment=True, filename='hello.pdf')

    
