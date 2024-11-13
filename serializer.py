# core/serializers.py

from rest_framework import serializers
from core.models import Customer
from django.db.models import Max  # Correct import here
import math

class CustomerSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(max_length=50)
    last_name = serializers.CharField(max_length=50)
    age = serializers.IntegerField()
    monthly_income = serializers.FloatField()
    phone_number = serializers.CharField(max_length=15)

    class Meta:
        model = Customer
        fields = ['first_name', 'last_name', 'age', 'monthly_income', 'phone_number']

    def create(self, validated_data):
        # Determine the new customer_id
        max_id = Customer.objects.aggregate(max_id=Max('customer_id'))['max_id'] or 0  # Corrected this line
        customer_id = max_id + 1

        # Calculate approved limit, rounded to the nearest lakh
        approved_limit = round(36 * validated_data['monthly_income'] / 100000) * 100000

        # Create the customer with calculated fields
        customer = Customer.objects.create(
            customer_id=customer_id,
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            age=validated_data['age'],
            monthly_salary=validated_data['monthly_income'],
            approved_limit=approved_limit,
            phone_number=validated_data['phone_number'],
        )

        return customer
