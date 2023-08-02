import json
import os
from datetime import datetime, timedelta
from bson import ObjectId
import numpy as np
import pandas as pd
import nltk

from nltk.corpus import stopwords, wordnet
from nltk.tokenize import word_tokenize
from pandasai import PandasAI
from pandasai.llm.openai import OpenAI

from knowledge.utils import *
from functools import reduce

nltk.download('stopwords')
nltk.download('punkt')
nltk.download('wordnet')

# Define the stop words to be removed from the user question
stop_words = set(stopwords.words('english'))
custom_stopwords = ['from', 'to', 'where', 'at', 'in', 'on']
updated_stopwords = [word for word in stop_words if word not in custom_stopwords]
draw_keywords = ["draw", "plot", "sketch", "graph", "histogram", "chart", "visualize", "illustrate",
                "demonstrate", "display", "depict", "show", "generate", "create", "design", "diagram",
                "bar graph", "line graph", "scatter plot", "pie chart", "area chart", "histogram",
                "box plot", "network graph", "flowchart"]

# Define the mappings between columns and dataframes
column_mappings = {
    'data_customer': {
        'customer_id': 'cus_id',
        'date_of_birth': 'cus_dob',
        'account_date': "cus_account_date",
        'customer_location': 'cus_location',
        'customer_gender': 'cus_gender',
        'customer_age': 'cus_age'
    },
    'data_transaction': {
        'transaction_id': 'trans_id',
        'customer_id': 'trans_cus_id',
        'transaction_date': 'trans_time',
        'transaction_status': 'trans_status',
        'transaction_revenue': 'trans_revenue_value',
        # Add more columns as needed
    },
    'data_transaction_item': {
        'transaction_id': 'trans_id',
        'product_id': 'item_id',
        'quantity': 'ti_quantity',
        # Add more columns as needed
    },
    'data_product': {
        'product_id': 'prod_id',
        'product_name': 'prod_name',
        'product_category': 'prod_category',
        'product_quantity': 'prod_quantity',
        'product_price': 'prod_price',
        'product_from_date': 'prod_from_date',
        'product_to_date': 'prod_to_date'
        # Add more columns as needed
    },
    'data_event': {
        'event_id': 'ev_id',
        'customer_id': 'ev_cus_id',
        'event_type': 'ev_type',
        'event_device_category': 'ev_dev_category',
        'event_device_browser': 'ev_dev_browser',
        'event_device_os': 'ev_dev_os',
        'event_device_brand': 'ev_dev_brand',
        'event_country': 'ev_geo_country',
        'event_continent': 'ev_geo_continent',
        'event_traffic_source': 'ev_traffic_source',
        'event_page_url': 'ev_page_url',
        'event_page_title': 'ev_page_title',
        'event_time': 'ev_start_time',
        # Add more columns as needed
    }
}
additional_tables = {
    'data_event': ['data_customer'],
    'data_transaction': ['data_customer', 'data_transaction_item'],
    'data_transaction_item': ['data_transaction', 'data_product'],
    'data_product': ['data_transaction', 'data_transaction_item'],
}
require_columns = {
    'data_customer': ['cus_id', 'cus_account_date'],
    'data_transaction': ['trans_id', 'trans_time', 'cus_id'],
    'data_transaction_item': ['trans_id', 'item_id'],
    'data_event': ['ev_id', 'ev_cus_id', 'ev_start_time'],
    'data_product': ['prod_id', 'prod_name', 'prod_from_date', 'prod_to_date']
}

class IntelligentAnswer:
    def __init__(self, org_id, db):
        self.db = db
        self.org_id = org_id

        llm = OpenAI(api_token=os.environ.get("OPEN_AI_API_KEY", ""))
        self.pandas_ai = PandasAI(llm, conversational=False)

    # Function to preprocess the user question
    def preprocess_question(self, question):
        # Tokenize the question
        tokens = word_tokenize(question.lower())
        # Remove stop words
        tokens = [token for token in tokens if token not in updated_stopwords]
        return tokens
    
    def calculate_similarity(self, text_1, text_2):
        # Tokenize the noun phrases into individual words
        words1 = word_tokenize(text_1)
        words2 = word_tokenize(text_2)
        
        synsets1 = []
        synsets2 = []
        
        # Get the synsets for each word in the first noun phrase
        for word in words1:
            synsets = wordnet.synsets(word)
            if synsets:
                synsets1.extend(synsets)
        
        # Get the synsets for each word in the second noun phrase
        for word in words2:
            synsets = wordnet.synsets(word)
            if synsets:
                synsets2.extend(synsets)
        
        max_similarity = 0.0
        
        # Calculate the maximum similarity score between the synsets of the two noun phrases
        for synset1 in synsets1:
            for synset2 in synsets2:
                similarity = synset1.path_similarity(synset2)
                if similarity is not None and similarity > max_similarity:
                    max_similarity = similarity
        
        return max_similarity
    
    # Function to find relevant dataframes and columns based on the user question
    def find_relevant_dataframes(self, question, similarity_score=0.8):
        # Preprocess the question
        tokens = self.preprocess_question(question)
        
        # Initialize the set of relevant dataframes and columns
        relevant_dataframes = set()
        relevant_columns = set()
        relevant_tokens = set()
        
        # Iterate over the tokens and find matches with column meanings
        for token in tokens:
            for dataframe, columns in column_mappings.items():
                for column in columns:
                    similarity = self.calculate_similarity(token, column.lower().replace("_", " "))
                    if similarity >= similarity_score:  # Adjust the similarity threshold as needed

                        relevant_dataframes.add(dataframe)
                        relevant_columns.add((dataframe, column))
                        relevant_tokens.add((token, column.lower()))
        
        return relevant_dataframes, relevant_columns, relevant_tokens
    
    def change_column_name(self, df, config):
        # Create a new list of column names based on the mappings
        inverted_config = {value: key for key, value in config.items()}
        selected_columns = df.loc[:, df.columns.isin([key for key in inverted_config])]
        new_columns = [inverted_config.get(col, None) for col in selected_columns.columns.tolist()]

        # Rename the columns of the DataFrame
        selected_columns.columns = new_columns
        
        return selected_columns
    
    def query_required_data(self, dataframes):
        dfs = []
        for dataframe in dataframes:
            query = ''
            if dataframe == 'data_customer':
                query = f"""select cus_id, cus_gender, cus_location, 
                DATE_PART('day', AGE(now(), cus_dob)) as cus_age, 
                CAST(cus_dob AS timestamp) AT TIME ZONE 'UTC' as cus_dob,
                CAST(cus_account_date AS timestamp) AT TIME ZONE 'UTC' as cus_account_date from data_customer 
                            where inf_org_id='{self.org_id}' and inf_is_deleted = FALSE"""
                df = self.db.select_rows_dict(query)
            elif dataframe == 'data_product':
                query = f"""select *, prod_category_1 as prod_category from data_product
                            where inf_org_id='{self.org_id}' and inf_is_deleted = FALSE
                            union select *, prod_category_2 as prod_category from data_product
                            where inf_org_id='{self.org_id}' and inf_is_deleted = FALSE
                            union select *, prod_category_3 as prod_category from data_product
                            where inf_org_id='{self.org_id}' and inf_is_deleted = FALSE"""
                df = self.db.select_rows_dict(query)
            elif dataframe == 'data_event':
                query = f"""select * from data_event
                where inf_org_id='{self.org_id}' and inf_is_deleted = FALSE"""
                df = self.db.select_rows_dict(query)
            elif dataframe == 'data_transaction':
                query = f"""select * from data_transaction
                where inf_org_id='{self.org_id}' and inf_is_deleted = FALSE"""
                df = self.db.select_rows_dict(query)
            elif dataframe == 'data_transaction_item':
                query = f"""select * from data_transaction_item
                where inf_org_id='{self.org_id}' and inf_is_deleted = FALSE"""
                df = self.db.select_rows_dict(query)
            
            if (not df.empty):
                df_renamed = self.change_column_name(df, column_mappings[dataframe])
                dfs.append(df_renamed)

        return dfs

    # Private methods
    def rank_function(self, element):
        sorted_order = ['data_transaction', 'data_transaction_item', 'data_product', 'data_customer', 'data_event']
        return sorted_order.index(element)
    
    def answer(self, question):
        try:
            #Find appropriate colums, tables
            dataframes, columns, similar_tokens = self.find_relevant_dataframes(question)

            #Format required columns
            dataframes = list(dataframes)
            for table_name, tables in additional_tables.items():
                if table_name in dataframes:
                    for table in tables:
                        if table not in dataframes:
                            dataframes.append(table)

            dataframes = sorted(dataframes, key=self.rank_function)
            
            #Get data:
            dfs = self.query_required_data(dataframes)
            merged_df = reduce(lambda left, right: pd.merge(left, right, on=list(set(left.columns) & set(right.columns))), dfs)
            result = self.pandas_ai.run(merged_df, question)
            answer = ""

            if isinstance(result, pd.core.series.Series):
                result = result.reset_index()
                answer = {
                    'type': 'table',
                    'data': {
                        'title': 'Result',
                        'data': result.astype(str).to_dict('records')
                    }}
            elif isinstance(result, list):
                answer = {
                    'type': 'table',
                    'data': {
                        'title': 'Result',
                        'data': [{'Item': item} for item in result]
                    }}
            elif isinstance(result, np.ndarray):
                result = result.tolist()
                answer = {
                    'type': 'table',
                    'data': {
                        'title': 'Result',
                        'data': [{'Item': item} for item in result]
                    }}
            else:
                answer = {
                    'type': 'text',
                    'data': str(result)
                }

            return {
                'status': 200,
                'message': 'Answering finished',
                'data': answer
            }
        
        except Exception as error:
            print(error)
            return {
                'status': 201,
                'message': str(error),
                'message': 'Answering finished',
                'data': {
                    'type': 'text',
                    'data': str(error)
                }
            }
