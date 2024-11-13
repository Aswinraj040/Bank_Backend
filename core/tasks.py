# core/tasks.py
import pandas as pd
from celery import shared_task
from core.models import Customer, Loan
from django.db import transaction

@shared_task
@transaction.atomic
def ingest_customer_data(file_path):
    # Load the Excel file with specified columns
    df = pd.read_excel(file_path)

    # Adjust column references to match your exact Excel headers
    for _, row in df.iterrows():
        Customer.objects.update_or_create(
            customer_id=row['Customer ID'],
            defaults={
                'first_name': row['First Name'],
                'last_name': row['Last Name'],
                'phone_number': row['Phone Number'],
                'age' : row['Age'],
                'monthly_salary': row['Monthly Salary'],
                'approved_limit': row['Approved Limit']
            }
        )


@shared_task
@transaction.atomic
def ingest_loan_data(file_path):
    # Load the Excel file with specified columns
    df = pd.read_excel(file_path)

    # Adjust column references to match your exact Excel headers
    for _, row in df.iterrows():
        customer = Customer.objects.filter(customer_id=row['Customer ID']).first()
        if customer:
            Loan.objects.update_or_create(
                loan_id=row['Loan ID'],
                defaults={
                    'customer': customer,
                    'loan_amount': row['Loan Amount'],
                    'tenure': row['Tenure'],
                    'interest_rate': row['Interest Rate'],
                    'monthly_repayment': row['Monthly payment'],
                    'emis_paid_on_time': row['EMIs paid on Time'],
                    'start_date': row['Date of Approval'],
                    'end_date': row['End Date']
                }
            )
