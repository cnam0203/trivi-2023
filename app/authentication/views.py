from django.shortcuts import render
from rest_framework import permissions, status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils.crypto import get_random_string
from django.contrib.auth.hashers import make_password, check_password

from .models import Organization, User
from .serializers import UserSerializer, OrganizationSerializer

import json

# Create your views here.
@api_view(['GET'])
def get_user_info(request):
    try: 
        user_serializer = UserSerializer(request.user)
        email = user_serializer.data['email']
        org_id = user_serializer.data['org_id']
        org_obj = Organization.objects.get(org_id=org_id)
        org_serializer = OrganizationSerializer(org_obj)
        org_name = org_serializer.data['org_name']


        return Response({
            'status': 200,
            'message': 'Get user info successfully',
            'username': email,
            'org_name': org_name,
        })
    except Exception as error:
        return Response({
            'status': 201,
            'message': error
        })

@api_view(['GET'])
def get_org_info(request):
    try: 
        user_serializer = UserSerializer(request.user)
        org_id = user_serializer.data['org_id']
        org_obj = Organization.objects.get(org_id=org_id)
        org_serializer = OrganizationSerializer(org_obj)
        org_name = org_serializer.data['org_name']
        org_key = org_serializer.data['org_secret_key']
        org_descript = org_serializer.data['org_description']


        return Response({
            'status': 200,
            'message': 'Get org info successfully',
            'org_name': org_name,
            'org_key': org_key,
            'org_descript': org_descript
        })
    except Exception as error:
        return Response({
            'status': 201,
            'message': error
        })

@api_view(['POST'])
def change_org_info(request):
    try: 
        user_serializer = UserSerializer(request.user)
        org_id = user_serializer.data['org_id']

        body = json.loads(request.body)
        org_name = body['orgName']
        org_descript = body['orgDescript']

        Organization.objects.filter(org_id=org_id).update(org_name=org_name, org_description=org_descript)

        return Response({
            'status': 200,
            'message': 'Change info successfully',
            'org_name': org_name,
            'org_descript': org_descript
        })
    except Exception as error:
        return Response({
            'status': 201,
            'message': error
        })
    
@api_view(['POST'])
def generate_secret_key(request):
    try: 
        user_serializer = UserSerializer(request.user)
        org_id = user_serializer.data['org_id']

        org_key_encoded = get_random_string()

        Organization.objects.filter(org_id=org_id).update(org_secret_key=org_key_encoded)

        return Response({
            'status': 200,
            'message': 'Generate new key successfully',
            'org_key': org_key_encoded,
        })
    except Exception as error:
        return Response({
            'status': 201,
            'message': error
        })


@api_view(['POST'])
def change_password(request):
    try: 
        status = 201
        message = ''

        user_serializer = UserSerializer(request.user)
        password = user_serializer.data['password']
        user_id = user_serializer.data['id']

        body = json.loads(request.body)
        old_password = body['oldPassword']
        new_password = body['newPassword']
        confirmed_password = body['confirmedPassword']

        if (not check_password(old_password, password)):
            print(password)
            print(make_password(old_password))
            print(old_password)
            message = 'You provided wrong old password'
        elif (new_password != confirmed_password):
            message = 'Confirmed password must match with new password'
        else:
            status = 200
            encrypted_new_password = make_password(confirmed_password)
            User.objects.filter(pk=user_id).update(password=encrypted_new_password)
            message = 'Change password successfully'


        return Response({
            'status': status,
            'message': message,
        })
    except Exception as error:
        return Response({
            'status': 201,
            'message': error
        })


@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def sign_up(request):
    try: 
        body = json.loads(request.body)
        org_name = body['org_name']
        org_descript = body['org_descript']
        org_key_encoded = get_random_string()

        email = body['email']
        password = body['password']

        try:
            user = User.objects.get(email=email)
            return Response({
                'status': 201,
                'message': 'This email existed',
            })

        except User.DoesNotExist:
            organization = Organization(org_name=org_name, 
                                        org_description=org_descript,
                                        org_secret_key=org_key_encoded)
            organization.save()

            org_id =  organization.org_id
            encrypted_password = make_password(password)
            user = User(email=email, password=encrypted_password, org_id=org_id)
            user.save()

            return Response({
                'status': 200,
                'message': 'Create account successfully',
            })

    except Exception as error:
        return Response({
            'status': 201,
            'message': error
        })
