from django.db import models
from django.conf import settings
from django.urls import reverse
from django_countries.fields import CountryField
from django.contrib.auth import get_user_model
User=get_user_model()
from django import template
register=template.Library()

# Create your models here.

CATEGORY_CHOICES={
      ('S','Shirt'),
      ('Sw','Sport wear'),
      ('OW','Outwear'),

}

LABEL_CHOICES={
      ('P','primary'),
      ('S','secondary'),
      ('D','danger'),

}


class Item(models.Model):
    title=models.CharField(max_length=200)
    price=models.FloatField()
    discount_price=models.FloatField(blank=True,null=True)
    category=models.CharField(choices=CATEGORY_CHOICES,max_length=200)
    label=models.CharField(choices=LABEL_CHOICES,max_length=200)
    slug=models.SlugField()
    description=models.TextField()
    picture=models.ImageField(max_length=255,null=True,blank=True)
    picture1=models.ImageField(max_length=255,null=True,blank=True)
    picture2=models.ImageField(max_length=255,null=True,blank=True)
    picture3=models.ImageField(max_length=255,null=True,blank=True)



    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("app:product",kwargs={'slug':self.slug})

    def get_add_to_cart_url(self):
        return reverse("app:add_to_cart",kwargs={'slug':self.slug})



class OrderItem(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
    ordered=models.BooleanField(default=False)
    item=models.ForeignKey(Item,on_delete=models.CASCADE)
    quantity=models.IntegerField(default=1)

    def __str__(self):
        return f'{self.quantity} of {self.item.title}'

    def get_total_item_price(self):
        return self.quantity * self.item.price

    def get_total_discount_item_price(self):
        return self.quantity*self.item.discount_price

    def get_amount_saved(self):
        return self.get_total_item_price()-self.get_total_discount_item_price()

    def get_final_price(self):
        if self.item.discount_price:
            return self.get_total_discount_item_price()
        return self.get_total_item_price()



class Order(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    items=models.ManyToManyField(OrderItem)
    start_date=models.DateTimeField(auto_now_add=True)
    ordered_date=models.DateTimeField()
    ordered=models.BooleanField(default=False)
    billing_address=models.ForeignKey('BillingAddress',on_delete=models.SET_NULL,null=True,blank=True)
    payment=models.ForeignKey('Payment',on_delete=models.SET_NULL,null=True,blank=True)


    def __str__(self):
        return self.user.username

    def get_total(self):
        total=0
        for order_item in self.items.all():
            total+=order_item.get_final_price()
        return total

class BillingAddress(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    street_address=models.CharField(max_length=200)
    apartment_address=models.CharField(max_length=200)
    country=CountryField(multiple=False)
    zip=models.CharField(max_length=200)


    def __str__(self):
        return self.user.username

class Payment(models.Model):
    stripe_charge_id=models.CharField(max_length=50)
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,blank=True,null=True)
    amount=models.FloatField()
    timestamp=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username

class UserProfile(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
    photo=models.ImageField(max_length=255,null=True,blank=True)
    phone_number=models.IntegerField(null=True,blank=True)
    state=models.CharField(max_length=255,null=True,blank=True)
    city=models.CharField(max_length=255,null=True,blank=True)


    def __str__(self):
        return self.user.username

class Success(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    picture=models.ImageField(max_length=225,null=True,blank=True)

    def __str__(self):
        return self.user.username
