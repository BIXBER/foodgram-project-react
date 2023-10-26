from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

from core.models import BaseRecipeModel, BaseNamedModel

User = get_user_model()


class Tag(BaseNamedModel):
    color = models.CharField(
        'Цвет в HEX',
        max_length=7,
        blank=True,
        null=True,
    )
    slug = models.SlugField(
        'Уникальный слаг',
        max_length=200,
        blank=True,
        null=True,
    )

    class Meta(BaseNamedModel.Meta):
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'


class Ingredient(BaseNamedModel):
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=200,
    )

    class Meta(BaseNamedModel.Meta):
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'


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
        max_length=200,
        db_index=True,
    )
    image = models.ImageField(
        'Ссылка на картинку на сайте',
        upload_to='recipes/',
    )
    text = models.TextField(
        'Описание',
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления в минутах',
        validators=[MinValueValidator(1)],
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('name',)

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
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )
    amount = models.PositiveSmallIntegerField(
        'Количество в рецепте',
    )

    def __str__(self):
        return f'"{self.ingredient}" есть в рецепте "{self.recipe}".'


class Cart(BaseRecipeModel):

    class Meta(BaseRecipeModel.Meta):
        pass

    def __str__(self):
        return f'"{self.recipe}" есть в корзине у пользователя {self.user}.'


class Favorite(BaseRecipeModel):

    class Meta(BaseRecipeModel.Meta):
        pass

    def __str__(self):
        return f'"{self.recipe}" есть в избранном у пользователя {self.user}.'


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        related_name='follower',
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    following = models.ForeignKey(
        User,
        related_name='following',
        on_delete=models.CASCADE,
        verbose_name='Подписчик',
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'following'),
                name='unique_follower',
            ),
        )

    def __str__(self):
        return f'{self.user} подписан на {self.following}.'
