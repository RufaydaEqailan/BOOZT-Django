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
# from ..models import user_validator, email_validator
# from cerberus import Validator


db = dbconfig.getDB()
mycollection_users = db.users


@csrf_exempt
def Set_test_old_users(req):
    try:
        req_body = json.loads(req.body)
        name_value = req_body['name']
        return JsonResponse({'msg': f'{name_value}'})
    except:
        return HttpResponseBadRequest(JsonResponse(
            {'msg': f'You forget some value in the request'}))
