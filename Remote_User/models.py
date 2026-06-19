from django.db import models

# Create your models here.
from django.db.models import CASCADE


class ClientRegister_Model(models.Model):
    username = models.CharField(max_length=30)
    email = models.EmailField(max_length=30)
    password = models.CharField(max_length=10)
    phoneno = models.CharField(max_length=10)
    country = models.CharField(max_length=30)
    state = models.CharField(max_length=30)
    city = models.CharField(max_length=30)
    address= models.CharField(max_length=300, default='')
    gender= models.CharField(max_length=30, default='')


class predict_ev_energy_consumption(models.Model):

    Fid= models.CharField(max_length=300)
    Vehicle_Model= models.CharField(max_length=300)
    Battery_Capacity_kWh= models.CharField(max_length=300)
    Charging_Station_ID= models.CharField(max_length=300)
    Charging_Station_Location= models.CharField(max_length=300)
    Charging_Start_Time= models.CharField(max_length=300)
    Charging_EndTime= models.CharField(max_length=300)
    Energy_Consumed_kWh= models.CharField(max_length=300)
    Charging_Duration_hours= models.CharField(max_length=300)
    Charging_Rate_kW= models.CharField(max_length=300)
    Charging_Cost_USD= models.CharField(max_length=300)
    Vehicle_Age_years= models.CharField(max_length=300)
    Charger_Type= models.CharField(max_length=300)
    User_Type= models.CharField(max_length=300)
    Prediction= models.CharField(max_length=3000)

class detection_accuracy(models.Model):

    names = models.CharField(max_length=300)
    ratio = models.CharField(max_length=300)

class detection_ratio(models.Model):

    names = models.CharField(max_length=300)
    ratio = models.CharField(max_length=300)



