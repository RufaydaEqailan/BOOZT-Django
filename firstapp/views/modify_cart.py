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


db = dbconfig.getDB()
mycollection_carts = db.carts
mycollection_users = db.users

@csrf_exempt 
def delete_one_cart(req):
    """Delete cart"""
    try:
        req_body=json.loads(req.body)
        cat_id = req_body['cat_id']
        user_id = req_body['user_id']
        if cat_id=="":
            raise ValueError
        if user_id == "":
            raise ValueError
    except:
        return HttpResponseBadRequest(JsonResponse({'msg': f'There is parameter is  missing..  '}))
    try:
        user_id = ObjectId(user_id)
    except:
        return HttpResponseBadRequest(JsonResponse({'msg': f'is not a valid ObjectId, it must be a 12-byte input or a 24-character hex string.  '}))
    try:
        cat_id=ObjectId(cat_id)
    except:
        return HttpResponseBadRequest(JsonResponse({'msg': f'is not a valid ObjectId, it must be a 12-byte input or a 24-character hex string.  '})) 
    try:
        users = mycollection_users.find_one({'_id': user_id})
        total_price=0
        total_sum=0
        for cart in users['users_carts']:
            cart = str(cart)
            try:
                query1 = {'_id': ObjectId(cart)}
                cartss = mycollection_carts.find(query1)
                if cartss:
                    carts=mycollection_carts.find_one_and_delete({"_id":cat_id},{"_id":0})
                    # if carts:
                    query = {"_id": user_id}
                    query_update = {
                        "$pull": {"users_carts": cat_id}}
                    update_user_cart = mycollection_users.update_one(query, query_update)
                    if update_user_cart.matched_count > 0:
                        return JsonResponse({'msg':f'The cart with this ID {cat_id} is delete successfully.'})
                    else:
                        return HttpResponse(JsonResponse({'msg': f'we have troubles now1{query_update}'}))
                    # else:
                    #     return HttpResponseBadRequest(JsonResponse({'msg': f'The cart with this ID {query1} is not delete .'}))
                else:
                    return HttpResponseBadRequest(JsonResponse({'msg': f'The cart with this ID {cat_id} is not exist.'}))
            except:
                return HttpResponse(JsonResponse({'msg': 'we have troubles now2'}))
        else:
            return HttpResponseBadRequest(JsonResponse({'msg': f'The user dont have carts.'}))

    except:    
        return HttpResponse(JsonResponse({'msg':f'we have troubles now3 '}))