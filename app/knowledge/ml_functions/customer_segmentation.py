import json
import os
from datetime import datetime, timedelta
from bson import ObjectId
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import LabelEncoder
import joblib

from knowledge.utils import *

class CustomerSegmentation:
    def __init__(self, db, mongo_db):
        self.valid_categorical_cols = ['cus_gender', 'cus_location']
        self.valid_numeric_cols = ['cus_age', 'cus_revenue', 'cus_account_age']
        self.model_path = ""
        self.kmeans = None
        self.col_dicts = {}
        self.labels = []
        self.clusters = []
        self.db = db
        self.mongo_db = mongo_db

    # Private methods

    def _check_customer_exist(self, cus_id, org_id):
        check_customer_exist = check_item_org(self.db, cus_id, org_id, 'data_customer', 'cus_id')
        if not check_customer_exist:
            return {
                'status': 201,
                'message': 'Customer ID invalid'
            }
        return None
    
    def _load_and_split_cols(self, query):
        df = self.db.select_rows_dict(query)
        df = df.loc[:, self.columns]
        data_types = df.dtypes

        categorical_cols = []
        numeric_cols = []

        for idx, col_type in enumerate(data_types):
            if col_type == 'object' and df.columns[idx] in self.valid_categorical_cols:
                categorical_cols.append(df.columns[idx])
            elif df.columns[idx] in self.valid_numeric_cols:
                numeric_cols.append(df.columns[idx])

        return df, categorical_cols, numeric_cols

    def _load_customer_dataset(self, start_date, end_date, org_id):
        query = f"""select a.cus_id, a.cus_gender, a.cus_location, 
                    a.cus_dob,
                    DATE_PART('day', AGE(now(), a.cus_dob)) as cus_age, 
                    DATE_PART('day', AGE(now(), a.cus_account_date)) as cus_account_age, 
                    sum(b.trans_revenue_value) as cus_revenue
                    from data_customer a
                    join data_transaction b
                    on a.cus_id = b.trans_cus_id
                    where b.trans_time >= '{start_date}' and b.trans_time <= '{end_date}'
                    and a.inf_org_id = '{org_id}' and b.inf_org_id = '{org_id}'
                    and a.inf_is_deleted = FALSE and b.inf_is_deleted = FALSE
                    group by a.cus_id, a.cus_gender, a.cus_location, a.cus_dob, cus_age, cus_account_age;
                    """
    
        return self._load_and_split_cols(query)

    def _preprocess_data(self, df, categorical_cols, numeric_cols):
        X_numeric = df[numeric_cols]
        X_numeric = np.array(X_numeric).reshape(-1, len(numeric_cols))
        X_categorical = df[categorical_cols]

        encoder = LabelEncoder()
        self.col_dicts = {}
        for col in X_categorical.columns:
            col_encoded = encoder.fit_transform(X_categorical.loc[:, col])
            col_dict = dict(zip(col_encoded, X_categorical.loc[:, col]))
            self.col_dicts[col] = col_dict
        
        new_dict = {}
        for key, value in self.col_dicts.items():
            new_dict[key] = {str(k): v for k, v in value.items()}
        self.col_dicts = new_dict   

        X_categorical_encoded = X_categorical.apply(encoder.fit_transform)
        X = np.hstack((X_numeric, X_categorical_encoded))

        return X

    def _fit_kmeans(self, df, X, num_clusters):
        self.kmeans = KMeans(n_clusters=num_clusters)
        self.kmeans.fit(X)
        self.labels = self.kmeans.labels_
        unique_labels, counts = np.unique(self.labels, return_counts=True)
        counts = [int(c) for c in counts]
        centroids = self.kmeans.cluster_centers_
        centroids_df = pd.DataFrame(centroids, columns=self.numeric_cols + self.categorical_cols)
        self.clusters = []
        pca = PCA(n_components=2)
        X_pca = pca.fit_transform(X)
        pca_df = pd.DataFrame(X_pca.tolist(), columns=['x', 'y'])
        label_df = pd.DataFrame({'label': self.labels})
        self.labels = (pd.concat([df, pca_df, label_df], axis=1)).reset_index().to_dict('records')
        self.labels.sort(key=lambda x: x["label"])

        for col in self.categorical_cols:
            centroids_df[col] = centroids_df[col].round(0).astype(int)

        for col, mapping in self.col_dicts.items():
            centroids_df[col] = centroids_df[col].replace(mapping)

        centroids_arr = centroids_df.to_dict(orient='records')

        for i in range(len(unique_labels)):
            self.clusters.append({
                "name": i,
                "count": counts[i],
                "centroid": centroids_arr[i]
            })

    def save_model_info(self, model_info, model_name):
        model_info = self.mongo_db.insert('customer-segmentation', model_info)
        model_id = model_info.inserted_id
        model_file_name = f'my_kmeans_model_{model_id}.pkl'
        self.model_path = os.path.join('ml_models', 'customer_segmentation', model_file_name)
        abs_model_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', self.model_path))
        joblib.dump(self.kmeans, abs_model_file_path)
        doc_id = ObjectId(model_id)
        self.mongo_db.update('customer-segmentation', {'_id': doc_id}, {
            'model_path': abs_model_file_path,
            'model_name': model_name if model_name != '' else f'MODEL_{model_id}',
            'api': os.environ.get("REACT_APP_BE_SERVER", "") + f'/knowledge/get-info-api/customer-segmentation/{model_id}/<customer_id>'
        })
        return model_id

    def _load_model(self, model_id):
        try:
            doc_id = ObjectId(model_id)
            row = self.mongo_db.find_one('customer-segmentation', {'_id': doc_id})
            self.model_path = row['model_path']
            self.kmeans = joblib.load(self.model_path)
            self.columns = row['fields']
            self.categorical_cols = self.valid_categorical_cols
            self.numeric_cols = self.valid_numeric_cols
            self.col_dicts = row['encoded_dict']
            self.labels = row['labels']
            self.clusters = row['clusters']
            return {
                'status': 200,
                'message': 'Model loaded successfully'
            }
        except Exception as error:
            return {
                'status': 201,
                'message': 'Model loading failed'
            }

    # Public methods

    def train_segmentation(self, start_date, end_date, columns, org_id, num_clusters=3, model_name=''):
        try:
            if len(columns) == 0:
                self.columns = self.valid_categorical_cols + self.valid_numeric_cols
            else:
                self.columns = columns

            df, self.categorical_cols, self.numeric_cols = self._load_customer_dataset(start_date, end_date, org_id)
            X = self._preprocess_data(df, self.categorical_cols, self.numeric_cols)
            self._fit_kmeans(df, X, num_clusters)

            segment_info = {
                "run_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "org_id": int(org_id),
                "is_deleted": False,
                "fields": self.columns,
                "start_date": start_date,
                'end_date': end_date,
                'clusters': self.clusters,
                "model_path": "",
                "img_path": "",
                "api": os.environ.get("REACT_APP_BE_SERVER", "") + f'/knowledge/get-info-api/customer-segmentation/<model_id>/<customer_id>',
                "num_clusters": num_clusters,
                "model_name": model_name if model_name != '' else f'MODEL_<model_id>',
                "encoded_dict": self.col_dicts,
                "labels": self.labels
            }

            self.save_model_info(segment_info, model_name)

            return {
                'status': 200,
                'message': 'Segmentation finished'
            }
        except Exception as error:
            print(error)
            return {
                'status': 201,
                'message': 'Segmentation failed'
            }

    def load_model(self, model_id):
        try:
            model_loading = self._load_model(model_id)
            if model_loading['status'] != 200:
                return {
                    'status': model_loading['status'],
                    'message': 'Model loading failed'
                }

            return {
                'status': 200,
                'message': 'Model loaded successfully'
            }
        except Exception as error:
            return {
                'status': 201,
                'message': 'Model loading failed'
            }

    def get_customer_segment_info(self, cus_id, org_id, model_id):
        try:
            check_customer_exist = self._check_customer_exist(cus_id, org_id)
            if check_customer_exist:
                return {
                    'status': 201,
                    'message': 'Customer ID invalid'
                }

            model_loading = self._load_model(model_id)
            if model_loading['status'] != 200:
                return {
                    'status': model_loading['status'],
                    'message': 'Model loading failed'
                }

            query = f"""SELECT a.cus_id, a.cus_gender, a.cus_location, 
                        a.cus_dob,
                        DATE_PART('day', AGE(now(), a.cus_dob)) as cus_age, 
                        DATE_PART('day', AGE(now(), a.cus_account_date)) as cus_account_age, 
                        sum(b.trans_revenue_value) as cus_revenue
                        FROM data_customer a
                        JOIN data_transaction b
                        ON a.cus_id = b.trans_cus_id
                        WHERE a.cus_id = '{cus_id}'
                        AND a.inf_org_id = '{org_id}' AND b.inf_org_id = '{org_id}'
                        AND a.inf_is_deleted = FALSE AND b.inf_is_deleted = FALSE
                        GROUP BY a.cus_id, a.cus_gender, a.cus_location, a.cus_dob, cus_age, cus_account_age
                        LIMIT 1;
                        """
            
            df, categorical_cols, numeric_cols = self._load_and_split_cols(query)

            X = self._preprocess_data(df, categorical_cols, numeric_cols)
            label = self.kmeans.predict(X)[0]
            label_name = self.clusters[label]['name']

            return {
                'status': 200,
                'result': {
                    'type': 'text',
                    'label': 'Customer belongs to segment: ',
                    'value': label_name
                }
            }

        except Exception as error:
            return {
                'status': 201,
                'message': 'Get results failed'
            }
