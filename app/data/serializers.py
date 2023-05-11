
from rest_framework import serializers
from .models import *

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = '__all__'       

class EventItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event_Item
        fields = '__all__'    

class TransactionItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction_Item
        fields = '__all__'           