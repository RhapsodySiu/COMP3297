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

# import csv
import csv

# import the logging library
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

import tsp
import numpy
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
    dist = {(i, j): d[i][j] for i in r for j in r}
    sol = tsp.tsp(r, dist)
    sol = sol[1]
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
    order_list = list(Order.objects.filter(order_by=request.user).exclude(status=4).exclude(status=5))
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

    return render(request, 'dispatch/dispatch.html', {'for_dispatch': for_dispatch, 'in_queue': in_queue, 'total_loc': len(for_dispatch), 'total_weight': total_weight})

def download_itinerary(request):
    orders = request.GET.getlist('order')
    itinerary = generate_itinerary(orders)
    with open('itinerary.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Order", "Name", "Latitude", "Longitude", "Altitude"])
        for x in range(len(itinerary)):
            writer.writerow([x, itinerary['name'][x], itinerary['latitude'][x], itinerary['longitude'][x], itinerary['altitude'][x] ])
    file = open('itinerary.csv', 'rb')
    response = FileResponse(file)
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="itinerary.csv"'
    return response

def mark_dispatched(request):
    orders = request.GET.getlist('order')
    for orderUUID in orders:
        order = Order.objects.get(id=orderUUID)
        order.status = 4
        order.dispatched_time = datetime.now()
        order.save()
    return redirect('dispatch:order_dispatch', permanent=True)