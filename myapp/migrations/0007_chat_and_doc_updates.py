# myapp/migrations/0007_chat_and_doc_updates.py
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0006_passwordresetotp'),
    ]

    operations = [
        # ── Add field_upload_times JSON field to StudentDocument ──────
        migrations.AddField(
            model_name='studentdocument',
            name='field_upload_times',
            field=models.JSONField(blank=True, default=dict),
        ),

        # ── Conversation model ────────────────────────────────────────
        migrations.CreateModel(
            name='Conversation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('conv_type', models.CharField(
                    choices=[('direct', 'Direct'), ('broadcast', 'Broadcast')],
                    default='direct', max_length=20
                )),
                ('broadcast_target', models.CharField(
                    blank=True, null=True,
                    choices=[('students', 'All Students'), ('consultants', 'All Consultants'), ('everyone', 'Everyone')],
                    max_length=20
                )),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(
                    null=True, on_delete=django.db.models.deletion.SET_NULL,
                    related_name='created_conversations',
                    to=settings.AUTH_USER_MODEL
                )),
                ('participants', models.ManyToManyField(
                    blank=True, related_name='conversations',
                    to=settings.AUTH_USER_MODEL
                )),
            ],
            options={'ordering': ['-updated_at']},
        ),

        # ── Message model ─────────────────────────────────────────────
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('is_edited', models.BooleanField(default=False)),
                ('edited_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('conversation', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='messages', to='myapp.conversation'
                )),
                ('sender', models.ForeignKey(
                    null=True, on_delete=django.db.models.deletion.SET_NULL,
                    related_name='sent_messages', to=settings.AUTH_USER_MODEL
                )),
            ],
            options={'ordering': ['created_at']},
        ),

        # ── MessageReadStatus model ───────────────────────────────────
        migrations.CreateModel(
            name='MessageReadStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('read_at', models.DateTimeField(auto_now_add=True)),
                ('message', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='read_statuses', to='myapp.message'
                )),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='read_statuses', to=settings.AUTH_USER_MODEL
                )),
            ],
            options={'unique_together': {('message', 'user')}},
        ),
    ]
