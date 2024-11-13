# core/models.py

from django.db import models

class Customer(models.Model):
    customer_id = models.AutoField(primary_key=True)  # Auto-incrementing ID
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=15)
    age = models.IntegerField()
    monthly_salary = models.FloatField()
    approved_limit = models.FloatField()

class Loan(models.Model):
    loan_id = models.AutoField(primary_key=True)  # Auto-incrementing ID
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    loan_amount = models.FloatField()
    tenure = models.IntegerField()
    interest_rate = models.FloatField()
    monthly_repayment = models.FloatField()
    emis_paid_on_time = models.IntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
