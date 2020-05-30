#!/usr/bin python
# coding: utf-8
# Polybar XO Currency
# https://t.me/XO490

BASE_URL = 'https://freecurrencyrates.com/api/action.php?do=cvals&iso={}&f={}&v={}&s=cbr'
BASE_URL_BC = 'https://blockchain.info/ticker?base={}'
BASE_URL_CMC = 'https://coinmarketcap.com/'
useragent = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:76.0) Gecko/20100101 Firefox/76.0'}
proxy = None
# proxy = {'http': 'http://45.76.255.75:3128'}  # you favourites proxy

import requests
import sys
import json


def save_json(data, filename):
    if data:
        with open(f'/tmp/{filename}', 'w') as file:
            json.dump(data, file, ensure_ascii=False)


def open_json(filename):
    try:
        with open(f'/tmp/{filename}', 'r') as file:
            data = json.load(file)
    except:
        mycur = filename.split('_')[0].upper()
        return None
    else:
        return data


def get_response(url):
    try:
        r = requests.get(url=url,
                         headers=useragent,
                         proxies=proxy,
                         timeout=60,
                         allow_redirects=True)
        r.encoding = 'utf-8'
    except:
        return None
    else:
        return r.json()


def get_attr():
    argv = sys.argv
    if (len(argv) < 3) or (len(argv) > 4):
        sys.exit('\nUSAGE:\n\tExample: python main.py rub usd\n\t\t python main.py rub eur 2\n')
    if (len(argv) == 3):
        mycur = argv[1]
        anycur = argv[2]
        data = {'mycur': mycur, 'anycur': anycur}
    if (len(argv) == 4):
        mycur = argv[1]
        anycur = argv[2]
        value = argv[3]
        data = {'mycur': mycur, 'anycur': anycur, 'value': value}
    return data


def main():
    attr = get_attr()
    mycur = attr.get('mycur')
    anycur = attr.get('anycur')
    value = attr.get('value')

    if mycur == '--blockchain':
        filename_saveopen_json = f'{anycur}.json'
        try:
            resp = get_response(BASE_URL_BC.format(anycur))
        except:
            print('ISO currency code error')
        else:
            if resp is not None:
                save_json(resp, filename_saveopen_json)
                curs = resp['USD']['15m']
                print(f'{curs}')
            else:
                resp = open_json(filename_saveopen_json)
                if resp is None:
                    print('!')
                else:
                    curs = resp['USD']['15m']
                    print(f'{curs}!')
    else:
        filename_saveopen_json = f'{mycur}_{anycur}.json'
        try:
            if value is None:
                value = 1
            resp = get_response(BASE_URL.format(mycur, anycur, value))
        except:
            print('ISO currency code error')
        else:
            if resp is not None:
                save_json(resp, filename_saveopen_json)
                curs = round(resp[mycur.upper()], 2)
                print(f'{curs}')
            else:
                resp = open_json(filename_saveopen_json)
                if resp is None:
                    print('!')
                else:
                    curs = round(resp[mycur.upper()], 2)
                    print(f'{curs}!')


if __name__ == "__main__":
    main()
