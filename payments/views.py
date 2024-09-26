import base64
import json
from datetime import datetime

from django.http import HttpResponse

import requests
from requests.auth import HTTPBasicAuth
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions

from mpesa_daraja import settings
from .models import Payment
from .serializers import PaymentSerializer


# Create your views here.
permissions_classes = [permissions.IsAuthenticatedOrReadOnly]

def get(self, request, *args, **kwargs):

    all_payments = Payment.objects.filter(user=request.user)
    serializer = PaymentSerializer(all_payments, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


class MpesaC2bCredentials:
    consumer_key = settings.CONSUMER_KEY
    consumer_secret = settings.CONSUMER_SECRET
    api_URL = settings.ACCESS_TOKEN_URL

class MpesaAccessToken:
    r = requests.get(MpesaC2bCredentials.api_URL, auth=HTTPBasicAuth(MpesaC2bCredentials.consumer_key, MpesaC2bCredentials.consumer_secret))
    mpesa_access_token = json.loads(r.text)
    validated_mpesa_access_token = mpesa_access_token['access_token']


class LipanaMpesaPassword:
    lipa_time = datetime.now().strftime('%Y%m%d%H%M%S')

    Business_short_code = settings.SHORT_CODE
    passkey = settings.MPESA_PASS_KEY

    data_to_encode  = Business_short_code + passkey + lipa_time
    online_password = base64.b64encode(data_to_encode.encode())
    decode_password = online_password.decode('utf-8')
    callback_url = settings.MPESA_CALLBACK_URL

def getAccessToken(request):
    consumer_key = settings.CONSUMER_KEY
    print(consumer_key)

    consumer_secret = settings.CONSUMER_SECRET
    print(consumer_secret)

    api_URL = settings.ACCESS_TOKEN_URL
    print(api_URL)

    r = requests.get(api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret))
    print(r)
    print('**************')
    mpesa_access_token = json.loads(r.text)
    validated_mpesa_access_token = mpesa_access_token['access_token']

    return HttpResponse(validated_mpesa_access_token)



class CheckoutMpesaView(APIView):
    permissions_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, *args, **kwargs):
        user = request.user
        if user.is_authenticated:
            # Show only payments for the authenticated user
            all_payments = Payment.objects.filter(user=user)
        else:
            # Show all payments for unauthenticated users
            all_payments = Payment.objects.all()

        serializer = PaymentSerializer(all_payments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        user = request.user

        if not user.is_authenticated:
            return Response({'error': 'User not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)

        # Accessing data from the request
        phoneNumber: any = request.data.get('phoneNumber')
        print(phoneNumber)
        amount = request.data.get('amount')
        print(amount)

        if not phoneNumber or not amount:
            return Response({'error': 'Missing phoneNumber or amount'}, status=status.HTTP_400_BAD_REQUEST)

        access_token = MpesaAccessToken.validated_mpesa_access_token
        api_url = settings.INITIATE_PAYMENT_URL
        print(api_url)
        headers = {'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json'}

        payload = {
            "BusinessShortCode": LipanaMpesaPassword.Business_short_code,
            "Password": LipanaMpesaPassword.decode_password,
            "Timestamp": LipanaMpesaPassword.lipa_time,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,
            "PartyA": phoneNumber,
            "PartyB": LipanaMpesaPassword.Business_short_code,
            "PhoneNumber": phoneNumber,
            "CallBackURL": LipanaMpesaPassword.callback_url,
            "AccountReference": "Briva Digital",
            "TransactionDesc": "Payment for services"
        }
        print(payload)

        # Making the request to the payment API
        response = requests.post(api_url, headers=headers, json=payload)
        print(response)

        # Handling the response
        if response.status_code == 200:
            response_data = response.json()
            transaction_id = response_data['CheckoutRequestID']
            print(transaction_id)

            data = {
                'amount': amount,
                'phoneNumber': phoneNumber,
                'responseDescription': response_data['ResponseDescription'],
                'responseCode': response_data['ResponseCode'],
                'merchantRequestID': response_data['MerchantRequestID'],
                'transactionId': transaction_id,
                'user': user.id
            }
            print(data)

            serializer = PaymentSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response("Failed to Save the data to the database")

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'Payment initiation failed', 'details': response.text}, status=response.status_code)

# def checkout_mpesa(request):
#     user = request.user
#
#     phoneNumber = request.data['phoneNumber']
#     amount = request.data['amount']
#
#     access_token = MpesaAccessToken.validated_mpesa_access_token
#     api_url = settings.INITIATE_PAYMENT_URL
#     headers = {'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json'}
#
#
#     payload = {
#         "BusinessShortCode": LipanaMpesaPassword.Business_short_code,
#         "Password": LipanaMpesaPassword.decode_password,
#         "Timestamp": LipanaMpesaPassword.lipa_time,
#         "TransactionType": "CustomerPayBillOnline",
#         "Amount": amount,
#         "PartyA": phoneNumber,
#         "PartyB": LipanaMpesaPassword.Business_short_code,
#         "PhoneNumber": phoneNumber,
#         "CallBackURL": LipanaMpesaPassword.callback_url,
#         "AccountReference": "Briva Digital",
#     }
#
#     #Making the request
#     response = requests.post(api_url, headers=headers, json=payload)
#
#     #Handling the response
#     if response.status_code == 200:
#         response_data = response.json()
#
#         transaction_id = response_data['CheckoutRequestID']
#
#         # Save to the database
#         # new_payment = Payment(
#         #     amount=amount,
#         #     phoneNumber=phoneNumber,
#         #     responseDescription=response_data['ResponseDescription'],
#         #     responseCode=response_data['ResponseCode'],
#         #     merchantRequestID=response_data['MerchantRequestID'],
#         #     transactionId=transaction_id,
#         #     user=user
#         # )
#         data = {
#             'amount': amount,
#             'phoneNumber': phoneNumber,
#             'responseDescription': response_data['ResponseDescription'],
#             'responseCode': response_data['ResponseCode'],
#             'merchantRequestID': response_data['MerchantRequestID'],
#             'transactionId': transaction_id,
#         }
#
#         serializer = PaymentSerializer(data=data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



