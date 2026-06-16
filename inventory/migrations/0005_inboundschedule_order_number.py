from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('inventory', '0004_independent_upload_types_and_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='inboundschedule',
            name='order_number',
            field=models.CharField(blank=True, max_length=120, verbose_name='발주번호'),
        ),
        migrations.AlterModelOptions(
            name='inboundschedule',
            options={'ordering': ['order_number', 'inbound_date', 'product_name', 'option_name']},
        ),
    ]
