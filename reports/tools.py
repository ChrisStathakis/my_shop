from django.db.models import Q, Sum, F

import datetime
from itertools import chain
from operator import attrgetter
from dateutil.relativedelta import relativedelta

from products.models import Category, Color, Size
from frontend.models import CategorySite, Brands
from inventory_manager.models import Vendor, Order, OrderItem
from point_of_sale.models import *


def diff_month(date_start, date_end):
    return (date_end.year - date_start.year)*12 + (date_end.month - date_start.month)


def get_filters_data(request):
    search_name = request.GET.get('search_name', None)
    cate_name = request.GET.getlist('cate_name', None)
    vendor_name = request.GET.getlist('vendor_name', None)
    brand_name = request.GET.getlist('brand_name', None)
    category_site_name = request.GET.getlist('category_site_name', None)
    site_status = request.GET.get('site_status', None)
    color_name = request.GET.getlist('color_name', None)
    size_name = request.GET.getlist('size_name', None)
    discount_name = request.GET.get('discount_name', None)
    qty_name = request.GET.get('qty_name', None)
    return [search_name, cate_name, vendor_name, brand_name, category_site_name, site_status, color_name, size_name,
            discount_name, qty_name]


def initial_data_from_database():
    vendors, categories, categories_site, colors, sizes, brands = [Vendor.objects.all(), Category.objects.all(), CategorySite.objects.all(),
                                                           Color.objects.all(), Size.objects.all(), Brands.objects.all()]
    return vendors, categories, categories_site, colors, sizes, brands


def warehouse_filters(request, products):
    category_name = request.GET.getlist('category_name', None)
    vendor_name = request.GET.getlist('vendor_name', None)
    site_status = request.GET.get('site_status', None)
    color_name = request.GET.getlist('color_name', None)
    size_name = request.GET.getlist('size_name', None)
    discount_name = request.GET.get('discount_name', None)
    qty_name = request.GET.get('qty_name', None)
    try:
        products = products.filter(qty__gt=0) if qty_name else products
        products = products.filter(price_discount__gt=1) if discount_name else products
        products = products.filter(color__id__in=color_name) if color_name else products
        products = products.filter(category__id__in=category_name) if category_name else products
        products = products.filter(supply__id__in=vendor_name) if vendor_name else  products
        products = products.filter(status__in=site_status) if site_status else products
        size_attr = SizeAttribute.objects.filter(product_related__in=products, title__id__in=size_name)
        products_with_size = [ele.product_related.id for ele in size_attr]
    except:
        pass
    #products = products.filter(id__in=products_with_size)
    query = request.GET.get('search_pro')
    if query:
        products = products.filter(
            Q(title__icontains=query)|
            Q(category__title__icontains=query) |
            Q(supply__title__icontains=query) |
            Q(order_code__icontains=query)
        ).distinct()
    return [products, category_name, vendor_name, color_name, discount_name, qty_name]


def initial_date(request, months=3):
    #gets the initial last three months or the session date
    date_now = datetime.datetime.today()
    try:
        date_range = request.session['date_range']
        date_range = date_range.split('-')
        date_range[0] = date_range[0].replace(' ','')
        date_range[1] = date_range[1].replace(' ','')
        date_start = datetime.datetime.strptime(date_range[0], '%m/%d/%Y')
        date_end = datetime.datetime.strptime(date_range[1],'%m/%d/%Y')
    except:
        date_three_months_ago = date_now - relativedelta(months=months)
        date_start = date_three_months_ago
        date_end = date_now
        date_range = '%s - %s' % (str(date_three_months_ago).split(' ')[0].replace('-','/'),str(date_now).split(' ')[0].replace('-','/'))
        request.session['date_range'] = '%s - %s'%(str(date_three_months_ago).split(' ')[0].replace('-','/'),str(date_now).split(' ')[0].replace('-','/'))
    return [date_start, date_end, date_range]


def clean_date_filter(request, date_pick, date_start=None, date_end=None, date_range=None):
    try:
        date_range = date_pick.split('-')
        date_range[0] = date_range[0].replace(' ', '')
        date_range[1] = date_range[1].replace(' ', '')
        date_start = datetime.datetime.strptime(date_range[0], '%m/%d/%Y')
        date_end = datetime.datetime.strptime(date_range[1], '%m/%d/%Y')
        date_range = '%s - %s' % (date_range[0], date_range[1])
    except:
        date_start, date_end, date_range = [date_start, date_end, date_range] if date_start and date_end else \
            initial_date(request)
    return [date_start, date_end, date_range]


def estimate_date_start_end_and_months(request):
    day_now, start_year = datetime.datetime.now(), datetime.datetime(datetime.datetime.now().year, 2, 1)
    date_pick = request.GET.get('date_pick', None)
    start_year, day_now, date_range = clean_date_filter(request, date_pick, date_start=start_year, date_end=day_now)
    months_list=12
    return [start_year, day_now, date_range, months_list]


def warehouse_vendors_analysis(request, date_start, date_end):
    vendor_name = request.GET.getlist('vendor_name', None)
    orders = Order.objects.filter(timestamp__range=[date_start, date_end])
    orders = orders.filter(vendor__id__in=vendor_name) if vendor_name else orders
    current_vendor_analysis = orders.values('vendor__title').annotate(total_value=Sum('final_value'),
                                                                      total_paid_=Sum('paid_value'),
                                                                      )
    # print(current_vendor_analysis)
    return [current_vendor_analysis]


def balance_sheet_chart_analysis(start_year, day_now, orders, value):
    get_data = []
    months = diff_month(start_year, day_now)
    string, string_sum = '%s' % value, '%s__sum' % value
    for month in range(months+1):
        new_date = day_now - relativedelta(months=month)
        string_month, month, year = new_date.strftime('%B'), new_date.month, new_date.year
        try:
            get_orders = orders.filter(date_expired__month=month, date_expired__year=year).aggregate(Sum(string))[
                string_sum] if orders.filter(date_expired__month=month, date_expired__year=year) else 0
        except:
            get_orders_ = orders.filter(date_expired__month=month, date_expired__year=year)
            get_orders = orders.filter(date_expired__month=month, date_expired__year=year).aggregate(Sum(string))[
                string_sum] if orders.filter(date_expired__month=month, date_expired__year=year) else 0
        get_orders = get_orders if get_orders else 0
        get_data.append((string_month, get_orders))
    get_data.reverse()
    return get_data