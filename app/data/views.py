from django.shortcuts import render
from rest_framework import permissions, status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils.crypto import get_random_string
from django.contrib.auth.hashers import make_password, check_password
import datetime
from dateutil.relativedelta import relativedelta


from .models import *
from .serializers import *
from authentication.serializers import UserSerializer, OrganizationSerializer
from authentication.models import Organization
from django.apps import apps
from .utils import *
from .modules.db import Database
import json
import pandas as pd
import random
import os
import csv
import io

db = Database(
    os.environ.get("SQL_HOST", "localhost"),
    os.environ.get("SQL_USER", "user"),
    os.environ.get("SQL_PASSWORD", "password"),
    os.environ.get("SQL_PORT", "5432"), 
    os.environ.get("SQL_DATABASE", "database"))

# Create your views here.
transform_func = [ 'remain', 'int', 'float', 'string', 'uppercase', 'lowercase', 'timestamp(micros) to datetime', 'timestamp(ms) to datetime', 'timestamp(s) to datetime']

@api_view(['GET'])
def get_list_view(request, item_type):
    try: 
        user_serializer = UserSerializer(request.user)
        org_id = user_serializer.data['org_id']

        import_id = request.GET.get("import_id", None)
        Model = apps.get_model(app_label='data', model_name=item_type)
        model_fields = [f.name for f in Model._meta.get_fields()]
        exclude_fields = ['inf_org_id', 'inf_import_id', 'inf_is_deleted', 'inf_created_at']
        include_fields = get_include_fields(model_fields, exclude_fields)

        query_dict = {}
        query_dict['inf_org_id'] = org_id
        query_dict['inf_is_deleted'] = False
        if (not import_id is None):
          query_dict['inf_import_id'] = import_id

        items = Model.objects.filter(**query_dict).order_by('-inf_created_at').values(*include_fields)
        return Response({
            'status': 200,
            'message': 'Get list data successfully',
            'item_tye': item_type,
            'items': items,
            'isViewDetail': True
        })
    except Exception as error:
        return Response({
            'status': 201,
            'message': error
        })
    
def create_chart(title, data, chart_type, is_change=False):
    return {
        'name': title,
        'title': title,
        'data': data.to_dict('records'),
        'type': chart_type,
        'isChange': is_change,
        'random': title + str(random.randint(0, 1000)),
    }

def get_range(df, column, range, range_labels):
    column_range_name = column + '_range'
    df[column_range_name] = pd.cut(df[column], bins=range, labels=range_labels, right=False).astype(str)

    return df

def get_group_date_field(date_field, group_by):
    if (group_by == 'Day'):
        group_date_field = f'date({date_field})'
    elif (group_by == 'Week'):
        group_date_field = f"date_trunc('week', {date_field})::date"
    else:
        group_date_field = f"to_char({date_field}, 'YYYY-MM')"
    
    return group_date_field

@api_view(['POST'])
def get_reports_analytics(request, item_type):
    try: 
        user_serializer = UserSerializer(request.user)
        org_id = user_serializer.data['org_id']
        body = json.loads(request.body)
        filters = {}
        charts = []

        age_range= [0,20,30,40,50,60,1000]
        groupByOptions = ['Day', 'Week', 'Month']
        isNewOptions = ['Yes']
        ageGroupOptions = ['0-20', '20-30', '30-40', '40-50', '50-60', '>=60']
        genderOptions = db.select_rows('select distinct cus_gender from data_customer')
        locationOptions = db.select_rows('select distinct cus_location from data_customer')
        segmentOptions = ['VIP', 'Gold', 'Silver']
        categoryOptions = db.select_rows("""select distinct a.prod_category from (
                select prod_category_1 as prod_category from data_product
                union    
                select prod_category_2 as prod_category from data_product  
                union 
                select prod_category_3 as prod_category from data_product           
            ) as a""")
        statusOptions = db.select_rows("""select distinct trans_status from data_transaction""")
        osOptions = db.select_rows('select distinct ev_dev_os from data_event')
        deviceCategoryOptions = db.select_rows('select distinct ev_dev_category from data_event')
        browserOptions = db.select_rows('select distinct ev_dev_browser from data_event')
        deviceBrandOptions = db.select_rows('select distinct ev_dev_brand from data_event')
        trafficSourceOptions = db.select_rows('select distinct ev_traffic_source from data_event')
        continentOptions = db.select_rows('select distinct ev_geo_continent from data_event')
        countryOptions = db.select_rows('select distinct ev_geo_country from data_event')
        eventTypeOptions = db.select_rows('select distinct ev_type from data_event')
        deviceLanguageOptions = db.select_rows('select distinct ev_dev_language from data_event')
        
        fromDate = body.get('fromDate', (datetime.datetime.today() - relativedelta(months=1)).strftime('%Y-%m-%d'))
        toDate = body.get('toDate', datetime.datetime.today().strftime('%Y-%m-%d'))
        groupBy = body.get('groupBy', groupByOptions[0])
        isNew = body.get('isNew', 'All')
        segment = body.get('segment', 'All')
        ageGroup = body.get('ageGroup', 'All')
        gender = body.get('gender', 'All')
        location = body.get('location', 'All')
        category = body.get('category', 'All')
        status = body.get('status', 'All')
        os = body.get('os', 'All')
        deviceCategory = body.get('deviceCategory', 'All')
        browser = body.get('browser', 'All')
        deviceBrand = body.get('deviceBrand', 'All')
        trafficSource = body.get('trafficSource', 'All')
        continent = body.get('continent', 'All')
        country = body.get('country', 'All')
        eventType = body.get('eventType', 'All')
        devLanguage = body.get('devLanguage', 'All')

        if (item_type == 'customer'):
            #Create filter menu
            filters = {
                'fromDate': {
                    'id': 'fromDate',
                    'label': 'From Date',
                    'type': 'date',
                    'value': fromDate
                },
                'toDate': {
                    'id': 'toDate',
                    'label': 'To Date',
                    'type': 'date',
                    'value': toDate
                },
                'groupBy': {
                    'id': 'groupBy',
                    'label': 'Group By',
                    'type': 'select',
                    'value': groupBy,
                    'options': groupByOptions,
                    'isAll': False,
                },
                'isNew': {
                    'id': 'isNew',
                    'label': 'Is New',
                    'type': 'select',
                    'value': isNew,
                    'options': isNewOptions
                },
                'segment': {
                    'id': 'segment',
                    'label': 'Segment',
                    'type': 'select',
                    'value': segment,
                    'options': segmentOptions,
                },
                'ageGroup': {
                    'id': 'ageGroup',
                    'label': 'Age Group',
                    'type': 'select',
                    'value': ageGroup,
                    'options': ageGroupOptions
                },
                'gender': {
                    'id': 'gender',
                    'label': 'Gender',
                    'type': 'select',
                    'value': gender,
                    'options': genderOptions
                },
                'location': {
                    'id': 'location',
                    'label': 'Location',
                    'type': 'select',
                    'value': location,
                    'options': locationOptions
                },
            }

            #Select data
            query = f"""
            select a.*, b.*, 
            {get_group_date_field('a.ev_start_time', groupBy)} as report_date, 
            (case when date(a.ev_start_time) = b.cus_account_date then 'Yes' else 'No' end) as is_new,
            'None' as cus_segment, DATE_PART('day', AGE(now(), b.cus_dob)) AS cus_age
            from data_event a 
            left join data_customer b 
            on a.ev_cus_id = b.cus_id 
            where a.inf_org_id = '{org_id}' and b.inf_org_id = '{org_id}'
            and a.inf_is_deleted = FALSE and b.inf_is_deleted = FALSE
            and date(a.ev_start_time) between '{fromDate}' and '{toDate}'"""
            df = db.select_rows_dict(query)
            df = get_range(df, 'cus_age', age_range, ageGroupOptions)

            #Filter data
            if (isNew != 'All'):
                df = df[df['is_new'] == isNew]
            if (segment != 'All'):
                df = df[df['cus_segment'] == segment]
            if (ageGroup!= 'All'):
                df = df[df['cus_age_range'] == ageGroup]
            if (gender != 'All'):
                df = df[df['cus_gender'] == gender]
            if (location != 'All'):
                df = df[df['cus_location'] == location]

            #Aggregate data
            total_pseudo_cus = df.groupby(['report_date'], as_index=False).agg({"ev_peusdo_user": pd.Series.nunique})
            total_cus = df.groupby(['report_date'], as_index=False).agg({"ev_cus_id": pd.Series.nunique})
            total_cus_gender = df.groupby(['report_date', 'cus_gender'], as_index=False).agg({"ev_cus_id": pd.Series.nunique})
            total_cus_location = df.groupby(['report_date', 'cus_location'], as_index=False).agg({"ev_cus_id": pd.Series.nunique})
            total_cus_age_range = df.groupby(['report_date', 'cus_age_range'], as_index=False).agg({"ev_cus_id": pd.Series.nunique})
            total_cus_segment = df.groupby(['report_date', 'cus_segment'], as_index=False).agg({"ev_cus_id": pd.Series.nunique})

            #Create chart
            charts.append(create_chart('Total pseudo customer', total_pseudo_cus, 'line'))
            charts.append(create_chart('Total customer', total_cus, 'line'))
            charts.append(create_chart('Total customer by gender', total_cus_gender, 'column'))
            charts.append(create_chart('Total customer by location', total_cus_location, 'column'))
            charts.append(create_chart('Total customer by age-range', total_cus_age_range, 'column'))
            charts.append(create_chart('Total customer by segment', total_cus_segment, 'column'))

        elif (item_type == 'item'):
            #Create filter menu
            filters = {
                'fromDate': {
                    'id': 'fromDate',
                    'label': 'From Date',
                    'type': 'date',
                    'value': fromDate,
                },
                'toDate': {
                    'id': 'toDate',
                    'label': 'toDate',
                    'type': 'date',
                    'value': toDate
                },
                'groupBy': {
                    'id': 'groupBy',
                    'label': 'Group By',
                    'type': 'select',
                    'value': groupBy,
                    'options': groupByOptions,
                    'isAll': False,
                },
                'isNew': {
                    'id': 'isNew',
                    'label': 'Is New',
                    'type': 'select',
                    'value': isNew,
                    'options': isNewOptions
                },
                'segment': {
                    'id': 'segment',
                    'label': 'Segment',
                    'type': 'select',
                    'value': segment,
                    'options': segmentOptions,
                },
                'ageGroup': {
                    'id': 'age',
                    'label': 'Age Group',
                    'type': 'select',
                    'value': ageGroup,
                    'options': ageGroupOptions
                },
                'gender': {
                    'id': 'gender',
                    'label': 'Gender',
                    'type': 'select',
                    'value': gender,
                    'options': genderOptions
                },
                'location': {
                    'id': 'location',
                    'label': 'Location',
                    'type': 'select',
                    'value': location,
                    'options': locationOptions
                },
                'category': {
                    'id': 'category',
                    'label': 'Category',
                    'type': 'select',
                    'value': category,
                    'options': categoryOptions
                },
            }

            #Query data
            query = f"""
            select a.*, b.*, c.*, d.*, {get_group_date_field('a.trans_time', groupBy)} as report_date, c.ti_quantity*COALESCE(NULLIF(d.prod_price, '')::DECIMAL, 0.00) as revenue,
            (case when date(a.trans_time) = b.cus_account_date then 'Yes' else 'No' end) as is_new,
            'None' as cus_segment , DATE_PART('day', AGE(now(), b.cus_dob)) AS cus_age
            from data_transaction a
            left join data_customer b
            on a.trans_cus_id = b.cus_id
            left join data_transaction_item c
            on a.trans_id = c.trans_id
            left join data_product d
            on c.item_id = d.prod_id
            where date(a.trans_time) between '{fromDate}' and '{toDate}'
            and a.inf_org_id = '{org_id}' and b.inf_org_id = '{org_id}' and c.inf_org_id = '{org_id}' and d.inf_org_id = '{org_id}'
            and a.inf_is_deleted = FALSE and b.inf_is_deleted = FALSE and c.inf_is_deleted = FALSE and d.inf_is_deleted = FALSE
            """
            df = db.select_rows_dict(query)
            df = get_range(df, 'cus_age', age_range, ageGroupOptions)

            #Format data
            df_1 = df.loc[:, ~df.columns.isin(['prod_category_2', 'prod_category_3'])].rename(columns={"prod_category_1": "prod_category"})
            df_2 = df.loc[:, ~df.columns.isin(['prod_category_1', 'prod_category_3'])].rename(columns={"prod_category_2": "prod_category"})
            df_3 = df.loc[:, ~df.columns.isin(['prod_category_2', 'prod_category_1'])].rename(columns={"prod_category_3": "prod_category"})
            df = pd.concat([df_1, df_2, df_3])
            df = df[df.prod_category.notnull()]

            #Filter data
            if (category != 'All'):
                df = df[df['prod_category'] == category]
            if (isNew != 'All'):
                df = df[df['is_new'] == isNew]
            if (segment != 'All'):
                df = df[df['cus_segment'] == segment]
            if (ageGroup!= 'All'):
                df = df[df['cus_age_range'] == ageGroup]
            if (gender != 'All'):
                df = df[df['cus_gender'] == gender]
            if (location != 'All'):
                df = df[df['cus_location'] == location]
            
            #Aggerate data
            total_product_name = df.groupby(['report_date', 'prod_name'], as_index=False)['ti_quantity'].sum()
            rev_product_name = df.groupby(['report_date', 'prod_name'], as_index=False)['revenue'].sum()
            total_product_category = df.groupby(['report_date', 'prod_category'], as_index=False)['ti_quantity'].sum()
            rev_product_category = df.groupby(['report_date', 'prod_category'], as_index=False)['revenue'].sum()

            #Create chart
            charts.append(create_chart('Total quantity by product name', total_product_name, 'column'))
            charts.append(create_chart('Total revenue by product name', rev_product_name, 'column'))
            charts.append(create_chart('Total quantity by product category', total_product_category, 'column'))
            charts.append(create_chart('Total revenue by product category', rev_product_category, 'column'))

        elif (item_type == 'transaction'):
            #Create filter menu
            filters = {
                'fromDate': {
                    'id': 'fromDate',
                    'label': 'From Date',
                    'type': 'date',
                    'value': fromDate,
                },
                'toDate': {
                    'id': 'toDate',
                    'label': 'toDate',
                    'type': 'date',
                    'value': toDate
                },
                'groupBy': {
                    'id': 'groupBy',
                    'label': 'Group By',
                    'type': 'select',
                    'value': groupBy,
                    'options': groupByOptions,
                    'isAll': False,
                },
                'isNew': {
                    'id': 'isNew',
                    'label': 'Is New',
                    'type': 'select',
                    'value': isNew,
                    'options': isNewOptions
                },
                'segment': {
                    'id': 'segment',
                    'label': 'Segment',
                    'type': 'select',
                    'value': segment,
                    'options': segmentOptions,
                },
                'ageGroup': {
                    'id': 'age',
                    'label': 'Age Group',
                    'type': 'select',
                    'value': ageGroup,
                    'options': ageGroupOptions
                },
                'gender': {
                    'id': 'gender',
                    'label': 'Gender',
                    'type': 'select',
                    'value': gender,
                    'options': genderOptions
                },
                'location': {
                    'id': 'location',
                    'label': 'Location',
                    'type': 'select',
                    'value': location,
                    'options': locationOptions
                },
                'category': {
                    'id': 'category',
                    'label': 'Category',
                    'type': 'select',
                    'value': category,
                    'options': categoryOptions
                },
                'status': {
                    'id': 'status',
                    'label': 'Status',
                    'type': 'select',
                    'value': status,
                    'options': statusOptions
                },
            }

            #Query data
            query = f"""
            select a.*, b.*, c.*, d.*, {get_group_date_field('a.trans_time', groupBy)} as report_date, c.ti_quantity*COALESCE(NULLIF(d.prod_price, '')::DECIMAL, 0.00) as revenue,
            (case when date(a.trans_time) = b.cus_account_date then 'Yes' else 'No' end) as is_new,
            'None' as cus_segment , DATE_PART('day', AGE(now(), b.cus_dob)) AS cus_age
            from data_transaction a
            left join data_customer b
            on a.trans_cus_id = b.cus_id
            left join data_transaction_item c
            on a.trans_id = c.trans_id
            left join data_product d
            on c.item_id = d.prod_id
            where date(a.trans_time) between '{fromDate}' and '{toDate}'
            and a.inf_org_id = '{org_id}' and b.inf_org_id = '{org_id}' and c.inf_org_id = '{org_id}' and d.inf_org_id = '{org_id}'
            and a.inf_is_deleted = FALSE and b.inf_is_deleted = FALSE and c.inf_is_deleted = FALSE and d.inf_is_deleted = FALSE
            """
            df = db.select_rows_dict(query)
            df = get_range(df, 'cus_age', age_range, ageGroupOptions)

            #Format data
            df_1 = df.loc[:, ~df.columns.isin(['prod_category_2', 'prod_category_3'])].rename(columns={"prod_category_1": "prod_category"})
            df_2 = df.loc[:, ~df.columns.isin(['prod_category_1', 'prod_category_3'])].rename(columns={"prod_category_2": "prod_category"})
            df_3 = df.loc[:, ~df.columns.isin(['prod_category_2', 'prod_category_1'])].rename(columns={"prod_category_3": "prod_category"})
            df = pd.concat([df_1, df_2, df_3])
            df = df[df.prod_category.notnull()]

            #Filter data
            if (category != 'All'):
                df = df[df['prod_category'] == category]
            if (isNew != 'All'):
                df = df[df['is_new'] == isNew]
            if (segment != 'All'):
                df = df[df['cus_segment'] == segment]
            if (ageGroup!= 'All'):
                df = df[df['cus_age_range'] == ageGroup]
            if (gender != 'All'):
                df = df[df['cus_gender'] == gender]
            if (location != 'All'):
                df = df[df['cus_location'] == location]
            if (status != 'All'):
                df = df[df['trans_status'] == status]

            #Aggregate data
            total_trans = df.groupby(['report_date'], as_index=False).size()
            total_trans_prod_category = df.groupby(['report_date', 'prod_category'], as_index=False).size()
            total_trans_segment = df.groupby(['report_date', 'cus_segment'], as_index=False).size()
            total_trans_age = df.groupby(['report_date', 'cus_age_range'], as_index=False).size()
            total_trans_gender = df.groupby(['report_date', 'cus_gender'], as_index=False).size()
            total_trans_location = df.groupby(['report_date', 'cus_location'], as_index=False).size()
            total_trans_status = df.groupby(['report_date', 'trans_status'], as_index=False).size()
            rev_trans = df.groupby(['report_date'], as_index=False)['trans_revenue_value'].sum()
            tax_trans = df.groupby(['report_date'], as_index=False)['trans_tax_value'].sum()
            refund_trans = df.groupby(['report_date'], as_index=False)['trans_refund_value'].sum()
            ship_trans = df.groupby(['report_date'], as_index=False)['trans_shipping_value'].sum()
            rev_trans_gender = df.groupby(['report_date', 'cus_gender'], as_index=False)['trans_revenue_value'].sum()
            rev_trans_location = df.groupby(['report_date', 'cus_location'], as_index=False)['trans_revenue_value'].sum()
            rev_trans_status = df.groupby(['report_date', 'trans_status'], as_index=False)['trans_revenue_value'].sum()
            rev_trans_prod_category = df.groupby(['report_date', 'prod_category'], as_index=False)['trans_revenue_value'].sum()
            rev_trans_segment = df.groupby(['report_date', 'cus_segment'], as_index=False)['trans_revenue_value'].sum()
            rev_trans_age = df.groupby(['report_date', 'cus_age_range'], as_index=False)['trans_revenue_value'].sum()

            #Create chart
            charts.append(create_chart('Total transaction', total_trans, 'line'))
            charts.append(create_chart('Total transaction by gender', total_trans_gender, 'column'))
            charts.append(create_chart('Total transaction by location', total_trans_location, 'column'))
            charts.append(create_chart('Total transaction by status', total_trans_status, 'column'))
            charts.append(create_chart('Total transaction by age group', total_trans_age, 'column'))
            charts.append(create_chart('Total transaction by segment', total_trans_segment, 'column'))
            charts.append(create_chart('Total transaction by product category', total_trans_prod_category, 'column'))
            charts.append(create_chart('Total revenue', rev_trans, 'line'))
            charts.append(create_chart('Total revenue by gender', rev_trans_gender, 'column'))
            charts.append(create_chart('Total revenue by location', rev_trans_location, 'column'))
            charts.append(create_chart('Total revenue by status', rev_trans_status, 'column'))
            charts.append(create_chart('Total revenue by age group', rev_trans_age, 'column'))
            charts.append(create_chart('Total revenue by segment', rev_trans_segment, 'column'))
            charts.append(create_chart('Total revenue by product category', rev_trans_prod_category, 'column'))
            charts.append(create_chart('Total tax value', tax_trans, 'line'))
            charts.append(create_chart('Total refund value', refund_trans, 'line'))
            charts.append(create_chart('Total shipping value', ship_trans, 'line'))

        elif (item_type == 'event'):
            #Create filter menu
            filters = {
                'fromDate': {
                    'id': 'fromDate',
                    'label': 'From Date',
                    'type': 'date',
                    'value': fromDate
                },
                'toDate': {
                    'id': 'toDate',
                    'label': 'To Date',
                    'type': 'date',
                    'value': toDate
                },
                'groupBy': {
                    'id': 'groupBy',
                    'label': 'Group By',
                    'type': 'select',
                    'value': groupBy,
                    'options': groupByOptions,
                    'isAll': False,
                },
                'isNew': {
                    'id': 'isNew',
                    'label': 'Is New',
                    'type': 'select',
                    'value': isNew,
                    'options': isNewOptions
                },
                'segment': {
                    'id': 'segment',
                    'label': 'Segment',
                    'type': 'select',
                    'value': segment,
                    'options': segmentOptions,
                },
                'ageGroup': {
                    'id': 'age',
                    'label': 'Age Group',
                    'type': 'select',
                    'value': ageGroup,
                    'options': ageGroupOptions
                },
                'gender': {
                    'id': 'gender',
                    'label': 'Gender',
                    'type': 'select',
                    'value': gender,
                    'options': genderOptions
                },
                'type': {
                    'id': 'eventType',
                    'label': 'Event Type',
                    'type': 'select',
                    'value': eventType,
                    'options': eventTypeOptions
                },
                'trafficSource': {
                    'id': 'trafficSource',
                    'label': 'Traffic Source',
                    'type': 'select',
                    'value': trafficSource,
                    'options': trafficSourceOptions
                },
                'device': {
                    'id': 'deviceCategory',
                    'label': 'Device',
                    'type': 'select',
                    'value': deviceCategory,
                    'options': deviceCategoryOptions
                },
                'deviceBrand': {
                    'id': 'deviceBrand',
                    'label': 'Device Brand',
                    'type': 'select',
                    'value': deviceBrand,
                    'options': deviceBrandOptions
                },
                'os': {
                    'id': 'os',
                    'label': 'Operating System',
                    'type': 'select',
                    'value': os,
                    'options': osOptions
                },
                'browser': {
                    'id': 'browser',
                    'label': 'Browser',
                    'type': 'select',
                    'value': browser,
                    'options': browserOptions
                },
                'continent': {
                    'id': 'continent',
                    'label': 'Continent',
                    'type': 'select',
                    'value': continent,
                    'options': continentOptions
                },
                'country': {
                    'id': 'country',
                    'label': 'Country',
                    'type': 'select',
                    'value': country,
                    'options': countryOptions
                },
                'devLanguage': {
                    'id': 'devLanguage',
                    'label': 'Device Language',
                    'type': 'select',
                    'value': devLanguage,
                    'options': deviceLanguageOptions
                },
            }

            #Select data
            query = f"""
            select a.*, b.*, 
            {get_group_date_field('a.ev_start_time', groupBy)} as report_date, 
            (case when date(a.ev_start_time) = b.cus_account_date then 'Yes' else 'No' end) as is_new,
            'None' as cus_segment , DATE_PART('day', AGE(now(), b.cus_dob)) AS cus_age
            from data_event a 
            left join data_customer b 
            on a.ev_cus_id = b.cus_id 
            where a.inf_org_id = '{org_id}' and b.inf_org_id = '{org_id}'
            and a.inf_is_deleted = FALSE and b.inf_is_deleted = FALSE
            and date(a.ev_start_time) between '{fromDate}' and '{toDate}'"""
            df = db.select_rows_dict(query)
            df = get_range(df, 'cus_age', age_range, ageGroupOptions)

            #Filter data
            if (isNew != 'All'):
                df = df[df['is_new'] == isNew]
            if (segment != 'All'):
                df = df[df['cus_segment'] == segment]
            if (ageGroup!= 'All'):
                df = df[df['cus_age_range'] == ageGroup]
            if (gender != 'All'):
                df = df[df['cus_gender'] == gender]
            if (location != 'All'):
                df = df[df['cus_location'] == location]
            if (os != 'All'):
                df = df[df['ev_dev_os'] == os]
            if (deviceCategory != 'All'):
                df = df[df['ev_dev_category'] == deviceCategory]
            if (browser != 'All'):
                df = df[df['ev_dev_browser'] == browser]
            if (deviceBrand != 'All'):
                df = df[df['ev_dev_brand'] == deviceBrand]
            if (trafficSource != 'All'):
                df = df[df['ev_traffic_source'] == trafficSource]
            if (continent != 'All'):
                df = df[df['ev_geo_continent'] == continent]
            if (country != 'All'):
                df = df[df['ev_geo_country'] == country]
            if (eventType != 'All'):
                df = df[df['ev_type'] == eventType]
            if (devLanguage != 'All'):
                df = df[df['ev_dev_language'] == devLanguage]

            #Aggregate data
            total_ev = df.groupby(['report_date'], as_index=False).size()
            total_ev_type = df.groupby(['report_date', 'ev_type'], as_index=False).size()
            total_ev_dev_category = df.groupby(['report_date', 'ev_dev_category'], as_index=False).size()
            total_ev_dev_brand = df.groupby(['report_date', 'ev_dev_brand'], as_index=False).size()
            total_ev_dev_os = df.groupby(['report_date', 'ev_dev_os'], as_index=False).size()
            total_ev_dev_browser = df.groupby(['report_date', 'ev_dev_browser'], as_index=False).size()
            total_ev_dev_language = df.groupby(['report_date', 'ev_dev_language'], as_index=False).size()
            total_ev_geo_continent = df.groupby(['report_date', 'ev_geo_continent'], as_index=False).size()
            total_ev_geo_country = df.groupby(['report_date', 'ev_geo_country'], as_index=False).size()
            total_ev_page_title = df.groupby(['report_date', 'ev_page_title'], as_index=False).size()
            total_ev_page_url = df.groupby(['report_date', 'ev_page_url'], as_index=False).size()
            total_ev_traffic_source = df.groupby(['report_date','ev_traffic_source'], as_index=False).size()
            
            #Create chart
            charts.append(create_chart('Total event', total_ev, 'line'))
            charts.append(create_chart('Total event by event type', total_ev_type, 'column'))
            charts.append(create_chart('Total event by device category', total_ev_dev_category, 'column'))
            charts.append(create_chart('Total event by device brand', total_ev_dev_brand, 'column'))
            charts.append(create_chart('Total event by device operating system', total_ev_dev_os, 'column'))
            charts.append(create_chart('Total event by browser', total_ev_dev_browser, 'column'))
            charts.append(create_chart('Total event by website language', total_ev_dev_language, 'column'))
            charts.append(create_chart('Total event by continent', total_ev_geo_continent, 'column'))
            charts.append(create_chart('Total event by country', total_ev_geo_country, 'column'))
            charts.append(create_chart('Total event by page title', total_ev_page_title, 'column'))
            charts.append(create_chart('Total event by page url', total_ev_page_url, 'column'))
            charts.append(create_chart('Total event by traffic source', total_ev_traffic_source, 'column'))

        return Response({
            'status': 200,
            'message': 'Get reports successfully',
            'filters': filters,
            'charts': charts
        })
    except Exception as error:
        return Response({
            'status': 201,
            'message': error
        })

def create_new_tab(tab_name, data):    
    return {
        "tabName": tab_name,
        "data": data
    }

def create_svg_chart(title, query, cur_date, prev_date, period):
    cur_query = query.replace('$$$', cur_date)
    prev_query = query.replace('$$$', prev_date)
    cur_num = db.select_first_row(cur_query)
    prev_num = db.select_first_row(prev_query)
    percentage = round((cur_num - prev_num)*100/(prev_num+0.000001), 2)

    return {
            'title': title,
            'number': cur_num,
            'period': period,
            'percentage': percentage,
            'type': 'svg'
            }

def create_pie_chart(title, query):
    data = db.select_rows_dict(query).to_dict('records')
    return {
        'title': title,
        'type': 'pie',
        'data': data
    }

def create_table(title, query):
    data = db.select_rows_dict(query).to_dict('records')
    return {
        'title': title,
        'type': 'table',
        'data': data
    }

@api_view(['GET'])
def get_reports_kpi(request):
    try:
        user_serializer = UserSerializer(request.user)
        org_id = user_serializer.data['org_id']
        cur_date = datetime.datetime.today().strftime('%Y-%m-%d')
        prev_date = (datetime.datetime.now() - datetime.timedelta(1)).strftime('%Y-%m-%d')

        #Customer tab
        customer_reports = []

        query = f"""select count(distinct ev_peusdo_user) as num 
                    from data_event where date(ev_start_time) = '$$$' 
                    and inf_org_id='{org_id}' 
                    and inf_is_deleted = FALSE"""
        customer_reports.append(create_svg_chart("Pseudo user", query, cur_date, prev_date, "day"))
        query = f"""select count(distinct cus_id) as num 
                    from data_event a join data_customer b 
                    on a.ev_cus_id = b.cus_id 
                    where date(ev_start_time) = '$$$' 
                    and a.inf_org_id='{org_id}' and a.inf_is_deleted = FALSE
                    and b.inf_org_id='{org_id}' and b.inf_is_deleted = FALSE"""
        customer_reports.append(create_svg_chart("Active customer", query, cur_date, prev_date, "day"))

        query = f"""select count(distinct cus_id) as num 
                    from data_event a join data_customer b 
                    on a.ev_cus_id = b.cus_id 
                    where date(ev_start_time) = '$$$' and b.cus_account_date = '$$$'
                    and a.inf_org_id='{org_id}' and a.inf_is_deleted = FALSE
                    and b.inf_org_id='{org_id}' and b.inf_is_deleted = FALSE"""
        customer_reports.append(create_svg_chart("New customer", query, cur_date, prev_date, "day"))

        query = f"""select b.cus_gender as category, count(distinct cus_id) as value
                    from data_event a join data_customer b 
                    on a.ev_cus_id = b.cus_id 
                    where date(ev_start_time) = '{cur_date}' 
                    and a.inf_org_id='{org_id}' and a.inf_is_deleted = FALSE
                    and b.inf_org_id='{org_id}' and b.inf_is_deleted = FALSE
                    group by b.cus_gender"""
        customer_reports.append(create_pie_chart('Gender', query))

        query = f"""select (
                        case when DATE_PART('day', AGE(now(), b.cus_dob)) < 20 then '0-20'
                        when DATE_PART('day', AGE(now(), b.cus_dob)) < 30 then '20-30'
                        when DATE_PART('day', AGE(now(), b.cus_dob)) < 40 then '30-40'
                        when DATE_PART('day', AGE(now(), b.cus_dob)) < 50 then '40-50'
                        when DATE_PART('day', AGE(now(), b.cus_dob)) < 60 then '50-60'
                        else '>60' end
                    ) as category, count(distinct cus_id) as value
                    from data_event a join data_customer b 
                    on a.ev_cus_id = b.cus_id 
                    where date(ev_start_time) = '{cur_date}' 
                    and a.inf_org_id='{org_id}' and a.inf_is_deleted = FALSE
                    and b.inf_org_id='{org_id}' and b.inf_is_deleted = FALSE
                    group by category"""
        customer_reports.append(create_pie_chart('Age-Group', query))

        query = f"""select ev_geo_continent category, count(distinct cus_id) as value
                    from data_event a join data_customer b 
                    on a.ev_cus_id = b.cus_id 
                    where date(ev_start_time) = '{cur_date}' 
                    and a.inf_org_id='{org_id}' and a.inf_is_deleted = FALSE
                    and b.inf_org_id='{org_id}' and b.inf_is_deleted = FALSE
                    group by category"""
        customer_reports.append(create_pie_chart('Continent', query))

        query = f"""select ev_geo_country category, count(distinct cus_id) as value
                    from data_event a join data_customer b 
                    on a.ev_cus_id = b.cus_id 
                    where date(ev_start_time) = '{cur_date}' 
                    and a.inf_org_id='{org_id}' and a.inf_is_deleted = FALSE
                    and b.inf_org_id='{org_id}' and b.inf_is_deleted = FALSE
                    group by category
                    order by value desc"""
        customer_reports.append(create_table('Top 5 countries', query))

        customer_tab = create_new_tab("Customer", customer_reports)


        #Revenue Tab
        revenue_reports = []
        query = f"""select sum(trans_revenue_value) as num 
                    from data_transaction where date(trans_time) = '$$$' 
                    and inf_org_id='{org_id}' 
                    and inf_is_deleted = FALSE"""
        revenue_reports.append(create_svg_chart("Total Revenue", query, cur_date, prev_date, "day"))

        query = f"""select count(*) as num 
                    from data_transaction where date(trans_time) = '$$$' 
                    and inf_org_id='{org_id}' 
                    and inf_is_deleted = FALSE"""
        revenue_reports.append(create_svg_chart("Num. Transaction", query, cur_date, prev_date, "day"))

        query = f"""select count(distinct trans_peusdo_user) as num 
                    from data_transaction where date(trans_time) = '$$$' 
                    and inf_org_id='{org_id}' 
                    and inf_is_deleted = FALSE"""
        revenue_reports.append(create_svg_chart("Pay pseudo user", query, cur_date, prev_date, "day"))

        query = f"""select count(distinct a.trans_cus_id) as num 
                    from data_transaction a 
                    join data_customer b 
                    on a.trans_cus_id = b.cus_id
                    where date(a.trans_time) = '$$$' 
                    and a.inf_org_id='{org_id}' and a.inf_is_deleted = FALSE
                    and b.inf_org_id='{org_id}' and b.inf_is_deleted = FALSE"""
        revenue_reports.append(create_svg_chart("Pay customer", query, cur_date, prev_date, "day"))

        query = f"""select count(distinct a.trans_cus_id) as num 
                    from data_transaction a 
                    join data_customer b 
                    on a.trans_cus_id = b.cus_id
                    where date(a.trans_time) = '$$$' and b.cus_account_date = '$$$'
                    and a.inf_org_id='{org_id}' and a.inf_is_deleted = FALSE
                    and b.inf_org_id='{org_id}' and b.inf_is_deleted = FALSE"""
        revenue_reports.append(create_svg_chart("Pay new customer", query, cur_date, prev_date, "day"))


        query = f"""select b.cus_gender as category, count(distinct cus_id) as value
                    from data_transaction a join data_customer b 
                    on a.trans_cus_id = b.cus_id 
                    where date(a.trans_time) = '{cur_date}' 
                    and a.inf_org_id='{org_id}' and a.inf_is_deleted = FALSE
                    and b.inf_org_id='{org_id}' and b.inf_is_deleted = FALSE
                    group by b.cus_gender"""
        revenue_reports.append(create_pie_chart('Gender', query))

        query = f"""select (
                        case when DATE_PART('day', AGE(now(), b.cus_dob)) < 20 then '0-20'
                        when DATE_PART('day', AGE(now(), b.cus_dob)) < 30 then '20-30'
                        when DATE_PART('day', AGE(now(), b.cus_dob)) < 40 then '30-40'
                        when DATE_PART('day', AGE(now(), b.cus_dob)) < 50 then '40-50'
                        when DATE_PART('day', AGE(now(), b.cus_dob)) < 60 then '50-60'
                        else '>60' end
                    ) as category, count(distinct cus_id) as value
                    from data_transaction a join data_customer b 
                    on a.trans_cus_id = b.cus_id 
                    where date(a.trans_time) = '{cur_date}' 
                    and a.inf_org_id='{org_id}' and a.inf_is_deleted = FALSE
                    and b.inf_org_id='{org_id}' and b.inf_is_deleted = FALSE
                    group by category"""
        revenue_reports.append(create_pie_chart('Age-Group', query))

        query = f"""select c.prod_category_1 as category, sum(b.ti_quantity*COALESCE(NULLIF(c.prod_price, '')::DECIMAL, 0.00)) as value
                    from data_transaction a 
                    join data_transaction_item b 
                    on a.trans_id = b.trans_id
                    join data_product c
                    on b.item_id = c.prod_id
                    where date(a.trans_time) = '{cur_date}' 
                    and a.inf_org_id='{org_id}' and a.inf_is_deleted = FALSE
                    and b.inf_org_id='{org_id}' and b.inf_is_deleted = FALSE
                    and c.inf_org_id='{org_id}' and c.inf_is_deleted = FALSE
                    group by category"""
        revenue_reports.append(create_pie_chart('Product category', query))

        query = f"""select c.prod_name as category, sum(b.ti_quantity*COALESCE(NULLIF(c.prod_price, '')::DECIMAL, 0.00)) as value
                    from data_transaction a 
                    join data_transaction_item b 
                    on a.trans_id = b.trans_id
                    join data_product c
                    on b.item_id = c.prod_id
                    where date(a.trans_time) = '{cur_date}' 
                    and a.inf_org_id='{org_id}' and a.inf_is_deleted = FALSE
                    and b.inf_org_id='{org_id}' and b.inf_is_deleted = FALSE
                    and c.inf_org_id='{org_id}' and c.inf_is_deleted = FALSE
                    group by category
                    order by value desc"""
        revenue_reports.append(create_table('Top 5 favorite products', query))

        query = f"""select b.cus_location as category, sum(trans_revenue_value) as value
                    from data_transaction a join data_customer b 
                    on a.trans_cus_id = b.cus_id 
                    where date(a.trans_time) = '{cur_date}' 
                    and a.inf_org_id='{org_id}' and a.inf_is_deleted = FALSE
                    and b.inf_org_id='{org_id}' and b.inf_is_deleted = FALSE
                    group by b.cus_location
                    order by value desc"""
        revenue_reports.append(create_table('Top 5 countries', query))

        revenue_tab = create_new_tab("Revenue", revenue_reports)

        #Interaction
        interaction_reports = []
        query = f"""select count(*) as num 
                    from data_event where date(ev_start_time) = '$$$' 
                    and inf_org_id='{org_id}' 
                    and inf_is_deleted = FALSE"""
        interaction_reports.append(create_svg_chart("Total Event", query, cur_date, prev_date, "day"))

        query = f"""select ev_type as category, count(*) as value 
                    from data_event where date(ev_start_time) = '{cur_date}' 
                    and inf_org_id='{org_id}' 
                    and inf_is_deleted = FALSE
                    group by ev_type"""
        interaction_reports.append(create_pie_chart("Event Type", query))

        query = f"""select ev_traffic_source as category, count(*) as value 
                    from data_event where date(ev_start_time) = '{cur_date}' 
                    and inf_org_id='{org_id}' 
                    and inf_is_deleted = FALSE
                    group by ev_traffic_source"""
        interaction_reports.append(create_pie_chart("Traffic Source", query))

        query = f"""select ev_dev_category as category, count(*) as value 
                    from data_event where date(ev_start_time) = '{cur_date}' 
                    and inf_org_id='{org_id}' 
                    and inf_is_deleted = FALSE
                    group by ev_dev_category"""
        interaction_reports.append(create_pie_chart("Device category", query))

        query = f"""select ev_dev_brand as category, count(*) as value 
                    from data_event where date(ev_start_time) = '{cur_date}' 
                    and inf_org_id='{org_id}' 
                    and inf_is_deleted = FALSE
                    group by ev_dev_brand"""
        interaction_reports.append(create_pie_chart("Device brand", query))

        query = f"""select ev_dev_browser as category, count(*) as value 
                    from data_event where date(ev_start_time) = '{cur_date}' 
                    and inf_org_id='{org_id}' 
                    and inf_is_deleted = FALSE
                    group by ev_dev_browser"""
        interaction_reports.append(create_pie_chart("Browser", query))

        query = f"""select ev_dev_os as category, count(*) as value 
                    from data_event where date(ev_start_time) = '{cur_date}' 
                    and inf_org_id='{org_id}' 
                    and inf_is_deleted = FALSE
                    group by ev_dev_os"""
        interaction_reports.append(create_pie_chart("OS", query))

        query = f"""select ev_geo_continent as category, count(*) as value 
                    from data_event where date(ev_start_time) = '{cur_date}' 
                    and inf_org_id='{org_id}' 
                    and inf_is_deleted = FALSE
                    group by ev_geo_continent"""
        interaction_reports.append(create_pie_chart("Continent", query))

        query = f"""select ev_geo_country as category, count(*) as value 
                    from data_event where date(ev_start_time) = '{cur_date}' 
                    and inf_org_id='{org_id}' 
                    and inf_is_deleted = FALSE
                    group by category
                    order by value desc"""
        interaction_reports.append(create_table("Top 5 countries", query))

        query = f"""select ev_dev_brand as category, count(*) as value 
                    from data_event where date(ev_start_time) = '{cur_date}' 
                    and inf_org_id='{org_id}' 
                    and inf_is_deleted = FALSE
                    group by category
                    order by value desc"""
        interaction_reports.append(create_table("Top 5 favorite device brands", query))

        query = f"""select ev_page_url as category, count(*) as value 
                    from data_event where date(ev_start_time) = '{cur_date}' 
                    and inf_org_id='{org_id}' 
                    and inf_is_deleted = FALSE
                    group by category
                    order by value desc"""
        interaction_reports.append(create_table("Top 5 favorite page urls", query))

        query = f"""select ev_page_title as category, count(*) as value 
                    from data_event where date(ev_start_time) = '{cur_date}' 
                    and inf_org_id='{org_id}' 
                    and inf_is_deleted = FALSE
                    group by category
                    order by value desc"""
        interaction_reports.append(create_table("Top 5 favorite page title", query))

        interaction_tab = create_new_tab("Interaction", interaction_reports)

        return Response({
            'status': 200,
            'message': 'Get reports successfully',
            'reports': [interaction_tab, customer_tab, revenue_tab]})
    except Exception as error:
            return Response({
                'status': 201,
                'message': error
            })

@api_view(['GET'])
def get_matching_template(request, item_type):
    try: 
        user_serializer = UserSerializer(request.user)
        org_id = user_serializer.data['org_id']

        model_fields = [f.name for f in Matching_Template._meta.get_fields()]
        exclude_fields = ['inf_org_id', 'inf_import_id', 'inf_is_deleted']
        include_fields = get_include_fields(model_fields, exclude_fields)

        items = Matching_Template.objects.filter(inf_org_id=org_id, inf_is_deleted=False, templ_table=item_type).order_by('-inf_created_at').values(*include_fields)
        return Response({
            'status': 200,
            'message': 'Get list data successfully',
            'item_tye': item_type,
            'items': items,
            'isViewDetail': True
        })
    except Exception as error:
        return Response({
            'status': 201,
            'message': error
        })
    
@api_view(['GET'])
def get_import_history(request, item_type):
    try: 
        user_serializer = UserSerializer(request.user)
        org_id = user_serializer.data['org_id']

        model_fields = [f.name for f in Import_History._meta.get_fields()]
        exclude_fields = ['inf_org_id', 'inf_is_deleted']
        include_fields = get_include_fields(model_fields, exclude_fields)

        items = Import_History.objects.filter(inf_org_id=org_id, inf_is_deleted=False, imp_table=item_type).order_by('-inf_created_at').values(*include_fields)
        return Response({
            'status': 200,
            'message': 'Get list data successfully',
            'item_tye': item_type,
            'items': items,
            'isViewDetail': True
        })
    except Exception as error:
        return Response({
            'status': 201,
            'message': error
        })
    
def get_match_fields(templ_id, org_id):
    match_rows = (Matching_Template_Field
                  .objects
                  .filter(inf_org_id=org_id, inf_is_deleted=False, tf_id=templ_id)
                  .values('tf_column', 'tf_field', 'tf_function'))
    fields = {}
    for match_row in match_rows:
        column_name = match_row['tf_column']
        model_field = match_row['tf_field']
        func = match_row['tf_function']
        fields[column_name] = {
            'modelField': model_field,
            'func': func,
        }
    
    return fields

def get_list_templates(item_type, org_id):
    rows = Matching_Template.objects.filter(inf_org_id=org_id, inf_is_deleted=False, templ_table=item_type).values('id', 'templ_name')
    templates = []
    for row in rows:
        templ_id = row['id']
        templ_name = row['templ_name']
        list_match_fields = get_match_fields(templ_id, org_id)
        templates.append({
            'name': templ_name,
            'listMatchFields': list_match_fields
        })
        
    return templates
   
def get_mandatory_fields(item_type):
    mandatory_fields = []

    if (item_type == 'event'):
        mandatory_fields = ['ev_id', 'ev_type'] 
    elif (item_type == 'transaction'):
        mandatory_fields = ['trans_id', 'trans_cus_id', 'trans_revenue_value', 'trans_time']
    elif (item_type == 'customer'):
        mandatory_fields = ['cus_id']
    elif (item_type == 'item'):
        mandatory_fields = ['item_id']
    elif (item_type == 'product'):
        mandatory_fields = ['prod_id']

    return mandatory_fields

@api_view(['GET'])
def get_import_file_info(request, item_type):
    try: 
        user_serializer = UserSerializer(request.user)
        org_id = user_serializer.data['org_id']

        templates = get_list_templates(item_type, org_id)

        Model = apps.get_model(app_label='data', model_name=item_type)
        model_fields = [f.name for f in Model._meta.get_fields()]
        exclude_fields = ['id', 'inf_org_id', 'inf_import_id', 'inf_is_deleted', 'inf_created_at']
        include_fields = get_include_fields(model_fields, exclude_fields)
        mandatory_fields = get_mandatory_fields(item_type)

        
        if (item_type == 'event'):
            mandatory_fields = ['ev_id', 'ev_type'] 
        elif (item_type == 'transaction'):
            include_fields.append('trans_items')
            mandatory_fields = ['trans_id', 'trans_cus_id', 'trans_revenue_value', 'trans_time']
        elif (item_type == 'customer'):
            mandatory_fields = ['cus_id']
        elif (item_type == 'item'):
            mandatory_fields = ['item_id']
        elif (item_type == 'product'):
            mandatory_fields = ['prod_id']

        return Response({
            'status': 200,
            'message': 'Get import info successfully',
            'item_type': item_type,
            'listFields': include_fields,
            'transFuncs': transform_func,
            'templates': templates,
            'mandatoryFields': mandatory_fields,
            'isViewDetail': True
        })
    except Exception as error:
        return Response({
            'status': 201,
            'message': error
        })
    
@api_view(['GET'])
def get_import_api_info(request, item_type):
    try: 
        user_serializer = UserSerializer(request.user)
        org_id = user_serializer.data['org_id']

        try:
            organization = Organization.objects.get(org_id=org_id)
            org_secret_key = organization.org_secret_key

            Model = apps.get_model(app_label='data', model_name=item_type)
            model_fields = [f.name for f in Model._meta.get_fields()]
            exclude_fields = ['id', 'inf_org_id', 'inf_import_id', 'inf_is_deleted', 'inf_created_at']
            include_fields = get_include_fields(model_fields, exclude_fields)
            mandatory_fields = get_mandatory_fields(item_type)

            example = {}
            for field in include_fields:
                if field in mandatory_fields:
                    example[field] = "field_required"
                else:
                    example[field] = "not_required"
            data_raw = {
                "api_key": org_secret_key,
                "data": [
                    example,
                    example
                ]
            }

            instruction = f"""curl --location --request POST '{os.environ.get('REACT_APP_BE_SERVER')}/data/import-data-api/event' \n--header 'Content-Type: application/json' \n--data-raw '{json.dumps(data_raw, indent=4)}'"""

            return Response({
                'status': 200,
                'instruction': instruction,
                'fields': data_raw
            })

        
        except Exception as error:
            return Response({
                'status': 201,
                'message': error
            })
        
    except Exception as error:
        return Response({
            'status': 201,
            'message': error
        })
    
def get_new_value(value, func):
    try:
        new_value = None
        if (value != ''):
            if (func == 'string'):
                new_value = str(value)
            elif (func == 'int'):
                new_value = int(value)
            elif (func == 'float'):
                new_value = float(value)
            elif (func == 'remain'):
                new_value = value
            elif (func == 'lowercase'):
                new_value = str(value).lower()
            elif (func == 'uppercase'):
                new_value = str(value).upper()
            elif (func == 'timestamp(micros) to datetime'):
                date = datetime.datetime.fromtimestamp(int(value)/1000000)
                new_value = date.strftime("%Y-%m-%d %H:%M:%S")
            elif (func == 'timestamp(ms) to datetime'):
                date = datetime.datetime.fromtimestamp(int(value)/1000)
                new_value = date.strftime("%Y-%m-%d %H:%M:%S")
            elif (func == 'timestamp(s) to datetime'):
                date = datetime.datetime.fromtimestamp(int(value))
                new_value = date.strftime("%Y-%m-%d %H:%M:%S")
            else:
                new_value = value
        return {'status': True, 'value': new_value}
    except Exception as error:
        return {'status': False,'msg': error}

def get_unique_field(item_type):
    field_dict = {
        'event': 'ev_id',
        'customer': 'cus_id',
        'transaction': 'trans_id',
        'item': 'item_id',
        'product': 'prod_id'
    }

    if (item_type in field_dict):
        return field_dict[item_type]
    return ''

def insert_new_row(item_type, values):
    try:
        Model = apps.get_model(app_label='data', model_name=item_type)
        new_obj = Model(**values)
        new_obj.save()
        return {'status': True}
        
    except Exception as error:
        return {'status': False, 'msg': error}
    
def update_row(item_type, query_dict, values):
    try:
        Model = apps.get_model(app_label='data', model_name=item_type)
        Model.objects.filter(**query_dict).update(**values)
        return {'status': True}
        
    except Exception as error:
        return {'status': False, 'msg': error}
        
@api_view(['POST'])
def import_csv_file(request, item_type):
    try: 
        user_serializer = UserSerializer(request.user)
        email = user_serializer.data['email']
        org_id = user_serializer.data['org_id']

        csv_file = request.FILES['csvFile']
        csv_text = io.TextIOWrapper(csv_file)
        csv_reader = csv.DictReader(csv_text)
        data = list(csv_reader)

        columns = json.loads(request.POST.get('columns'))
        matchFields = json.loads(request.POST.get('matchFields'))
        matchFuncs = json.loads(request.POST.get('matchFuncs'))
        is_overwrite = bool(request.POST.get('isOverwrite'))

        unique_field = get_unique_field(item_type)
        total_overwrite = 0
        total_inserted = 0

        errors = []

        imp_obj = Import_History(imp_table=item_type, inf_org_id=org_id, inf_import_by=email)
        imp_obj.save()
        imp_id = imp_obj.id

        for idx, row in enumerate(data):
            values = {}
            for index, column in enumerate(columns):
                column_name = column['Header']
                if len(matchFields) and matchFields[index] != '':
                    model_field = matchFields[index]
                    new_value = row[column_name]
                    if len(matchFuncs) and (matchFuncs[index] != '' or matchFuncs[index] != 'remain'):
                        transform_val = get_new_value(new_value, matchFuncs[index])
                        if (transform_val['status']):
                            new_value = transform_val['value']
                        else:
                            errors.append(f"Error at row {idx}: {transform_val['msg']}")
                            continue

                    values[model_field] = new_value
            if values:
                values['inf_org_id'] = org_id
                values['inf_import_id'] = imp_id
                Model = apps.get_model(app_label='data', model_name=item_type)
                if (is_overwrite and unique_field):
                    query_dict = {}
                    query_dict[unique_field] = values[unique_field]
                    query_dict['inf_org_id'] = org_id
                    query_dict['inf_is_deleted'] = False
                    obj = Model.objects.filter(**query_dict).values()
                    if (len(obj)):
                        updated_row = update_row(item_type, query_dict, values)
                        if (updated_row['status']):
                            total_overwrite += 1
                        else:
                            errors.append(f"Error at row {idx}: {updated_row['msg']}")
                    else:   
                        new_row = insert_new_row(item_type, values)
                        if (new_row['status']):
                            total_inserted += 1
                        else:
                            errors.append(f"Error at row {idx}: {new_row['msg']}")
                else:
                    new_row = insert_new_row(item_type, values)
                    if (new_row['status']):
                        total_inserted += 1
                    else:
                        errors.append(f"Error at row {idx}: {new_row['msg']}")

        Import_History.objects.filter(
                id=imp_id,
                imp_table=item_type, 
                inf_org_id=org_id,
                inf_is_deleted=False,
                inf_import_by=email
            ).update(
                imp_is_overwrite=is_overwrite,
                imp_total_data=len(data),
                imp_total_overwrite=total_overwrite,
                imp_total_inserted=total_inserted,
                imp_total_error=len(errors)
            )    

        return Response({
            'status': 200,
            'message': 'Import successfully',
            'totalData': len(data),
            'totalOverwrite': total_overwrite,
            'totalInsert': total_inserted,
            'totalError': len(errors),
            'errors': errors
        })
    except Exception as error:
        print(error)
        return Response({
            'status': 201,
            'message': error
        })
    
@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def import_data_api(request, item_type):
    try: 
        data = []
        total_overwrite = 0
        total_inserted = 0
        errors = []

        if request.body.decode('utf-8') != '':
            body = json.loads(request.body)
            api_key = body.get('api_key', None)
            data = body.get('data', [])
            is_overwrite = body.get('is_overwrite', True)
            unique_field = get_unique_field(item_type)

            try:
                organization = Organization.objects.get(org_secret_key=api_key)
                org_id = organization.org_id

                imp_obj = Import_History(imp_table=item_type, inf_org_id=org_id, inf_import_by='API')
                imp_obj.save()
                imp_id = imp_obj.id

                for idx, row in enumerate(data):
                    values = row
                    if values:
                        values['inf_org_id'] = org_id
                        values['inf_import_id'] = imp_id
                        Model = apps.get_model(app_label='data', model_name=item_type)
                        if (is_overwrite and unique_field):
                            query_dict = {}
                            query_dict[unique_field] = values[unique_field]
                            query_dict['inf_org_id'] = org_id
                            query_dict['inf_is_deleted'] = False
                            obj = Model.objects.filter(**query_dict).values()
                            if (len(obj)):
                                updated_row = update_row(item_type, query_dict, values)
                                if (updated_row['status']):
                                    total_overwrite += 1
                                else:
                                    errors.append(f"Error at row {idx}: {updated_row['msg']}")
                            else:   
                                new_row = insert_new_row(item_type, values)
                                if (new_row['status']):
                                    total_inserted += 1
                                else:
                                    errors.append(f"Error at row {idx}: {new_row['msg']}")
                        else:
                            new_row = insert_new_row(item_type, values)
                            if (new_row['status']):
                                total_inserted += 1
                            else:
                                errors.append(f"Error at row {idx}: {new_row['msg']}")

                Import_History.objects.filter(
                        id=imp_id,
                        imp_table=item_type, 
                        inf_org_id=org_id,
                        inf_is_deleted=False,
                        inf_import_by='API'
                    ).update(
                        imp_is_overwrite=is_overwrite,
                        imp_total_data=len(data),
                        imp_total_overwrite=total_overwrite,
                        imp_total_inserted=total_inserted,
                        imp_total_error=len(errors)
                    )  

                return Response({
                    'status': 200,
                    'message': 'Import successfully',
                    'totalData': len(data),
                    'totalOverwrite': total_overwrite,
                    'totalInsert': total_inserted,
                    'totalError': len(errors),
                    'errors': errors
                })  

            except Organization.DoesNotExist:
                return Response({
                    'status': 201,
                    'message': 'Wrong API Key',
                })
            except Exception as error:
                return Response({
                    'status': 201,
                    'message': error,
                })
    
        else:
            return Response({
                'status': 201,
                'message': 'There is no data in request body',
            })
            
    except Exception as error:
        return Response({
            'status': 201,
            'message': error
        })
    
@api_view(['POST'])
def import_matching_template(request, item_type):
    try: 
        body = json.loads(request.body)
        template_name = body['templateName']
        list_fields = body['listFields']
        list_match_fields = body['matchFields']
        list_match_funcs = body['matchFuncs']

        user_serializer = UserSerializer(request.user)
        email = user_serializer.data['email']
        org_id = user_serializer.data['org_id']

        matching_template = Matching_Template(templ_name=template_name, 
                                        templ_table=item_type,
                                        inf_org_id=org_id)
        matching_template.save()
        templ_id = matching_template.id

        for (idx, field) in enumerate(list_fields):
            match_field = list_match_fields[idx]
            if (len(list_match_funcs)):
                match_func = list_match_funcs[idx]
            else:
                match_func = 'remain'

            template_field = Matching_Template_Field(tf_column=match_field,
                                    tf_field=field,
                                    tf_function=match_func,
                                    tf_id=templ_id,
                                    tf_order=idx,
                                    inf_org_id=org_id)
            template_field.save()

        return Response({
            'status': 200,
            'message': 'Import info successfully',
        })
    except Exception as error:
        return Response({
            'status': 201,
            'message': error
        })   

@api_view(['POST'])
def update_matching_template(request, item_type, templ_id):
    try: 
        body = json.loads(request.body)
        template_name = body['templateName']
        list_fields = body['listFields']
        list_match_fields = body['matchFields']
        list_match_funcs = body['matchFuncs']

        user_serializer = UserSerializer(request.user)
        org_id = user_serializer.data['org_id']

        Matching_Template.objects.filter(id=templ_id, 
                                        templ_table=item_type,
                                        inf_org_id=org_id, inf_is_deleted=False).update(templ_name=template_name)

        for (idx, field) in enumerate(list_fields):
            match_field = list_match_fields[idx]
            if (len(list_match_funcs)):
                match_func = list_match_funcs[idx]
            else:
                match_func = 'remain'

            Matching_Template_Field.objects.filter(
                                    tf_field=field,
                                    tf_id=templ_id,
                                    inf_org_id=org_id, inf_is_deleted=False).update(tf_column=match_field,
                                    tf_function=match_func)

        return Response({
            'status': 200,
            'message': 'Update info successfully',
        })
    except Exception as error:
        return Response({
            'status': 201,
            'message': error
        })   

@api_view(['GET'])
def get_detail_template(request, item_type, templ_id):
    try: 
        user_serializer = UserSerializer(request.user)
        org_id = user_serializer.data['org_id']

        matching_templates = Matching_Template.objects.filter(
                                        templ_table=item_type,
                                        inf_org_id=org_id, id=templ_id, inf_is_deleted=False).values()
        
        if len(matching_templates):
            matching_template = matching_templates[0]
            templ_name = matching_template['templ_name']

            matching_fields = Matching_Template_Field.objects.filter(
                                        tf_id=templ_id,
                                        inf_org_id=org_id, inf_is_deleted=False).order_by('tf_order').values()
            list_fields = [row['tf_field'] for row in matching_fields]
            list_match_fields = [row['tf_column'] for row in matching_fields]
            list_match_functions = [row['tf_function'] for row in matching_fields]
            list_mandatory_fields = get_mandatory_fields(item_type)

            return Response({
                'status': 200,
                'message': 'Get template successfully',
                'templateName': templ_name,
                'listTransFuncs' : transform_func,
                'listMandatoryFields': list_mandatory_fields,
                'listFields': list_fields,
                'listMatchFields': list_match_fields,
                'listMatchFuncs': list_match_functions,
            })
        else:
            return Response({
                'status': 201,
                'message': 'Get template unsuccessfully',
            })
    except Exception as error:
        return Response({
            'status': 201,
            'message': error
        })   

@api_view(['DELETE'])
def delete_item(request, item_type, item_id):
    try:
        user_serializer = UserSerializer(request.user)
        org_id = user_serializer.data['org_id']

        Model = apps.get_model(app_label='data', model_name=item_type)
        Model.objects.filter(id=item_id, inf_org_id=org_id).update(inf_is_deleted=True)
        return Response({
            'status': 200,
            'message': 'Delete successfully',
        })
        
    except Exception as error:
        return Response({
            'status': 201,
            'message': error,
        })
    
@api_view(['DELETE'])
def delete_import_log(request, import_id):
    try:
        user_serializer = UserSerializer(request.user)
        org_id = user_serializer.data['org_id']

        rows = Import_History.objects.filter(id=import_id, inf_org_id=org_id, inf_is_deleted=False).values()
        for row in rows:
            item_type = row['imp_table']
            Model = apps.get_model(app_label='data', model_name=item_type)
            Model.objects.filter(inf_import_id=import_id, inf_org_id=org_id).update(inf_is_deleted=True)

        Import_History.objects.filter(id=import_id, inf_org_id=org_id, inf_is_deleted=False).update(inf_is_deleted=True)
        return Response({
            'status': 200,
            'message': 'Delete successfully',
        })
        
    except Exception as error:
        return Response({
            'status': 201,
            'message': error,
        })
    