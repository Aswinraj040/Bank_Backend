# core/management/commands/fetch_loans.py

from django.core.management.base import BaseCommand
from core.models import Loan

class Command(BaseCommand):
    help = 'Fetch all loan details from the database'

    def handle(self, *args, **kwargs):
        loans = Loan.objects.all()
        for loan in loans:
            self.stdout.write(f'Loan ID: {loan.loan_id}')
            self.stdout.write(f'Customer ID: {loan.customer.customer_id}')
            self.stdout.write(f'Loan Amount: {loan.loan_amount}')
            self.stdout.write(f'Tenure: {loan.tenure} months')
            self.stdout.write(f'Interest Rate: {loan.interest_rate}%')
            self.stdout.write(f'Monthly Repayment: {loan.monthly_repayment}')
            self.stdout.write(f'EMIs Paid On Time: {loan.emis_paid_on_time}')
            self.stdout.write(f'Start Date: {loan.start_date}')
            self.stdout.write(f'End Date: {loan.end_date}')
            self.stdout.write('---------------------------')
