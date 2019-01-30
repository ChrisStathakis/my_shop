from django.contrib.admin.filters import SimpleListFilter


class HaveDeptFilter(SimpleListFilter):
    title = 'Dept'
    parameter_name = 'have_dept'

    def lookups(self, request, model_admin):
        return (
            ('Yes', 'Yes'),
            ('No', 'No')
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value == 'Yes':
            return queryset.filter(balance__gt=0)
        elif value == 'No':
            return queryset.filter(balance__lt=0.01)
        return queryset