from django.urls import path
from . import views

urlpatterns = [
    path('',views.index,name="index"),
    path('create',views.acc_creation,name="create"),
    path('pin',views.pin_generation,name="pin"),
    path('validate',views.pin_validate,name="validate"),
    path('bal',views.balance,name="bal"),
    path('withdraw',views.withdrawl,name="withdraw"),
    path('deposit',views.deposit,name="deposit"),
    path('transfer',views.acc_transfer,name="transfer"),
    path('transfer_validation',views.transfer_validation,name="transfer_validation"),
    path('delete',views.acc_deletion,name="delete"),
    path('delete_validate',views.delete_validate,name="delete_validate"),
    path('about',views.about,name="about"),
    path('contact',views.contact,name="contact"),
    path('help',views.help,name="help")
]
