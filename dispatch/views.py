from django.shortcuts import render, get_object_or_404
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

# import csv
import csv

# import the logging library
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

import tsp
import numpy
def test(dispatch_list):
    # get the clinics involved: 0 represents the hospital
    t = [0]
    clinics = {}
    for order in dispatch_list:
        if order.clinic.id not in t:
            t.append(order.clinic.id)
            clinics[str(order.clinic.id)] = order.clinic
    # create distance matrix from t
    r = range(len(t))
    d = numpy.zeros((len(t), len(t)))
    
    # return list
    ret = ["22.270257,114.131376,161.00"]
    name = ["Queen Mary Hospital Drone Port"]
    latitude = [22.270257]
    longitude = [114.131376]
    altitude = [161.00]
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
            ret.append(s)
            name.append(clinics[str(id)].name)
            latitude.append(clinics[str(id)].latitude)
            longitude.append(clinics[str(id)].longitude)
            altitude.append(clinics[str(id)].altitude)
    #t = tsp.tsp([(0,0), (0,1), (1,2), (4,1)])
    return {'ret': ret, 'name': name, 'latitude': latitude, 'longitude': longitude, 'altitude':altitude}

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
    t = test(for_dispatch)
    return render(request, 'dispatch/dispatch.html', {'for_dispatch': for_dispatch, 'in_queue': in_queue, 'total_loc': len(for_dispatch), 'total_weight': total_weight, 'test': t["ret"]})

def download_itinerary(request):
    with open('test.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['testing','123'])
    file = open('test.csv', 'rb')
    response = FileResponse(file)
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="test.csv"'
    return response