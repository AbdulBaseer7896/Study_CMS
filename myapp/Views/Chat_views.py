# myapp/Views/Chat_views.py  —  FULLY ASYNC REST endpoints for chat
from adrf.decorators import api_view
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from asgiref.sync import sync_to_async

from myapp.Models.Auth_models import User
from myapp.Models.Chat_models import Conversation, Message, MessageReadStatus
from myapp.serializers.Chat_serializers import (
    ConversationSerializer, MessageSerializer, ConversationCreateSerializer
)


def _role(user):
    return user.role


# ── Helpers ───────────────────────────────────────────────────────────
def _can_message(sender, recipient):
    """Check if sender is allowed to start a conversation with recipient."""
    if sender.role == User.Role.ADMIN:
        return True  # admin ↔ anyone
    if sender.role == User.Role.CONSULTANT:
        # consultant ↔ consultant, consultant ↔ admin, consultant ↔ own student
        if recipient.role == User.Role.ADMIN:
            return True
        if recipient.role == User.Role.CONSULTANT:
            return True
        if recipient.role == User.Role.STUDENT and recipient.assigned_to_id == sender.id:
            return True
        return False
    if sender.role == User.Role.STUDENT:
        # student ↔ admin, student ↔ assigned consultant
        if recipient.role == User.Role.ADMIN:
            return True
        if recipient.role == User.Role.CONSULTANT and sender.assigned_to_id == recipient.id:
            return True
        return False
    return False


# ── LIST MY CONVERSATIONS ─────────────────────────────────────────────
@api_view(['GET'])
@permission_classes([IsAuthenticated])
async def list_conversations(request):
    def _fetch():
        convs = Conversation.objects.filter(participants=request.user).prefetch_related(
            'participants', 'messages'
        ).order_by('-updated_at')
        return ConversationSerializer(convs, many=True, context={'request': request}).data

    data = await sync_to_async(_fetch)()
    return Response({"status": "success", "conversations": data})


# ── CREATE / GET DIRECT CONVERSATION ─────────────────────────────────
@api_view(['POST'])
@permission_classes([IsAuthenticated])
async def create_or_get_conversation(request):
    """Start or retrieve a direct conversation with another user."""
    recipient_id = request.data.get('recipient_id')
    if not recipient_id:
        return Response({"error": "recipient_id is required."}, status=400)

    try:
        recipient = await sync_to_async(User.objects.get)(id=recipient_id)
    except User.DoesNotExist:
        return Response({"error": "User not found."}, status=404)

    if not _can_message(request.user, recipient):
        return Response({"error": "You are not allowed to message this user."}, status=403)

    def _get_or_create():
        # Look for existing direct conv between exactly these two users
        existing = Conversation.objects.filter(
            conv_type=Conversation.ConvType.DIRECT,
            participants=request.user
        ).filter(participants=recipient)

        for c in existing:
            if c.participants.count() == 2:
                return c, False

        conv = Conversation.objects.create(
            conv_type=Conversation.ConvType.DIRECT,
            created_by=request.user
        )
        conv.participants.add(request.user, recipient)
        return conv, True

    conv, created = await sync_to_async(_get_or_create)()
    data = await sync_to_async(
        lambda: ConversationSerializer(conv, context={'request': request}).data
    )()
    return Response({"status": "success", "conversation": data, "created": created},
                    status=201 if created else 200)


# ── BROADCAST (admin only) ────────────────────────────────────────────
@api_view(['POST'])
@permission_classes([IsAuthenticated])
async def create_broadcast(request):
    if request.user.role != User.Role.ADMIN:
        return Response({"error": "Only admin can broadcast."}, status=403)

    target  = request.data.get('target')   # students / consultants / everyone
    content = request.data.get('content', '').strip()

    if target not in ['students', 'consultants', 'everyone']:
        return Response({"error": "target must be students, consultants, or everyone."}, status=400)
    if not content:
        return Response({"error": "content is required."}, status=400)

    def _create():
        conv = Conversation.objects.create(
            conv_type=Conversation.ConvType.BROADCAST,
            broadcast_target=target,
            created_by=request.user
        )
        # Add all target participants
        if target == 'students':
            qs = User.objects.filter(role=User.Role.STUDENT)
        elif target == 'consultants':
            qs = User.objects.filter(role=User.Role.CONSULTANT)
        else:
            qs = User.objects.exclude(id=request.user.id)
        conv.participants.add(request.user)
        conv.participants.add(*list(qs))

        msg = Message.objects.create(conversation=conv, sender=request.user, content=content)
        conv.save()  # bump updated_at
        return conv, msg

    conv, msg = await sync_to_async(_create)()

    # Send first-message email notification to all participants
    from myapp.Utils.email_tasks import send_first_message_email_task
    await sync_to_async(send_first_message_email_task.delay)(msg.id)

    data = await sync_to_async(
        lambda: ConversationSerializer(conv, context={'request': request}).data
    )()
    return Response({"status": "success", "conversation": data}, status=201)


# ── GET MESSAGES IN A CONVERSATION — paginated (cursor-based, scroll-up) ──
#
# Query params:
#   page_size  — messages per page (default 15, max 50)
#   before_id  — load messages with id < before_id (scroll-up / load older)
#
# Returns messages in chronological order (oldest first in the page).
# The frontend uses `before_id` to implement "load more" when user scrolls up.
@api_view(['GET'])
@permission_classes([IsAuthenticated])
async def get_messages(request, conv_id):
    page_size = int(request.query_params.get('page_size', 15))
    page_size = min(max(page_size, 1), 50)
    before_id = request.query_params.get('before_id')  # cursor for older msgs

    def _fetch():
        try:
            conv = Conversation.objects.get(id=conv_id)
        except Conversation.DoesNotExist:
            return None, None, False
        if request.user.role != User.Role.ADMIN:
            if not conv.participants.filter(id=request.user.id).exists():
                return None, "forbidden", False

        qs = Message.objects.filter(conversation=conv).select_related('sender')
        if before_id:
            qs = qs.filter(id__lt=before_id)
        # Take newest N, then reverse for chronological order
        msgs      = list(qs.order_by('-id')[:page_size])
        has_more  = qs.order_by('-id').count() > page_size
        msgs      = list(reversed(msgs))
        data      = MessageSerializer(msgs, many=True, context={'request': request}).data
        return conv, data, has_more

    conv, data, has_more = await sync_to_async(_fetch)()
    if conv is None:
        if data == "forbidden":
            return Response({"error": "Access denied."}, status=403)
        return Response({"error": "Conversation not found."}, status=404)

    return Response({
        "status": "success",
        "messages": data,
        "has_more": has_more,
        "page_size": page_size,
    })


# ── SEND MESSAGE (REST fallback — WS is primary) ─────────────────────
@api_view(['POST'])
@permission_classes([IsAuthenticated])
async def send_message(request, conv_id):
    content = request.data.get('content', '').strip()
    if not content:
        return Response({"error": "content is required."}, status=400)

    def _send():
        try:
            conv = Conversation.objects.get(id=conv_id)
        except Conversation.DoesNotExist:
            return None, "not_found", None
        if request.user.role != User.Role.ADMIN:
            if not conv.participants.filter(id=request.user.id).exists():
                return None, "forbidden", None
        is_first = not conv.messages.exists()
        msg = Message.objects.create(conversation=conv, sender=request.user, content=content)
        conv.save()
        return conv, None, (msg, is_first)

    conv, err, result = await sync_to_async(_send)()
    if err == "not_found":
        return Response({"error": "Conversation not found."}, status=404)
    if err == "forbidden":
        return Response({"error": "Access denied."}, status=403)

    msg, is_first = result
    if is_first:
        from myapp.Utils.email_tasks import send_first_message_email_task
        await sync_to_async(send_first_message_email_task.delay)(msg.id)

    data = await sync_to_async(
        lambda: MessageSerializer(msg, context={'request': request}).data
    )()
    return Response({"status": "success", "message": data}, status=201)


# ── EDIT MESSAGE (within 5 min; admin has no time limit) ─────────────
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
async def edit_message(request, msg_id):
    content = request.data.get('content', '').strip()
    if not content:
        return Response({"error": "content is required."}, status=400)

    try:
        msg = await sync_to_async(Message.objects.select_related('sender').get)(id=msg_id)
    except Message.DoesNotExist:
        return Response({"error": "Message not found."}, status=404)

    can_edit = await sync_to_async(msg.can_edit)(request.user)
    if not can_edit:
        return Response({"error": "You cannot edit this message (not yours or 5-min window expired)."}, status=403)

    from django.utils import timezone
    msg.content  = content
    msg.is_edited = True
    msg.edited_at = timezone.now()
    await sync_to_async(msg.save)()

    data = await sync_to_async(
        lambda: MessageSerializer(msg, context={'request': request}).data
    )()
    return Response({"status": "success", "message": data})


# ── MARK MESSAGES AS READ ─────────────────────────────────────────────
@api_view(['POST'])
@permission_classes([IsAuthenticated])
async def mark_read(request, conv_id):
    def _mark():
        msgs = Message.objects.filter(conversation_id=conv_id).exclude(
            read_statuses__user=request.user
        )
        for m in msgs:
            MessageReadStatus.objects.get_or_create(message=m, user=request.user)
    await sync_to_async(_mark)()
    return Response({"status": "success"})


# ── ADMIN: LIST ALL CONVERSATIONS ────────────────────────────────────
@api_view(['GET'])
@permission_classes([IsAuthenticated])
async def admin_list_all_conversations(request):
    if request.user.role != User.Role.ADMIN:
        return Response({"error": "Admin only."}, status=403)

    def _fetch():
        convs = Conversation.objects.all().prefetch_related('participants', 'messages').order_by('-updated_at')
        return ConversationSerializer(convs, many=True, context={'request': request}).data

    data = await sync_to_async(_fetch)()
    return Response({"status": "success", "conversations": data})


# ── GET CONTACTABLE USERS ─────────────────────────────────────────────
@api_view(['GET'])
@permission_classes([IsAuthenticated])
async def get_contactable_users(request):
    """Returns the list of users this person can start a chat with."""
    def _fetch():
        user = request.user
        if user.role == User.Role.ADMIN:
            users = User.objects.exclude(id=user.id).values('id', 'name', 'email', 'role')
        elif user.role == User.Role.CONSULTANT:
            users = User.objects.filter(
                role__in=[User.Role.ADMIN, User.Role.CONSULTANT]
            ).exclude(id=user.id).values('id', 'name', 'email', 'role')
            students = User.objects.filter(role=User.Role.STUDENT, assigned_to=user).values('id', 'name', 'email', 'role')
            users = list(users) + list(students)
        else:  # student
            admins = User.objects.filter(role=User.Role.ADMIN).values('id', 'name', 'email', 'role')
            users = list(admins)
            if user.assigned_to_id:
                consultants = User.objects.filter(id=user.assigned_to_id).values('id', 'name', 'email', 'role')
                users += list(consultants)
        return list(users)

    users = await sync_to_async(_fetch)()
    return Response({"status": "success", "users": users})


# ── CONSULTANT BROADCAST (to own students, one-way) ─────────────────
@api_view(['POST'])
@permission_classes([IsAuthenticated])
async def create_consultant_broadcast(request):
    """Consultant can broadcast one-way to their own assigned students."""
    if request.user.role not in [User.Role.CONSULTANT, User.Role.ADMIN]:
        return Response({"error": "Only consultants or admin can use this."}, status=403)

    content = request.data.get('content', '').strip()
    if not content:
        return Response({"error": "content is required."}, status=400)

    def _create():
        conv = Conversation.objects.create(
            conv_type=Conversation.ConvType.BROADCAST,
            broadcast_target='my_students',
            created_by=request.user
        )
        # Add only the consultant's own students
        students = User.objects.filter(
            role=User.Role.STUDENT,
            assigned_to=request.user
        )
        conv.participants.add(request.user)
        if students.exists():
            conv.participants.add(*list(students))
        msg = Message.objects.create(conversation=conv, sender=request.user, content=content)
        conv.save()
        return conv, msg

    conv, msg = await sync_to_async(_create)()

    from myapp.Utils.email_tasks import send_first_message_email_task
    await sync_to_async(send_first_message_email_task.delay)(msg.id)

    data = await sync_to_async(
        lambda: ConversationSerializer(conv, context={'request': request}).data
    )()
    return Response({"status": "success", "conversation": data}, status=201)
