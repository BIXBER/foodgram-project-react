from django.db import models


class BaseRecipeModel(models.Model):
    user = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        'Recipe',
        on_delete=models.CASCADE,
        related_name='users',
        verbose_name='Рецепт',
    )

    class Meta:
        abstract = True
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_recipe',
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
