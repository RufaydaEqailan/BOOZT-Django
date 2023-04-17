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


@csrf_exempt
def add_user(req):
    """Add new user"""
    if req.method == 'POST':
        try:
            req_body = json.loads(req.body)
            users_name = req_body['name']
            users_email = req_body['email']
            users_password = req_body['password']
            users_status = req_body['status']
            users_online = ""
            users_carts = []
            users_payment_methods = req_body['payment']
            users_regiterd_at = ""
            users_credit_card = req_body['cridtcard']
        except:
            return HttpResponseBadRequest(JsonResponse({'msg': f'There is parameter missing  '}))

        newuser = {
            'users_name': users_name,
            'users_email': users_email,
            'users_password': users_password,
            'users_status': users_status,
            'online':users_online,
            'users_carts': users_carts,
            'users_payment_methods': users_payment_methods,
            'users_regiterd_at': datetime.datetime.now(),
            'users_credit_card': users_credit_card
        }
        uservalidation = user_validator.validate(newuser)
        emailvalidation = email_validator.validate({'users_email': users_email})
        if uservalidation == True:
            if emailvalidation == True:
                if len(users_credit_card) == 16:
                    part_one = users_credit_card[0:4]
                    part_two = users_credit_card[4:8]
                    part_three = users_credit_card[8:12]
                    part_four = users_credit_card[12:16]
                    users_credit_card = part_one+" "+part_two+" "+part_three+" "+part_four
                    try:
                        add_new_user = mycollection_users.insert_one(newuser)
                        if add_new_user.inserted_id:
                            return JsonResponse({'msg': f'user with this {users_name} is added successfully.'})
                    except:
                        return HttpResponseServerError({'msg': 'We are having troubles now.'})
                else:
                    return HttpResponseBadRequest(JsonResponse({'msg': "The cridet card is wrong (Less\More) 16 Digit ..  "}))
            else:
                return HttpResponseBadRequest(JsonResponse({'msg': email_validator.errors}))
        else:
            return HttpResponseBadRequest(JsonResponse({'msg': user_validator.errors}))
    else:
        return HttpResponseServerError({'msg': 'We are having troubles now.'})


@csrf_exempt 
def show_user(req):
    """User information"""
    try:
        req_body = json.loads(req.body)
        user_id = req_body['id']
        if user_id == "":
            raise ValueError
    except:
        return HttpResponseBadRequest(JsonResponse({'msg': f'There is parameter is  missing..  '}))
    try:
        user_id = ObjectId(user_id)
    except:
        return HttpResponseBadRequest(JsonResponse({'msg': f'is not a valid ObjectId, it must be a 12-byte input or a 24-character hex string.  '}))
    try:   
        users = mycollection_users.find({'_id': user_id})
        users=list(users)
        user_list=[]
        for user in users:
            cart_list = []
            for cart in user['users_carts']:
                cart = str(cart)
                cart_list.append(cart)
            else:
                user['users_carts'] = cart_list
            payment_list=[]
            for payment in user['users_payment_methods']:
                payment_list.append(payment) 
            else:
                user['users_payment_methods']=payment_list
                payment_list=[]
            user_dic={
                'user ID':str(user['_id']),
                'name': user['users_name'],
                'email': user['users_email'],
                'status': user['users_status'],
                'password': user['users_password'],
                'online': user['users_online'],
                'carts': user['users_carts'],
                'payment methods': user['users_payment_methods'],
                'regiterd at': user['users_regiterd_at'],
                'credit card': user['users_credit_card'],
            }
            user_list.append(user_dic)
        return JsonResponse({'msg':user_list})
    except:
        return HttpResponseServerError({'msg':'We are having troubles now.'})
    
    
@csrf_exempt 
def show_payment_methods(req):
    """show payment methods for user"""
    try:
        req_body = json.loads(req.body)
        user_id = req_body['id']
        if user_id == "":
            raise ValueError
    except:
        return HttpResponseBadRequest(JsonResponse({'msg': f'There is parameter is  missing..  '}))
    try:
        user_id = ObjectId(user_id)
    except:
        return HttpResponseBadRequest(JsonResponse({'msg': f'is not a valid ObjectId, it must be a 12-byte input or a 24-character hex string.  '}))
    try:
        users = mycollection_users.find({'_id': user_id})
        users=list(users)
        user_list=[]
        for user in users:
            user_dic={
                'user name':user['users_name'],
                'payment methods': user['users_payment_methods']
            }
            user_list.append(user_dic)
        return JsonResponse({'msg':user_list})
    except:
        HttpResponseServerError({'msg':'We are having troubles now.'})   
        

@csrf_exempt
def search_by_value(req):
    """search parameter value user """
    try:
        req_body = json.loads(req.body)
        user_id = req_body['id']
        cat_name = req_body['Category']
        if user_id == "":
            raise ValueError
        if cat_name == "":
            raise ValueError
    except:
        return HttpResponseBadRequest(JsonResponse({'msg': f'The Category or the value you typing is not correct..  '}))
    try:
        user_id = ObjectId(user_id)
    except:
        return HttpResponseBadRequest(JsonResponse({'msg': f'is not a valid ObjectId, it must be a 12-byte input or a 24-character hex string.  '}))
    try:
        if cat_name.lower() == "carts":
            users = mycollection_users.find({'_id': user_id})
            users = list(users)
            if users:
                cart_list = []
                user_list = []
                for user in users:
                    for cart in user['users_carts']:
                        cart = str(cart)
                        cart_list.append(cart)
                    else:
                        user['users_carts'] = cart_list
                        cart_list = []
                        user_dic = {
                            'user ID': str(user['_id']),
                            'name': user['users_name'],
                            'carts': user['users_carts']
                        }
                        user_list.append(user_dic)
                return JsonResponse({'msg': user_list})
            else:
                return HttpResponseBadRequest(JsonResponse({'msg': 'There is no users have this ID'}))
        else:
            users = mycollection_users.find({'_id': user_id})
            if users:
                users = list(users)
                if users:
                    users_list = []
                    for user in users:
                        user_dic = {
                            "id": str(user['_id']),
                            "name": user['users_name'],
                        }
                        users_list.append(user_dic)
                    return JsonResponse({'msg': users_list})
                else:
                    return HttpResponseBadRequest(JsonResponse({'msg': 'There is no users'}))
    except:
        return HttpResponseServerError({'msg': 'We are having troubles now.'})


@csrf_exempt
def set_old_user(req):
    """Set an status 'terminated' for all users accounts where Online < some value - Deactive acount"""
    try:
        req_body = json.loads(req.body)
        user_id = req_body['id']
        if user_id == "":
            raise ValueError
    except:
        return HttpResponseBadRequest(JsonResponse({'msg': f'The date you enter is (Less\More) 10 Digit - YYY MM-DD..  '}))
    try:
        user_id = ObjectId(user_id)
    except:
        return HttpResponseBadRequest(JsonResponse({'msg': f'is not a valid ObjectId, it must be a 12-byte input or a 24-character hex string.  '}))

    try:
        myquery = {'_id': user_id}
        newvalues = {"$set": {"users_status": "terminated"}}
        result = mycollection_users.update_many(myquery, newvalues)
        if result.matched_count > 0:
            return JsonResponse({'msg': f'The new status :terminated for user acount   is updated successfully'})
        else:
            return JsonResponse({'msg': f'{result.matched_count}  are updated not  successfully'})
    except:
        return HttpResponseServerError(JsonResponse({'msg': 'we are having troubles now.'}))
 
 
@csrf_exempt
def login_user(req):
    """Login User"""
    try:
        req_body = json.loads(req.body)
        user_email = req_body['email']
        user_password = req_body['password']
        if user_email == "" or user_password == "":
            raise ValueError
    except:
        return HttpResponseBadRequest(JsonResponse({'msg': f'There is parameter is  missing..  '}))
    try:
        email_pattern = "([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+"
        if re.search(email_pattern, user_email) == None:
            raise ValueError
    except:
            return HttpResponseBadRequest(JsonResponse({'msg': "Not valid email formate , must be like this formate: name.surname@gmail.com"}))
    try:   
        users = mycollection_users.find_one({ 'users_email': user_email, 'users_password':user_password})
        if users:
            user_id = users['_id']
            query = {"_id": user_id}
            newvalues = {"$set": {"users_online": datetime.datetime.now()}}
            users = mycollection_users.update_one(query, newvalues)
            if users.matched_count > 0:
                return JsonResponse({'msg': f' User is login successfully'})
            else:
                return HttpResponseBadRequest(JsonResponse({'msg': "There is something wrong  happend... Try again later"}))
        else:
            return HttpResponseBadRequest(JsonResponse({'msg': "Email or Password is wrong."}))
    except:
        return HttpResponseServerError({'msg':'We are having troubles now.'})
    

@csrf_exempt
def logout_user(req):
    """Logout User"""
    try:
        req_body = json.loads(req.body)
        user_email = req_body['email']
        user_password = req_body['password']
        if user_email == "" or user_password == "":
            raise ValueError
    except:
        return HttpResponseBadRequest(JsonResponse({'msg': f'There is parameter is  missing..  '}))
    try:
        email_pattern = "([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+"
        if re.search(email_pattern, user_email) == None:
            raise ValueError
    except:
            return HttpResponseBadRequest(JsonResponse({'msg': "Not valid email formate , must be like this formate: name.surname@gmail.com"}))
    try:   
        users = mycollection_users.find_one({ 'users_email': user_email, 'users_password':user_password})
        if users:
            user_id = users['_id']
            query = {"_id": user_id}
            newvalues = {"$set": {"users_offline": datetime.datetime.now()}}
            users = mycollection_users.update_one(query, newvalues)
            if users.matched_count > 0:
                return JsonResponse({'msg': f' User is logout successfully '})
            else:
                return HttpResponseBadRequest(JsonResponse({'msg': "There is something wrong  happend... Try again later"}))
        else:
            return HttpResponseBadRequest(JsonResponse({'msg': "Email or Password is wrong."}))
    except:
        return HttpResponseServerError({'msg':'We are having troubles now.'})