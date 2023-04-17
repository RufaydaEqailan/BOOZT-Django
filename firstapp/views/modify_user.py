# from django.shortcuts import render
import json
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest, HttpResponseServerError
from django.http.response import JsonResponse
import dbconfig
import pdb
import datetime
import re
from django.views.decorators.csrf import csrf_exempt
from bson import ObjectId, _encode_datetime
from ..models import user_validator, email_validator
from cerberus import Validator


db = dbconfig.getDB()  
mycollection_users = db.users
mycollection_carts=db.carts

@csrf_exempt 
def delete_one_user(req):
    """Delete user"""
    try:
        req_body=json.loads(req.body)
        cat_value=req_body['id'] 
        if cat_value=="":
            raise ValueError   
    except:
        return HttpResponseBadRequest(JsonResponse({'msg': f'The id is missing..  '})) 
    try:
        cat_value=ObjectId(cat_value)
    except:
        return HttpResponseBadRequest(JsonResponse({'msg': f'is not a valid ObjectId, it must be a 12-byte input or a 24-character hex string.  '})) 
    try:
        user=mycollection_users.find_one({'_id':cat_value})
        if user:
            user['_id'] = str(user['_id'])
            for cart in user['users_carts']:
                cart = str(cart)
                carts = mycollection_carts.find_one({'_id':  ObjectId(cart)})
                if carts:
                    cart_del=mycollection_carts.find_one_and_delete({'_id': ObjectId(cart)})
                    if cart_del:
                        continue
                    else:
                        return HttpResponseBadRequest(JsonResponse({'msg': f'this cart is {cart} not deleted  '}))
                else:
                    return HttpResponseBadRequest(JsonResponse({'msg': f'The cart with this ID {cart} is not exist .'}))
            users=mycollection_users.find_one_and_delete({"_id":cat_value},{"_id":0})
            if users:
                return JsonResponse({'msg':f'The user with this ID {cat_value} is delete successfully.'})
            else:
                return HttpResponseBadRequest(JsonResponse({'msg': f'The user with this ID {cat_value} is not delete .'}))
        else:
             return HttpResponse(JsonResponse({'msg':'this user is not exist'}))
    except:    
        return HttpResponse(JsonResponse({'msg':'we have troubles now'}))
    
    
@csrf_exempt
def modify_master_category(req):
    """modify_master_category"""
    try:
        req_body = json.loads(req.body)
        user_id = req_body['id']
        cat_name = req_body['Category']
        cat_value = req_body['Value']
        if user_id == "" or cat_name == "" or cat_value == "":
            raise ValueError
    except:
        return HttpResponseBadRequest(JsonResponse({'msg': f'There is parameter is  missing..  '}))
    try:
        user_id = ObjectId(user_id)
    except:
        return HttpResponseBadRequest(JsonResponse({'msg': f'is not a valid ObjectId, it must be a 12-byte input or a 24-character hex string.  '}))
    try:
        user = mycollection_users.find_one({'_id': user_id}, {'_id': 0})
        if user:
            if cat_name.lower() == "users_online":
                if len(cat_value) == 10:
                    try:
                        year = cat_value[:4]
                        month = cat_value[5:7]
                        day = cat_value[8:]
                        cat_value = datetime.datetime(
                            int(year), int(month), int(day))
                    except:
                        return HttpResponseBadRequest(JsonResponse({'msg': "Wrong format (YYYY-MM-DD)"}))
                else:
                    return HttpResponseBadRequest(JsonResponse({'msg': 'The date you enter is (Less\More) 10 Digit - .  '}))

            elif cat_name.lower() == "users_email":
                try:
                    email_pattern = "([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+"
                    if re.search(email_pattern, cat_value) == None:
                        raise ValueError
                except:
                        return HttpResponseBadRequest(JsonResponse({'msg': "Not valid email formate , must be like this formate: name.surname@gmail.com"}))

            elif cat_name.lower() =="users_payment_methods":
                # "payment method code goes here"
                payment_list = []
                available_methods = ["VISA","PayPal","Master"]
                if cat_value in available_methods:
                    payment_list = [cat_value]
                    cat_value = payment_list
                else:
                     return HttpResponseBadRequest(JsonResponse({'msg': f"The paymentmethod {cat_value} is not in the available payment method list [VISA,PayPal,Master] ."}))

            query = {"_id":user_id}    
            newvalues = { "$set": { cat_name: cat_value } }                        
            users = mycollection_users.update_one(query,newvalues) 
            if users.matched_count >0:     
                return JsonResponse({'msg': f' The new value : {cat_value } for a filed : {cat_name} is updated successfully")'})
            else:
                return HttpResponseBadRequest(JsonResponse({'msg': "\nThere is something wrong  happend... Try again later"}))   
        else:
            return  HttpResponseBadRequest(JsonResponse({'msg': f'The user with this ID {user_id} is not exiest.'}))
    except:
           return HttpResponse(JsonResponse({'msg': 'we have troubles now'}))
