from django.shortcuts import render
from rest_framework import permissions, status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from django.utils.crypto import get_random_string
from django.contrib.auth.hashers import make_password, check_password
from authentication.serializers import UserSerializer

from .models import *
from data.models import *
from authentication.models import *
from .utils import *
from django.apps import apps
from data.modules.db import Database
from data.modules.mongo_db import MongoDB
import json
import datetime

from bson.objectid import ObjectId
import os
import joblib
import pymongo
from datetime import datetime, timedelta
from itertools import combinations
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import MinMaxScaler


import numpy as np
import pandas as pd

# Customer segmentation
from .ml_functions.customer_segmentation import CustomerSegmentation;
from .ml_functions.product_recommendation import ProductRecommendation;
from .ml_functions.association_rule import AssociationRule;
from .ml_functions.correlation import Correlation;

# Recommendation
from sklearn.model_selection import train_test_split
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer

# Association rules
from mlxtend.frequent_patterns import apriori
from mlxtend.frequent_patterns import association_rules

import matplotlib

#Correlation
# import matplotlib.pyplot as plt

db = Database(
    os.environ.get("SQL_HOST", "localhost"),
    os.environ.get("SQL_USER", "user"),
    os.environ.get("SQL_PASSWORD", "password"),
    os.environ.get("SQL_PORT", "5432"), 
    os.environ.get("SQL_DATABASE", "database"))

mongo_db = MongoDB(
    os.environ.get("MONGO_HOST", "localhost"),
    os.environ.get("MONGO_PORT", "27017"), 
    os.environ.get("MONGO_USER", "user"),
    os.environ.get("MONGO_PASSWORD", "password"),
    os.environ.get("MONGO_DB", "model"))

recommendation_algorithms = {
    "1": 'Content-based',
    "2": 'Item-item collaborative filtering',
    "3": 'User-user collaborative filtering'
}          

correlation_dimensions = [
        {
            "id": 'prod_price',
            "label": 'Product price',
        }, 
        {
            "id": 'cus_age',
            "label": 'Customer age'
        }, 
        {
            "id": 'cus_account_age',
            "label": 'Customer account age'
        }, 
        {
            "id": 'trans_time',
            "label": 'Transaction time'
        }, 
        {
            "id": 'total_revenue',
            "label": 'Transaction revenue'
        }]

@api_view(['GET'])
def get_model_config(request, model_type):
    config = []
    end_date = datetime.today().strftime('%Y-%m-%d')
    start_date = (datetime.strptime(end_date, '%Y-%m-%d') - timedelta(days=365)).strftime('%Y-%m-%d')

    if (model_type == 'customer-segmentation'):
        fields = ['cus_gender', 'cus_location', 'cus_age', 'cus_account_age', 'cus_revenue']
        config = [
            {
                'id': 'model_name',
                'label': 'Model name',
                'type': 'text',
                'value': ''
            },
            {
                'id': 'num_clusters',
                'label': 'Number of clusters',
                'type': 'integer',
                'value': 3
            }, {
                'id': 'start_date',
                'label': 'Data from',
                'type': 'date',
                'value': start_date
            }, {
                'id': 'end_date',
                'label': 'Data to',
                'type': 'date',
                'value': end_date
            }, {
                'id': 'columns',
                'label': 'Fields used to segment',
                'type': 'multi-select',
                'options': fields,
                'value': []
            }
        ]

    elif (model_type == 'product-recommendation'):
        algorithms = [{"id": key, "label": recommendation_algorithms[key]} for key in recommendation_algorithms.keys()]
        fields = ['total_revenue', 'purchase_frequency', 'total_quantity']
        config = [
            {
                'id': 'algorithm',
                'label': 'Algorithm',
                'type': 'select',
                'options': algorithms,
                'value': algorithms[0]['id']
            },
            {
                'id': 'similarity_score',
                'label': 'Min similarity score',
                'type': 'float',
                'value': 0.3
            },
            {
                'id': 'threshold',
                'label': 'Recommended threshold',
                'type': 'float',
                'value': 0.5
            },
            {
                'id': 'numbers',
                'label': 'Number of recommended products',
                'type': 'integer',
                'value': 5
            }, {
                'id': 'start_date',
                'label': 'Data from',
                'type': 'date',
                'value': start_date
            }, {
                'id': 'end_date',
                'label': 'Data to',
                'type': 'date',
                'value': end_date
            }, {
                'id': 'fields',
                'label': 'Fields used to run algorithm',
                'type': 'select',
                'options': fields,
                'value': fields[0]
            }, 
            {
                'id': 'model_name',
                'label': 'Model name',
                'type': 'text',
                'value': ''
            },
        ]
    
    elif (model_type == 'association-rule'):
        config = [
            {
                'id': 'min_support',
                'label': 'Min support',
                'type': 'float',
                'value': 0.01
            },
            {
                'id': 'threshold',
                'label': 'Confidence threshold',
                'type': 'float',
                'value': 0.9
            }, {
                'id': 'start_date',
                'label': 'Data from',
                'type': 'date',
                'value': start_date
            }, {
                'id': 'end_date',
                'label': 'Data to',
                'type': 'date',
                'value': end_date
            },
            {
                'id': 'model_name',
                'label': 'Model name',
                'type': 'text',
                'value': ''
            },
        ]

    elif (model_type == 'correlation'):
        config = [
            {
                'id': 'start_date',
                'label': 'Data from',
                'type': 'date',
                'value': start_date
            }, {
                'id': 'end_date',
                'label': 'Data to',
                'type': 'date',
                'value': end_date
            },
            {
                'id': 'model_name',
                'label': 'Model name',
                'type': 'text',
                'value': ''
            },
            {
                'id': 'dimension',
                'label': 'Dimension',
                'type': 'multi-select',
                'options': correlation_dimensions,
                'value': []
            },
        ]
        
    return Response({
        'status': 200,
        'config': config
    })

@api_view(['GET'])
def get_list_models(request, model_type):
    try: 
        user_serializer = UserSerializer(request.user)
        org_id = user_serializer.data['org_id']
        rows =  mongo_db.find(model_type, {'org_id': int(org_id), 'is_deleted': False}).sort("run_at", pymongo.DESCENDING)
        rows = list(rows)
        new_rows = []
        excluded_fields = []
        key_order = []

        if model_type == 'customer-segmentation':
            excluded_fields = ['_id', 'org_id', 'is_deleted', 'model_path', 'clusters', 'img_path']
            key_order = ['id', 'model_name', 'num_clusters', 'fields', 'start_date', 'end_date', 'run_at', 'api']
            for row in rows:
                row['fields'] = list_to_string(row['fields'])

        elif model_type == 'product-recommendation':
            excluded_fields = ['_id', 'org_id', 'is_deleted', 'model_path']
            key_order = ['id', 'model_name', 'algorithm', 'fields', 'threshold', 'numbers', 'start_date', 'end_date', 'run_at', 'api']
            for row in rows:
                if type(row['fields']) == list:
                    row['fields'] = list_to_string(row['fields'])
                algorithm_id = str(row['algorithm'])
                if algorithm_id in list(recommendation_algorithms.keys()):
                    row['algorithm'] = recommendation_algorithms[algorithm_id]
                else:
                    row['algorithm'] = 'Not existed'

        elif model_type == 'association-rule':
            excluded_fields = ['_id', 'org_id', 'is_deleted', 'model_path']
            key_order = ['id', 'model_name', 'min_support', 'threshold', 'total_itemsets', 'start_date', 'end_date', 'run_at', 'api']

        elif model_type == 'correlation':
            excluded_fields = ['_id', 'org_id', 'is_deleted', 'model_path']
            key_order = ['id', 'model_name', 'dimension', 'correlation-coefficient', 'start_date', 'end_date', 'run_at']
            for row in rows:
                if type(row['dimension']) == list:
                    row['dimension'] = list_to_string(row['dimension'])

        for row in rows:
            row['id'] = str(row['_id'])
            new_row = { k: v for k, v in row.items() if k not in excluded_fields}
            new_row = {key: new_row[key] for key in key_order if key in new_row}
            new_rows.append(new_row)

        return Response({
            'status': 200,
            'items': new_rows,
            'isViewDetail': True
        })
    except Exception as error:
            return Response({
                'status': 201,
                'message': 'Run model failed'
            })

@api_view(['GET'])
def get_model_info(request, model_type, model_id):
    user_serializer = UserSerializer(request.user)
    org_id = user_serializer.data['org_id']
    doc_id = ObjectId(model_id)
    row =  mongo_db.find_one(model_type, { 'org_id': int(org_id), 'is_deleted': False, '_id': doc_id})
    excluded_fields = ['_id', 'org_id', 'is_deleted', 'model_path']
    row['id'] = str(row['_id'])

    if (model_type == 'customer-segmentation'):
        if type(row['fields']) == list:
            row['fields'] = list_to_string(row['fields'])
    elif (model_type == 'product-recommendation'):
        if type(row['fields']) == list:
            row['fields'] = list_to_string(row['fields'])

        algorithm_id = str(row['algorithm'])
        if algorithm_id in list(recommendation_algorithms.keys()):
            row['algorithm'] = recommendation_algorithms[algorithm_id]
        else:
            row['algorithm'] = 'Not existed'
    elif (model_type == 'correlation'):
        excluded_fields.extend(['correlation_coefficient', 'dimensions'])
        corr_df = pd.DataFrame(columns=row['dimensions'], index=row['dimensions'])
        for key in row['correlation_coefficient']:
            column = row['correlation_coefficient'][key]
            corr_df[key] = column.values()
        row['corr_coefficient'] = {
            'title': 'Correlation - coefficient',
            'data': corr_df.reset_index().to_dict('records')
        }
    
    new_row = { k: v for k, v in row.items() if k not in excluded_fields}
    return Response({
        'status': 200,
        'info': new_row
    })

@api_view(['GET'])
def get_api_info(request, model_type, model_id):
    user_serializer = UserSerializer(request.user)
    org_id = user_serializer.data['org_id']
    doc_id = ObjectId(model_id)
    row =  mongo_db.find_one(model_type, { 'org_id': int(org_id), 'is_deleted': False, '_id': doc_id})
    api = ''
    item_label = ''

    if 'api' in row.keys():
        api = row['api']

    if model_type == 'customer-segmentation':
        item_label = 'Customer ID'
    elif model_type == 'product-recommendation':
        item_label = 'Customer ID'
    elif model_type == 'association-rule':
        item_label = 'Product ID'

    return Response({
        'status': 200,
        'api': api,
        'item_label': item_label
    })

@api_view(['POST'])
def update_model_info(request, model_type, model_id):
    user_serializer = UserSerializer(request.user)
    org_id = user_serializer.data['org_id']
    doc_id = ObjectId(model_id)
    data = json.loads(request.body)

    if (model_type == 'customer-segmentation'):
        row =  mongo_db.update(model_type, { '_id': doc_id }, {
            'model_name': data['name'],
            'clusters': data['clusters']
        })
    elif (model_type == 'product-recommendation'):
        row =  mongo_db.update(model_type, { '_id': doc_id }, {
            'model_name': data['name']
        })
    elif (model_type == 'association-rule'):
        row =  mongo_db.update(model_type, { '_id': doc_id }, {
            'model_name': data['name']
        })

    return Response({
        'status': 200,
        'message': 'Update successfully'
    })

@api_view(['DELETE'])
def delete_model(request, model_type, model_id):
    user_serializer = UserSerializer(request.user)
    org_id = user_serializer.data['org_id']
    doc_id = ObjectId(model_id)
    row =  mongo_db.update(model_type, { '_id': doc_id, 'org_id': int(org_id) }, {'is_deleted': True})

    return Response({
        'status': 200,
        'message': 'Delete successfully'
    })

@api_view(['POST'])
def run_model(request, model_type):
    result = {
            'status': 201,
            'message': 'Run model not found'
    }

    if model_type == 'customer-segmentation':
        result = run_segmentation(request)
    elif model_type == 'product-recommendation':
        result = run_recommendation(request)
    elif model_type == 'association-rule':
        result = run_association_rule(request)
    elif model_type == 'correlation':
        result = run_correlation(request)
    
    return Response(result)

@api_view(['GET'])
def get_test_model_api(request, model_type, model_id, item_id):
    try:
        user_serializer = UserSerializer(request.user)
        org_id = user_serializer.data['org_id']

        result = {
            'status': 201,
            'message': 'Get results failed'
        }
        
        if (model_type == 'customer-segmentation'):
            model = CustomerSegmentation(db, mongo_db)
            result = model.get_customer_segment_info(item_id, org_id, model_id)
        elif (model_type == 'product-recommendation'):
            model = ProductRecommendation(db, mongo_db)
            result = model.get_recommended_products(model_id, item_id, org_id)
        elif (model_type == 'association-rule'):
            model = AssociationRule(db, mongo_db)
            result = model.get_association_rule(model_id, item_id, org_id)

        return Response(result)
    except Exception as error:
        return Response({
            'status': 201,
            'message': 'Get results failed'
        })

@api_view(['GET'])
@authentication_classes([])
@permission_classes([])
def get_info_api(request, model_type, model_id, item_id):
    try: 
        if request.body.decode('utf-8') != '':
            body = json.loads(request.body)
            api_key = body.get('api_key', None)

            try:
                organization = Organization.objects.get(org_secret_key=api_key)
                org_id = organization.org_id

                result = {
                    'status': 201,
                    'message': 'Get results failed'
                }
                
                if (model_type == 'customer-segmentation'):
                    model = CustomerSegmentation(db, mongo_db)
                    result = model.get_customer_segment_info(item_id, org_id, model_id)
                elif (model_type == 'product-recommendation'):
                    model = ProductRecommendation(db, mongo_db)
                    result = model.get_recommended_products(model_id, item_id, org_id)
                elif (model_type == 'association-rule'):
                    result = get_association_rule(model_id, item_id, org_id)

                return Response(result)
            except Exception as error:
                return Response({
                    'status': 201,
                    'message': 'Get results failed'
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

def run_segmentation(request):
    try:
        user_serializer = UserSerializer(request.user)
        org_id = user_serializer.data['org_id']

        body = json.loads(request.body)
        num_clusters = int(body.get('num_clusters', 3))
        model_name = body.get('model_name', '')
        columns = body.get('columns', [])
        end_date = body.get('end_date', datetime.today().strftime('%Y-%m-%d'))
        start_date = body.get('start_date', (datetime.strptime(end_date, '%Y-%m-%d') - timedelta(days=365*40)).strftime('%Y-%m-%d'))

        model = CustomerSegmentation(db, mongo_db)
        result = model.train_segmentation(start_date, end_date, columns, org_id, num_clusters, model_name)

        return result
    except Exception as error:
        return {
            'status': 201,
            'message': 'Segmentation failed'
        }

def run_recommendation(request):
    try:
        user_serializer = UserSerializer(request.user)
        org_id = user_serializer.data['org_id']

        body = json.loads(request.body)
        algorithm = int(body.get('algorithm', 1))
        similarity_score = float(body.get('similarity_score', 0.3))
        model_name = body.get('model_name', '')
        fields = body.get('fields', 'purchase_frequency')
        threshold = body.get('threshold', 0.5)
        numbers = body.get('numbers', 5)
        end_date = body.get('end_date', datetime.today().strftime('%Y-%m-%d'))
        start_date = body.get('start_date', (datetime.strptime(end_date, '%Y-%m-%d') - timedelta(days=365*40)).strftime('%Y-%m-%d'))
        
        model = ProductRecommendation(db, mongo_db)
        result = model.train_recommendation(algorithm, similarity_score, model_name, fields, threshold, numbers, end_date, start_date, org_id)
        return result

    except Exception as error:
        return {
            'status': 201,
            'message': 'Run recommendation failed'
        }
    
def run_association_rule(request):
    try:
        user_serializer = UserSerializer(request.user)
        org_id = user_serializer.data['org_id']

        body = json.loads(request.body)
        min_support = float(body.get('min_support', 0.01))
        model_name = body.get('model_name', '')
        threshold = float(body.get('threshold', 0.9))
        end_date = body.get('end_date', datetime.today().strftime('%Y-%m-%d'))
        start_date = body.get('start_date', (datetime.strptime(end_date, '%Y-%m-%d') - timedelta(days=365*40)).strftime('%Y-%m-%d'))

        model = AssociationRule(db, mongo_db)
        result = model.train_association_rule(model_name, min_support, threshold, end_date, start_date, org_id)

        return result
        
    except Exception as error:
        return {
            'status': 201,
            'message': 'Run association-rule failed'
        }

def run_correlation(request):
    try:
        user_serializer = UserSerializer(request.user)
        org_id = user_serializer.data['org_id']

        body = json.loads(request.body)
        model_name = body.get('model_name', '')
        dimensions = body.get('dimension', [corr['id'] for corr in correlation_dimensions])
        end_date = body.get('end_date', datetime.today().strftime('%Y-%m-%d'))
        start_date = body.get('start_date', (datetime.strptime(end_date, '%Y-%m-%d') - timedelta(days=365*40)).strftime('%Y-%m-%d'))

        model = Correlation(db, mongo_db)
        result = model.train_correlation(model_name, dimensions, end_date, start_date, org_id)

        return result
        
    except Exception as error:
        print(error)
        return {
            'status': 201,
            'message': 'Run correlation failed'
        }
