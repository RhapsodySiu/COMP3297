# COMP3297
Air Supply Pilot

## Dependencies
+ pip install django
+ pip install django-enumfields
+ pip install reportlab
+ pip install tsp
+ pip install numpy

## Current stage
Construction

update 13/11/2018
## To-do list
+ **Registration and Authentication** (坤)
  * Enable sending registration token through email
  * Registration form for new user
  * Allow clinic manager to input their clinic in registration
  * Limit different groups of users to use their own functions
+ **Warehouse order** (Clarissa)
  * ~~Print shipping label~~
  * ~~Show all orders waiting for processing~~
  * ~~Allow warehouse personel to change order status to processing, then waiting for dispatch~~
  * ~~Mark the timestamp~~
+ **Delivery notification** (Michael)
  * ~~Allow clinic manager to confirm the arrival of order~~
  * ~~Mark the timestamp~~
+ **Misc** (Siu?)
  * ~~shorten order id length~~ **Please update the table using `python manage.py migrate --run-syncdb`, or simply drop the order table**
  * ~~update status label~~ Please stick with `status.value` to do conditional branch instead
  * ~~weight constraint~~ Clinic manager cannot proceed if overweight
  * ~~update use case, glossary~~
  * more testing on itinerary
  * ~~sorting order based on priority~~

## Document
+ **Sprint backlog**
+ **Analysis model**
+ **Design model**
