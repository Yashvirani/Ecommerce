from django.shortcuts import render,get_object_or_404
from django.conf import settings
from .models import Item
from django.views.generic import ListView,DetailView,View,CreateView,TemplateView
from app.models import Item,OrderItem,Order,BillingAddress,Payment,UserProfile
from django.shortcuts import redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from .forms import CheckoutForm,UserProfileForm,OtherUpdateForm
import stripe
from django.db.models import Q
from django.core.mail import send_mail
stripe.api_key ="sk_test_9FkziyXAET6iNdQ1SwZebMYy00s9ZGRf7b"

# `source` is obtained with Stripe.js; see https://stripe.com/docs/payments/accept-a-payment-charges#web-create-token

# Create your views here.

def products(request):
    context={
       'items':Item.objects.all()
    }
    return render(request,'products.html',context)

class CheckoutView(View):
    def get(self,*args,**kwargs):
        form=CheckoutForm()
        context={
            'form':form
        }
        return render(self.request,'checkout.html',context)

    def post(self,*args,**kwargs):
        form=CheckoutForm(self.request.POST or None)
        try:
            order=Order.objects.get(user=self.request.user,ordered=False)
            if form.is_valid():
                street_address=form.cleaned_data.get('street_address')
                apartment_address=form.cleaned_data.get('apartment_address')
                country=form.cleaned_data.get('billing_country')
                zip=form.cleaned_data.get('zip')
                #same_billing_address=forms.cleaned_data.get('same_billing_address')
                #save_info=forms.cleaned_data.get('save_info')
                payment_option=form.cleaned_data.get('payment_option')
                billing_address=BillingAddress(
                      user=self.request.user,
                      street_address=street_address,
                      apartment_address=apartment_address,
                      country=country,
                      zip=zip,
                )
                billing_address.save()
                order.billing_address=billing_address
                order.save()
                return redirect("payments:pay")
            messages.warning(self.request,'Failed Checkout')
            return redirect('app:checkout')


        except ObjectDoesNotExist:
            messages.error(self.request,"You dont have an active order")
            return redirect("/")

class PaymentView(View):
    def get(self,*args,**kwargs):
        return render(self.request,'payment.html')

    def post(self,*args,**kwargs):
        token=self.request.POST.get('stripeToken')
        order=Order.objects.get(user=self.request.user,ordered=False)
        amount=int(order.get_total())
        try:
          # Use Stripe's library to make requests...
          charge=stripe.Charge.create(
            amount=amount,
            currency="usd",
            source=token,
            description="My First Test Charge (created for API docs)",
          )

          payment=Payment()
          payment.stripe_charge_id=charge['id']
          payment.user=self.request.user
          payment.amount=order.get_total()
          payment.save()

          order.ordered=True
          order.payment=payment
          order.save()
          messages.success(self.request,'Your order was successful.')
          return redirect("/")


        except stripe.error.CardError as e:
          # Since it's a decline, stripe.error.CardError will be caught
          body = e.json_body
          err = body.get('error', {})
          messages.warning(self.request, f"{err.get('message')}")
          return redirect("/")

        except stripe.error.RateLimitError as e:
            # Too many requests made to the API too quickly
            messages.warning(self.request, "Rate limit error")
            return redirect("/")

        except stripe.error.InvalidRequestError as e:
            # Invalid parameters were supplied to Stripe's API
            print(e)
            messages.warning(self.request, "Invalid parameters")
            return redirect("/")

        except stripe.error.AuthenticationError as e:
            # Authentication with Stripe's API failed
            # (maybe you changed API keys recently)
            messages.warning(self.request, "Not authenticated")
            return redirect("/")

        except stripe.error.APIConnectionError as e:
            # Network communication with Stripe failed
            messages.warning(self.request, "Network error")
            return redirect("/")

        except stripe.error.StripeError as e:
            # Display a very generic error to the user, and maybe send
            # yourself an email
            messages.warning(
                self.request, "Something went wrong. You were not charged. Please try again.")
            return redirect("/")

        except Exception as e:
            # send an email to ourselves
            messages.warning(
                self.request, "A serious error occurred. We have been notifed.")
            return redirect("/")
        card=True



class HomeView(ListView):
    model=Item
    template_name='home.html'

class OrderSummaryView(LoginRequiredMixin,View):
    def get(self,*args,**kwargs):
        try:
            order=Order.objects.get(user=self.request.user,ordered=False)
            context={
               'object':order
            }
            return render(self.request,'order_summary.html',context)
        except ObjectDoesNotExist:
            messages.error(self.request,"You dont have an active order")
            return redirect("/")

class ItemDetailView(DetailView):
    model=Item
    template_name='products.html'

@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item,created=OrderItem.objects.get_or_create(
               item=item,
               user=request.user,
               ordered=False

    )
    order_qs=Order.objects.filter(user=request.user,ordered=False)
    if order_qs.exists():
        order=order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity+=1
            order_item.save()
            messages.info(request,"Item quantity was updated.")
            return redirect("app:order_summary")
        else:
            order.items.add(order_item)
            messages.info(request,"This item was added to your cart.")
            return redirect("app:order_summary")

    else:
        ordered_date=timezone.now()
        order=Order.objects.create(user=request.user,ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request,"This item was added to your cart.")
    return redirect("app:order_summary")

@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            order.items.remove(order_item)
            order_item.delete()
            messages.info(request, "This item was removed from your cart.")
            return redirect("app:product",slug=slug)
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("app:product", slug=slug)
    else:
        messages.info(request, "You do not have an active order")
        return redirect("app:product", slug=slug)

@login_required
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
            messages.info(request, "This item quantity was updated.")
            return redirect("app:order_summary")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("app:product", slug=slug)
    else:
        messages.info(request, "You do not have an active order")
        return redirect("app:product", slug=slug)

def search(request):
    query=request.GET['search']
    object_list=Item.objects.filter(title__icontains=query)
    params={
         'object_list':object_list
    }
    return render(request,'search.html',params)

def contact(request):
    if request.method=='POST':
        email=request.POST['email']
        message=request.POST['message']
        if (send_mail('Test',
                  message,
                  email,
                  [settings.EMAIL_HOST_USER],
                  fail_silently=False,)):
                  messages.success(request,'Mail sent successfully! We will reply you soon.')
                  return redirect("/")
        else:
            messages.error(request,"Mail couldn't be sent due to some technical error, try again after sometime.")
    return render(request,'contact.html')

def profile(request):
    form1=UserProfileForm()
    form2=OtherUpdateForm()
    if request.method=='POST':
        form1=UserProfileForm(request.POST)
        form2=OtherUpdateForm(request.POST)
        if form1.is_valid() and form2.is_valid():
            form1.save()
            form2.save()
    context={
           'form1':form1,
           'form2':form2}
    messages.success(request,"Profile created successfully")
    return render(request,'profile.html',context)

def Profile(request):
    return render(request,'newprofile.html')
