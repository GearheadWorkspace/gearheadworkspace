import os
import json
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

import braintree

from promo.models import Subscriber


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
    errors = []
    amount = {
        'premium': settings.PREMIUM_MEMBERSHIP,
        'regular': settings.REGULAR_MEMBERSHIP,
		'reservation': settings.MEMBERSHIP_RESERVATION,
        'donation': request.POST.get("amount", 0)
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
                return redirect_for_email(email)

            # Handle the Transaction Error
            else:
                _append_errors(errors, txn_result)

        # Handle Customer Creation Error
        else:
            _append_errors(errors, cust_result)

    # Get the braintree environment
    if os.environ.get('BRAINTREE_PRODUCTION', False):
        env = braintree.Environment.Production
    else:
        env = braintree.Environment.Sandbox

    # Configure braintree
    braintree.Configuration.configure(
        env,
        merchant_id=os.environ.get('BRAINTREE_MERCHANT_ID'),
        public_key=os.environ.get('BRAINTREE_PUBLIC_KEY'),
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
        context.update({'errors': errors})

    return render(request, 'payment.html', context)


def _append_errors(errors, response_errors):
    # It'd be great if this worked, but it doesn't. thanks braintree...
    for error in response_errors.errors.deep_errors:
        errors.append({
            'code': error.code,
            'message': error.message
        })
    # So we have to guess...
    if response_errors.transaction.processor_response_text:
        errors.append({
            'code':'Payment Processor Error',
            'message': response_errors.transaction.processor_response_text
        })
    if response_errors.transaction.processor_settlement_response_text:
        errors.append({
            'code':'Payment Processor Settlement Error',
            'message': response_errors.transaction.processor_settlement_response_text
        })
    if response_errors.transaction.gateway_rejection_reason:
        errors.append({
            'code':'Payment Processor Gateway Error',
            'message': response_errors.transaction.gateway_rejection_reason
        })


def payment_success(request, show_mailinglist=''):
    return render(request, 'payment_success.html', {'show_mailinglist': show_mailinglist})


# API JUNK

@csrf_exempt
def subscriber(request):
    """
    POST API endpoint for compiling a list of newsletter subscribers
    """
    message = {}
    status = 200
    try:
        email = request.POST.get('email', '').lower()
        sub, created = Subscriber.objects.get_or_create(email=email)
        message = {
            'status': 'success',
            'data': {
                'email': sub.email,
                'created': created
            }
        }

    except Exception, e:
        message = {'status': 'error', 'message': e.message}
        status = 500

    return HttpResponse(json.dumps(message), status=status)


# HELPER JUNK

def redirect_for_email(email):
    """
    Check if the submitted email address exists in the list of users we've
    seen subscribe to the mailing list. If they have not yet subscribed, show
    them the Mail Chimp subscription form.
    """
    if Subscriber.objects.filter(email=email).count() == 0:
        return redirect('payment_success', show_mailinglist='mailinglist')
    else:
        return redirect('payment_success')
