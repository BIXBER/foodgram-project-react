from django.conf import settings
from drf_extra_fields.fields import Base64ImageField


class RelativeImageField(Base64ImageField):

    def to_representation(self, path):
        request = self.context.get('request')
        if request is not None:
            image_url = f'{settings.MEDIA_URL}{path}'
            return image_url
        return super().to_representation(path)
