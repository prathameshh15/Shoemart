from django.urls import path
from shoemart import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('index',views.index),
    path('details/<id>',views.details),
    path('cart/<rid>',views.cart),
    path('order',views.order),
    path('about',views.about),
    path('contact',views.contact),
    path('login',views.userlogin),
    path('payment',views.payment),
    path('register',views.register),
    path('catfilter/<cv>',views.catfilter),
    path('pricerange',views.pricerange),
    path('sort/<sv>',views.sort),
    path('logout',views.user_logout),
    path('viewcart',views.viewcart),
    path('remove/<cid>',views.remove),
    path('cartqty/<sig>/<pid>',views.cartqty),
    path('sendmail',views.sendmail),
    path('search',views.search),

]

if settings.DEBUG:
    urlpatterns+=static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)