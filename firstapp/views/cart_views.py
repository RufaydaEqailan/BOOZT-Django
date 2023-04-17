# from django.shortcuts import render
import json
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest, HttpResponseServerError
from django.http.response import JsonResponse
import dbconfig
import pdb
import datetime
import re
from django.views.decorators.csrf import csrf_exempt
from bson import ObjectId
from geopy.geocoders import Nominatim
from time import sleep
from pymongo import DESCENDING
from pymongo.operations import IndexModel
from ..models import cart_validator
from cerberus import Validator

db = dbconfig.getDB()
mycollection_carts = db.carts
mycollection_users = db.users
mycollection_products=db.product


@csrf_exempt
def show_carts(req):
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
        users = list(users)
        user_list = []
        for user in users:
            all_cart_list = []
            for cart in user['users_carts']:
                cart = str(cart)
                try:
                    carts = mycollection_carts.find({'_id':ObjectId(cart)}, {'cart_status': 1, 'cart_total_price': 1,
                                                    'cart_discount': 1, 'cart_payment_methods': 1, 'cart_products':1, '_id': 1})
                    prod_list = []
                    cart_list=[]
                    for cart in carts:
                        for product in cart['cart_products']:
                            prod_dic = {
                                'product ID': str(product['pro_id']),
                                'product quantity': product['pro_qua'],
                                'product price': product['prodcts_price']
                            }
                            prod_list.append(prod_dic)
                        else:
                            cart['cart_products'] = prod_list
                            prod_list = []
                            cart_dic = {
                                'cart ID': str(cart['_id']),
                                'status': cart['cart_status'],
                                'total price': cart['cart_total_price'],
                                'discount': cart['cart_discount'],
                                'products': cart['cart_products']
                            }
                            cart_list.append(cart_dic)
                            all_cart_list.append(cart_list)
                except:
                    return HttpResponseServerError({'msg': 'We are having troubles now.'})
            
            return JsonResponse({f'carts for user id {user_id}': all_cart_list})
    except:
        return HttpResponseServerError({'msg': 'We are having troubles now.'})


@csrf_exempt
def delete_carts(req):
    """Clear carts list"""
    try:
        req_body = json.loads(req.body)
        user_id = req_body['id']
        if user_id == "":
            raise ValueError
    except:
        return HttpResponseBadRequest(JsonResponse({'msg': f'The id is missing..  '}))
    try:
        user_id = ObjectId(user_id)
    except:
        return HttpResponseBadRequest(JsonResponse({'msg': f'is not a valid ObjectId, it must be a 12-byte input or a 24-character hex string.  '}))
    try:
        user = mycollection_users.find_one({'_id': user_id})
        if user:
            user['_id'] = str(user['_id'])
            for cart in user['users_carts']:
                cart = str(cart)
                carts = mycollection_carts.find_one({'_id':  ObjectId(cart)})
                if carts:
                    cart_del = mycollection_carts.find_one_and_delete({'_id': ObjectId(cart)})
                    if cart_del:
                        continue
                    else:
                        return HttpResponseBadRequest(JsonResponse({'msg': f'this cart with this ID {cart} not deleted  '}))
                else:
                    return HttpResponseBadRequest(JsonResponse({'msg': f'The cart with this ID {cart} is not exist .'}))
            else:
                query = {"_id": user_id}
                newvalues = {"$set": {"users_carts": []}}
                users = mycollection_users.update_one(query, newvalues)
                if users.matched_count > 0:
                    return JsonResponse({'msg': f'All carts for user id {user_id} are deleted successfully'})
                else:
                    return HttpResponseBadRequest(JsonResponse({'msg': "There is something wrong  happend... Try again later"})) 
        else:
            return HttpResponse(JsonResponse({'msg': 'this user is not exist'}))
    except:
        return HttpResponse(JsonResponse({'msg': 'we have troubles now'}))
    
    
@csrf_exempt
def set_old_carts(req):
    """Set an status 'pending to abandon ' for all carts  where date < some value"""
    try:
        req_body = json.loads(req.body)
        user_id = req_body['id']
        cart_id = req_body['cart']
        if user_id == "":
            raise ValueError
        if cart_id == "":
            raise ValueError
    except:
        return HttpResponseBadRequest(JsonResponse({'msg': f'Missing parameter or the date you enter is (Less\More) 10 Digit - YYY MM-DD..  '}))
    try:
        user_id = ObjectId(user_id)
    except:
        return HttpResponseBadRequest(JsonResponse({'msg': f'is not a valid user ObjectId, it must be a 12-byte input or a 24-character hex string.  '}))
    try:
        cart_id = ObjectId(cart_id)
    except:
        return HttpResponseBadRequest(JsonResponse({'msg': f'is not a valid cart ObjectId, it must be a 12-byte input or a 24-character hex string.  '}))
    try:
        user=mycollection_users.find_one({'_id':user_id})
        if user:
            carts = mycollection_users.find_one({'users_carts': {"$in": [cart_id]}})
            if carts:
                myquery = {"_id": cart_id, "cart_status": "pending"}
                newvalues = {"$set": {"cart_status": "abandon",
                                    "cart_abandoned_date": datetime.datetime.now(), "cart_paid_date": ""}}
                cart = mycollection_carts.update_many(myquery, newvalues)
                if cart.matched_count > 0:
                    return JsonResponse({'msg': f'The new status :abandon for  cart which has ID  : {cart_id} carts  are updated successfully'})
                else:
                    return JsonResponse({'msg': f'{cart.matched_count} carts  are updated   successfully'})
            else:
                
                return HttpResponseServerError(JsonResponse({'msg': 'This cart is not for this user'}))
    except:
        return HttpResponseServerError(JsonResponse({'msg': 'we are having troubles now.'}))


@csrf_exempt
def show_by_status(req):
    """search status for carts"""
    try:
        req_body = json.loads(req.body)
        user_id = req_body['id']
        cat_value = req_body['status']
        if user_id == "":
            raise ValueError
        if cat_value == "":
            raise ValueError
    except:
        return HttpResponseBadRequest(JsonResponse({'msg': f'Missing parameter or The Status or the value you typing is not correct..  '}))
    try:
        user_id = ObjectId(user_id)
    except:
        return HttpResponseBadRequest(JsonResponse({'msg': f'is not a valid user ObjectId, it must be a 12-byte input or a 24-character hex string.  '}))
    try:
        user = mycollection_users.find_one({'_id': user_id})
        if user:
            user['_id'] = str(user['_id'])
            all_user_carts=[]
            for cart in user['users_carts']:
                cart = str(cart)
                available_status = ["paid", "abandon", "pending"]
                if cat_value in available_status:
                    query = {'_id':  ObjectId(cart), "cart_status": cat_value}
                    carts = mycollection_carts.find_one(query)
                    if carts:
                        carts_list = []
                        products_list = []
                        for products in carts['cart_products']:
                            prod_dic = {
                                "product ID": str(products["pro_id"]),
                                "product quantity": products["pro_qua"],
                                "products price": products["prodcts_price"]
                            }
                            products_list.append(prod_dic)
                        else:  
                            carts['cart_products'] = products_list
                            products_list = []
                            cart_dic = {
                                "id": str(carts['_id']),
                                "cart total price": carts['cart_total_price'],
                                "cart status": cat_value,
                                "cart products": carts['cart_products']
                            }
                            all_user_carts.append(cart_dic)   
                    else:
                        continue
                else:
                    return HttpResponseBadRequest(JsonResponse({'msg': 'This status is wrong [ paid , abandon , pending]'}))
            else:
                return JsonResponse({f'The carts for this user ID {user_id} with status {cat_value} ': all_user_carts})
        else:
            return HttpResponseBadRequest(JsonResponse({'msg': f'The user with this ID {user_id} is not exist .'}))
    except:
        return HttpResponseServerError(JsonResponse({'msg': 'we are having troubles now.'}))


@csrf_exempt
def search_by_value(req):
    """search parameter value cart """
    try:
        req_body = json.loads(req.body)
        user_id = req_body['id']
        prod_id = req_body['product']
        if user_id == "":
            raise ValueError
        if prod_id == "":
            raise ValueError
    except:
        return HttpResponseBadRequest(JsonResponse({'msg': f'Missing parameter or The Status or the value you typing is not correct..  '}))
    try:
        user_id = ObjectId(user_id)
    except:
        return HttpResponseBadRequest(JsonResponse({'msg': f'is not a valid user ObjectId, it must be a 12-byte input or a 24-character hex string.  '}))
    try:
        prod_id = ObjectId(prod_id)
    except:
        return HttpResponseBadRequest(JsonResponse({'msg': f'is not a valid user ObjectId, it must be a 12-byte input or a 24-character hex string.  '}))
    try:
        """sreach by cart_products"""
        user = mycollection_users.find_one({'_id': user_id})
        if user:
            user['_id'] = str(user['_id'])
            all_user_carts = []
            for cartt in user['users_carts']:
                cartt = str(cartt)
                query = {'_id': ObjectId(cartt), 'cart_products.pro_id': {"$in": [ObjectId(prod_id)]}}
                carts = mycollection_carts.find(query)
                carts = list(carts)
                if carts:
                    prod_list = []
                    cart_list = []
                    for cart in carts:
                        for product in cart['cart_products']:
                            prod_dic = {
                                'product ID': str(product['pro_id']),
                                'product quantity': product['pro_qua'],
                                'product price': product['prodcts_price']
                            }
                            prod_list.append(prod_dic)
                        else:
                            cart['cart_products'] = prod_list
                            prod_list = []
                            cart_dic = {
                                'cart ID': str(cart['_id']),
                                'status': cart['cart_status'],
                                'total price': cart['cart_total_price'],
                                'discount': cart['cart_discount'],
                                "cart products": cart['cart_products']
                            }
                            all_user_carts.append(cart_dic)
                else:
                    continue
            else:
                return JsonResponse({f'The carts for this user ID {user_id} with product ID {prod_id} ': all_user_carts})
        else:
            return HttpResponseBadRequest(JsonResponse({'msg': f'The user with this ID {user_id} is not exist .'}))
    except:
        return HttpResponseServerError({'msg': 'We are having troubles now.'})


@csrf_exempt 
def add_cart(req):
    """Add new cart"""
    if req.method=='POST':
        try:
            req_body = json.loads(req.body)
            add_products = req_body['add_products']
            cart_discount = req_body['cart_discount']
            cart_payment_methods = req_body['cart_payment_methods']
            city = req_body['city']
            pro_qua = req_body['pro_qua']
        except:
            return HttpResponseBadRequest(JsonResponse({'msg': f'There is parameter missing  '})) 
        try:
            add_products = ObjectId(add_products)
        except:
            return HttpResponseBadRequest(JsonResponse({'msg': f'is not a valid ObjectId, it must be a 12-byte input or a 24-character hex string.  '}))
        try:
            cart_products=[]
            cart_location=[]
            cart_total_price=0
            product = mycollection_products.find_one({'_id': add_products})
            if product:
                price = product['price']
                prodcts_price = price*pro_qua

                cart_dic = {
                    "pro_id": add_products,
                    "pro_qua": pro_qua,
                    "prodcts_price": prodcts_price
                }
                cart_products.append(cart_dic)
                cart_total_price = prodcts_price
                mycollection_carts.create_index(
                    [("cart_location", "2dsphere")])
                geoLoc = Nominatim(user_agent="GetLoc")
                location = geoLoc.geocode(city)
                coordinates = [int(location.latitude),
                               int(location.longitude)]
                sleep(1)
                cart_location = coordinates
            else:
                return HttpResponseBadRequest(JsonResponse({'msg': f'the product ID {add_products} is not exiest.'}))
            try:
                newcart={
                'cart_created_at': datetime.datetime.now(),
                'cart_products': cart_products,
                'cart_status':"pending",
                'cart_abandoned_date': "",
                'cart_paid_date': "",
                'cart_total_price': cart_total_price,
                'cart_discount': cart_discount,
                'cart_payment_methods': cart_payment_methods,
                'cart_location': cart_location
                }
                cartvalidation=cart_validator.validate(newcart)
                if cartvalidation==True:
                    try:
                        add_new_product=mycollection_carts.insert_one(newcart)
                        if add_new_product.inserted_id:
                            return JsonResponse({'msg':f'product to new cart is added successfully.'})
                    except:
                        return HttpResponseServerError({'msg':'We are having troubles now.'})
                    # return JsonResponse({'msg':'ok'})
                else:
                    return HttpResponseBadRequest(JsonResponse({'msg':cart_validator.errors}))
            except:
                return HttpResponseServerError({'msg':'We are having troubles now.'})
        except:
            return HttpResponseServerError({'msg': 'We are having troubles now.'})
    else:
        return HttpResponseServerError({'msg':'Method should be POST.'})     
