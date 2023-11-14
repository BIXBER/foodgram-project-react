import csv
from datetime import datetime as dt

from django.http.response import HttpResponse


def build_file(user, ingredients, filename='shopping_list.txt'):
    created_time = dt.now().strftime('%d.%m.%Y %H:%M')

    response = HttpResponse(content_type='text/plain; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename={filename}'

    writer = csv.writer(response, delimiter=',',
                        quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer.writerow([f'Список покупок пользователя: {user.first_name} '
                     f'{user.last_name}', ])
    writer.writerow([f'Дата и время создания: {created_time}', ])
    writer.writerow(['-----', ])
    writer.writerow(['Ингредиент', 'Количество', 'Единица измерения'])
    for ingredient in ingredients:
        writer.writerow(
            [
                ingredient['ingredients'],
                ingredient['sum_amount'],
                ingredient['measure'],
            ]
        )
    writer.writerow(['-----', ])
    writer.writerow(['*Сформировано в продуктовом помощнике Foodgram', ])
    return response
