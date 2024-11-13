# core/management/commands/start_data_ingestion.py

from django.core.management.base import BaseCommand
from core.tasks import ingest_customer_data, ingest_loan_data

class Command(BaseCommand):
    help = 'Ingest customer and loan data from Excel files into the database'

    def handle(self, *args, **kwargs):
        customer_file_path = '/app/customer_data.xlsx'
        loan_file_path = '/app/loan_data.xlsx'

        ingest_customer_data.delay(customer_file_path)
        ingest_loan_data.delay(loan_file_path)

        self.stdout.write(self.style.SUCCESS('Data ingestion tasks have been triggered'))
