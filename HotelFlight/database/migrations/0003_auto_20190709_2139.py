# Generated by Django 2.2.3 on 2019-07-09 15:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('database', '0002_hotel_hotel_room_room'),
    ]

    operations = [
        migrations.CreateModel(
            name='Air_Company',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('AirCompany_Name', models.CharField(max_length=200)),
                ('TotalSentMoney', models.DecimalField(decimal_places=2, max_digits=20)),
                ('Percentage', models.DecimalField(decimal_places=2, max_digits=3)),
                ('CompanyAdmin', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('MoneyToPay', models.DecimalField(decimal_places=2, max_digits=20)),
                ('MoneyToRefund', models.DecimalField(decimal_places=2, max_digits=20)),
                ('DateOfBooking', models.DateField()),
                ('DateOfCancellation', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='Cancellation_Policy',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Description', models.TextField()),
                ('Start_Date', models.DateField()),
                ('End_Date', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='Flight',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Airplane_Number', models.CharField(max_length=200)),
                ('Aircraft', models.CharField(max_length=200, null=True)),
                ('AirCompany', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='database.Air_Company')),
            ],
        ),
        migrations.CreateModel(
            name='Route',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Source', models.CharField(max_length=200)),
                ('Destination', models.CharField(max_length=200)),
            ],
        ),
        migrations.RemoveField(
            model_name='hotel_room',
            name='Checkin_Date',
        ),
        migrations.RemoveField(
            model_name='hotel_room',
            name='Checkout_Date',
        ),
        migrations.AddField(
            model_name='hotel',
            name='Address',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='hotel',
            name='Phone',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AddField(
            model_name='hotel_room',
            name='FreeRoomCount',
            field=models.IntegerField(default=2),
        ),
        migrations.AddField(
            model_name='hotel_room',
            name='TotalRoomCount',
            field=models.IntegerField(default=2),
        ),
        migrations.CreateModel(
            name='Hotel_Booking',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Checkin_Date', models.DateField(null=True)),
                ('Checkout_Date', models.DateField(null=True)),
                ('Booking', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='database.Booking')),
                ('Hotel_Room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='database.Hotel_Room')),
            ],
        ),
        migrations.CreateModel(
            name='Flight_Route',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Time', models.TimeField()),
                ('Date', models.DateField()),
                ('Price', models.DecimalField(decimal_places=2, max_digits=20)),
                ('Duration', models.DurationField()),
                ('Source_Airport', models.CharField(max_length=200, null=True)),
                ('Destination_Airport', models.CharField(max_length=200, null=True)),
                ('Flight', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='database.Flight')),
                ('Route', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='database.Route')),
            ],
        ),
        migrations.CreateModel(
            name='Flight_Booking',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Booking', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='database.Booking')),
                ('Flight_Route', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='database.Flight_Route')),
            ],
        ),
        migrations.AddField(
            model_name='booking',
            name='Cancellation_Policy',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='database.Cancellation_Policy'),
        ),
        migrations.AddField(
            model_name='booking',
            name='User',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='database.Profile'),
        ),
    ]
