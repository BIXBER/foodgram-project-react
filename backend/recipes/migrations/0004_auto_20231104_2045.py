# Generated by Django 3.2.16 on 2023-11-04 17:45

import django.db.models.expressions
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_auto_20231104_0211'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='cart',
            options={'default_related_name': 'shopping_cart', 'verbose_name': 'Список покупок', 'verbose_name_plural': 'Списки покупок'},
        ),
        migrations.AlterModelOptions(
            name='follow',
            options={'verbose_name': 'Подписка', 'verbose_name_plural': 'Подписки'},
        ),
        migrations.AddConstraint(
            model_name='follow',
            constraint=models.CheckConstraint(check=models.Q(('user', django.db.models.expressions.F('following')), _negated=True), name='prevent_self_following'),
        ),
    ]
