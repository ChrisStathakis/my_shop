from django.contrib import admin
from django.db.models import Count, Sum, Min, Max
from django.db.models import DateField
from django.db.models.functions import Trunc
from .models import RetailOrderItem, RetailOrder, GiftRetailItem
from import_export.admin import ImportExportModelAdmin
# Register your models here.


@admin.register(RetailOrder)
class RetailOrderAdmin(ImportExportModelAdmin):
    list_display = ['date_expired', 'title', 'order_type', 'tag_final_value']
    list_filter = ['is_paid', 'date_expired', 'order_type']
    list_per_page = 50
    fieldsets = (
        ('General', {
            'fields': (
                ('is_paid'),

                      )
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        my_list = ['tag_final_value', 'is_paid']
        return my_list


class RetailOrderAdmini(admin.ModelAdmin):
    change_list_template = 'admin_/sale_summary_change_list.html'
    date_hierarchy = 'date_expired'
    list_filter = ['payment_method', ]

    def get_next_in_date_hierarchy(self, request, date_hierarchy):
        if date_hierarchy + '__day' in request.GET:
            return 'hour'
        if date_hierarchy + '__month' in request.GET:
            return 'day'
        if date_hierarchy + '__year' in request.GET:
            return 'week'
        return 'month'

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(
            request,
            extra_context=extra_context
        )
        try:
            qs = response.context_data['cl'].queryset
        except:
            return response

        metrics = {
            'total': Count('id'),
            'total_sales': Sum('final_value')
        }
        response.context_data['summary'] = list(
            qs
            .values('payment_method__title')
            .annotate(**metrics)
            .order_by('total_sales')
        )
        period = self.get_next_in_date_hierarchy(
            request,
            self.date_hierarchy,
        )
        response.context_data['period'] = period
        summary_over_time = qs.annotate(
            period=Trunc(
                'date_expired',
                period,
                output_field=DateField(),
            ),
        ).values('period').annotate(total=Sum('final_value')).order_by('period')

        summary_range = summary_over_time.aggregate(
            low=Min('total'),
            high=Max('total')
        )
        high = summary_range.get('high', 0)
        low = summary_range.get('low', 0)
        print(summary_over_time)
        response.context_data['summary_over_time'] = [{
            'period': x['period'],
            'total': x['total'] or 0,
            'pct': ((x['total'] or 0) - low) / (high - low) * 100 if high > low else 0,
        } for x in summary_over_time]
        return response


admin.site.register(RetailOrderItem)
admin.site.register(GiftRetailItem)