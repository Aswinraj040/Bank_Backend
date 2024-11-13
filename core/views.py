# core/views.py


from serializer import CustomerSerializer
from django.db.models import Max
from django.utils import timezone
from datetime import timedelta
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from core.models import Customer, Loan



@api_view(['POST'])
def register_customer(request):
    serializer = CustomerSerializer(data=request.data)

    if serializer.is_valid():
        customer = serializer.save()

        # Prepare response data
        response_data = {
            'customer_id': customer.customer_id,
            'name': f"{customer.first_name} {customer.last_name}",
            'age': customer.age,
            'monthly_income': customer.monthly_salary,
            'approved_limit': customer.approved_limit,
            'phone_number': customer.phone_number,
        }

        return Response(response_data, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
def check_loan_eligibility(request):
    customer_id = request.data.get("customer_id")
    loan_amount = request.data.get("loan_amount")
    requested_interest_rate = request.data.get("interest_rate")
    tenure = request.data.get("tenure")

    # Validate the input data
    if not all([customer_id, loan_amount, requested_interest_rate, tenure]):
        return Response({"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)

    # Fetch the customer data
    try:
        customer = Customer.objects.get(customer_id=customer_id)
    except Customer.DoesNotExist:
        return Response({"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)

    # Fetch the customer's loan history
    past_loans = Loan.objects.filter(customer=customer)
    current_year = timezone.now().year

    # Credit score calculation based on history
    credit_score = 100  # Start with max score and deduct based on criteria
    total_current_loan = sum(loan.loan_amount for loan in past_loans)
    total_emis_paid_on_time = sum(loan.emis_paid_on_time for loan in past_loans)
    loans_in_current_year = past_loans.filter(start_date__year=current_year).count()
    loan_volume = sum(loan.loan_amount for loan in past_loans)

    # If the sum of current loans exceeds approved limit, credit score is 0
    if total_current_loan > customer.approved_limit:
        credit_score = 0
    else:
        # Deduct points based on criteria
        credit_score -= max(0, 100 - total_emis_paid_on_time * 2)  # Deduct based on EMIs on time
        credit_score -= min(20, loans_in_current_year * 5)  # Deduct based on loans in current year
        credit_score -= min(20, loan_volume / 100000)  # Deduct based on volume of loans

    # If sum of all current EMIs > 50% of monthly salary, do not approve
    total_monthly_emis = sum(loan.monthly_repayment for loan in past_loans)
    if total_monthly_emis > 0.5 * customer.monthly_salary:
        return Response({
            "customer_id": customer_id,
            "approval": False,
            "reason": "EMIs exceed 50% of monthly income"
        }, status=status.HTTP_200_OK)

    # Determine loan approval and adjust interest rate based on credit score
    corrected_interest_rate = requested_interest_rate
    approval = False
    if credit_score > 50:
        approval = True
    elif 50 > credit_score > 30:
        corrected_interest_rate = max(12, requested_interest_rate)
        approval = True
    elif 30 > credit_score > 10:
        corrected_interest_rate = max(16, requested_interest_rate)
        approval = True
    elif credit_score <= 10:
        approval = False

    # Compound interest formula for calculating EMI (monthly installment)
    if approval:
        monthly_rate = corrected_interest_rate / 1200
        monthly_installment = loan_amount * monthly_rate * ((1 + monthly_rate) ** tenure) / (((1 + monthly_rate) ** tenure) - 1)
    else:
        monthly_installment = 0

    # Prepare response data
    response_data = {
        "customer_id": customer_id,
        "approval": approval,
        "interest_rate": requested_interest_rate,
        "corrected_interest_rate": corrected_interest_rate,
        "tenure": tenure,
        "monthly_installment": monthly_installment if approval else None
    }

    return Response(response_data, status=status.HTTP_200_OK)

@api_view(['POST'])
def create_loan(request):
    customer_id = request.data.get("customer_id")
    loan_amount = request.data.get("loan_amount")
    requested_interest_rate = request.data.get("interest_rate")
    tenure = request.data.get("tenure")

    # Validate the input data
    if not all([customer_id, loan_amount, requested_interest_rate, tenure]):
        return Response({"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)

    # Fetch the customer data
    try:
        customer = Customer.objects.get(customer_id=customer_id)
    except Customer.DoesNotExist:
        return Response({"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)

    # Fetch the customer's loan history
    past_loans = Loan.objects.filter(customer=customer)
    current_year = timezone.now().year

    # Calculate the credit score
    credit_score = 100  # Start with max score
    total_current_loan = sum(loan.loan_amount for loan in past_loans)
    total_emis_paid_on_time = sum(loan.emis_paid_on_time for loan in past_loans)
    loans_in_current_year = past_loans.filter(start_date__year=current_year).count()
    loan_volume = sum(loan.loan_amount for loan in past_loans)

    # Check if total current loans exceed the approved limit
    if total_current_loan > customer.approved_limit:
        credit_score = 0
    else:
        credit_score -= max(0, 100 - total_emis_paid_on_time * 2)
        credit_score -= min(20, loans_in_current_year * 5)
        credit_score -= min(20, loan_volume / 100000)

    # Check if sum of current EMIs > 50% of monthly salary
    total_monthly_emis = sum(loan.monthly_repayment for loan in past_loans)
    if total_monthly_emis > 0.5 * customer.monthly_salary:
        return Response({
            "loan_id": None,
            "customer_id": customer_id,
            "loan_approved": False,
            "message": "EMIs exceed 50% of monthly income",
            "monthly_installment": None
        }, status=status.HTTP_200_OK)

    # Determine approval based on credit score and adjust interest rate if needed
    corrected_interest_rate = requested_interest_rate
    loan_approved = False
    message = "Loan approved"

    if credit_score > 50:
        loan_approved = True
    elif 50 > credit_score > 30:
        corrected_interest_rate = max(12, requested_interest_rate)
        loan_approved = True
    elif 30 > credit_score > 10:
        corrected_interest_rate = max(16, requested_interest_rate)
        loan_approved = True
    elif credit_score <= 10:
        message = "Credit score too low for loan approval"
        loan_approved = False

    # If the loan is approved, calculate monthly installment and save loan details
    if loan_approved:
        # Compound interest formula for EMI calculation
        monthly_rate = corrected_interest_rate / 1200
        monthly_installment = loan_amount * monthly_rate * ((1 + monthly_rate) ** tenure) / (
                    ((1 + monthly_rate) ** tenure) - 1)

        # Save the loan in the database
        new_loan = Loan.objects.create(
            loan_id=Loan.objects.aggregate(max_id=Max('loan_id'))['max_id'] + 1 or 1,
            customer=customer,
            loan_amount=loan_amount,
            tenure=tenure,
            interest_rate=corrected_interest_rate,
            monthly_repayment=monthly_installment,
            emis_paid_on_time=0,  # Assuming it's a new loan
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=tenure * 30)
        )

        return Response({
            "loan_id": new_loan.loan_id,
            "customer_id": customer_id,
            "loan_approved": loan_approved,
            "message": message,
            "monthly_installment": monthly_installment
        }, status=status.HTTP_201_CREATED)

    # If loan is not approved, return the failure message
    return Response({
        "loan_id": None,
        "customer_id": customer_id,
        "loan_approved": loan_approved,
        "message": message,
        "monthly_installment": None
    }, status=status.HTTP_200_OK)



@api_view(['GET'])
def view_loan(request, loan_id):
    try:
        loan = Loan.objects.get(loan_id=loan_id)
    except Loan.DoesNotExist:
        return Response({"error": "Loan not found"}, status=status.HTTP_404_NOT_FOUND)

    customer = loan.customer
    response_data = {
        "loan_id": loan.loan_id,
        "customer": {
            "id": customer.customer_id,
            "first_name": customer.first_name,
            "last_name": customer.last_name,
            "phone_number": customer.phone_number,
            "age": customer.age
        },
        "loan_amount": loan.loan_amount,
        "interest_rate": loan.interest_rate,
        "monthly_installment": loan.monthly_repayment,
        "tenure": loan.tenure
    }

    return Response(response_data, status=status.HTTP_200_OK)
@api_view(['GET'])
def view_loans(request, customer_id):
    try:
        customer = Customer.objects.get(customer_id=customer_id)
    except Customer.DoesNotExist:
        return Response({"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)

    loans = Loan.objects.filter(customer=customer)

    if not loans.exists():
        return Response({"message": "No loans found for this customer"}, status=status.HTTP_200_OK)

    loan_list = []
    for loan in loans:
        repayments_left = loan.tenure - loan.emis_paid_on_time  # Calculating remaining repayments
        loan_list.append({
            "loan_id": loan.loan_id,
            "loan_amount": loan.loan_amount,
            "interest_rate": loan.interest_rate,
            "monthly_installment": loan.monthly_repayment,
            "repayments_left": repayments_left
        })

    return Response(loan_list, status=status.HTTP_200_OK)
