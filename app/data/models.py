from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import UserManager


# Create your models here.
class Customer(models.Model):
    id = models.AutoField(primary_key=True)
    cus_id = models.TextField(default='', blank=True, null=True)
    cus_first_name = models.TextField(default='', blank=True, null=True)
    cus_last_name = models.TextField(default='', blank=True, null=True)
    cus_email = models.TextField(default='', blank=True, null=True)
    cus_dob = models.DateField(default=timezone.now)
    cus_phone_num = models.TextField(default='', blank=True, null=True)
    cus_gender = models.TextField(default='', blank=True, null=True)
    cus_job_title = models.TextField(default='', blank=True, null=True)
    cus_location = models.TextField()
    cus_account_date = models.DateField(default=timezone.now)
    #OtherInfo
    inf_org_id = models.TextField(default='', blank=True, null=True)
    inf_import_id = models.TextField(default='', blank=True, null=True)
    inf_is_deleted = models.BooleanField(default=False)
    inf_created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.id


# Create your models here.
class Event(models.Model):
    id = models.AutoField(primary_key=True)
    ev_id = models.TextField(default='', blank=True, null=True)
    ev_type = models.TextField(default='', blank=True, null=True)
    ev_cus_id = models.TextField(default='', blank=True, null=True)
    ev_touchpoint_type = models.TextField(default='', blank=True, null=True)
    ev_peusdo_user = models.TextField(default='', blank=True, null=True)
    #Behavior
    ev_dev_category = models.TextField(default='', blank=True, null=True)
    ev_dev_brand = models.TextField(default='', blank=True, null=True)
    ev_dev_os = models.TextField(default='', blank=True, null=True)
    ev_dev_browser = models.TextField(default='', blank=True, null=True)
    ev_dev_language = models.TextField(default='', blank=True, null=True)
    ev_geo_continent = models.TextField(default='', blank=True, null=True)
    ev_geo_sub_continent = models.TextField(default='', blank=True, null=True)
    ev_geo_country = models.TextField(default='', blank=True, null=True)
    ev_geo_city = models.TextField(default='', blank=True, null=True)
    ev_session_id = models.TextField(default='', blank=True, null=True)
    ev_page_title = models.TextField(default='', blank=True, null=True)
    ev_page_url = models.TextField(default='', blank=True, null=True)
    ev_traffic_source = models.TextField(default='', blank=True, null=True)
    ev_ip_address = models.TextField(default='', blank=True, null=True)
    ev_keyword = models.TextField(default='', blank=True, null=True)
    ev_start_time = models.DateTimeField(default=timezone.now)
    ev_end_time = models.DateTimeField(default=timezone.now)
    #Feedback
    ev_is_like = models.TextField(default='', blank=True, null=True)
    ev_rate = models.FloatField(default=0, blank=True, null=True)
    ev_review = models.TextField()
    #OtherInfo
    inf_org_id = models.TextField(default='', blank=True, null=True)
    inf_import_id = models.TextField(default='', blank=True, null=True)
    inf_is_deleted = models.BooleanField(default=False)
    inf_created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.id
    
# Create your models here.
class Transaction(models.Model):
    id = models.AutoField(primary_key=True)
    trans_id = models.TextField(default='', blank=True, null=True)
    trans_cus_id = models.TextField(default='', blank=True, null=True)
    trans_peusdo_user = models.TextField(default='', blank=True, null=True)
    trans_revenue_value = models.FloatField(default=0, blank=True, null=True)
    trans_tax_value = models.FloatField(default=0, blank=True, null=True)
    trans_refund_value = models.FloatField(default=0, blank=True, null=True) 
    trans_shipping_value = models.FloatField(default=0, blank=True, null=True)
    trans_shipping_type = models.TextField(default='', blank=True, null=True)
    trans_shipping_address = models.TextField(default='', blank=True, null=True)
    trans_status = models.TextField(default='', blank=True, null=True)
    trans_time = models.DateTimeField(default=timezone.now)
    #OtherInfo
    inf_org_id = models.TextField(default='', blank=True, null=True)
    inf_import_id = models.TextField(default='', blank=True, null=True)
    inf_is_deleted = models.BooleanField(default=False)
    inf_created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.id
    
# Create your models here.
class Item(models.Model):
    id = models.AutoField(primary_key=True)
    item_id = models.TextField(default='', blank=True, null=True)
    item_name = models.TextField(default='', blank=True, null=True)
    item_url = models.TextField(default='', blank=True, null=True)
    item_description = models.TextField()
    item_category_1 = models.TextField(default='', blank=True, null=True)
    item_category_2 = models.TextField(default='', blank=True, null=True)
    item_category_3 = models.TextField(default='', blank=True, null=True)
    item_extra_value_1 = models.TextField(default='', blank=True, null=True)
    item_extra_value_2 = models.TextField(default='', blank=True, null=True)
    item_extra_value_3 = models.TextField(default='', blank=True, null=True)
    item_extra_value_4 = models.TextField(default='', blank=True, null=True)
    #OtherInfo
    inf_org_id = models.TextField(default='', blank=True, null=True)
    inf_import_id = models.TextField(default='', blank=True, null=True)
    inf_is_deleted = models.BooleanField(default=False)
    inf_created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.id
    
# Create your models here.
class Product(models.Model):
    id = models.AutoField(primary_key=True)
    prod_id = models.TextField(default='', blank=True, null=True)
    prod_name = models.TextField(default='', blank=True, null=True)
    prod_url = models.TextField(default='', blank=True, null=True)
    prod_description = models.TextField()
    prod_category_1 = models.TextField(default='', blank=True, null=True)
    prod_category_2 = models.TextField(default='', blank=True, null=True)
    prod_category_3 = models.TextField(default='', blank=True, null=True)
    prod_quantity = models.IntegerField(default=0, blank=True, null=True)
    prod_price = models.TextField(default='', blank=True, null=True)
    prod_from_date = models.DateTimeField(default=timezone.now)
    prod_to_date = models.DateTimeField(default=timezone.now)
    #OtherInfo
    inf_org_id = models.TextField(default='', blank=True, null=True)
    inf_import_id = models.TextField(default='', blank=True, null=True)
    inf_is_deleted = models.BooleanField(default=False)
    inf_created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.id
    
# Create your models here.
class Event_Item(models.Model):
    id = models.AutoField(primary_key=True)
    event_id = models.TextField(default='', blank=True, null=True)
    item_id = models.TextField(default='', blank=True, null=True)
    evi_description = models.TextField(default='', blank=True, null=True)
    evi_extra_value_1 = models.TextField(default='', blank=True, null=True)
    evi_extra_value_2 = models.TextField(default='', blank=True, null=True)
    evi_extra_value_3 = models.TextField(default='', blank=True, null=True)
    #OtherInfo
    inf_org_id = models.TextField(default='', blank=True, null=True)
    inf_import_id = models.TextField(default='', blank=True, null=True)
    inf_is_deleted = models.BooleanField(default=False)
    inf_created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.id
    
# Create your models here.
class Transaction_Item(models.Model):
    id = models.AutoField(primary_key=True)
    trans_id = models.TextField(default='', blank=True, null=True)
    item_id = models.TextField(default='', blank=True, null=True)
    ti_quantity = models.IntegerField(default=0, blank=True, null=True)
    ti_description = models.TextField(default='', blank=True, null=True)
    ti_extra_value_1 = models.TextField(default='', blank=True, null=True)
    ti_extra_value_2 = models.TextField(default='', blank=True, null=True)
    ti_extra_value_3 = models.TextField(default='', blank=True, null=True)
    #OtherInfo
    inf_org_id = models.TextField(default='', blank=True, null=True)
    inf_import_id = models.TextField(default='', blank=True, null=True)
    inf_is_deleted = models.BooleanField(default=False)
    inf_created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.id
    
# Create your models here.
class Matching_Template(models.Model):
    id = models.AutoField(primary_key=True)
    templ_table = models.TextField(default='', blank=True, null=True)
    templ_name = models.TextField(default='', blank=True, null=True)
    #OtherInfo
    inf_org_id = models.TextField(default='', blank=True, null=True)
    inf_import_id = models.TextField(default='', blank=True, null=True)
    inf_is_deleted = models.BooleanField(default=False)
    inf_created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.id
    
# Create your models here.
class Matching_Template_Field(models.Model):
    id = models.AutoField(primary_key=True)
    tf_id = models.TextField(default='', blank=True, null=True)
    tf_column = models.TextField(default='', blank=True, null=True)
    tf_field = models.TextField(default='', blank=True, null=True)
    tf_function = models.TextField(default='', blank=True, null=True)
    tf_order = models.IntegerField(default=0, blank=True, null=True)
    #OtherInfo
    inf_org_id = models.TextField(default='', blank=True, null=True)
    inf_import_id = models.TextField(default='', blank=True, null=True)
    inf_is_deleted = models.BooleanField(default=False)
    inf_created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.id
    

# Create your models here.
class Import_History(models.Model):
    id = models.AutoField(primary_key=True)
    imp_table = models.TextField(default='', blank=True, null=True)
    imp_is_overwrite = models.IntegerField(default=0, blank=True, null=True)
    imp_total_data = models.IntegerField(default=0, blank=True, null=True)
    imp_total_overwrite = models.IntegerField(default=0, blank=True, null=True)
    imp_total_inserted = models.IntegerField(default=0, blank=True, null=True)
    imp_total_error = models.IntegerField(default=0, blank=True, null=True)
    #OtherInfo
    inf_import_by = models.TextField(default='', blank=True, null=True)
    inf_org_id = models.TextField(default='', blank=True, null=True)
    inf_is_deleted = models.BooleanField(default=False)
    inf_created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.id