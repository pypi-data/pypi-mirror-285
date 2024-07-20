import os

from flask import render_template, g

from cbr_website_beta.config.CBR__Config__Data                         import cbr_config
from cbr_website_beta.apps.llms                                 import blueprint
from cbr_website_beta.apps.llms.Prompt_Examples                 import Prompt_Examples
from cbr_website_beta.aws.s3.DB_Users                           import DB_Users
from cbr_website_beta.cbr__flask.decorators.allow_annonymous    import admin_only
from cbr_website_beta.config.CBR__Site_Info import cbr_site_info

EXPECTED_ROUTES__LLMS = ['/llms/dev/just-chat-ui'     ,
                         '/llms/dev/multiple-athenas' ,
                         '/llms/dev/no-system-prompt' ]
INTRO_TO_USER_DATA     = "We have asked the user to provide some information and included below is the data provided, please customise the answers as much as possible to these user preferences:\n"


@blueprint.route('/dev/no-system-prompt')
@admin_only
def no_system_prompt():
    kwargs = dict(examples_title        = 'Prompt examples'                                          ,
                  examples_texts        = Prompt_Examples().no_system_prompt()                       ,  # todo: improve caching of Prompt_Examples
                  title                 = "Dev | FMs with no system prompt"                          ,
                  url_athena            = cbr_site_info.target_athena_url() + '/open_ai/prompt_with_system__stream',  # todo: refactor into helper method
                  content_view          = '/llms/dev/no_prompt.html'                                 ,
                  template_name_or_list = '/pages/page_with_view.html'                               )
    return render_template(**kwargs)

@blueprint.route('/dev/just-chat-ui')
@admin_only
def just_chat_ui():
    kwargs = dict(examples_title        = 'Just Chat UI',
                  examples_texts        = Prompt_Examples().no_system_prompt(),  # todo: improve caching of Prompt_Examples
                  title                 = "Dev | FMs with no system prompt",
                  url_athena            = cbr_site_info.target_athena_url(),
                  content_view          = '/llms/dev/no_prompt.html',
                  template_name_or_list = '/layouts/empty-page.html')
    return render_template(**kwargs)

@blueprint.route('/dev/multiple-athenas')
@admin_only
def multiple_athenas():
    kwargs = dict(examples_title='Prompt examples',
                  examples_texts=Prompt_Examples().no_system_prompt(),  # todo: improve caching of Prompt_Examples
                  title="Athena (model 4.5)",
                  url_athena=cbr_site_info.target_athena_url() + '/open_ai/prompt_with_system__stream',
                  content_view='/llms/dev//multiple-athenas.html',
                  #template_name_or_list='/pages/page_with_view.html',
                  template_name_or_list='/layouts/just-top-banner.html'
                  )
    return render_template(**kwargs)
    #return render_template('/llms/open_ai/osbot_llm.html', user_data=user_data_for_prompt())



# previous version of the routes

# @blueprint.route('/chat-gpt/ui-simple')
# def ui_simple():
#     questions = ['hi', 'who are you?', 'what questions should I ask my CISO?', 'do you have siblings?']
#     return render_template('llms/chat_gpt/ui_simple.html', questions=questions)
#
# @blueprint.route('/chat-gpt/ui-with-prompts')
# def ui_with_prompts():
#     athena_rest_api = Athena_Rest_API()
#     athena_prompt   = athena_rest_api.athena_prompt()
#
#     questions     = ['hi', 'who are you?', 'what questions should I ask my CISO?', 'do you have siblings?']
#     user_data     = user_data_for_prompt()
#     system_prompt = athena_prompt
#     return render_template('llms/chat_gpt/ui_with_prompts.html', questions=questions, user_data=user_data, system_prompt=system_prompt)
#
# @blueprint.route('/chat-gpt/prompt', methods=['POST'])
# def prompt():
#     open_api     = API_Open_AI()
#     request_form = request.form.to_dict()
#     prompt       = request_form.get('prompt')
#     answer       = open_api.ask_athena_one_question(prompt)
#     ui_data      = {'response':answer}
#     return jsonify(ui_data)
#
# @blueprint.route('/chat-gpt/question-with-prompt', methods=['POST'])
# def question_with_prompt():
#     request_form  = request.form.to_dict()
#     user_data     = request_form.get('user_data'    )
#     user_question = request_form.get('user_question')
#     system_prompt = request_form.get('system_prompt')
#     user_history  = json_parse(request_form.get('user_history' , "[]"))
#     #user_history = []
#
#     #full_prompt = f"---SYSTEM--PROMPT---\n\n {system_prompt}\n\n ---USER--QUESTION---\n\n {user_question}\n\n ---USER--DATA---\n\n {user_data}\n\n"
#     print('user_history', user_history)
#     open_api = API_Open_AI()
#     answer = open_api.ask_question_with_user_data_and_prompt(user_question, user_data, system_prompt, user_history)
#     #system_prompt = replace(system_prompt, '\n', '<br/>')
#     answer = replace(answer, '\n', '<br/>')
#     ui_data      = {'response': answer}
#     return jsonify(ui_data)


# def user_data_for_prompt():
#     raw_user_data = current_user_data()
#     vars_to_add = ['user_id', 'name', 'title', 'email', 'organisation', 'sector', 'size of organisation', 'country', 'linkedin', 'Profile', 'Prompt Helper']
#     user_data = f"This is info about the user from its profile:\n"
#     for var in vars_to_add:
#         value = raw_user_data.get(var)
#         if value:
#             user_data += f"\n{var}: {value}"
#     return user_data




def user_data_for_prompt():
    raw_user_data = current_user_data()
    if raw_user_data == {} or raw_user_data.get('user_id') is None:
        return ""
    vars_to_add = [
        'First name', 'Last name', 'Role', 'Organisation',
        'Sector', 'Size of organisation', 'Country', 'Linkedin',
        'Additional suggested prompts for Athena, your AI advisor' ]

    # Determine the longest variable name for proper alignment
    longest_var = max(len(var) for var in vars_to_add)

    lines_of_data = [INTRO_TO_USER_DATA]

    # Format the data into a readable list, aligned in columns
    for var in vars_to_add:
        value = raw_user_data.get(var)
        if value:
            # Capitalize each word in var_name for better presentation
            var_name_capitalized = ' '.join(word.capitalize() for word in var.split())
            # Align the data with the longest variable name
            line = f"{var_name_capitalized:<{longest_var + 2}}: {value}"
            lines_of_data.append(line)

    # Join the lines into a single string with newline separation
    user_data = "\n".join(lines_of_data)
    return user_data


def current_user_data():
    if cbr_config.login_disabled():
        return {}
    db_users = DB_Users()
    #user_data = Current_User().user_data()
    user_data = g.user_data
    user_id = user_data.get('username')
    if user_id:
        db_user = db_users.db_user(user_id)
        if db_user.exists() is False:
            print(f"Creating user: {user_id}")
            db_user.create()
        return db_user.metadata()
    return {}





