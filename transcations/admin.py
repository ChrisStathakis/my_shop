from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from import_export.admin import ImportExportModelAdmin
from .models import Bill, BillCategory, Payroll, Person, Occupation, GenericExpense, GenericExpenseCategory


def paid_action(modeladmin, queryset):
    for ele in queryset:
        ele.is_paid = True
        ele.save()


paid_action.short_description = 'Αποπληρωμή'


@admin.register(Occupation)
class OccupationAdmin(admin.ModelAdmin):
    list_display = ['title', 'active']
    list_filter = ['active']
    fields = ['active', 'title', 'notes']


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ['title', 'phone', 'occupation', 'tag_balance', 'active']
    list_select_related = ['store', 'occupation']
    list_filter = ['occupation', 'active', 'store']
    readonly_fields = ['tag_balance', 'timestamp', 'edited']
    fieldsets = (
        ('General Info', {
            'fields': ('active',
                       ('title', 'date_added'),
                       ('timestamp', 'edited')
                       )
        }),
        ('Edit', {
            'fields': (('occupation', 'store'),
                       ('phone', 'phone1'),
                       ('vacation_days',)
                       )
        }),
    )


@admin.register(Payroll)
class PayrollAdmin(admin.ModelAdmin):
    list_display = ['date_expired', 'person', 'category', 'tag_final_value', 'is_paid']
    list_filter = ['is_paid', 'category', 'person']
    fieldsets = (
        ('General Info', {
            'fields': ('is_paid',
                       ('title', 'date_expired'),
                       ('timestamp', 'edited')
                       )
        }),
        ('Edit info', {
            'fields': (('person', 'category'),
                       ('payment_method', 'value'),
                       )
        })
    )

    def get_readonly_fields(self, request, obj=None):
        my_list = ['timestamp', 'edited']
        if obj:
            my_list.append('person')
        return my_list


@admin.register(BillCategory)
class BillCategoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'tag_balance', 'active']
    readonly_fields = ['tag_balance', ]
    list_filter = ['active']
    fields = ['active', 'title', 'tag_balance']


@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    date_hierarchy = 'date_expired'
    list_per_page = 50
    list_select_related = ['payment_method', 'category', 'user_account']
    list_display = ['date_expired', 'category', 'title', 'tag_final_value', 'payment_method', 'is_paid']
    list_filter = ['is_paid', 'category', 'date_expired', 'user_account']
    actions = [paid_action, ]

    fieldsets = (
        ('General', {
            'fields': (
                'is_paid',
                ('title', 'date_expired', 'category'),
                ('timestamp', 'edited'),
                ('tag_final_value', 'user_account'),
                )
        }),
        ('Edit Data', {
            'fields': (
                ('value', 'payment_method'),
                ('tag_paid_value')
            )
        }),
    )

    def save_model(self, request, obj, form, change):
        if not obj.user_account:
            obj.user_account = request.user
        super(BillAdmin, self).save_model(request, obj, form, change)

    def get_readonly_fields(self, request, obj=None):
        my_list = ['timestamp', 'edited', 'tag_final_value', 'user_account', 'paid_value', 'tag_paid_value']
        if obj:
            my_list.append('category')
            if obj.is_paid:
                my_list.append('value')
        return my_list


@admin.register(GenericExpenseCategory)
class GenericExpenseCategory(admin.ModelAdmin):
    list_per_page = 50
    list_display = ['title', 'tag_balance', 'active']
    list_filter = ['active']
    fields = ['active', 'title', 'tag_balance']


@admin.register(GenericExpense)
class GenericExpense(admin.ModelAdmin):
    list_per_page = 50
    list_display = ['title', 'user_account']
    readonly_fields = ['timestamp', 'edited', 'user_account']
    fieldsets = (
        ('General', {
            'fields': ('is_paid',
                       ('title', 'date_expired'),
                       ('timestamp', 'edited', 'user_account')
                       )
        }),
        ('Edit', {
            'fields': (
                ('payment_method', 'value'),

                    )
        }),

    )

    def save_model(self, request, obj, form, change):
        if not obj.user_account:
            obj.user_account = request.user
        super().save_model(request, obj, form, change)