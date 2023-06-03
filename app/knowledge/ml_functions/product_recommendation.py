import json
from datetime import timedelta, datetime
import os
from itertools import combinations
import numpy as np
import pandas as pd
import joblib
from bson.objectid import ObjectId
from sklearn.neighbors import NearestNeighbors
from authentication.serializers import UserSerializer

from knowledge.utils import *


class ProductRecommendation:
    def __init__(self, db, mongo_db):
        self.db = db
        self.mongo_db = mongo_db

    def train_recommendation(self, algorithm, similarity_score, model_name, fields, num_neighbor, threshold, numbers, end_date, start_date, org_id):
        try:
            result = {
                'status': 201,
                'message': 'Run recommendation failed'
            }
            recommendation_info = {}
            if algorithm == 1:
                result = self.train_recommendation_1(start_date, end_date, similarity_score, org_id)
                if result['status'] == 200:
                    recommendation_info = {
                        "run_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        "org_id": int(org_id),
                        "is_deleted": False,
                        "start_date": start_date,
                        'end_date': end_date,
                        'fields': '',
                        "model_path": "",
                        "api": "",
                        "numbers": numbers,
                        "algorithm":  algorithm,
                        "model_name": model_name,
                        "similarity_score": similarity_score,
                        "similarity_scores": result['similarity_scores']
                    }
            elif algorithm == 2:
                result = self.train_recommendation_2(start_date, end_date, similarity_score, fields, org_id)
                if result['status'] == 200:
                    recommendation_info = {
                        "run_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        "org_id": int(org_id),
                        "is_deleted": False,
                        "fields": fields,
                        "start_date": start_date,
                        'end_date': end_date,
                        "model_path": "",
                        "api": "",
                        "numbers": numbers,  
                        "algorithm":  algorithm,
                        "model_name": model_name,
                        "similarity_score": similarity_score,
                        "similarity_scores": result['similarity_scores']
                    }
            elif algorithm == 3:
                result = self.train_recommendation_3(start_date, end_date, num_neighbor, fields, numbers, org_id)
                if result['status'] == 200:
                    recommendation_info = {
                        "run_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        "org_id": int(org_id),
                        "is_deleted": False,
                        "fields": fields,
                        "start_date": start_date,
                        'end_date': end_date,
                        "model_path": "",
                        "api": "",
                        "numbers": numbers,
                        "num_neighbor": num_neighbor, 
                        "algorithm":  algorithm,
                        "model_name": model_name,
                        "similarity_score": similarity_score,
                        "similarity_scores": result['similarity_scores']
                    }

            self.save_model_info(recommendation_info, model_name, result)

            return {
                'status': result['status'],
                'message': result['message']
            }

        except Exception as error:
            print(error)
            return {
                'status': 201,
                'message': 'Run recommendation failed'
            }
        
    def save_model_info(self, recommendation_info, model_name, result):
        model_info = self.mongo_db.insert('product-recommendation', recommendation_info)
        model_id = model_info.inserted_id
        abs_model_file_path = ''
        matrix = []

        if 'model' in result.keys():
            model_file_name = f'my_kmeans_model_{model_id}.pkl'
            model_file_path = os.path.join('ml_models', 'product_recommendation', model_file_name)
            # Get the absolute path of the model file
            abs_model_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', model_file_path))
            joblib.dump(result['model'], abs_model_file_path)
        if 'matrix' in result.keys():
            matrix = result['matrix']

        doc_id = ObjectId(model_id)
        self.mongo_db.update('product-recommendation', { '_id': doc_id }, {
            'model_name': model_name if model_name != '' else f'MODEL_{model_id}',
            'model_path': abs_model_file_path,
            'matrix': matrix,
            'api': os.environ.get("REACT_APP_BE_SERVER", "") + f'/knowledge/get-info-api/product-recommendation/{model_id}/<customer_id>'
        })

        return model_id

    def train_recommendation_1(self, start_date, end_date, similarity_score, org_id):
        try:
            query = f"""SELECT a.* FROM (SELECT prod_id, prod_name, prod_category_1 AS prod_category FROM data_product
                        WHERE inf_org_id = '{org_id}' AND inf_is_deleted = FALSE
                        UNION
                        SELECT prod_id, prod_name, prod_category_2 AS prod_category FROM data_product
                        WHERE inf_org_id = '{org_id}' AND inf_is_deleted = FALSE
                        UNION
                        SELECT prod_id, prod_name, prod_category_3 AS prod_category FROM data_product
                        WHERE inf_org_id = '{org_id}' AND inf_is_deleted = FALSE) a
                        inner join data_transaction_item b on a.prod_id = b.item_id
                        inner join data_transaction c on b.trans_id = c.trans_id
                        where c.trans_time between '{start_date}' and '{end_date}'
                        AND b.inf_org_id = '{org_id}' AND b.inf_is_deleted = FALSE
                        AND c.inf_org_id = '{org_id}' AND c.inf_is_deleted = FALSE"""
            prod_df = self.db.select_rows_dict(query)

            prod_df = pd.pivot_table(data=prod_df, index=['prod_id'], columns='prod_category', values='prod_category', fill_value=0, aggfunc='count').reset_index()
            similarity_scores = []

            for product1, product2 in combinations(prod_df['prod_id'], 2):
                features1 = prod_df.loc[prod_df['prod_id'] == product1].iloc[:, 1:].values
                features2 = prod_df.loc[prod_df['prod_id'] == product2].iloc[:, 1:].values

                intersection = np.logical_and(features1, features2)
                union = np.logical_or(features1, features2)
                score = np.sum(intersection) / np.sum(union)

                if score >= similarity_score:
                    similarity_scores.append({
                        'prod_1': product1,
                        'prod_2': product2,
                        'score': score
                    })

            return {
                'status': 200,
                'message': 'Run recommendation finished',
                'similarity_scores': similarity_scores
            }

        except Exception as error:
            print(error)
            return {
                'status': 201,
                'message': 'Run model failed'
            }

    def train_recommendation_2(self, start_date, end_date, similarity_score, fields, org_id):
        try:
            query = f"""SELECT b.item_id AS prod_id, a.trans_cus_id AS cus_id, COUNT(*) AS purchase_frequency,
                        SUM(b.ti_quantity) AS total_quantity,
                        SUM(b.ti_quantity*COALESCE(NULLIF(c.prod_price, '')::DECIMAL, 0.00)) AS total_revenue
                        FROM data_transaction a
                        INNER JOIN data_transaction_item b
                        ON a.trans_id = b.trans_id
                        INNER JOIN data_product c
                        ON b.item_id = c.prod_id
                        WHERE a.trans_time BETWEEN '{start_date}' AND '{end_date}' AND
                        a.inf_org_id = '{org_id}' AND a.inf_is_deleted = FALSE
                        AND b.inf_org_id = '{org_id}' AND b.inf_is_deleted = FALSE
                        AND c.inf_org_id = '{org_id}' AND c.inf_is_deleted = FALSE
                        GROUP BY b.item_id, a.trans_cus_id"""
            prod_df = self.db.select_rows_dict(query)
            similarity_scores = []
            prod_df = pd.pivot_table(data=prod_df, index=['prod_id'], columns='cus_id', values=fields, fill_value=0).reset_index()
    
            for product1, product2 in combinations(prod_df['prod_id'], 2):
                features1 = prod_df.loc[prod_df['prod_id'] == product1].iloc[:, 1:].values
                features2 = prod_df.loc[prod_df['prod_id'] == product2].iloc[:, 1:].values

                intersection = np.logical_and(features1, features2)
                union = np.logical_or(features1, features2)
                score = np.sum(intersection) / np.sum(union)

                if score >= similarity_score:
                    similarity_scores.append({
                        'prod_1': product1,
                        'prod_2': product2,
                        'score': score
                    })

            return {
                'status': 200,
                'message': 'Run recommendation finished',
                'similarity_scores': similarity_scores
            }
        except Exception as error:
            print(error)
            return {
                'status': 201,
                'message': 'Run model failed'
            }

    def train_recommendation_3(self, start_date, end_date, num_neighbor, fields, numbers, org_id):
        try:
            query = f"""SELECT b.item_id AS prod_id, a.trans_cus_id AS cus_id, COUNT(*) AS purchase_frequency,
                        SUM(b.ti_quantity) AS total_quantity,
                        SUM(b.ti_quantity*COALESCE(NULLIF(c.prod_price, '')::DECIMAL, 0.00)) AS total_revenue
                        FROM data_transaction a
                        INNER JOIN data_transaction_item b
                        ON a.trans_id = b.trans_id
                        INNER JOIN data_product c
                        ON b.item_id = c.prod_id
                        WHERE a.trans_time BETWEEN '{start_date}' AND '{end_date}' AND
                        a.inf_org_id = '{org_id}' AND a.inf_is_deleted = FALSE
                        AND b.inf_org_id = '{org_id}' AND b.inf_is_deleted = FALSE
                        AND c.inf_org_id = '{org_id}' AND c.inf_is_deleted = FALSE
                        GROUP BY b.item_id, a.trans_cus_id"""
            prod_df = self.db.select_rows_dict(query)
            matrix = prod_df.pivot_table(index='cus_id', columns='prod_id', values=fields, fill_value=0)
            k = int(num_neighbor)
            model = NearestNeighbors(n_neighbors=k, metric='cosine')
            model.fit(matrix)

            distances, indices = model.kneighbors(matrix)
            # Initialize an empty dictionary
            neighbors_dict = {}

            # Iterate over the matrix.index
            for i, cus_id in enumerate(matrix.index):
                # Get the corresponding indices from the indices array
                indice = indices[i]
                similar_users = matrix.index[indice.flatten()]
                predicted_freqs = matrix.loc[similar_users].mean(axis=0)

                # lấy danh sách sản phẩm cần gợi ý và số lần mua được dự đoán
                recommended_id = predicted_freqs.sort_values(ascending=False).index.tolist()[:int(numbers)]

                # Add the cus_id and its neighbors to the dictionary
                neighbors_dict[cus_id] = recommended_id
            return {
                'status': 200,
                'message': 'Run recommendation finished',
                'similarity_scores': [],
                'model': model,
                'matrix': neighbors_dict
            }

        except Exception as error:
            print(error)
            return {
                'status': 201,
                'message': 'Run model failed'
            }
        
    def get_recommended_products(self, model_id, cus_id, org_id):
        try:
            check_customer_exist = check_item_org(self.db, cus_id, org_id, 'data_customer', 'cus_id')
            if (check_customer_exist ==  False):
                return {
                    'status': 201,
                    'message': 'Customer ID invalid'
                }
            
            doc_id = ObjectId(model_id)
            config =  self.mongo_db.find_one('product-recommendation', { 'org_id': int(org_id), 'is_deleted': False, '_id': doc_id})
            algorithm = config['algorithm']
            result = {}

            if (algorithm == 1):
                result = self.get_recommended_products_1(config, cus_id, org_id)
            elif (algorithm == 2):
                result = self.get_recommended_products_2(config, cus_id, org_id)
            elif (algorithm == 3):
                result = self.get_recommended_products_3(config, cus_id, org_id)

            return result
        except Exception as error:
            print(error)
            return {
                'status': 201,
                'message': 'Get results failed'
            }
            
    def get_recommended_products_1(self, config, cus_id, org_id):
        try:
            # Wer can change quantity to frequency
            query = f"""select item_id as prod_id, sum(ti_quantity) as quantity
                        from data_transaction a
                        inner join data_transaction_item b
                        on a.trans_id = b.trans_id and a.trans_cus_id='{cus_id}'
                        where a.inf_org_id = '{org_id}' and a.inf_is_deleted = FALSE
                        and b.inf_org_id = '{org_id}' and b.inf_is_deleted = FALSE
                        group by item_id"""
            cus_df = self.db.select_rows_dict(query)

            scores = {}
            similarity_scores = config['similarity_scores']

            for index, row in cus_df.iterrows():
                prod_id = row['prod_id']
                weight = row['quantity']

                for pair in similarity_scores:
                    prod_1 = str(pair['prod_1'])
                    prod_2 = str(pair['prod_2'])
                    score = pair['score']

                    if prod_1 == prod_id:
                        if prod_2 not in scores:
                            scores[str(prod_2)] = 0
                        scores[prod_2] = scores[prod_2] + score*weight
            n = config['numbers']
            sorted_list = [key for key, value in sorted(scores.items(), key=lambda item: item[1], reverse=True)]
            recommended_id = sorted_list[:n]
            recommended_df = []

            if (len(recommended_id)):
                recommended_id_str = ', '.join(["'" + x + "'" for x in recommended_id])

                query = f"""select distinct prod_id, prod_name
                            from data_product
                            where prod_id in ({recommended_id_str}) 
                            and inf_org_id = '{org_id}' and inf_is_deleted = FALSE"""
            
                recommended_df = self.db.select_rows_dict(query).to_dict(orient='records')

            result = {
                    'status': 200,
                    'result': {
                        'type': 'table',
                        'info': {
                            'title': 'List of recommended products',
                            'data': recommended_df
                        },
                        'value': recommended_df
                    }
                }
            
            return result
        except Exception as error:
                print(error)
                return {
                    'status': 201,
                    'message': 'Get results failed'
                }

    def get_recommended_products_2(self, config, cus_id, org_id):
        try:
            # Wer can change quantity to frequency
            query = f"""select item_id as prod_id, sum(ti_quantity) as quantity
                        from data_transaction a
                        inner join data_transaction_item b
                        on a.trans_id = b.trans_id and a.trans_cus_id='{cus_id}'
                        where a.inf_org_id = '{org_id}' and a.inf_is_deleted = FALSE
                        and b.inf_org_id = '{org_id}' and b.inf_is_deleted = FALSE
                        group by item_id"""
            cus_df = self.db.select_rows_dict(query)

            scores = {}
            similarity_scores = config['similarity_scores']

            for index, row in cus_df.iterrows():
                prod_id = row['prod_id']
                weight = row['quantity']

                for pair in similarity_scores:
                    prod_1 = str(pair['prod_1'])
                    prod_2 = str(pair['prod_2'])
                    score = pair['score']

                    if prod_1 == prod_id:
                        if prod_2 not in scores:
                            scores[str(prod_2)] = 0
                        scores[prod_2] = scores[prod_2] + score*weight

            n = config['numbers']
            sorted_list = [key for key, value in sorted(scores.items(), key=lambda item: item[1], reverse=True)]
            recommended_id = sorted_list[:n]
            recommended_df = []

            if (len(recommended_id)):
                recommended_id_str = ', '.join(["'" + x + "'" for x in recommended_id])

                query = f"""select distinct prod_id, prod_name
                            from data_product
                            where prod_id in ({recommended_id_str}) 
                            and inf_org_id = '{org_id}' and inf_is_deleted = FALSE"""
            
                recommended_df = self.db.select_rows_dict(query).to_dict(orient='records')

            result = {
                    'status': 200,
                    'result': {
                        'type': 'table',
                        'info': {
                            'title': 'List of recommended products',
                            'data': recommended_df
                        },
                        'value': recommended_df
                    }
                }
            
            return result
        except Exception as error:
                print(error)
                return {
                    'status': 201,
                    'message': 'Get results failed'
                }

    def get_recommended_products_3(self, config, cus_id, org_id):
        try:
            # lấy danh sách sản phẩm cần gợi ý và số lần mua được dự đoán
            recommended_id = config['matrix'][cus_id]
            recommended_df = []

            if (len(recommended_id)):
                recommended_id_str = ', '.join(["'" + x + "'" for x in recommended_id])

                query = f"""select distinct prod_id, prod_name
                            from data_product
                            where prod_id in ({recommended_id_str}) 
                            and inf_org_id = '{org_id}' and inf_is_deleted = FALSE"""
            
                recommended_df = self.db.select_rows_dict(query).to_dict(orient='records')

            result = {
                    'status': 200,
                    'result': {
                        'type': 'table',
                        'info': {
                            'title': 'List of recommended products',
                            'data': recommended_df
                        },
                        'value': recommended_df
                    }
                }
            
            return result
        except Exception as error:
            print(error)
            return {
                'status': 201,
                'message': 'Get results failed'
            }
