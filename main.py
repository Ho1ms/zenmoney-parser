import json
import gspread
import requests as req
from oauth2client.service_account import ServiceAccountCredentials
import os.path

print('Инициализация...')
def error_exit():
    input('Нажмите любую клавишу для выхода...')
    exit()

def handler(account_id, list_id):
    main_url = 'https://api.zenmoney.ru/share/account/'
    r = req.get(f'{main_url}{account_id}/account/').json()

    array = [('Баланс:',r.get('balance'))]
    r = req.get(f'{main_url}{account_id}/transactions/').json()

    for row in r.get('transaction'):
        array.append((row.get('date'), row.get('income'), row.get('comment')))

    nextToken = r.get("nextPageToken")

    while True:
        data = req.get(f'{main_url}{account_id}/transactions/', params={'nextPageToken':nextToken}).json()

        for row in data.get('transaction'):
            array.append((row.get('date'), row.get('income'), row.get('comment')))

        if data.get('nextPageToken') is None:
            break

        nextToken = data.get('nextPageToken')

    sheet = table.get_worksheet_by_id(list_id)
    sheet.clear()
    sheet.append_rows(array, value_input_option='USER_ENTERED')

print('Проверка заданных параметров...')

if not os.path.isfile('config_parser.json'):
    with open('config_parser.json','w+',encoding='utf-8') as file:
        file.write('{"list_id":"ID таблицы","":""}')

with open('config_parser.json','r',encoding='utf-8') as file:
    f = file.read()
    if not len(f):
        print('Заполните файл config_parser.json:\n{"код аккаунта":"id листа"}')
        file.write('{"list_id":"ID таблицы","код аккаунта":"id листа"}')
        error_exit()

    try:
        cfg = json.loads(f)
    except json.decoder.JSONDecodeError:
        print('Неверный формат файла, он должен быть формата json! (проверьте валидацию)')
        error_exit()

    GOOGLE_KEY_FILE = 'creds.json'
    scope = [
        'https://www.googleapis.com/auth/spreadsheets',
    ]
    try:
        credentials = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_KEY_FILE, scope)
    except FileNotFoundError:
        print('Файл creds.json не найден! (Файл с ключами к Google аккаунту)')
        error_exit()

    gc = gspread.authorize(credentials)
    table = gc.open_by_key(cfg.get('list_id'))

    del cfg['list_id']

    for account_id, list_id in cfg.items():
        print(f'Обновляю {account_id} в {list_id}')
        handler(account_id, list_id)
        print(f'Успешно обновил {account_id} в {list_id}')

    print('Данные успешно обновлены!')

