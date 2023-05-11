from django.urls import path
from django.conf import settings
from rest_framework_jwt.views import obtain_jwt_token
from .views import *

urlpatterns = [
    path("sign-in", obtain_jwt_token),
    path("sign-up", sign_up),
    path("user-info", get_user_info),
    path("change-password", change_password),
    path("get-org-info", get_org_info),
    path("change-org-info", change_org_info),
    path("generate-secret-key", generate_secret_key)
]