from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

from core.models import BaseNamedModel, BaseRecipeModel
from core.constants import (MAX_CHARACTER_COUNT,
                            MAX_HEXFIELD_LENGTH,
                            MIN_VALUE_AMOUNT)
from .validators import hex_validator


User = get_user_model()


class Tag(BaseNamedModel):
    color = models.CharField(
        'Цвет в HEX',
        max_length=MAX_HEXFIELD_LENGTH,
        validators=(hex_validator,),
        help_text="Например: #FFF или #0F0F0F",
    )
    slug = models.SlugField(
        'Уникальный слаг',
        max_length=MAX_CHARACTER_COUNT,
        help_text='Не более 200 символов. Буквы, цифры и только @/./+/-/_',
    )

    class Meta(BaseNamedModel.Meta):
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'


class Ingredient(BaseNamedModel):
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=MAX_CHARACTER_COUNT,
    )

    class Meta(BaseNamedModel.Meta):
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_ingredient',
            ),
        )

    def __str__(self):
        return self.name


class Recipe(models.Model):
    tags = models.ManyToManyField(
        Tag,
        related_name='tag_recipes',
        verbose_name='Теги',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='author_recipes',
        verbose_name='Автор',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe',
        verbose_name='Ингредиенты',
    )
    name = models.CharField(
        'Название',
        max_length=MAX_CHARACTER_COUNT,
        db_index=True,
    )
    image = models.ImageField(
        'Ссылка на картинку на сайте',
        upload_to='recipes/images/',
    )
    text = models.TextField(
        'Описание',
        help_text='Описание способа приготовления блюда',
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления в минутах',
        validators=[MinValueValidator(1)],
    )
    pub_date = models.DateField(
        'Дата публикации',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date', 'name')

    def __str__(self):
        return self.name


class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Рецепт',
    )
    amount = models.PositiveSmallIntegerField(
        'Количество в рецепте',
        validators=[MinValueValidator(MIN_VALUE_AMOUNT)],
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                name='unique_ingredient_recipe',
                fields=('ingredient', 'recipe'),
            ),
        )

    def __str__(self):
        return (f'"{self.ingredient.name.capitalize()}" '
                f'— добавлено в рецепт "{self.recipe.name.capitalize()}".')


class Cart(BaseRecipeModel):

    class Meta(BaseRecipeModel.Meta):
        default_related_name = 'shopping_cart'
        verbose_name = "Список покупок"
        verbose_name_plural = "Списки покупок"

    def __str__(self):
        return (f'"{self.recipe.name.capitalize()}" '
                f'в корзине у пользователя {self.user}.')


class Favorite(BaseRecipeModel):

    class Meta(BaseRecipeModel.Meta):
        default_related_name = 'favorites'
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'

    def __str__(self):
        return (f'"{self.recipe.name.capitalize()}" '
                f'в избранном у пользователя {self.user}.')


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        related_name='follower',
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        help_text='Укажите того, кто подписывается',
    )
    following = models.ForeignKey(
        User,
        related_name='following',
        on_delete=models.CASCADE,
        verbose_name='Подписчик',
        help_text='Укажите того, на кого подписываются',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = (
            models.UniqueConstraint(
                name='unique_following',
                fields=('user', 'following'),
            ),
            models.CheckConstraint(
                name='prevent_self_following',
                check=~models.Q(user=models.F('following')),
            )
        )

    def __str__(self):
        return f'{self.user} подписан на {self.following}.'
