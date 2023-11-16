from django.contrib.auth import get_user_model
from django.db import models

from core.constants import MAX_CHARACTER_COUNT

User = get_user_model()


class BaseRecipeModel(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        'Recipe',
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )

    class Meta:
        abstract = True
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_%(class)s_recipe'.lower(),
            ),
        )


class BaseNamedModel(models.Model):
    name = models.CharField(
        'Название',
        max_length=MAX_CHARACTER_COUNT,
        db_index=True,
    )

    class Meta:
        abstract = True
        ordering = ('name',)

    def __str__(self):
        return self.name
