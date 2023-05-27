import os
import json
import pandas as pd
from datetime import datetime, timedelta
from bson import ObjectId
from authentication.serializers import UserSerializer

from knowledge.utils import *
import matplotlib.pyplot as plt


class Correlation:
    def __init__(self, db, mongo_db):
        self.db = db
        self.mongo_db = mongo_db

    def save_model(self, df, corr_info, model_name):
        model_info = self.mongo_db.insert('correlation', corr_info)
        model_id = model_info.inserted_id
        model_file_name = f'my_correlation_{model_id}.png'
        model_file_path = os.path.join('media', 'ml_images', 'correlation', model_file_name)

        abs_model_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', model_file_path))

        scatter_matrix = pd.plotting.scatter_matrix(df, figsize=(8, 8), alpha=0.8)

        # Set diagonal plots to kernel density estimation (KDE) plots
        for ax in scatter_matrix.flatten():
            ax.xaxis.label.set_rotation(45)
            ax.yaxis.label.set_rotation(0)
            ax.yaxis.label.set_ha('right')

        # Save the scatter matrix plot as an image
        plt.savefig(abs_model_file_path)
    
        doc_id = ObjectId(model_id)
        self.mongo_db.update('correlation', { '_id': doc_id }, {
            'img_path': os.environ.get("REACT_APP_BE_SERVER", "") + f'/knowledge/static/ml_images/correlation/' +  model_file_name,
            'model_name': model_name if model_name != '' else f'MODEL_{model_id}',
        })

    def train_correlation(self, model_name, dimensions, end_date, start_date, org_id):
        try:
             # Load the data from the database tables into pandas dataframes
            customer_df = self.db.select_rows_dict(f"""
                select cus_id, cus_gender, cus_location,
                DATE_PART('day', AGE(now(), cus_dob)) as cus_age,   
                DATE_PART('day', AGE(now(), cus_account_date)) as cus_account_age
                from data_customer
                where inf_org_id = '{org_id}' and inf_is_deleted = FALSE
            """)
            product_df = self.db.select_rows_dict(f"""
                select prod_id, prod_category_1 as prod_category,
                COALESCE(NULLIF(prod_price, '')::DECIMAL, 0.00) as prod_price
                from data_product
                where inf_org_id = '{org_id}' and inf_is_deleted = FALSE
                union
                select prod_id, prod_category_2 as prod_category,
                COALESCE(NULLIF(prod_price, '')::DECIMAL, 0.00) as prod_price
                from data_product
                where inf_org_id = '{org_id}' and inf_is_deleted = FALSE
                union
                select prod_id, prod_category_3 as prod_category,
                COALESCE(NULLIF(prod_price, '')::DECIMAL, 0.00) as prod_price
                from data_product
                where inf_org_id = '{org_id}' and inf_is_deleted = FALSE
            """)
            transaction_df = self.db.select_rows_dict(f"""
                select trans_id, trans_cus_id as cus_id, trans_time, 
                trans_revenue_value, trans_tax_value, 
                trans_refund_value, trans_shipping_value
                from data_transaction
                where inf_org_id = '{org_id}' and inf_is_deleted = FALSE
            """)
            transaction_item_df = self.db.select_rows_dict(f"""
                select trans_id, item_id as prod_id, ti_quantity
                from data_transaction_item
                where inf_org_id = '{org_id}' and inf_is_deleted = FALSE
            """)

            # Calculate the correlation between product category and total revenue
            # Merge transaction_item_df and product_df on prod_id column
            age_price_df = (transaction_df.merge(customer_df, on='cus_id')
                                .merge(transaction_item_df, on='trans_id')
                                .merge(product_df, on='prod_id')[dimensions])
            
            corr_age_price = age_price_df.corr()

            corr_info = {
                "run_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "org_id": int(org_id),
                "is_deleted": False,
                "start_date": start_date,
                'end_date': end_date,
                "model_path": "",
                "api": "",
                "model_name": model_name,
                "dimension": dimensions,
                "correlation_coefficient": corr_age_price.fillna(0).round(3).to_dict(),
                "dimensions": corr_age_price.columns.tolist()
            }

            self.save_model(age_price_df, corr_info, model_name)

            return {
                    'status': 200,
                    'message': 'Run correlation finished',
                }

        except Exception as error:
            print(error)
            return {
                'status': 201,
                'message': 'Run correlation failed'
            }
