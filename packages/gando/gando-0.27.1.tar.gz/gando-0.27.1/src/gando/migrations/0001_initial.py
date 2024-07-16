# Generated by Django 5.0.1 on 2024-02-04 00:33

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserAgentDevice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(blank=True, db_index=True, max_length=255, null=True, unique=True, verbose_name='Key')),
                ('user_agent_is_mobile', models.IntegerField(blank=True, choices=[(0, 'No'), (1, 'Yes')], null=True, verbose_name='Mobile')),
                ('user_agent_is_tablet', models.IntegerField(blank=True, choices=[(0, 'No'), (1, 'Yes')], null=True, verbose_name='Tablet')),
                ('user_agent_is_touch_capable', models.IntegerField(blank=True, choices=[(0, 'No'), (1, 'Yes')], null=True, verbose_name='TouchCapable')),
                ('user_agent_is_pc', models.IntegerField(blank=True, choices=[(0, 'No'), (1, 'Yes')], null=True, verbose_name='PC')),
                ('user_agent_is_bot', models.IntegerField(blank=True, choices=[(0, 'No'), (1, 'Yes')], null=True, verbose_name='Bot')),
                ('user_agent_browser_family', models.CharField(blank=True, max_length=255, null=True, verbose_name='BrowserFamily')),
                ('user_agent_browser_version', models.CharField(blank=True, max_length=255, null=True, verbose_name='BrowserVersion')),
                ('user_agent_os_family', models.CharField(blank=True, max_length=255, null=True, verbose_name='OSFamily')),
                ('user_agent_os_version', models.CharField(blank=True, max_length=255, null=True, verbose_name='OSVersion')),
                ('user_agent_device_family', models.CharField(blank=True, max_length=255, null=True, verbose_name='DeviceFamily')),
                ('user_agent_device_brand', models.CharField(blank=True, max_length=255, null=True, verbose_name='DeviceBrand')),
                ('user_agent_device_model', models.CharField(blank=True, max_length=255, null=True, verbose_name='DeviceModel')),
                ('ip', models.CharField(blank=True, max_length=255, null=True, verbose_name='IP')),
                ('created_dt', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Created Datetime')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='uad', to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'verbose_name': 'UserAgentDevice',
                'verbose_name_plural': 'UserAgentDevices',
            },
        ),
    ]
