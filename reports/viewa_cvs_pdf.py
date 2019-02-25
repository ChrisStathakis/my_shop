from django.shortcuts import render, HttpResponseRedirect
import openpyxl

from products.models import Product


def product_csv_view(request):
    products = Product.objects.all()
    HEADER = ('id', 'title', 'category', 'price_buy', 'final_price', 'vendor')
    DATA = products.values_list('id', 'title', 'category', 'price_buy', 'final_price', 'vendor')
    xlsfile = openpyxl.Workbook()
    products_excel = xlsfile['Products QuerySet']
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))