# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

# -------------------------------------------------------------------------
# This is a sample controller
# - index is the default action of any application
# - user is required for authentication and authorization
# - download is for downloading files uploaded in the db (does streaming)
# -------------------------------------------------------------------------
import json

def get_user_name_from_email(email):
    """Returns a string corresponding to the user first and last names,
    given the user email."""
    u = db(db.auth_user.email == email).select().first()
    #u = db(db.post.email == email).select().first()
    if u is None:
        return 'None'
    else:
        return ' '.join([u.first_name, u.last_name])
        #return u



def index():
    """
    This is your main controller.
    """
    # I am creating a bogus list here, just to have some divs appear in the
    # view.  You need to read at most 20 posts from the database, in order of
    # most recent first, and you need to return that list here.
    # Note that posts is NOT a list of strings in your actual code; it is
    # what you get from a db(...).select(...).
    # The user is logged in.
    # Gets the list of all checklists for the user.
    posts = db().select(db.post.ALL, orderby=~db.post.created_on, limitby=(0,20))
    #return dict(posts=posts, names=get_user_name_from_email)
    return dict(posts=posts)


def showmore():
    posts = db().select(db.post.ALL, orderby=~db.post.created_on,limitby=(0,20))
    return response.json(posts)
    #return json.dumps([[r.id, r.FlowRate] for r in posts])

@auth.requires_login()
def edit():
    """
    This is the page to create / edit / delete a post.
    """

    if request.args(0) is None:
        # If edit() has no args, create a form for adding new post
        form_type = 'create'
        form = SQLFORM(db.post)
    else:
        # Check if the user is the author of the post to grant editing permission
        q = ((db.post.user_email == auth.user.email) &
             (db.post.id == request.args(0)))
        pt = db(q).select().first()
        if pt is None:
            session.flash = T('Permission Denied - You are not the Author')
            redirect(URL('default','index'))

        is_edit = (request.vars.edit == 'true')
        form_type = 'edit' if is_edit else 'view'
        form = SQLFORM(db.post, record=pt, deletable=is_edit, readonly=not is_edit)


    # Add buttons
    button_list = []
    if form_type == 'edit':
        button_list.append(A('Cancel', _class='btn btn-warning',
                             _href=URL('default', 'edit', args=[pt.id])))
    elif form_type == 'create':
        button_list.append(A('Cancel', _class='btn btn-warning',
                             _href=URL('default', 'index')))
    elif form_type == 'view':
        button_list.append(A('Edit', _class='btn btn-warning',
                             _href=URL('default', 'edit', args=[pt.id], vars=dict(edit='true'))))
        button_list.append(A('Back', _class='btn btn-primary',
                             _href=URL('default', 'index')))

    if form.process().accepted:
        # At this point, the record has already been inserted.
        if form_type == 'create':
            session.flash = T('Post added.')
        else:
            session.flash = T('Post edited.')
        redirect(URL('default', 'index'))
    elif form.errors:
        session.flash = T('Please enter correct values.')

    return dict(form=form, button_list=button_list)


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

def delete():
    db(db.post.id == request.args(0)).delete()
    return redirect(URL('default','index'))
