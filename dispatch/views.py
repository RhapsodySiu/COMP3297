from django.shortcuts import render, get_object_or_404, redirect
from order.models import Order,OrderContent, MedicalSupply, Type, DistanceClinicHospital, DistanceClinic
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
#pdf generation
from reportlab.pdfgen import canvas
#sending email
from smtplib import SMTP_SSL, SMTPException
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.utils import formataddr
from email import encoders



# import csv
import csv

# import the logging library
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

#import tsp
import numpy
from tsp_solver.greedy_numpy import solve_tsp
def generate_itinerary(dispatch_list):
    # get the clinics involved: 0 represents the hospital
    t = [0]
    clinics = {}
    for orderUUID in dispatch_list:
        order = Order.objects.get(id=orderUUID)
        if order.clinic.id not in t:
            t.append(order.clinic.id)
            clinics[str(order.clinic.id)] = order.clinic
    # create distance matrix from t
    r = range(len(t))
    d = numpy.zeros((len(t), len(t)))

    # return list
    name = ["Queen Mary Hospital Drone Port"]
    latitude = [22.270257]
    longitude = [114.131376]
    altitude = [161.00]
    # calculate distance matrix
    for i, a in enumerate(t):
        for j, b in enumerate(t):
            if i == 0 and j != 0: # i is hospital
                dist = DistanceClinicHospital.objects.filter(b__id = b).values('distance')
                d[i][j] = dist[0]['distance']
            elif j == i:
                d[i][j] = 0
            elif j == 0 and i != 0: # j is hospital
                dist = DistanceClinicHospital.objects.filter(b__id = a).values('distance')
                d[i][j] = dist[0]['distance']
            else:
                dist = DistanceClinic.objects.filter(a__id = a, b__id = b).values('distance')
                d[i][j] = dist[0]['distance']
    #dist = {(i, j): d[i][j] for i in r for j in r}
    #sol = tsp.tsp(r, dist)
    sol = solve_tsp(d)
    #sol = sol[1]
    while sol[-1] != 0:
        temp = sol[-1]
        sol.remove(temp)
        sol.insert(0, temp)
    for clinic in sol:
        id = t[clinic]
        if id != 0:
            c = clinics[str(id)]
            s = str(c.latitude) + "," + str(c.longitude) + "," + str(c.altitude)
            name.insert(0,clinics[str(id)].name)
            latitude.insert(0,clinics[str(id)].latitude)
            longitude.insert(0,clinics[str(id)].longitude)
            altitude.insert(0,clinics[str(id)].altitude)
    return {'name': name, 'latitude': latitude, 'longitude': longitude, 'altitude':altitude}

def order_dispatch(request):
    status = [1,2,4,5]
    order_list = list(Order.objects.all().exclude(status__in=status))
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

    return render(request, 'dispatch/dispatch.html', {'for_dispatch': for_dispatch, 'in_queue': in_queue, 'total_loc': len(for_dispatch), 'total_weight': total_weight, 'role': str(request.user.groups.all()[0].name)})

def download_itinerary(request):
    orders = request.GET.getlist('order')
    itinerary = generate_itinerary(orders)
    test = 0
    with open('itinerary.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Order", "Name", "Latitude", "Longitude", "Altitude"])
        for x in range(len(itinerary['name'])):
            test += 1
            writer.writerow([x, itinerary['name'][x], itinerary['latitude'][x], itinerary['longitude'][x], itinerary['altitude'][x] ])
    file = open('itinerary.csv', 'rb')
    response = FileResponse(file)
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="itinerary.csv"'
    return response

def mark_dispatched(request):
    orders = request.GET.getlist('order')
    mailHost = "smtp.zoho.com"
    mailUsername = "admin@accoladehk.com"
    mailPassword = "knb9A1Zv3b3U"
    sender = "admin@accoladehk.com"
    content = ""
    for orderUUID in orders:

        order = Order.objects.get(id=orderUUID)
        item_no = order.get_item_no()
        order.status = 4
        order.dispatched_time = datetime.now()
        order.save()
        order_id = "order_id: " + order.id + "\n"
        order_destination = order.clinic.__str__()+ "\n"
        c = canvas.Canvas("ShippingLabel.pdf")
        y= 600
        c.drawString(50, y, "order id : " + order.id)
        y-=20
        order_content = OrderContent.objects.filter(order=orderUUID)
        for item in order_content:
            c.drawString(50, y , "Type: " + item.medical_supply.type.name + "           " + "Name: "+ item.medical_supply.description + " " )
            y-=20
            c.drawString(50,y , "Weight :" + str(item.weight) +"kg" + "           " +"Quantity :" + str(item.quantity) + "          "  )
            y-=20
        c.drawString(50,y, "order destination: " + order.clinic.__str__() )
        c.save()
        receiver=  order.order_by.email

        msg = MIMEMultipart()
        msg['From']= formataddr(["Dispatcher",sender])
        msg['To'] = receiver
        msg['Subject']= "Shipping label"
        body= "Below is the PDF file containing the shipping label"
        msg.attach(MIMEText(body,'plain'))

        filename = "ShippingLabel.pdf"
        attachment= open(filename, 'rb')

        part = MIMEBase('application','octect-stream')
        part.set_payload((attachment).read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition',"attachment; filename= "+filename)
        msg.attach(part)

        try:
            smtpObj = SMTP_SSL(mailHost, 465)
            smtpObj.login(mailUsername, mailPassword)
            smtpObj.sendmail(sender, receiver, msg.as_string())
            print("Email Sent")
        except SMTPException:
            print("Failed to send email")


    return redirect('dispatch:order_dispatch', permanent=True)
