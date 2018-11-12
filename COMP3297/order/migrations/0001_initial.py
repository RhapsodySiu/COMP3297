# Generated by Django 2.1.2 on 2018-11-12 19:22

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import enumfields.fields
import order.models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Clinic',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('latitude', models.DecimalField(decimal_places=6, max_digits=10)),
                ('longitude', models.DecimalField(decimal_places=6, max_digits=10)),
                ('altitude', models.DecimalField(decimal_places=2, max_digits=5)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='DistanceClinic',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('distance', models.DecimalField(decimal_places=2, max_digits=5)),
                ('a', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='clinicA', to='order.Clinic')),
                ('b', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='clinicB', to='order.Clinic')),
            ],
        ),
        migrations.CreateModel(
            name='DistanceClinicHospital',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('distance', models.DecimalField(decimal_places=2, max_digits=5)),
            ],
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Hospital',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('latitude', models.DecimalField(decimal_places=6, max_digits=10)),
                ('longitude', models.DecimalField(decimal_places=6, max_digits=10)),
                ('altitude', models.DecimalField(decimal_places=2, max_digits=5)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MedicalSupply',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('description', models.CharField(max_length=200)),
                ('weight', models.DecimalField(decimal_places=2, max_digits=5)),
                ('img', models.ImageField(blank=True, null=True, upload_to=order.models.get_image_path)),
            ],
            options={
                'verbose_name_plural': 'medical supplies',
                'ordering': ('description',),
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('priority', enumfields.fields.EnumIntegerField(default=3, enum=order.models.Priority)),
                ('order_time', models.DateTimeField(auto_now_add=True)),
                ('processing_time', models.DateTimeField(blank=True, null=True)),
                ('processed_time', models.DateTimeField(blank=True, null=True)),
                ('dispatched_time', models.DateTimeField(blank=True, null=True)),
                ('delivered_time', models.DateTimeField(blank=True, null=True)),
                ('status', enumfields.fields.EnumIntegerField(default=1, enum=order.models.Status)),
                ('clinic', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='order.Clinic')),
                ('order_by', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('priority', 'order_time'),
            },
        ),
        migrations.CreateModel(
            name='OrderContent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('weight', models.DecimalField(decimal_places=2, max_digits=5)),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('medical_supply', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order_items', to='order.MedicalSupply')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='order.Order')),
            ],
        ),
        migrations.CreateModel(
            name='Type',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
            ],
        ),
        migrations.AddField(
            model_name='medicalsupply',
            name='type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='supply', to='order.Type'),
        ),
        migrations.AddField(
            model_name='distanceclinichospital',
            name='a',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='hospital', to='order.Hospital'),
        ),
        migrations.AddField(
            model_name='distanceclinichospital',
            name='b',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='clinic', to='order.Clinic'),
        ),
        migrations.AlterUniqueTogether(
            name='distanceclinichospital',
            unique_together={('a', 'b')},
        ),
        migrations.AlterUniqueTogether(
            name='distanceclinic',
            unique_together={('a', 'b')},
        ),
    ]
