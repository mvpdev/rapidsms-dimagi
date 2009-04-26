#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.http import HttpResponse, HttpResponseNotAllowed, HttpResponseServerError, Http404
from django.template import RequestContext
from apps.reporters.models import Location, LocationType
from apps.supply.models import Shipment, Transaction, Stock, PartialTransaction
from rapidsms.webui.utils import render_to_response
from django.db import models
# The import here newly added for serializations
from django.core import serializers
from django.core.paginator import *
from random import randrange, seed
import time
import sys

ITEMS_PER_PAGE = 10

#Views for handling summary of Reports Displayed as Location Tree
def index(req, locid=None):
    reload(sys)
    sys.setdefaultencoding('utf-8')
    # TODO (better) ajax this
    if not locid:
        locid = 1
    try:
        location = Location.objects.get(id=locid)
    except Location.DoesNotExist:
        location= None
    
    return render_to_response(req, "nigeria/index.html",{'location':location })

def logistics_summary(req, locid):
    # Get the location we are going to work with.
    # If there is no location set, this will default to the first
    # one in the database.  If there are no locations in the
    # database we are S.O.L.
    if not locid:
        locid = 1
    try: 
        location = Location.objects.get(pk=locid)
    except Location.DoesNotExist:
        location = None

    # get all the transactions that this location was involved in 
    transactions_from_loc = Transaction.objects.all().filter(shipment__origin=location) 
    transactions_to_loc = Transaction.objects.all().filter(shipment__destination=location)  
    transactions = (transactions_from_loc | transactions_to_loc).order_by("-shipment__sent") 
        
    # get any place this location has shipped to or from.  
    # we will use these to generate some plots
    # and pass them forward to the template
    locations_shipped_to = []
    [locations_shipped_to.append(trans.shipment.destination) for trans in transactions_from_loc if trans.shipment.destination not in locations_shipped_to]
    
    # set the stock value in all the children.
    # this is now handled by signals!  see supply/models.py
    #[_set_stock(child) for child in locations_shipped_to]
    
    # get some JSON strings for the plots
    stock_per_loc_data, stock_per_loc_options = _get_stock_per_location_strings(locations_shipped_to)
    stock_over_time_data, stock_over_time_options = _get_stock_over_time_strings([location])
    stock_over_time_child_data, stock_over_time_child_options = _get_stock_over_time_strings(locations_shipped_to)
    
    paginator = Paginator(transactions, ITEMS_PER_PAGE)

    try:
        page = int(req.GET['page'])
    except:
        page = 1

    try:
        transactions_pager = paginator.page(page)
    except:
        raise Http404

    # send the whole list of stuff back to the template
    return render_to_response(req, "nigeria/logistics_summary.html", 
                              {'location': location,
                               'child_locations': locations_shipped_to,
                               'transactions_pager': transactions_pager,
                               'paginator': paginator,
                               'page': page,
                               'stock_per_loc_plot_data' : stock_per_loc_data, 
                               'stock_per_loc_plot_options' : stock_per_loc_options, 
                               'stock_over_time_data' : stock_over_time_data, 
                               'stock_over_time_options' : stock_over_time_options, 
                               'stock_over_time_child_data' : stock_over_time_child_data, 
                               'stock_over_time_child_options' : stock_over_time_child_options 
                               })

def generate(req):
    # for the demo, to quickly generate dps and teams for all wards
    all_wards = Location.objects.all().filter(type__name__iexact="ward")
    dps_per_ward = 3
    teams_per_dp = 4
    dp_type = LocationType.objects.get(name__iexact="Distribution Point")
    team_type = LocationType.objects.get(name__iexact="Mobilization Team")
    teams_created = 0
    dps_created = 0
    ward_count = 1
    for ward in all_wards:
        print "ward: %s, %s of %s" %(ward.name, ward_count, len(all_wards))
        ward_count = ward_count + 1
        # assume if this ward already has DPs we don't need to do this
        if (len(ward.children.all()) > 0):
            continue
        for dp_id in range(1, dps_per_ward + 1):
            dp_name = "%s DP %s" %(ward.name, dp_id)
            dp_code = "%s%s" % (ward.code, dp_id)
            dp = Location.objects.create(name=dp_name, type=dp_type, code=dp_code, parent=ward)
            dps_created = dps_created + 1
            for team_id in range(1, teams_per_dp + 1):
                team_name = "%s TEAM %s" %(dp_name, team_id)
                team_code = "%s%s" % (dp_code, team_id)
                team = Location.objects.create(name=team_name, type=team_type, code=team_code, parent=dp)
                teams_created = teams_created + 1
    return HttpResponse("Successfully created %s distribution points and %s teams" % (dps_created, teams_created))
    
def supply_summary(req, frm, to, range):
    return render_to_response(req, "nigeria/supply_summary.html")

def bednets_summary(req, frm, to, range):
    return render_to_response(req, "nigeria/bednets_summary.html")

def coupons_summary(req, frm, to, range):
    return render_to_response(req, "nigeria/coupons_summary.html")


# Periodical Reporting  by day, week, month for coupons
def coupons_daily(req, locid):
    location = False
    try:
        location_object = Location.objects.get(code=locid)
        location = {'name': location_object.name}
    except: pass
    return render_to_response(req, "nigeria/coupons_daily.html", {'location': location})

def coupons_weekly(req, locid):
    return render_to_response(req, "nigeria/coupons_weekly.html")

def coupons_monthly(req, locid):
    return render_to_response(req, "nigeria/coupons_monthly.html")


# Periodical Reporting  by day, week, month for bednets
def bednets_daily(req, locid):
    return render_to_response(req, "nigeria/bednets_daily.html")

def bednets_weekly(req, locid):
    return render_to_response(req, "nigeria/bednets_weekly.html")

def bednets_monthly(req, locid):
    return render_to_response(req, "nigeria/bednets_monthly.html")


# Periodical Reporting  by day, week, month for supply
#Builds daily supply reporting
def supply_daily(req, locid):
    return render_to_response(req, "nigeria/supply_daily.html")

#Builds weekly supply detail
def supply_weekly(req, locid):
    return render_to_response(req, "nigeria/supply_weekly.html")

#Build Monthly supply detail
def supply_monthly(req, locid):
    return render_to_response(req, "nigeria/supply_monthly.html")




def _set_stock(location):
    '''Get the stock object associated with this.  None if none found'''
    try:
        location.stock = Stock.objects.get(location=location)
    except Stock.DoesNotExist:
        # this isn't a real error, we just don't have any stock information
        location.stock = None

def _set_net_data(location):
    '''Get the stock object associated with this.  None if none found'''
    try:
        location.stock = Stock.objects.get(location=location)
    except Stock.DoesNotExist:
        # this isn't a real error, we just don't have any stock information
        location.stock = None

def _set_net_card_data(location):
    '''Get the stock object associated with this.  None if none found'''
    try:
        location.stock = Stock.objects.get(location=location)
    except Stock.DoesNotExist:
        # this isn't a real error, we just don't have any stock information
        location.stock = None

def _get_stock_per_location_strings(locations):
    '''Get a JSON formatted list that flot can plot
       based on the data in the stock table'''
    # this is the sample format
    #data = '''[
    #        {"bars":{"show":true},"label":"Ajingi","data":[[-0.5,100]]},
    #        {"bars":{"show":true},"label":"Bebeji","data":[[0.5,650]]}
    #        ]'''
    
    # loop over all the locations and if they have a stock
    # create a string describing it and add it to the list.
    # count will store the index of each item.  
    count = 0
    rows = []
    for location in locations:
        # if the location doesn't have any stock we won't display it
        if location.stock:
            row = '{"bars":{"show":true},"label":"%s","data":[[%s,%s]]}' % (location.name, count, location.stock.balance)
            rows.append(row)
            count = count + 1
    data = "[%s]" % ", ".join(rows)
    options = '{"grid":{"clickable":true},"xaxis":{"min":0,"ticks":[],"tickFormatter":"string"},"yaxis":{"min":0}}'
    return (data, options)


def _get_stock_over_time_strings(locations):
    '''Get a JSON formatted list that flot can plot
       based on the data in the stock table'''
    
    # this is the sample format
    #data = '''[
    #        {"label":"Ajingi","data":[[1239706800000,1000],[1239793200000,800],[1239966000000,650]]},
    #        {"label":"Bebeji","data":[[1239706800000,500],[1239793200000,350],[1239836400000,250]]},
    #        ]'''
    
    rows = []
    for location in locations:
        # get all the partial transactions that affected this stock
        updates = PartialTransaction.get_all_with_stock_updates(location).order_by("date")
        if len(updates) > 0:
            update_strings = []
            for update in updates:
                ud_time = str(time.mktime(update.date.timetuple()))
                udt_formatted = ud_time[0:ud_time.find(".")] + "000"
                update_strings.append("[%s,%s]" % (udt_formatted, update.stock))
            #print "adding update for %s" % location 
            rows.append('{"label":"%s", "data":[%s]}' % (location.name, ",".join(update_strings)))
    data = "[%s]" % (",".join(rows))
    options = '{"bars":{"show":false},"points":{"show":true},"grid":{"clickable":false},"xaxis":{"mode":"time","timeformat":"%m/%d/%y"},"yaxis":{"min":0},"legend":{"show":true},"lines":{"show":true}}'
    return (data, options)