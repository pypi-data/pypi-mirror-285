from flask import render_template

from cbr_website_beta.apps.chat import blueprint
from cbr_website_beta.cbr__flask.decorators.allow_annonymous import allow_anonymous
from cbr_website_beta.config.CBR__Site_Info import cbr_site_info


@blueprint.route('/history')
@allow_anonymous
def chat_history():
    from cbr_athena.llms.storage.CBR__Chats_Storage__Local import CBR__Chats_Storage__Local
    title         = "Chat - History"
    content_view  = '/llms/chat_with_llms/history.html'
    template_name = '/pages/page_with_view.html'


    cbr_chats_storage_local = CBR__Chats_Storage__Local().setup()
    chat_ids = cbr_chats_storage_local.cached_ids()

    return render_template( template_name_or_list = template_name ,
                            content_view          = content_view  ,
                            title                 = title         ,
                            chat_ids              = chat_ids      )

@blueprint.route('/view/<chat_id>')
@allow_anonymous
def chat_view__from_chat_id(chat_id):
    title             = "Chat - View past chat"
    content_view      = '/llms/chat_with_llms/view_chat_from_chat_id.html'
    template_name     = '/pages/page_with_view.html'
    url_athena        = cbr_site_info.target_athena_url()  + '/llms/chat/completion'
    url_chat_data     = cbr_site_info.target_athena_url()  + f'/llms/chat/view?chat_id={chat_id}'
    platform = "Groq (Free)"
    provider = "1. Meta"             # "Google"
    model    = "llama3-70b-8192"  # "gemma-7b-it"

    #provider =  "Meta"
    #model    = "llama3-70b-8192"

    return render_template( template_name_or_list = template_name ,
                            content_view          = content_view  ,
                            title                 = title         ,
                            url_athena            = url_athena    ,
                            platform              = platform      ,
                            provider              = provider      ,
                            model                 = model         ,
                            chat_id               = chat_id       ,
                            url_chat_data         = url_chat_data )