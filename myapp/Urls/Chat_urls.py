# # myapp/Urls/Chat_urls.py
# from django.urls import path
# from myapp.Views.Chat_views import (
#     list_conversations, create_or_get_conversation,
#     create_broadcast, create_consultant_broadcast,
#     get_messages, send_message,
#     edit_message, mark_read,
#     admin_list_all_conversations, get_contactable_users,
# )

# urlpatterns = [
#     path('chat/contacts/',                          get_contactable_users,          name='chat_contacts'),
#     path('chat/conversations/',                     list_conversations,             name='list_conversations'),
#     path('chat/conversations/create/',              create_or_get_conversation,     name='create_conversation'),
#     path('chat/conversations/broadcast/',           create_broadcast,               name='create_broadcast'),
#     path('chat/conversations/consultant-broadcast/', create_consultant_broadcast,    name='consultant_broadcast'),
#     path('chat/conversations/admin/all/',           admin_list_all_conversations,   name='admin_all_conversations'),
#     path('chat/conversations/<int:conv_id>/messages/', get_messages,               name='get_messages'),
#     path('chat/conversations/<int:conv_id>/send/',     send_message,               name='send_message'),
#     path('chat/conversations/<int:conv_id>/read/',     mark_read,                  name='mark_read'),
#     path('chat/messages/<int:msg_id>/edit/',            edit_message,              name='edit_message'),
# ]



# myapp/Urls/Chat_urls.py
from django.urls import path
from myapp.Views.Chat_views import (
    list_conversations, create_or_get_conversation,
    create_broadcast, create_consultant_broadcast,
    get_messages, send_message,
    edit_message, mark_read,
    admin_list_all_conversations, get_contactable_users,
)

urlpatterns = [
    path('chat/contacts/',                          get_contactable_users,          name='chat_contacts'),
    path('chat/conversations/',                     list_conversations,             name='list_conversations'),
    path('chat/conversations/create/',              create_or_get_conversation,     name='create_conversation'),
    path('chat/conversations/broadcast/',           create_broadcast,               name='create_broadcast'),
    path('chat/conversations/consultant-broadcast/', create_consultant_broadcast,    name='consultant_broadcast'),
    path('chat/conversations/admin/all/',           admin_list_all_conversations,   name='admin_all_conversations'),
    path('chat/conversations/<int:conv_id>/messages/', get_messages,               name='get_messages'),
    path('chat/conversations/<int:conv_id>/send/',     send_message,               name='send_message'),
    path('chat/conversations/<int:conv_id>/read/',     mark_read,                  name='mark_read'),
    path('chat/messages/<int:msg_id>/edit/',            edit_message,              name='edit_message'),
]
