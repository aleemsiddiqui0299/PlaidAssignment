from django.shortcuts import render, HttpResponse
from django.http import JsonResponse, HttpResponseRedirect
from datetime import datetime
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie,csrf_exempt
from home.models import Contact
import json

import plaid
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.model.accounts_get_request import AccountsGetRequest


from plaid.api.plaid_api import PlaidApi
from plaid import ApiClient, Configuration
from tests.integration.util import create_client


config = Configuration(host = plaid.Environment.Sandbox,
                    api_key={
                         'clientId': '6382e1227917640013138cc5',
                         'secret': '44fe151077e2f4049457df08174d5b',
                    } )

access_token = None
item_id = None

@csrf_exempt
def create_link_token(request):
     
     client = create_client()
     user = request.user  
     client_user_id = user.id
     if user.is_authenticated:
          
          request = LinkTokenCreateRequest(
          products=[Products("auth"), Products("transactions")],
          client_name="John's Finance App",
          country_codes=[CountryCode("GB")],
          language="en",
          user=LinkTokenCreateRequestUser(client_user_id=str(client_user_id)),
          )
          
          # create link token
          response = client.link_token_create(request) 
  
          return JsonResponse({'link_token' : response['link_token']})
     else :
          return HttpResponseRedirect("/")


@csrf_exempt
def exchange_public_token(request):
     
     global access_token
     client = create_client()
     public_token = request.form["public_token"]
     request = ItemPublicTokenExchangeRequest(public_token=public_token)
     response = client.item_public_token_exchange(request)
     
     access_token = response['access_token']
     item_id = response["item_id"]
     
     print("ACCESS TOKEN: "+access_token)
     print("ITEM_ID: "+item_id)
     return JsonResponse({'public_token_exchange': 'complete'})


@csrf_exempt
def get_accounts(request):
     client = create_client()
     try:
          
          request = AccountsGetRequest(
              access_token=access_token
          )
          accounts_response = client.accounts_get(request)
          
     except plaid.ApiException as e:
          response = json.loads(e.body)
          return JsonResponse({'error': {'status_code': e.status, 'display_message':
                          response['error_message'], 'error_code': response['error_code'], 'error_type': response ['error_type']}})
     return JsonResponse(accounts_response.to_dict())
  
     

def index(request):
    context = {
        'variable':"This is sent",
    }
    return render(request, 'index.jinja', context)

def about(request):
     return render(request, 'about.jinja')

def services(request):
     return render(request, 'services.jinja')

def contact(request):
     print(request.method)
     if request.method == "POST":
          password = request.POST.get("inputPassword4")
          address = request.POST.get("inputAddress")
          city = request.POST.get("inputCity")    
          contact = Contact(password = password, address = address, city=city)
          contact.save() 
     return render(request, 'contacts.jinja')

