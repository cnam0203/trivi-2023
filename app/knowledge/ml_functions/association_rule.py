import os
import json
import pandas as pd
from datetime import datetime, timedelta
from mlxtend.frequent_patterns import apriori, association_rules
from bson import ObjectId
from authentication.serializers import UserSerializer

from knowledge.utils import *

class AssociationRule:
    def __init__(self, db, mongo_db):
        self.db = db
        self.mongo_db = mongo_db

    def save_model(self, rule_info, model_name):
        model_info = self.mongo_db.insert('association-rule', rule_info)
        model_id = model_info.inserted_id
        # Get the absolute path of the model file
        abs_model_file_path = ''
        doc_id = ObjectId(model_id)
        self.mongo_db.update('association-rule', {'_id': doc_id}, {
            'model_path': abs_model_file_path,
            'model_name': model_name if model_name != '' else f'MODEL_{model_id}',
            'api': os.environ.get("REACT_APP_BE_SERVER", "") + f'/knowledge/get-info-api/association-rules/{model_id}/<product_id>'
        })

    def train_association_rule(self, model_name, min_support, threshold, end_date, start_date, org_id):
        try:
            # Load dataframes
            query = f"""SELECT trans_id
                        FROM data_transaction
                        WHERE inf_org_id = '{org_id}' 
                        AND trans_time between '{start_date}' and '{end_date}'
                        AND inf_is_deleted = FALSE"""
            transaction = self.db.select_rows_dict(query)

            query = f"""SELECT trans_id, item_id AS prod_id
                        FROM data_transaction_item 
                        WHERE inf_org_id = '{org_id}' 
                        AND inf_is_deleted = FALSE"""
            transaction_item = self.db.select_rows_dict(query)

            query = f"""SELECT prod_id, prod_name
                        FROM data_product 
                        WHERE inf_org_id = '{org_id}' 
                        AND inf_is_deleted = FALSE"""
            product = self.db.select_rows_dict(query)

            # Merge dataframes
            df = pd.merge(transaction, transaction_item, on='trans_id')
            df = pd.merge(df, product, on='prod_id')

            # Create list of transactions
            transactions = df.groupby(['trans_id', 'prod_id'])['prod_id'].count().unstack().reset_index().fillna(0).set_index('trans_id')
            transactions = transactions.applymap(lambda x: 1 if x > 0 else 0).astype(bool)

            # Generate frequent itemsets
            frequent_itemsets = apriori(transactions, min_support=min_support, use_colnames=True)

            # Generate association rules
            rules = association_rules(frequent_itemsets, metric="lift", min_threshold=threshold)

            # Sort rules by confidence and lift
            rules = rules.sort_values(['confidence', 'lift'], ascending=[False, False])

            # Create list of lists
            result = []
            for i in range(len(rules)):
                antecedents = list(rules.iloc[i]['antecedents'])
                consequents = list(rules.iloc[i]['consequents'])
                itemset = []
                for item in antecedents + consequents:
                    itemset.append(item)
                result.append(itemset)

            rule_info = {
                "run_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "org_id": int(org_id),
                "is_deleted": False,
                "start_date": start_date,
                'end_date': end_date,
                "model_path": "",
                "api": "",
                "model_name": model_name if model_name != '' else f'MODEL_{model_id}',
                "threshold": threshold,
                "min_support": min_support,
                "rules": result,
                "total_itemsets": len(result)
            }

            self.save_model(rule_info, model_name)

            return {
                'status': 200,
                'message': 'Run association-rule finished',
            }

        except Exception as error:
            print(error)
            return {
                'status': 201,
                'message': 'Run association-rule failed'
            }
