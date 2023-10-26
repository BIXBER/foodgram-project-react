from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class BaseRecipeModel(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='%(class)s_recipes'.lower(),
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        'Recipe',
        on_delete=models.CASCADE,
        related_name='%(class)s_users'.lower(),
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
        max_length=200,
        unique=True,
        db_index=True,
    )

    class Meta:
        abstract = True
        ordering = ('name',)

    def __str__(self):
        return self.name
