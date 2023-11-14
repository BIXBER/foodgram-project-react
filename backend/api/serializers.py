import base64

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.core.files.base import ContentFile
from django.db.models import F
from djoser.serializers import UserCreateSerializer as DjoserCreateUser
from rest_framework import serializers
from rest_framework.fields import ReadOnlyField
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import (Cart, Favorite, Follow, Ingredient,
                            IngredientRecipe, Recipe, Tag)

User = get_user_model()

MIN_VALUE_AMOUNT = 1


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)

    def to_representation(self, path):
        request = self.context.get('request')
        if request is not None:
            current_site = get_current_site(request)
            image_url = (f'{request.scheme}://{current_site.domain}'
                         f'{settings.MEDIA_URL}{path}')
            return image_url
        return super().to_representation(path)


class UserCreateSerializer(DjoserCreateUser):

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name', 'password',
        )


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username',
            'first_name', 'last_name', 'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.following.filter(user=request.user).exists()
        return False


class FollowSerializer(UserSerializer):

    class Meta:
        model = Follow
        fields = ('user', 'following')
        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('user', 'following'),
                message='Вы уже подписаны на этого пользователя.',
            )
        ]

    def validate(self, attrs):
        user, following = (attrs.get('user'), attrs.get('following'))
        if user == following:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя.',
            )
        return attrs

    def to_representation(self, instance):
        return SubscribeSerializer(instance, context=self.context).data


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientWriteSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(write_only=True)
    amount = serializers.IntegerField(required=True)
    name = serializers.SerializerMethodField()
    measurement_unit = serializers.SerializerMethodField()

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount', 'name', 'measurement_unit')

    def get_measurement_unit(self, ingredient):
        return ingredient.measurement_unit

    def get_name(self, ingredient):
        return ingredient.name


class RecipeReadSerializer(serializers.ModelSerializer):
    author = UserSerializer()
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    tags = TagSerializer(many=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time',
        )
        read_only_fields = ('author',)

    def get_ingredients(self, obj):
        ingredients = obj.ingredients.values(
            'id', 'name',
            'measurement_unit', amount=F('ingredientrecipe__amount'),
        )
        return ingredients

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Favorite.objects.filter(
                user=request.user, recipe=obj,
            ).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Cart.objects.filter(
                user=request.user, recipe=obj,
            ).exists()
        return False


class RecipeSerializer(serializers.ModelSerializer):
    default_error_messages = {
        'ingredients_doesnt_exist': 'Такого ингредиента не существует',
        'no_ingredients': 'Рецепт должен содержать минимум один ингредиент',
        'unique_ingredients': 'Ингредиенты для рецепта не должны повторяться',
        'invalid_amount': 'Неверное количество ингредиента',
        'tags_doesnt_exist': 'Такого тега не существует',
        'no_tags': 'Рецепт должен содержать минимум один тег',
        'unique_tags': 'Теги для рецепта не должны повторяться',
        'no_image': 'Изображение должно быть установлено для рецепта',
    }
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all(),
    )
    ingredients = RecipeIngredientWriteSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'ingredients', 'tags', 'image', 'name', 'text', 'cooking_time',
        )

    def add_ingredients(self, ingredients_data, recipe):
        recipe_ingredients = [
            IngredientRecipe(
                recipe=recipe,
                ingredient_id=ingredient_data.get('id'),
                amount=ingredient_data.get('amount'),
            )
            for ingredient_data in ingredients_data
        ]
        IngredientRecipe.objects.bulk_create(recipe_ingredients)

    def create(self, validated_data):
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags_data)
        recipe.save()
        self.add_ingredients(ingredients_data, recipe)
        return recipe

    def validate_ingredients(self, ingredients):
        if not ingredients:
            self.fail('no_ingredients')
        ingredients_data = [ingredient.get('id') for ingredient in ingredients]
        for ingredient_id in ingredients_data:
            if not Ingredient.objects.filter(id=ingredient_id).exists():
                self.fail('ingredients_doesnt_exist')
        if len(ingredients_data) != len(set(ingredients_data)):
            self.fail('unique_ingredients')
        for ingredient in ingredients:
            if int(ingredient.get('amount')) < MIN_VALUE_AMOUNT:
                self.fail('invalid_amount')
        return ingredients

    def validate_tags(self, tags):
        if not tags:
            self.fail('no_tags')
        tags_data = [tag.id for tag in tags]
        for tag_id in tags_data:
            if not Tag.objects.filter(id=tag_id).exists():
                self.fail('tags_doesnt_exist')
        if len(tags) != len(set(tags)):
            self.fail('unique_tags')
        return tags

    def update(self, instance, validated_data):
        fixed_fields = ['image', 'name', 'text', 'cooking_time']
        for field in fixed_fields:
            setattr(instance,
                    field,
                    validated_data.get(field, getattr(instance, field)))

        instance.tags.clear()
        instance.ingredients.clear()
        tags_data = validated_data.get('tags')
        ingredients_data = validated_data.get('ingredients')
        self.validate_ingredients(ingredients_data)
        self.validate_tags(tags_data)

        instance.tags.set(tags_data)
        IngredientRecipe.objects.filter(recipe=instance.id).delete()
        self.add_ingredients(ingredients_data, instance)
        instance.save()
        return instance

    def to_representation(self, instance):
        serializer = RecipeReadSerializer(instance, context=self.context)
        return serializer.data


class RecipeSmallSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('__all__',)


class FavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')
        validators = (
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=['recipe', 'user'],
                message='Рецепт уже находится в Вашем избранном!',
            ),
        )

    def to_representation(self, instance):
        return RecipeSmallSerializer(instance.recipe).data


class CartSerializer(serializers.ModelSerializer):

    class Meta:
        model = Cart
        fields = ('user', 'recipe')
        validators = (
            UniqueTogetherValidator(
                queryset=Cart.objects.all(),
                fields=['recipe', 'user'],
                message='Рецепт уже лежит в Вашей корзине!',
            ),
        )

    def to_representation(self, instance):
        return RecipeSmallSerializer(instance.recipe).data


class SubscribeSerializer(serializers.ModelSerializer):
    id = ReadOnlyField(source='user.id')
    email = ReadOnlyField(source='user.email')
    username = ReadOnlyField(source='user.username')
    first_name = ReadOnlyField(source='user.first_name')
    last_name = ReadOnlyField(source='user.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'recipes', 'recipes_count')

    def get_recipes(self, obj):
        recipes_set = obj.user.author_recipes.all()
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        recipes_limit = request.query_params.get('recipes_limit')
        if recipes_limit:
            recipes_set = recipes_set[:int(recipes_limit)]
        return RecipeSmallSerializer(recipes_set, many=True).data

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Follow.objects.filter(
                user=request.user, following=obj.following,
            ).exists()
        return False

    def get_recipes_count(self, obj):
        return obj.following.author_recipes.count()
