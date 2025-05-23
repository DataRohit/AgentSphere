# Generated by Django 5.0.13 on 2025-05-08 10:25

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('organization', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MCPTool',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated At')),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
                ('description', models.TextField(blank=True, verbose_name='Description')),
            ],
            options={
                'verbose_name': 'MCP Tool',
                'verbose_name_plural': 'MCP Tools',
                'db_table': 'tools_mcptool',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='MCPServer',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated At')),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
                ('description', models.TextField(blank=True, verbose_name='Description')),
                ('url', models.URLField(max_length=255, verbose_name='URL')),
                ('tags', models.CharField(blank=True, help_text='Comma-separated tags for categorizing the server', max_length=255, verbose_name='Tags')),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mcp_servers', to='organization.organization', verbose_name='Organization')),
            ],
            options={
                'verbose_name': 'MCP Server',
                'verbose_name_plural': 'MCP Servers',
                'db_table': 'tools_mcpserver',
                'ordering': ['name'],
            },
        ),
    ]
