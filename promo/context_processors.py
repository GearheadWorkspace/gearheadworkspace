from django.conf import settings 


def membership_prices(request):
	# Add the membership prices to all request context
    return {
    	'PREMIUM_MEMBERSHIP': settings.PREMIUM_MEMBERSHIP,
    	'REGULAR_MEMBERSHIP': settings.REGULAR_MEMBERSHIP,
		'MEMBERSHIP_RESERVATION': settings.MEMBERSHIP_RESERVATION,
    }
