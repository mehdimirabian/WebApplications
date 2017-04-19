# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

# -------------------------------------------------------------------------
# This is a sample controller
# - index is the default action of any application
# - user is required for authentication and authorization
# - download is for downloading files uploaded in the db (does streaming)
# -------------------------------------------------------------------------

def get_user_name_from_email(email):
    """Returns a string corresponding to the user first and last names,
    given the user email."""
    u = db(db.auth_user.email == email).select().first()
    if u is None:
        return 'None'
    else:
        return ' '.join([u.first_name, u.last_name])


def index():
    """
    This is your main controller.
    """
    # I am creating a bogus list here, just to have some divs appear in the
    # view.  You need to read at most 20 posts from the database, in order of
    # most recent first, and you need to return that list here.
    # Note that posts is NOT a list of strings in your actual code; it is
    # what you get from a db(...).select(...).
    posts = None
    if auth.user_id is not None:
        # The user is logged in.
        # Gets the list of all checklists for the user.
        posts = db(db.post.user_email == auth.user.email).select(
            orderby=~db.post.created_on
        )

    else:
        posts = db().select(
            orderby=~db.post.updated_on
        )


    return dict(posts=posts)




@auth.requires_login()
def edit():
    """Creates, displays, or views a new checklist:
    - If there is no checklist id, it offers a form to create a checklist.
    - If there is a checklist id, it offers a form to display a checklist.
    - If there is a checklist id, and there is an additional argument edit=true, it offers a form
      to edit or delete a checklist.
    """

    pst= None

    if request.args(0) is None:
        # request.args[0] would give an error if there is no argument 0.
        form_type = 'create'
        # We create a form for adding a new checklist item.  So far, the checklist items
        # are displayed in very rough form only.
        form = SQLFORM.factory(
            Field('post_content'),
        )

    else:
        #lets get the post
        q = ((db.post.user_email == auth.user.email) &
             (db.post.id == request.args(0)))
        pst = db(q).select().first()

        if pst is None:
            session.flash = T('Not Authorized')
            redirect(URL('default', 'index'))

        #lets update the date and time
        pst.updated_on = datetime.datetime.utcnow()
        pst.update_record()

        # is it edit form ?
        is_edit = (request.vars.edit == 'true')
        if is_edit == True:
            form_type = 'edit'

        else:
            form_type = 'view'
        #here we add the content of prexisting code
        form = SQLFORM.factory(
            Field('post_content', default=pst.post_content, writable=is_edit)
        )

    # Adds some buttons.  Yes, this is essentially glorified GOTO logic.
    button_list = []
    if form_type == 'edit':
        button_list.append(A('Cancel', _class='btn btn-warning',
                             _href=URL('default', 'edit', args=[pst.id])))
        button_list.append(A('Delete', _class='btn btn-danger',
                             _href=URL('default', 'index', vars=dict(delete='true'))))

    elif form_type == 'create':
        button_list.append(A('Cancel', _class='btn btn-warning',
                             _href=URL('default', 'index')))
    elif form_type == 'view':
        button_list.append(A('Edit', _class='btn btn-warning',
                             _href=URL('default', 'edit', args=[pst.id], vars=dict(edit='true'))))
        button_list.append(A('Back', _class='btn btn-primary',
                             _href=URL('default', 'index')))




    if form.process().accepted:
        # We have to update/insert the record.
        if form_type == 'create':
            db.post.insert(post_content=form.vars.post_content)
            logger.info("THIS IS POST CONTENT")
            session.flash = T('post added.')
        else:
            session.flash = T('Checklist edited.')
            pst.post_content = form.vars.post_content
            pst.update_record()
            pst.update_record()
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
