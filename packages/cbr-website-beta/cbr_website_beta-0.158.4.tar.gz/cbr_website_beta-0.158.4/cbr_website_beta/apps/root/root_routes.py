from enum import Enum

from flask import render_template, redirect, Response, request

from cbr_website_beta.apps.llms.LLMs__Platforms import LLMs__Platforms
from cbr_website_beta.config.CBR__Config__Data                         import cbr_config, CBR__Config
from cbr_website_beta.apps.llms.Initial_Message                 import Initial_Message
from cbr_website_beta.apps.llms.Prompt_Examples                 import Prompt_Examples
from cbr_website_beta.apps.llms.System_Prompt                   import System_Prompt
from cbr_website_beta.apps.llms.llms_routes                     import user_data_for_prompt, current_user_data
from cbr_website_beta.apps.root                                 import blueprint
from cbr_website_beta.apps.user.user_profile                    import render_page__login_required
from cbr_website_beta.cbr__flask.decorators.allow_annonymous    import allow_anonymous
from cbr_website_beta.config.CBR__Site_Info                     import cbr_site_info
from cbr_website_beta.utils.Version                             import Version
from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Files import folder_create, folder_exists


@blueprint.route('/version')
@allow_anonymous
def version():
    version = Version().value()         # get this value dynamically (which useful in some live customisation and debugging sessions)
    return Response(version, content_type='text/plain')

@blueprint.route('/home')
@blueprint.route('/home.html')
@allow_anonymous
def home():
    user_data       = current_user_data()
    title           = 'Welcome'
    first_name      = user_data.get('First name','')
    last_name       = user_data.get('Last name' ,'')
    content_view    = 'includes/home.html'

    template_name = '/pages/page_with_view.html'
    return render_template(template_name_or_list = template_name,
                           title                 =  title       ,
                           content_view          = content_view ,
                           first_name            = first_name   ,
                           last_name             = last_name    )


@blueprint.route('/athena')
@allow_anonymous
def athena():
    user_data = user_data_for_prompt()
    title     = 'Athena'
    if user_data or cbr_config.login_disabled():
        url_athena       = cbr_site_info.target_athena_url() + '/open_ai/prompt_with_system__stream'  # todo: refactor into helper method
        content_view     = '/llms/open_ai/chat_bot_ui.html'
        template_name    = '/pages/page_with_view.html'
        examples_title   = 'Prompt examples'
        platform         = "OpenAI (Paid)"
        provider         = "OpenAI"
        model            =  "gpt-4o" # "gpt-3.5-turbo"

        return render_template( template_name_or_list = template_name               ,
                                content_view          = content_view                ,
                                examples_texts        = Prompt_Examples().athena()  ,        # todo: refactor to not need to call Prompt_Examples() on all calls
                                examples_title        = examples_title              ,
                                initial_message       = Initial_Message().athena()  ,         # todo: refactor to not need to call Prompt_Examples() on all calls
                                system_prompt         = System_Prompt().athena()    ,
                                title                 = title                       ,
                                url_athena            = url_athena                  ,
                                user_data             = user_data                   ,
                                platform              = platform                    ,
                                provider              = provider                    ,
                                model                 = model                       )
    else:
        return render_page__login_required(title)

########### llms-chat ###########



@blueprint.route('/chat-with-llms')
@allow_anonymous
def llms_chat():
    llms_platforms    = LLMs__Platforms()
    current_language  = request.args.get('lang', 'en').lower()
    url_athena        = cbr_site_info.target_athena_url()  + '/llms/chat/completion'
    title             = "Chat with Multiple LLMs (with no system prompt)"
    content_view      = '/llms/chat_with_llms/multiple-llms.html'
    template_name     = '/pages/page_with_view.html'
    examples_title    = 'Prompt examples'
    system_prompt     = ""
    languages = { 'en': 'English'  ,
                  'pt': 'Português'}
    if current_language == 'pt':
        system_prompt = "You are speaking to a native Portuguese speaker. so all responses should be in Portuguese"
    initial_language = Initial_Message().chat_with_llms(current_language)
    platform = "Groq (Free)"
    provider = "Google"
    model    = "gemma-7b-it"

    return render_template( template_name_or_list = template_name                       ,
                            content_view          = content_view                        ,
                            examples_texts        = Prompt_Examples().chat_with_llms()  ,        # todo: refactor to not need to call Prompt_Examples() on all calls
                            examples_title        = examples_title                      ,
                            initial_message       = initial_language                    ,         # todo: refactor to not need to call Prompt_Examples() on all calls
                            current_language      = current_language                    ,
                            title                 = title                               ,
                            url_athena            = url_athena                          ,
                            languages             = languages                           ,
                            model_options         = llms_platforms.model_options()      ,
                            system_prompt         = system_prompt                       ,
                            platform              = platform                            ,
                            provider              = provider                            ,
                            model                 = model                               )

@blueprint.route('/chat/single')
@allow_anonymous
def chat_simple():
    title             = "Chat - Simple View"
    content_view      = '/llms/chat_with_llms/single.html'
    template_name     = '/pages/page_with_view.html'
    url_athena        = cbr_site_info.target_athena_url()  + '/llms/chat/completion'

    platform = "Ollama (Local)"     # todo: refactor to LLM config object
    platform = "Groq (Free)"
    provider = "Meta" #"Google"
    model    = "llama3-70b-8192"  #"gemma-7b-it"

    #provider =  "Meta"
    #model    = "llama3-70b-8192"

    return render_template( template_name_or_list = template_name ,
                            content_view          = content_view  ,
                            title                 = title         ,
                            url_athena            = url_athena    ,
                            platform              = platform      ,
                            provider              = provider      ,
                            model                 = model         )


@blueprint.route('/chat/three-llms')
@allow_anonymous
def chat_with_three_llms():
    title         = "Chat - Three Llms"
    content_view  = '/llms/chat_with_llms/three-llms.html'
    template_name =  "/pages/page_with_view-no-menu.html"

    return render_template( template_name_or_list = template_name ,
                            content_view          = content_view  ,
                            title                 = title         )

@blueprint.route('/chat/six-languages')
@allow_anonymous
def chat_with_three_system_prompts():
    title         = "Chat - Six Languages"
    content_view  = '/llms/chat_with_llms/three-system-prompts.html'                # todo swap this content with six-languages.html
    template_name =  "/pages/page_with_view-no-menu.html"

    return render_template( template_name_or_list = template_name ,
                            content_view          = content_view  ,
                            title                 = title         )


@blueprint.route('/chat/three-system-prompts')
@allow_anonymous
def chat_in_six_languages():
    title         = "Chat - Three System Prompts"
    content_view  = '/llms/chat_with_llms/six-languages.html'
    template_name =  "/pages/page_with_view-no-menu.html"

    return render_template( template_name_or_list = template_name ,
                            content_view          = content_view  ,
                            title                 = title         )

@blueprint.route('/chat/three-board-members')
@allow_anonymous
def chat_to_three_board_members():
    title         = "Chat - Three Board Members"
    content_view  = '/llms/chat_with_llms/three-board-members.html'
    template_name =  "/pages/page_with_view-no-menu.html"

    return render_template( template_name_or_list = template_name ,
                            content_view          = content_view  ,
                            title                 = title         )

@blueprint.route('/chat/three-execs-personas')
@allow_anonymous
def chat_to_three_execs_personas():
    title         = "Chat - Three Exec's Personas"
    content_view  = '/llms/chat_with_llms/three-execs-personas.html'
    template_name =  "/pages/page_with_view-no-menu.html"

    return render_template( template_name_or_list = template_name ,
                            content_view          = content_view  ,
                            title                 = title         )


@blueprint.route('/chat/three-plus-one-llms')
@allow_anonymous
def chat_to_three_plus_one_llms():
    title         = "Chat - History"
    content_view  = '/llms/chat_with_llms/three-plus-one-llms.html'
    template_name =  "/pages/page_with_view-no-menu.html"

    return render_template( template_name_or_list = template_name ,
                            content_view          = content_view  ,
                            title                 = title         )

