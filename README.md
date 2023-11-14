# FOODGRAM

## 🔍 Описание:

**Проект FOODGRAM** представляет из себя продвинутый продуктовый помощник, который позволит пользователям
не только делиться своими уникальными рецептами, но и рассчитывать продуктовую корзину перед походом в магазин, отслеживать рецепты других пользователей и сохранять их в избранное.

**[API_FOODGRAM*](#foodgram)** - интерфейс для взаимодействия c пользователем, позволяющий получать, создавать, удалять и изменять объекты только своих рецептов в базе данных [проекта](#🔍-описание).
![LOGOTYPE](https://cdn-icons-png.flaticon.com/512/2565/2565417.png "img.png")

---

## 💡 Как начать пользоваться проектом:
#### 1. Открыть проект в веб-браузере:
- Перейти по **[ссылке](https://www.foodhelper.shop/)**, зарегистрироваться на сайте и разместить свой рецепт.

#### 2. Запустить проект локально в контейнерах Docker:
**Рекомендуемые системные требования к компьютерам:**
- Ubuntu Linux 20.04 и выше;
- Windows 10 (2H20) и выше;
- macOS Monterey и выше.
  * Минимально необходимый объем ОЗУ компьютера — 4 Gb.

1. Установить Docker Desktop (версию, зависящую от Вашей ОС) на свой компьютер, с [официального сайта поставщика продукта.](https://www.docker.com/get-started/)

*Далее, если у Вас операционная система:*
- **Linux:**
  * можно пропустить этот шаг
- **Windows 8 или более ранние версии:**
  * нужно запускать проект при помощи виртуальной машины с ОС Linux Ubuntu
    через [программу Virtual Box](https://www.virtualbox.org/wiki/Downloads)
- **Windows 10 или 11:**
  * необходимо [установить утилиту Windows Subsystem for Linux ](https://learn.microsoft.com/ru-ru/windows/wsl/install)

> После выполнения шага, все сводится к дальнейшему использованию консоли для установки Docker:

2. Запустить Docker Desktop, установленную на шаге 1 данной инструкции;

3. Установить Docker (выполнение команд требуется выполнять последовательно):
```bash
sudo apt update
sudo apt install curl
curl -fSL https://get.docker.com -o get-docker.sh
sudo sh ./get-docker.sh

# Дополнительно к Docker установите утилиту Docker Compose:
sudo apt install docker-compose-plugin
# Проверить работу Docker'a:
sudo systemctl status docker
```
4. Склонировать репозиторий на свой компьютер и перейти в папку с ним:

```bash
git clone https://github.com/BIXBER/foodgram-project-react.git
cd foodgram-project-react/
```
5. ***Опционально:** создать, активировать и наполнить виртуальное окружение:*

    1. Создать и активировать виртуальное окружение:

    ```bash
    cd backend/
    python -m venv venv
    source venv/Scripts/activate
    ```

    2. Установить зависимости из файла requirements.txt, предварительно обновив пакетный менеджер pip:

    ```bash
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    ```

6. Поднять контейнеры на основе уже созданных образов:
```bash
sudo docker compose up
```

7. Перейти в директорию с файлом docker-compose.yml и выполнить миграции:
```bash
cd ..
docker compose exec backend python manage.py migrate
# Проект запустится на 8090 порту
```

8. Загрузить в проект все необходимые данные для работы с запросами:

```bash
# Загрузить ингредиенты в БД
docker compose exec backend python manage.py load_ingredients
# Загрузить теги в БД
docker compose exec backend python manage.py load_tags
```

9. [Открыть локальное подключение](http://localhost:8090) через браузер и начать пользоваться проектом!

> Если возникнут некоторые трудности при установке Docker или непосредственно в его работе - вот 
  **[ссылка](https://code.s3.yandex.net/backend-developer/learning-materials/%D0%A3%D1%81%D1%82%D1%80%D0%B0%D0%BD%D0%B5%D0%BD%D0%B8%D0%B5%20%D0%BF%D1%80%D0%BE%D0%B1%D0%BB%D0%B5%D0%BC%20Docker%20for%20Windows.pdf)** с возможными решениями некоторых проблем.
---

## ▶️ Примеры запросов:
> Перед запуском ознакомьтесь с условиями, описанные в [примечании⬇️](#примечание)...
1. **Эндпоинт: https://www.foodhelper.shop/api/users/. Метод запроса: POST<br>Права доступа: Доступно без токена**

    При передаче следующих данных:
    * "email": "string" **(required)**,
    * "first_name": "string" **(required)**,
    * "last_name": "string" **(required)**,
    * "username": "string" **(required)**,
    * "password": "string" **(required)**,
  
    Вы получите ответ о создании нового пользователя:

    * "email": "string"
    * "id": "integer",
    * "username": "string",
    * "first_name": "string",
    * "last_name": "string"
<br>

2. **Эндпоинт: https://www.foodhelper.shop/api/auth/token/login/. Метод запроса: POST<br>Права доступа: Доступно без токена**

    При передаче имени зарегистрированного пользователя и пароля:

    * "password": "string" **(required)**,
    * "email": "string" **(required)**
    
    Вам в ответе будет выдан ***JWT Token***, позволяющий авторизоваться:

    * "auth_token": "string"

  > ***JWT Token*** необходимо вставить в *header* вашего запроса под ключом `Authorization`: `Token <ваш_токен>`

<br>

3. **Эндпоинт: https://www.foodhelper.shop/api/recipes/. Метод запроса: GET<br>Права доступа: Доступно без токена**

    В ответ вы получите список всех рецептов, которые имеются в базе данных проекта. Опционально, можно параметризировать запрос количеством записей, а также номером записи от общей выборки, от которой нужно начать просмотр с рецептами: для этого необходимо дописать к запросу следующую строку: `?limit=<кол-во_записей_на_вывод>&offset=<номер_записи_в_выборке>`.

    Также, можно применить параметра `is_in_shopping_cart=1` или `is_favorited=1`, чтобы отсортировать рецепты по состоящим в Вашей корзине или списке избранного соотвестсвенно.

<br>

4. **Эндпоинт: https://www.foodhelper.shop/api/recipes/ Метод запроса: POST.<br> Права доступа: Авторизованный пользователь**

    При передаче следующих данных **в теле запроса**:

    * "ingredients": "array" **(required)**,
    * "tags": "array" **(required)**,
    * "image": "binary" **(required)**,
    * "name": "string" **(required)**,
    * "text": "string" **(required)**,
    * "cooking_time": "integer" **(required)**
    
    В базу будет добавлен новый рецепт и придет ответ в виде:

    * "id": "integer",
    * "tags": "array",
    * "author": "integer",
    * "ingredients": "array",
    * "is_in_shopping_cart": "bool",
    * "is_favorited": "bool",
    * "name": "string",
    * "image": "binary",
    * "text": "string",
    * "cooking_time": "integer"

<br>

5. **Эндпоинт: https://www.foodhelper.shop/api/recipes/(int:id)/shopping_cart/ Параметр: `int:id` - номер рецепта в БД.
Метод запроса: POST. <br> Права доступа: Авторизованный пользователь**

    В корзину будет добавлен рецепт с id номером, указанном в параметре запроса, и придет ответ в виде:

    * "id": "integer",
    * "name": "string",
    * "image": "binary",
    * "cooking_time": "integer"

<br>

6. **Эндпоинт: https://www.foodhelper.shop/api/recipes/download_shopping_cart/ Метод запроса: POST. <br> Права доступа: Авторизованный пользователь**
    В ответ Вы получите возможность скачать список покупок на основе рецептов в корзине, в формате текстового файла `.txt`.
---

### Примечание:
> Проект **[FOODGRAM](#foodgram)** находится во временном доступе для пользователей сети Интернет. В связи с этим, в случае, если возникает ошибка доступа при обращении к домену https://www.foodhelper.shop/ - Вы можете [использовать проект локально](#2-запустить-проект-локально-в-контейнерах-docker) на своем компьютере, соответственно отправляя запросы по адресу http://127.0.0.1:8090
> **В данном руководстве, в качестве примера приведена лишь часть запросов к эндпоинтам, имеющихся в проекте [FOODGRAM](#foodgram)**

