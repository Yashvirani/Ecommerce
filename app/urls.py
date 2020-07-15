from django.conf.urls import url
from . import views

app_name='app'

urlpatterns=[
     url(r'^$',views.HomeView.as_view(),name='home'),
     url(r'^checkout/$',views.CheckoutView.as_view(),name='checkout'),
     url(r'^order_summary/$',views.OrderSummaryView.as_view(),name='order_summary'),
     url(r'^product/(?P<slug>[-\w]+)/$',views.ItemDetailView.as_view(),name='product'),
     url(r'^add_to_cart/(?P<slug>[-\w]+)/$',views.add_to_cart,name='add_to_cart'),
     url(r'^remove_from_cart/(?P<slug>[-\w]+)/$',views.remove_from_cart,name='remove_from_cart'),
     url(r'^remove_single_item_from_cart/(?P<slug>[-\w]+)/$',views.remove_single_item_from_cart,name='remove_single_item_from_cart'),
     url(r'^payment/<payment_option>/$',views.PaymentView.as_view(),name='payment'),
     url(r'^search/$',views.search,name='search'),
     url(r'^contact/$',views.contact,name='contact'),
     url(r'^profile/$',views.Profile,name='profile'),

]
