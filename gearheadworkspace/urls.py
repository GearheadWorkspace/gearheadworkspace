from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'gearheadworkspace.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
	url(r'^$', 'promo.views.index', name='home'),
	url(r'^about/$', 'promo.views.about', name='about'),
	url(r'^contact/$', 'promo.views.contact', name='contact'),
	url(r'^register/$', 'promo.views.register', name='register'),
	url(r'^membership/$', 'promo.views.membership', name='membership'),
	url(r'^payment/(?P<membership>premium|regular)/$', 'promo.views.payment', name='payment'),
	url(r'^payment/success/$', 'promo.views.payment_success', name='payment_success'),
    url(r'^admin/', include(admin.site.urls)),
) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
