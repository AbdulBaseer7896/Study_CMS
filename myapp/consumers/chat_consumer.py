"""
WebSocket consumer for real-time chat — ONE socket per user.
URL: ws://host/ws/chat/user/

Instead of one WS per conversation (which caused connection storms),
each authenticated user opens a SINGLE WebSocket. The backend pushes
ALL their conversation events through that one connection.

Auth: JWT token via query string ?token=<access_token>

Channel groups used:
  - conv_{conv_id}  → room group (all participants of that conv)

When user A sends a message in conv 5:
  1. Message saved to DB
  2. group_send → conv_5 group
  3. Every participant who is connected receives it on their single socket
"""
import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError

logger = logging.getLogger(__name__)


class ChatConsumer(AsyncWebsocketConsumer):

    # ─────────────────────────────────────────────────────────────────
    # Lifecycle
    # ─────────────────────────────────────────────────────────────────

    async def connect(self):
        self.user = None
        self.user_group = None
        self.conv_groups = set()

        user = await self._authenticate()
        if user is None:
            await self.close(code=4001)
            return

        self.user = user
        self.user_group = f"user_{user.id}"

        # Join personal inbox group
        try:
            await self.channel_layer.group_add(self.user_group, self.channel_name)
        except Exception as e:
            logger.warning(f"group_add user group failed: {e}")

        # Join all conversation groups this user participates in
        conv_ids = await self._get_user_conversation_ids()
        for cid in conv_ids:
            group = f"conv_{cid}"
            try:
                await self.channel_layer.group_add(group, self.channel_name)
                self.conv_groups.add(group)
            except Exception as e:
                logger.warning(f"group_add conv_{cid} failed: {e}")

        await self.accept()
        logger.info(f"WS connected: user={user.id}, joined {len(conv_ids)} conv groups")

    async def disconnect(self, close_code):
        if self.user_group:
            try:
                await self.channel_layer.group_discard(self.user_group, self.channel_name)
            except Exception:
                pass
        for group in list(self.conv_groups):
            try:
                await self.channel_layer.group_discard(group, self.channel_name)
            except Exception:
                pass

    async def receive(self, text_data):
        if not self.user:
            return
        try:
            data = json.loads(text_data)
        except (json.JSONDecodeError, Exception):
            return

        action = data.get('action', '')

        if action == 'send_message':
            await self._handle_send(
                conv_id=data.get('conv_id'),
                content=data.get('content', '').strip(),
            )
        elif action == 'edit_message':
            await self._handle_edit(
                message_id=data.get('message_id'),
                content=data.get('content', '').strip(),
            )
        elif action == 'mark_read':
            await self._handle_mark_read(data.get('conv_id'))
        elif action == 'join_conv':
            await self._join_conv_group(data.get('conv_id'))
        elif action == 'ping':
            await self._safe_send({'type': 'pong'})

    # ─────────────────────────────────────────────────────────────────
    # Action handlers
    # ─────────────────────────────────────────────────────────────────

    async def _handle_send(self, conv_id, content):
        if not content or not conv_id:
            return

        allowed = await self._check_access(conv_id)
        if not allowed:
            await self._safe_send({'type': 'error', 'error': 'Access denied.'})
            return

        msg, is_first = await self._create_message(conv_id, content)
        if msg is None:
            await self._safe_send({'type': 'error', 'error': 'Could not save message.'})
            return

        payload = {
            'type':         'chat_message',
            'message_id':   msg.id,
            'conversation': int(conv_id),
            'sender_id':    self.user.id,
            'sender_name':  self.user.name,
            'sender_role':  self.user.role,
            'content':      msg.content,
            'is_edited':    False,
            'created_at':   msg.created_at.isoformat(),
        }

        # Broadcast to the conversation group — all participants get it
        await self._group_send(f"conv_{conv_id}", payload)

        # Email notification for first message
        if is_first:
            try:
                from myapp.Utils.email_tasks import send_first_message_email_task
                await database_sync_to_async(send_first_message_email_task.delay)(msg.id)
            except Exception as e:
                logger.warning(f"Email task dispatch failed: {e}")

    async def _handle_edit(self, message_id, content):
        if not content or not message_id:
            return

        result = await self._edit_message(message_id, content)
        if result is None:
            await self._safe_send({
                'type': 'error',
                'error': 'Cannot edit — not your message or 5-min window expired.',
            })
            return

        conv_id = await self._get_message_conv_id(message_id)
        if not conv_id:
            return

        payload = {
            'type':         'message_edited',
            'message_id':   int(message_id),
            'content':      content,
            'is_edited':    True,
            'edited_at':    result.isoformat(),
            'conversation': int(conv_id),
        }
        await self._group_send(f"conv_{conv_id}", payload)

    async def _handle_mark_read(self, conv_id):
        if not conv_id:
            return
        try:
            await self._mark_messages_read(conv_id)
        except Exception as e:
            logger.warning(f"mark_read failed: {e}")

    async def _join_conv_group(self, conv_id):
        """Called when user creates a new conversation — join its group live."""
        if not conv_id:
            return
        group = f"conv_{conv_id}"
        if group not in self.conv_groups:
            try:
                await self.channel_layer.group_add(group, self.channel_name)
                self.conv_groups.add(group)
            except Exception as e:
                logger.warning(f"join_conv_group {conv_id} failed: {e}")

    # ─────────────────────────────────────────────────────────────────
    # Channel layer helpers
    # ─────────────────────────────────────────────────────────────────

    async def _group_send(self, group_name, payload):
        try:
            await self.channel_layer.group_send(
                group_name,
                {'type': 'broadcast_message', 'payload': payload}
            )
        except Exception as e:
            logger.warning(f"group_send to {group_name} failed: {e}")
            await self._safe_send(payload)

    async def _safe_send(self, data):
        try:
            await self.send(text_data=json.dumps(data))
        except Exception:
            pass

    async def broadcast_message(self, event):
        """Channel layer handler — called for every group_send to groups we're in."""
        await self._safe_send(event['payload'])

    # ─────────────────────────────────────────────────────────────────
    # DB operations
    # ─────────────────────────────────────────────────────────────────

    @database_sync_to_async
    def _authenticate(self):
        from urllib.parse import parse_qs
        qs     = self.scope.get('query_string', b'').decode()
        params = parse_qs(qs)
        tokens = params.get('token', [])
        if not tokens:
            return None
        try:
            payload = AccessToken(tokens[0])
            from myapp.Models.Auth_models import User
            return User.objects.get(id=payload['user_id'])
        except (TokenError, Exception):
            return None

    @database_sync_to_async
    def _get_user_conversation_ids(self):
        from myapp.Models.Chat_models import Conversation
        from myapp.Models.Auth_models import User
        try:
            if self.user.role == User.Role.ADMIN:
                return list(Conversation.objects.values_list('id', flat=True))
            return list(
                Conversation.objects.filter(participants=self.user).values_list('id', flat=True)
            )
        except Exception:
            return []

    @database_sync_to_async
    def _check_access(self, conv_id):
        from myapp.Models.Chat_models import Conversation
        from myapp.Models.Auth_models import User
        try:
            conv = Conversation.objects.get(id=conv_id)
        except Conversation.DoesNotExist:
            return False
        if self.user.role == User.Role.ADMIN:
            return True
        return conv.participants.filter(id=self.user.id).exists()

    @database_sync_to_async
    def _create_message(self, conv_id, content):
        from myapp.Models.Chat_models import Conversation, Message
        try:
            conv     = Conversation.objects.get(id=conv_id)
            is_first = not conv.messages.exists()
            msg      = Message.objects.create(conversation=conv, sender=self.user, content=content)
            Conversation.objects.filter(id=conv_id).update(updated_at=timezone.now())
            return msg, is_first
        except Exception as e:
            logger.error(f"_create_message error: {e}")
            return None, False

    @database_sync_to_async
    def _edit_message(self, message_id, content):
        from myapp.Models.Chat_models import Message
        try:
            msg = Message.objects.select_related('sender').get(id=message_id)
            if not msg.can_edit(self.user):
                return None
            now           = timezone.now()
            msg.content   = content
            msg.is_edited = True
            msg.edited_at = now
            msg.save(update_fields=['content', 'is_edited', 'edited_at'])
            return now
        except Message.DoesNotExist:
            return None
        except Exception as e:
            logger.error(f"_edit_message error: {e}")
            return None

    @database_sync_to_async
    def _get_message_conv_id(self, message_id):
        from myapp.Models.Chat_models import Message
        try:
            return Message.objects.get(id=message_id).conversation_id
        except Exception:
            return None

    @database_sync_to_async
    def _mark_messages_read(self, conv_id):
        from myapp.Models.Chat_models import Message, MessageReadStatus
        unread = Message.objects.filter(
            conversation_id=conv_id
        ).exclude(read_statuses__user=self.user)
        objs = [MessageReadStatus(message=m, user=self.user) for m in unread]
        if objs:
            MessageReadStatus.objects.bulk_create(objs, ignore_conflicts=True)
