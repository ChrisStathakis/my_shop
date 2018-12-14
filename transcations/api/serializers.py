from rest_framework import serializers

from ..models import BillCategory, Bill, Occupation, Person, Payroll


class BillCategoryListSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='api_bill_category_detail', read_only=True)

    class Meta:
        model = BillCategory
        fields = ['id', 'title', 'active', 'tag_balance', 'store', 'url']


class BillCategoryDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = BillCategory
        fields = ['id', 'title', 'active', 'tag_balance', 'store' ]


class BillListSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='api_bill_detail', read_only=True)

    class Meta:
        model = Bill
        fields = ['id', 'date_expired', 'title', 'is_paid', 'tag_final_value',
                  'value', 'tag_paid_value', 'payment_method', 'tag_payment_method',
                  'category', 'tag_category',
                  'url'
                  ]


class BillDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = Bill
        fields = ['id', 'date_expired', 'title', 'is_paid', 'tag_final_value',
                  'value', 'tag_paid_value', 'payment_method', 'tag_payment_method',
                  'category', 'tag_category',
                ]


class OccupationListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Occupation
        fields = ['id', 'title', 'active']


class PersonListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Person
        fields = ['id', 'title', 'occupation', 'tag_occupation',
                  'active', 'tag_balance'
                  ]


class PayrollListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Payroll
        fields = ['id', 'person', 'tag_person', 'category', 'tag_person',
                  'tag_final_value', 'is_paid'
                  ]