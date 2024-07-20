from flask import request, redirect, render_template, g

from cbr_website_beta.aws.s3.DB_Users import DB_Users
from cbr_website_beta.cbr__flask.filters.Current_User import Current_User, g_user_data
from cbr_website_beta.cbr__flask.utils.current_server import current_server

def render_page__login_required(title='Login Required'):
    template_name = '/pages/page_with_view.html'
    title         = title
    content_view  = 'includes/login_required.html'
    #title         = "Login Required"
    return render_template(template_name, content_view=content_view, title=title)

def user_profile():
    db_users      = DB_Users()
    user_data     = g_user_data()
    if user_data == {}:
        return render_page__login_required('User Profile')

    user_id      = user_data.get('username')
    db_user      = db_users.db_user(user_id)
    db_user.set_metadata_value('user_id', user_id       )           # todo: remove (for now auto convert logged in users)
    db_user.set_metadata_value('cognito_data', user_data)           # todo: remove (for now auto convert logged in users)
    profile_data = db_user.metadata()

    if request.method == 'POST':
        # Grab profile data from form
        profile_data = request.form.to_dict()

        db_user = db_users.db_user(user_id)
        db_user.set_metadata_values(profile_data)
        user_profile_uri = f"{current_server()}user/profile"
        return redirect(user_profile_uri)


    template_name = '/user/profile.html'
    form_fields = get_form_fields(profile_data)
    return render_template(template_name, user_id=user_id, profile_data=profile_data, form_fields=form_fields)

def get_form_fields(profile_data):
    form_fields        = []
    default_html_class = 'form-control ps-0 form-control-line'
    def add_fields(field_names, field_type, html_class=default_html_class):
        for field_name in field_names:
            field_value = profile_data.get(field_name,'')                 # note the next check is only needed because we changed the capitalisation of the field names (and don't want to lose user data)

            field_data = {  'name': field_name,
                            'type': field_type,
                            'value': field_value,
                            'html_class': html_class }
            form_fields.append(field_data)

    add_fields(['First name','Last name', 'Role', 'Organisation', 'Sector', 'Size of organisation', 'Country', 'Linkedin'], field_type='text'    )
    add_fields(['Additional suggested prompts for Athena, your AI advisor'                                               ], field_type='textarea')
    return form_fields