from django.urls import path
from django.conf import settings
from rest_framework_jwt.views import obtain_jwt_token
from .views import *

urlpatterns = [
    path("get-list-view/<item_type>", get_list_view),
    path("get-reports-analytics/<item_type>", get_reports_analytics),
    path("get-reports-kpi", get_reports_kpi),
    path("get-import-file-info/<item_type>", get_import_file_info),
    path("get-import-api-info/<item_type>", get_import_api_info),
    path("get-matching-template/<item_type>", get_matching_template),
    path("get-import-history/<item_type>", get_import_history),
    path("get-detail-template/<item_type>/<templ_id>", get_detail_template),
    path("import-csv-file/<item_type>", import_csv_file),
    path("import-data-api/<item_type>", import_data_api),
    path("import-matching-template/<item_type>", import_matching_template),
    path("update-matching-template/<item_type>/<templ_id>", update_matching_template),
    path("delete-item/<item_type>/<item_id>", delete_item),
    path("delete-import-log/<import_id>", delete_import_log)
]