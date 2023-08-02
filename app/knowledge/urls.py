from django.urls import path
from django.conf import settings
from rest_framework_jwt.views import obtain_jwt_token
from .views import *

urlpatterns = [
    path("get-list-models/<model_type>", get_list_models),
    path("get-model-config/<model_type>", get_model_config),
    path("get-model-info/<model_type>/<model_id>", get_model_info),
    path("update-model/<model_type>/<model_id>", update_model_info),
    path("delete-model/<model_type>/<model_id>", delete_model),
    path("run-model/<model_type>", run_model),
    path("get-api-info/<model_type>/<model_id>", get_api_info),
    path("get-test-model-api/<model_type>/<model_id>/<item_id>", get_test_model_api),
    path("get-info-api/<model_type>/<model_id>/<item_id>", get_info_api),
    path("get-answer", get_answer),
]