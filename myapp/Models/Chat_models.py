# # myapp/Models/Chat_models.py
# from django.db import models
# from django.utils import timezone
# from myapp.Models.Auth_models import User


# class Conversation(models.Model):
#     """
#     A conversation between two or more participants.
#     Types:
#       - direct    : exactly 2 users (student↔consultant, consultant↔consultant, admin↔anyone)
#       - broadcast : admin sends to a group (all_students / all_consultants / everyone)
#     """
#     class ConvType(models.TextChoices):
#         DIRECT    = 'direct',    'Direct'
#         BROADCAST = 'broadcast', 'Broadcast'

#     class BroadcastTarget(models.TextChoices):
#         STUDENTS     = 'students',     'All Students'
#         CONSULTANTS  = 'consultants',  'All Consultants'
#         EVERYONE     = 'everyone',     'Everyone'
#         MY_STUDENTS  = 'my_students',  'My Students'

#     conv_type        = models.CharField(max_length=20, choices=ConvType.choices, default=ConvType.DIRECT)
#     broadcast_target = models.CharField(max_length=20, choices=BroadcastTarget.choices, null=True, blank=True)
#     participants     = models.ManyToManyField(User, related_name='conversations', blank=True)
#     created_by       = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_conversations')
#     created_at       = models.DateTimeField(auto_now_add=True)
#     updated_at       = models.DateTimeField(auto_now=True)

#     class Meta:
#         ordering = ['-updated_at']

#     def __str__(self):
#         if self.conv_type == self.ConvType.BROADCAST:
#             return f"Broadcast → {self.broadcast_target} by {self.created_by}"
#         names = ", ".join(p.name for p in self.participants.all()[:3])
#         return f"Conversation: {names}"


# class Message(models.Model):
#     conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
#     sender       = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='sent_messages')
#     content      = models.TextField()
#     is_edited    = models.BooleanField(default=False)
#     edited_at    = models.DateTimeField(null=True, blank=True)
#     created_at   = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         ordering = ['created_at']

#     def can_edit(self, user):
#         """Only sender can edit, within 5 minutes, and only non-admin roles (admin can always edit)."""
#         if self.sender_id != user.id:
#             return False
#         if user.role == User.Role.ADMIN:
#             return True
#         limit = self.created_at + timezone.timedelta(minutes=5)
#         return timezone.now() < limit

#     def __str__(self):
#         return f"Msg#{self.id} by {self.sender} in Conv#{self.conversation_id}"


# class MessageReadStatus(models.Model):
#     """Tracks which messages a user has read."""
#     message  = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='read_statuses')
#     user     = models.ForeignKey(User, on_delete=models.CASCADE, related_name='read_statuses')
#     read_at  = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         unique_together = ('message', 'user')





# myapp/Models/Chat_models.py
from django.db import models
from django.utils import timezone
from myapp.Models.Auth_models import User


class Conversation(models.Model):
    """
    A conversation between two or more participants.
    Types:
      - direct    : exactly 2 users (student↔consultant, consultant↔consultant, admin↔anyone)
      - broadcast : admin sends to a group (all_students / all_consultants / everyone)
    """
    class ConvType(models.TextChoices):
        DIRECT    = 'direct',    'Direct'
        BROADCAST = 'broadcast', 'Broadcast'

    class BroadcastTarget(models.TextChoices):
        STUDENTS     = 'students',     'All Students'
        CONSULTANTS  = 'consultants',  'All Consultants'
        EVERYONE     = 'everyone',     'Everyone'
        MY_STUDENTS  = 'my_students',  'My Students'

    conv_type        = models.CharField(max_length=20, choices=ConvType.choices, default=ConvType.DIRECT)
    broadcast_target = models.CharField(max_length=20, choices=BroadcastTarget.choices, null=True, blank=True)
    participants     = models.ManyToManyField(User, related_name='conversations', blank=True)
    created_by       = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_conversations')
    created_at       = models.DateTimeField(auto_now_add=True)
    updated_at       = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        if self.conv_type == self.ConvType.BROADCAST:
            return f"Broadcast → {self.broadcast_target} by {self.created_by}"
        names = ", ".join(p.name for p in self.participants.all()[:3])
        return f"Conversation: {names}"


class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender       = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='sent_messages')
    content      = models.TextField()
    is_edited    = models.BooleanField(default=False)
    edited_at    = models.DateTimeField(null=True, blank=True)
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def can_edit(self, user):
        """Only sender can edit, within 5 minutes, and only non-admin roles (admin can always edit)."""
        if self.sender_id != user.id:
            return False
        if user.role == User.Role.ADMIN:
            return True
        limit = self.created_at + timezone.timedelta(minutes=5)
        return timezone.now() < limit

    def __str__(self):
        return f"Msg#{self.id} by {self.sender} in Conv#{self.conversation_id}"


class MessageReadStatus(models.Model):
    """Tracks which messages a user has read."""
    message  = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='read_statuses')
    user     = models.ForeignKey(User, on_delete=models.CASCADE, related_name='read_statuses')
    read_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('message', 'user')
