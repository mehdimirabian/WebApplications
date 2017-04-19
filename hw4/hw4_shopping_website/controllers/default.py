# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

# -------------------------------------------------------------------------
# Sample shopping cart implementation.
# -------------------------------------------------------------------------

import traceback
import requests

@auth.requires_login()
def index():
    """
    I am not doing anything here.  Look elsewhere.
    """
    return dict()


def get_products():
    """Gets the list of products, possibly in response to a query."""
    r = requests.get("http://luca-teaching.appspot.com/get_products")
    result = r.json()
    products = result['products']
    for p in products:
        p['desired_quantity'] = min(1, p['quantity'])
        p['cart_quantity'] = 0
    return response.json(dict(products=products, ))


def purchase_without_stripe():
    if not URL.verify(request, hmac_key=session.hmac_key):
        raise HTTP(500)
    print (request.vars.cart)
    db.orders.insert(order_json=request.vars.cart)
    return "ok"


#here I will retrieve the order_json
def get_history():
    history_list = []
    row = db().select(db.orders.ALL)
    for r in row:
        if auth.user.email == r['username']:
            d= dict(
                created_on=r.created_on,
                order_json=r.order_json
            )
            history_list.append(d)
    return response.json(dict(
        history_list=history_list,
    ))


# Normally here we would check that the user is an admin, and do programmatic
# APIs to add and remove products to the inventory, etc.
@auth.requires_login()
def product_management():
    q = db.product # This queries for all products.
    form = SQLFORM.grid(
        q,
        editable=True,
        create=True,
        user_signature=True,
        deletable=True,
        fields=[db.product.product_name, db.product.quantity, db.product.price,
                db.product.image],
        details=True,
    )
    return dict(form=form)


@auth.requires_login()
def view_orders():
    q = db.customer_order # This queries for all products.
    db.customer_order.customer_info.represent = lambda v, r: nicefy(v)
    db.customer_order.cart.represent = lambda v, r: nicefy(v)
    form = SQLFORM.grid(
        q,
        editable=True,
        create=True,
        user_signature=True,
        deletable=True,
        details=True,
    )
    return dict(form=form)


def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    also notice there is http://..../[app]/appadmin/manage/auth to allow administrator to manage users
    """
    return dict(form=auth())


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


