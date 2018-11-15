from django.shortcuts import render, get_object_or_404, redirect
from order.models import Order, DistanceClinicHospital, DistanceClinic, MedicalSupply, OrderContent
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
from io import BytesIO
from django.http import FileResponse, HttpResponse
from reportlab.graphics.barcode import code39, code128, code93
from reportlab.graphics.barcode import eanbc, qr, usps
from reportlab.graphics.shapes import Drawing
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.graphics import renderPDF

# import the logging library for debugging
import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)

@login_required
def order_warehouse(request):
    order_list = Order.objects.all()
    for_processing = []
    for_dispatch = []
    for order in order_list:
        logger.error(order.status)
        if order.status.value == 1:
            for_processing.append(order)
        elif order.status.value == 2:
            for_dispatch.append(order)
    return render(request, 'warehouse/warehouse.html', {'for_processing': for_processing, 'for_dispatch': for_dispatch, 'role': str(request.user.groups.all()[0].name)})

@login_required
def processOrder(request):
    orders = request.GET.getlist('order')
    for orderUUID in orders:
        order = Order.objects.get(id=orderUUID)
        order.status = 2
        order.processing_time = datetime.now()
        order.save()
    return redirect('warehouse:order_warehouse', permanent=True)

@login_required
def queueForDispatch(request):
    orders = request.GET.getlist('order')
    for orderUUID in orders:
        order = Order.objects.get(id=orderUUID)
        order.status = 3
        order.processed_time = datetime.now()
        order.save()
    return redirect('warehouse:order_warehouse', permanent=True)
    
@login_required
def getShippingLabel(request, order_id):
    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment;filename="'+order_id+'.pdf"'
    
    # Create a file-like buffer to receive PDF data.
    buffer = BytesIO()

    # logger.error(buffer)

    # Create the PDF object, using the buffer as its "file."
    p = canvas.Canvas(buffer, pagesize=letter)
    
    barcode_value = order_id
    
    barcode39 = code39.Extended39(barcode_value)
    # barcode39Std = code39.Standard39(barcode_value, barHeight=20, stop=1)
    # barcode93 = code93.Standard93(barcode_value)
    # barcode128 = code128.Code128(barcode_value)
    # barcode_usps = usps.POSTNET("50158-9999")
    
    # codes = [barcode39, barcode39Std, barcode93, barcode128, barcode_usps]
    # x = 65*mm
    # y = 225*mm
    p.drawString(10*mm, 260*mm, "Order ID: " + order_id)
    barcode39.drawOn(p, 10*mm, 235*mm)
    # for code in codes:
    #     code.drawOn(p, x, y)
    #     y = y - 5*mm
    #     p.drawString(x+10*mm, y, order_id)
    #     y = y - 40*mm

    # get the information of the order
    overview = get_object_or_404(Order, id=order_id)
    order_detail = OrderContent.objects.filter(order=overview)

    p.drawString(10*mm, 220*mm, "Destination (Clinic): " + str(overview.clinic))
    p.drawString(10*mm, 210*mm, "Items (" + str(overview.get_total_weight()) + " kg): ")
    x = 10*mm
    y = 205*mm
    for item in order_detail:
        p.drawString(x, y, "(Type: " + str(item.medical_supply.type) + ") " + str(item.medical_supply.description) + ": " +  str(item.quantity) + " X " + str(item.medical_supply.weight) + " kg = " + str(item.quantity * item.medical_supply.weight) + " kg")
        y -= 5*mm

    # Close the PDF object cleanly, and we're done.
    p.showPage()
    p.save()

    # present the option to save the file.
    #return FileResponse(buffer, as_attachment=True, filename='hello.pdf')
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response

    
