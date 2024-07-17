import argparse
import requests
import json
import os
import getpass
from tusclient import client

# Глобальная переменная для хранения конфигурации
config = {}

# Функция для загрузки конфигурации
def load_config():
    global config
    with open(os.path.join(os.path.dirname(__file__), 'config.json'), 'r') as f:
        config = json.load(f)

load_config()  # Вызовите эту функцию при старте вашего приложения

# common

def get_total_size_of_directory(directory_path):
    total_size = 0
    for root, dirs, files in os.walk(directory_path):
        for f in files:
            file_path = os.path.join(root, f)
            if not os.path.islink(file_path):  # Игнорировать символические ссылки
                total_size += os.path.getsize(file_path)
    return total_size

# Функция для логина
def login(args):
    print(f"Logging in with email: {args.email}")
    file = './.codenrock'
    base_url = args.endpoint if args.endpoint else config['base_url']
    url = f'{base_url}/api/auth/login'

    # Получение пароля в интерактивном режиме
    password = getpass.getpass(prompt='Enter your password: ')

    data = {
            'email': args.email,
            'password': password
        }

    # Отправка POST-запроса
    response = requests.post(url, json=data)

    if response.status_code == 200:
        # Запись ответа в файл
        with open(file, 'w', encoding='utf-8') as file:
            response_data = response.json()
            token = response_data.get('token', None)
            file.write(token)
            print(f"Вы авторизовались!")
    else:
        print(f"Ошибка при авторизации: {response.json()}")

# Функции для create

def create_model(name, description, path, team_id, headers, base_url):
    url = f'{base_url}/api/ml-models'
    directory_structure = get_directory_structure(path)
    size_of_directory = get_total_size_of_directory(path)

    data = {
        'name': name,
        'description': description,
        'structure': directory_structure,
        'team_id': team_id,
        'size': size_of_directory
    }

    # Отправка POST-запроса с токеном в заголовках
    response = requests.post(url, json=data, headers=headers)

    if response.status_code == 200:
        print("Модель успешно создана.")
        model_id = response.json()['mlModel']['id']  # Получение ID модели из ответа
        return model_id
    else:
        print(f"Ошибка при создании модели: {response.json()}")
        return None

def get_directory_structure(rootdir):
    """
    Создает словарь, который представляет структуру папок и файлов,
    начиная с корневого каталога rootdir.
    """
    directory_structure = {}
    for root, dirs, files in os.walk(rootdir):
        # Получение пути относительно корневого каталога
        relative_path = os.path.relpath(root, rootdir)
        if relative_path == '.':
            relative_path = ''
        file_list = [f for f in files]
        directory_structure[relative_path] = file_list
    return directory_structure

def upload_files(path, headers, model_id, base_url):
    directory_structure = get_directory_structure(path)
    # Создание клиента tus для загрузки файлов
    tus_client_url = f'{base_url}/api/ml-models/upload-file'

    my_client = client.TusClient(tus_client_url, headers=headers)

    # Проход по всем файлам и их загрузка
    for relative_path in directory_structure:
        for file_name in directory_structure[relative_path]:
            file_path = os.path.join(path, relative_path, file_name)

            # Создание uploader'а и установка метаданных
            uploader = my_client.uploader(file_path, chunk_size=1024*1024)
            uploader.metadata['filename'] = file_name
            uploader.metadata['directory_path'] = os.path.join(relative_path, file_name)
            uploader.metadata['model_id'] = f'{model_id}'

            # Начало загрузки
            print(f"Загрузка: {file_path}")
            uploader.upload()
            print(f"Загружен: {file_path}")

def complete_upload(model_id, headers, base_url):
    data = {
        'status': 'completed'
    }
    completion_url = f'{base_url}/api/ml-models/{model_id}/set-status'
    try:
        completion_response = requests.post(completion_url, json=data, headers=headers)
        if completion_response.status_code == 200:
            # Проверка, что ответ содержит JSON
            if 'application/json' in completion_response.headers.get('Content-Type', ''):
                print(f"Ссылка на модель: {completion_response.json().get('mlModel', {}).get('link', 'Нет ссылки')}")
            else:
                print(f"Ответ сервера не в формате JSON: {completion_response.text}")
        else:
            print(f"Ошибка при уведомлении сервера о завершении загрузки: {completion_response.status_code}")
            if completion_response.text:
                print(f"Детали ошибки: {completion_response.text}")
    except requests.RequestException as e:
        print(f"Ошибка при уведомлении сервера о завершении загрузки: {e}")

def create(args):
    print(f"Creating model with name: {args.name} and path: {args.path}")
    file_path = './.codenrock'

    # Чтение токена из файла
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            token = file.read().strip()
    except FileNotFoundError:
        print("Файл с токеном не найден. Пожалуйста, авторизуйтесь сначала.")
        return

    headers = {
        'Authorization': f'Bearer {token}'
    }

    base_url = args.endpoint if args.endpoint else config['base_url']

    # Создание модели и получение ID
    model_id = create_model(args.name, args.description, args.path, args.team_id, headers, base_url)
    if model_id is not None:
        # Загрузка файлов
        upload_files(args.path, headers, model_id, base_url)
        complete_upload(model_id, headers, base_url)

# UPDATE
def update_model(model_id, name, description, path, headers, base_url):
    url = f'{base_url}/api/ml-models/{model_id}'
    directory_structure = get_directory_structure(path)
    size_of_directory = get_total_size_of_directory(path)
    data = {
        'name': name,
        'description': description,
        'structure': directory_structure,
        'size': size_of_directory
    }

    # Отправка PUT-запроса с токеном в заголовках
    response = requests.put(url, json=data, headers=headers)

    if response.status_code == 200:
        print("Модель успешно обновлена.")
        return model_id  # Возвращаем ID обновленной модели
    else:
        print(f"Ошибка при обновлении модели: {response.json()}")
        return None

# Функция, связанная с командой "update"
def update(args):
    print(f"Updating model with ID: {args.id}, name: {args.name} and path: {args.path}")
    file_path = './.codenrock'

    # Чтение токена из файла
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            token = file.read().strip()
    except FileNotFoundError:
        print("Файл с токеном не найден. Пожалуйста, авторизуйтесь сначала.")
        return

    headers = {
        'Authorization': f'Bearer {token}'
    }

    base_url = args.endpoint if args.endpoint else config['base_url']

    # Обновление модели
    model_id = args.id
    update_model(model_id, args.name, args.description, args.path, headers, base_url)
    upload_files(args.path, headers, model_id, base_url)
    complete_upload(model_id, headers, base_url)

# DELETE

# Функция, связанная с командой "delete"
def delete(args):
    print(f"Deleting model with ID: {args.id}")
    file_path = './.codenrock'

    # Чтение токена из файла
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            token = file.read().strip()
    except FileNotFoundError:
        print("Файл с токеном не найден. Пожалуйста, авторизуйтесь сначала.")
        return

    headers = {
        'Authorization': f'Bearer {token}'
    }

    base_url = args.endpoint if args.endpoint else config['base_url']

    # Удаление модели
    delete_model(args.id, headers, base_url)

def delete_model(model_id, headers, base_url):
    url = f'{base_url}/api/ml-models/{model_id}'

    # Отправка DELETE-запроса с токеном в заголовках
    response = requests.delete(url, headers=headers)

    if response.status_code == 200:
        print(f"Модель с ID {model_id} успешно удалена.")
    else:
        print(f"Ошибка при удалении модели с ID {model_id}: {response.json()}")

# LIST
# Функция, связанная с командой "list"
def list(args):
    file_path = './.codenrock'

    # Чтение токена из файла
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            token = file.read().strip()
    except FileNotFoundError:
        print("Файл с токеном не найден. Пожалуйста, авторизуйтесь сначала.")
        return

    headers = {
        'Authorization': f'Bearer {token}'
    }

    base_url = args.endpoint if args.endpoint else config['base_url']

    # Получение списка моделей
    list_models(headers, base_url)

def list_models(headers, base_url):
    url = f'{base_url}/api/ml-models'

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        models = response.json()['mlModels']
        print("Список доступных моделей:")
        for model in models:
            print(f"ID: {model['id']}, Name: {model['name']}")
    else:
        print(f"Ошибка при получении списка моделей: {response.status_code}")
        print(response.json())

# TEAM LIST
# Функция, связанная с командой "team list"
def team_list(args):
    file_path = './.codenrock'

    # Чтение токена из файла
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            token = file.read().strip()
    except FileNotFoundError:
        print("Файл с токеном не найден. Пожалуйста, авторизуйтесь сначала.")
        return

    headers = {
        'Authorization': f'Bearer {token}'
    }

    base_url = args.endpoint if args.endpoint else config['base_url']

    # Получение списка команд
    list_teams(headers, base_url)

def list_teams(headers, base_url):
    url = f'{base_url}/api/user/my-teams'

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        teams = response.json()['teams']
        print("Список доступных команд:")
        for team in teams:
            print(f"ID: {team['id']}, Name: {team['name']}")
    else:
        print(f"Ошибка при получении списка команд: {response.status_code}")
        print(response.json())

# SHOW

def print_directory_structure(structure, indent=0):
    # Сортировка ключей для последовательного вывода
    for key in sorted(structure.keys()):
        # Вывод отступа и имени папки/файла
        print('  ' * indent + f"- {key}/" if key else "Root:")
        # Если это папка, то рекурсивно выводим её содержимое
        if isinstance(structure[key], dict):
            print_directory_structure(structure[key], indent + 1)
        else:
            for item in structure[key]:
                print('  ' * (indent + 1) + f"- {item}")

def show_model(model_id, headers, base_url):
    url = f'{base_url}/api/ml-models/{model_id}'

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        model = response.json()['mlModel']
        print(f"Детали модели с ID {model_id}:")
        print(f"Имя: {model['name']}")
        print(f"Описание: {model['description']}")
        print(f"Размер: {model['size']} Kb")
        print("Структура файлов:")
        print_directory_structure(model['structure'])
        print(f"Статус: {model['status']}")
    else:
        print(f"Ошибка при получении данных модели с ID {model_id}: {response.text if response.text else response.status_code}")

# Функция, связанная с командой "show"
def show(args):
    file_path = './.codenrock'

    # Чтение токена из файла
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            token = file.read().strip()
    except FileNotFoundError:
        print("Файл с токеном не найден. Пожалуйста, авторизуйтесь сначала.")
        return

    headers = {
        'Authorization': f'Bearer {token}'
    }

    base_url = args.endpoint if args.endpoint else config['base_url']

    # Показать детали модели
    show_model(args.id, headers, base_url)

def main():
    # Создание парсера
    parser = argparse.ArgumentParser(description="CLI для codenrock ML-models")
    subparsers = parser.add_subparsers(help='commands')

    # Создание парсера для команды "login"
    login_parser = subparsers.add_parser('login', help='Авторизоваться')
    login_parser.add_argument('--email', type=str, required=True, help='Email пользователя')
    login_parser.add_argument('--endpoint', type=str, help='backend endpoint')
    login_parser.set_defaults(func=login)

    # Создание парсера для команды "create"
    create_parser = subparsers.add_parser('model create', help='Создать модель')
    create_parser.add_argument('--name', type=str, required=True, help='Название модели')
    create_parser.add_argument('--description', type=str, required=False, help='Описание модели')
    create_parser.add_argument('--path', type=str, required=True, help='Путь до папки')
    create_parser.add_argument('--team_id', type=str, help='id команды')
    create_parser.add_argument('--endpoint', type=str, help='backend endpoint')
    create_parser.set_defaults(func=create)

    # Создание парсера для команды "update"
    update_parser = subparsers.add_parser('model update', help='Обновить модель')
    update_parser.add_argument('--id', type=str, required=True, help='ID модели')
    update_parser.add_argument('--name', type=str, required=True, help='Новое название модели')
    update_parser.add_argument('--description', type=str, required=False, help='Описание модели')
    update_parser.add_argument('--path', type=str, required=True, help='Путь до папки с обновленными файлами')
    update_parser.add_argument('--endpoint', type=str, help='backend endpoint')
    update_parser.set_defaults(func=update)

    # Создание парсера для команды "delete"
    delete_parser = subparsers.add_parser('model delete', help='Удалить модель')
    delete_parser.add_argument('--id', type=str, required=True, help='ID модели для удаления')
    delete_parser.add_argument('--endpoint', type=str, help='backend endpoint')
    delete_parser.set_defaults(func=delete)

    # Создание парсера для команды "list"
    list_parser = subparsers.add_parser('model list', help='Получить список всех моделей')
    list_parser.add_argument('--endpoint', type=str, help='backend endpoint')
    list_parser.set_defaults(func=list)

    # Создание парсера для команды "show"
    show_parser = subparsers.add_parser('model show', help='Показать детали модели')
    show_parser.add_argument('--id', type=str, required=True, help='ID модели для показа деталей')
    show_parser.add_argument('--endpoint', type=str, help='backend endpoint')
    show_parser.set_defaults(func=show)

    # Создание парсера для команды "team list"
    team_list_parser = subparsers.add_parser('team list', help='Получить список всех команд')
    team_list_parser.add_argument('--endpoint', type=str, help='backend endpoint')
    team_list_parser.set_defaults(func=team_list)

    # Обработка аргументов
    args = parser.parse_args()
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
