# myapp/serializers/Chat_serializers.py
from rest_framework import serializers
from myapp.Models.Chat_models import Conversation, Message, MessageReadStatus
from myapp.Models.Auth_models import User


class ParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model  = User
        fields = ['id', 'name', 'email', 'role']


class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.SerializerMethodField()
    sender_role = serializers.SerializerMethodField()
    can_edit    = serializers.SerializerMethodField()

    class Meta:
        model  = Message
        fields = ['id', 'conversation', 'sender', 'sender_name', 'sender_role',
                  'content', 'is_edited', 'edited_at', 'created_at', 'can_edit']

    def get_sender_name(self, obj):
        return obj.sender.name if obj.sender else 'Deleted User'

    def get_sender_role(self, obj):
        return obj.sender.role if obj.sender else None

    def get_can_edit(self, obj):
        request = self.context.get('request')
        if not request:
            return False
        return obj.can_edit(request.user)


class ConversationSerializer(serializers.ModelSerializer):
    participants  = ParticipantSerializer(many=True, read_only=True)
    last_message  = serializers.SerializerMethodField()
    unread_count  = serializers.SerializerMethodField()

    class Meta:
        model  = Conversation
        fields = ['id', 'conv_type', 'broadcast_target', 'participants',
                  'created_by', 'created_at', 'updated_at', 'last_message', 'unread_count']

    def get_last_message(self, obj):
        msg = obj.messages.order_by('-created_at').first()
        if not msg:
            return None
        return {
            'id':         msg.id,
            'content':    msg.content,
            'sender':     msg.sender.name if msg.sender else 'Deleted',
            'created_at': msg.created_at.isoformat(),
        }

    def get_unread_count(self, obj):
        request = self.context.get('request')
        if not request:
            return 0
        return obj.messages.exclude(read_statuses__user=request.user).count()


class ConversationCreateSerializer(serializers.Serializer):
    recipient_id = serializers.IntegerField()
