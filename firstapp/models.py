from django.db import models
from cerberus import Validator

# Create your models here.
user_schema = {
    "users_name": {
        'type': 'string'
    },
    "users_carts": {
        'type': 'list'
    },
    "users_payment_methods": {
        'type': 'list'
    },
    "users_credit_card": {
        'type': 'integer'
    },
    "users_password": {
        'type': 'string'
    },
    "users_status": {
        'type': 'string'
    },
    "users_email": {
        'type': 'string'
    },
    "online": {
        'type': 'string'
    },
    "users_regiterd_at": {
        'type': 'datetime'
    }
}
user_validator = Validator(user_schema, require_all=False)
email_schema = {
    "users_email": {
        "type": "string",
        "minlength": 8,
        "maxlength": 255,
        "required": True,
        "regex": "^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\\.[a-zA-Z0-9-.]+$"
    }
}
email_validator = Validator(email_schema)

product_schema = {
    "gender": {
        'type': 'string'
    },
    "masterCategory": {
        'type': 'string'
    },
    "subCategory": {
        'type': 'string'
    },
    "articleType": {
        'type': 'string'
    },
    "baseColour": {
        'type': 'string'
    },
    "season": {
        'type': 'string'
    },
    "year": {
        'type': 'integer'
    },
    "usage": {
        'type': 'string'
    },
    "productDisplayName": {
        'type': 'string'
    },
    "price": {
        'type': 'integer'
    },
    "filename": {
        'type': 'string'
    },
    "Link": {
        'type': 'string'
    },
    "old_products": {
        'type': 'boolean'
    }
}
product_validator = Validator(product_schema, require_all=False)

cart_schema = {
    "cart_created_at": {
        'type': 'datetime'
    },
    "cart_products": {
        'type': 'list'
    },
    "cart_status": {
        'type': 'string'
    },
    "cart_abandoned_date": {
        'type': 'string'
    },
    "cart_paid_date": {
        'type': 'string'
    },
    "cart_total_price": {
        'type': 'integer'
    },
    "cart_discount": {
        'type': 'integer'
    },
    "cart_payment_methods": {
        'type': 'list'
    },
    "cart_location": {
        'type': 'list'
    }
}
cart_validator = Validator(cart_schema, require_all=False)
