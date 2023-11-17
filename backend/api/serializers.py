from django.contrib.auth import get_user_model
from django.db.models import F
from rest_framework import serializers
from rest_framework.fields import ReadOnlyField
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import (Cart, Favorite, Follow, Ingredient,
                            IngredientRecipe, Recipe, Tag)
from core.constants import MIN_VALUE_AMOUNT
from .fields import RelativeImageField

User = get_user_model()


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
    name = ReadOnlyField(source='ingredient.name')
    measurement_unit = ReadOnlyField(source='ingredient.measurement_unit')

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount', 'name', 'measurement_unit')


class RecipeReadSerializer(serializers.ModelSerializer):
    author = UserSerializer()
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    tags = TagSerializer(many=True)
    image = RelativeImageField()

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
    image = RelativeImageField()

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
        tags_data = validated_data.pop('tags', [])
        ingredients_data = validated_data.pop('ingredients', [])
        super().update(instance, validated_data)

        instance.tags.set(tags_data)

        IngredientRecipe.objects.filter(recipe=instance).delete()
        self.add_ingredients(ingredients_data, instance)
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
    id = ReadOnlyField(source='following.id')
    email = ReadOnlyField(source='following.email')
    username = ReadOnlyField(source='following.username')
    first_name = ReadOnlyField(source='following.first_name')
    last_name = ReadOnlyField(source='following.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'recipes', 'recipes_count')

    def get_recipes(self, obj):
        recipes_set = obj.following.author_recipes.all()
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
