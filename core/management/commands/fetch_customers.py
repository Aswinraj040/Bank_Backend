# core/management/commands/fetch_customers.py

from django.core.management.base import BaseCommand
from core.models import Customer

class Command(BaseCommand):
    help = 'Fetch all customer details from the database'

    def handle(self, *args, **kwargs):
        customers = Customer.objects.all()
        if customers:
            for customer in customers:
                self.stdout.write(f'Customer ID: {customer.customer_id}')
                self.stdout.write(f'First Name: {customer.first_name}')
                self.stdout.write(f'Last Name: {customer.last_name}')
                self.stdout.write(f'Phone Number: {customer.phone_number}')
                self.stdout.write(f'Age : {customer.age}')
                self.stdout.write(f'Monthly Salary: {customer.monthly_salary}')
                self.stdout.write(f'Approved Limit: {customer.approved_limit}')
                self.stdout.write('---------------------------')
        else:
            self.stdout.write("No customers found.")
