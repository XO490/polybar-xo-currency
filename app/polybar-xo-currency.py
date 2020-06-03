#!/usr/bin/env python
# coding: utf-8
# Polybar XO Currency
# https://t.me/XO490

BASE_URL = 'https://freecurrencyrates.com/api/action.php?do=cvals&iso={}&f={}&v={}&s=cbr'
BASE_URL_BC = 'https://blockchain.info/ticker?base={}'
BASE_URL_CMC = 'https://coinmarketcap.com/all/views/all/'
useragent = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:76.0) Gecko/20100101 Firefox/76.0'}
proxy = None
# proxy = {'http': 'http://45.76.255.75:3128'}  # you favourites proxy

import requests
import sys
import json
from bs4 import BeautifulSoup


def save_json(data, filename):
    if data:
        with open(f'/tmp/{filename}', 'w') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)


def open_json(filename):
    try:
        with open(f'/tmp/{filename}', 'r') as file:
            data = json.load(file)
    except:
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
        return r


def get_coinmarketcap_data(html):
    if html is None:
        sys.exit('[Err] get_coinmarketcap_data: HTML is None')
    try:
        soup = BeautifulSoup(html.text, 'lxml')
        parser = soup.find_all('div', class_='cmc-table__table-wrapper-outer')[2]
        trs = parser.find_all('tr')[1:]
        data = []
        for tr in trs:
            tds = tr.find_all('td')

            name = tds[1].text
            symbol = tds[2].text
            price = (tds[4].text).replace('$', '').replace(',', '')
            h1 = tds[7].text
            h24 = tds[8].text
            d7 = tds[9].text

            data.append({symbol: {
                         'name': name,
                         'price': price,
                         '1h': h1,
                         '24h': h24,
                         '7d': d7}})

        jdata = {'coins': data}
    except EnvironmentError as e:
        print(f'[Err] get_coinmarketcap_data:\n     \--{e}')
    else:
        save_json(jdata, 'coinmarketcap.json')
        return True


def get_coinmarketcap_price(coin_symbol, changes=False):
    if coin_symbol is None:
        sys.exit('[Err] get_coin_price: coin_symbol is None.')
    try:
        symbol = coin_symbol.upper()
        coin = open_json('coinmarketcap.json')['coins'][0][symbol]
        price = coin['price']
        hour = coin['1h']
        day = coin['24h']
        week = coin['7d']
    except Exception as e:
        print(f'[Err] get_coin_price:\n     \-{e}')
    else:
        if changes:
            print(f'{price} {hour} {day} {week}')
        else:
            print(price)


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
            resp = get_response(BASE_URL_BC.format(anycur)).json()
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
            resp = get_response(BASE_URL.format(mycur, anycur, value)).json()
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
    resp = get_coinmarketcap_data(get_response(BASE_URL_CMC))
    if resp:
        get_coinmarketcap_price('btc', changes=True)
    # main()
