import os
from django.conf import settings
from django.shortcuts import render, redirect

import braintree


# Create your views here.
def index(request):
    return render(request, 'index.html')


def about(request):
    return render(request, 'about.html')


def contact(request):
    return render(request, 'contact.html')


def register(request):
    return render(request, 'register.html')


def membership(request):
    return render(request, 'membership.html')

def payment(request, membership):
    # Initalize variables
    context = {}
    errors = {}
    amount = {
        'premium': settings.PREMIUM_MEMBERSHIP,
        'regular': settings.REGULAR_MEMBERSHIP,
    }

    # Handle form submission
    if request.method == 'POST':

        # Payment Nonce
        nonce = request.POST.get("payment_method_nonce")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        
        # Create a new customer record with Braintree
        cust_result = braintree.Customer.create({
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "payment_method_nonce": nonce
        })

        # Customer creation successful, submit transaction for the customer
        if cust_result.is_success:

            # Submit the transaction
            txn_result = braintree.Transaction.sale({
                "customer_id": cust_result.customer.id,
                "amount": amount[membership]
            })

            # Customer & Transaction Successful
            if txn_result.is_success:
                return redirect('payment_success')

            # Handle the Transaction Error
            else:
                errors.update(cust_result.errors.deep_errors)

        # Handle Customer Creation Error
        else:
            errors.update(cust_result.errors.deep_errors)


    # Configure braintree
    braintree.Configuration.configure(
        braintree.Environment.Sandbox,
        merchant_id="jw8gd3ccpk8x7sbq",
        public_key="56wc54324vdcmcrn",
        private_key=os.environ.get('BRAINTREE_PRIVATE_KEY')
    )
    # Get a client token
    token = braintree.ClientToken.generate()

    # Context variables
    context.update({
        'token': token,
        'membership': membership,
        'amount': amount[membership],
    })
    if errors:
        context.update(errors)

    return render(request, 'payment.html', context)


def payment_success(request):
    return render(request, 'payment_success.html')




