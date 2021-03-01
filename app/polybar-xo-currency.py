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

import argparse
import requests
import os
import json
from bs4 import BeautifulSoup
from requests import Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects


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
        return None
    try:
        soup = BeautifulSoup(html.text, 'lxml')
        parser = soup.find_all('div', class_='cmc-table__table-wrapper-outer')[2]
        trs = parser.find_all('tr')[1:]
        coins = {}
        for tr in trs:
            tds = tr.find_all('td')

            name = tds[1].text
            symbol = tds[2].text
            price = (tds[4].text).replace('$', '').replace(',', '')
            hour = tds[7].text
            day = tds[8].text
            week = tds[9].text

            coins.update({symbol: {
                         'name': name,
                         'price': price,
                         'hour': hour,
                         'day': day,
                         'week': week}})
    except:
        return False
    else:
        save_json({'coins': coins}, 'coinmarketcap.json')
        return True


def get_fiat_fcr(base, quote, value):
    filename_saveopen_json = f'{quote}_{base}.json'
    try:
        resp = get_response(BASE_URL.format(quote, base, value))
    except:
        pass
    if resp is not None:
        if resp.status_code == 500:
            return resp.text
        if resp.status_code == 200:
            save_json(resp.json(), filename_saveopen_json)
            exchange_rate = round(resp.json()[quote], 2)
            return f'{exchange_rate}'
    else:
        resp = open_json(filename_saveopen_json)
        if resp is None:
            return '!'
        else:
            exchange_rate = round(resp[quote], 2)
            return f'{exchange_rate}!'


def get_crypto_bc(base, quote, value):
    filename_saveopen_json = f'{base}.json'
    try:
        resp = get_response(BASE_URL_BC.format(base)).json()
    except:
        resp = None
    if resp is not None:
        save_json(resp, filename_saveopen_json)
        if resp.get(quote):
            exchange_rate = resp[quote]['last']
        else:
            exchange_rate = f'unknown currency: {quote}'
        return f'{exchange_rate}'
    else:
        resp = open_json(filename_saveopen_json)
        if resp is None:
            return '!'
        else:
            if resp.get(quote):
                exchange_rate = resp[quote]['last']
            else:
                exchange_rate = f'unknown currency: {quote}'
            return f'{exchange_rate}!'


# def get_crypto_cmc(base, quote, value, changes):

#     def get_price():
#         try:
#             if base != 'USD':
#                 if open_json('coinmarketcap.json')['coins'].get(base):
#                     coin = open_json('coinmarketcap.json')['coins'].get(base)
#                 else:
#                     return f'unknown currency: {base}'
#                 another_quote = get_fiat_fcr('USD', quote, value)
#                 if another_quote.isdigit():
#                     price = round(float(coin['price']) * float(another_quote), 2)
#                 else:
#                     another_quote = another_quote.split('!')[0]
#                     price = round(float(coin['price']) * float(another_quote), 2)
#             else:
#                 coin = open_json('coinmarketcap.json')['coins'][quote]
#                 price = coin['price']
#             hour = coin['hour']
#             day = coin['day']
#             week = coin['week']
#         except:
#             pass
#         else:
#             if changes:
#                 if changes == 'all':
#                     return f'{price} {hour} {day} {week}'
#                 else:
#                     return f'{price} {coin[changes]}'
#             else:
#                 return price

#     resp = get_coinmarketcap_data(get_response(BASE_URL_CMC))
#     if resp:
#         return get_price()
#     else:
#         path = '/tmp/coinmarketcap.json'
#         if os.path.exists(path) is not True:
#             return '!'
#         return f'{get_price()}!'


def get_cmc_api_currency(url=None, symbol=None, accuracy=2, base='USD', changes=None):
    if url is None:
        url = 'https://web-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
    parameters = {
        'start': '1',
        'limit': '5000',
        'convert': f'{base}'}
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': 'b54bcf4d-1bca-4e8e-9a24-22ff2c3d462c', }

    session = Session()
    session.headers.update(headers)

    try:
        response = session.get(url, params=parameters)
        data = json.loads(response.text)
    except (ConnectionError, Timeout, TooManyRedirects) as err:
        print(err)
        return err
    else:
        # with open('response.json', 'w') as file:
            # json.dump(data, file, ensure_ascii=False, indent=4)
        # print(data['data'][0])

        def get_msg_currency(symbol=None):
            for coin in data['data']:
                if coin['symbol'] == symbol:
                    currecy = coin['quote'][f'{base}']['price']
                    if changes:
                        ch = coin['quote'][f'{base}'][f'percent_change_{changes}']
                        change = f' {ch:.2f}% {changes}'
                    else:
                        change = ''
                    msg = f'{currecy:.{accuracy}f}{change}'
                    return msg

        symbol = symbol.upper()
        if symbol is not None:
            msg_currency = get_msg_currency(symbol=symbol)
        if msg_currency is not None:
            return msg_currency
        else:
            print('Wrong symbol..')
            return 'Wrong symbol..'


def get_args():
    parser = argparse.ArgumentParser(description='Polybar XO Crypto and Fiat currency.')
    parser.add_argument('--fiat',
                        choices=['fcr'],
                        type=str,
                        help='For fiat currency and basic crypto')
    parser.add_argument('--crypto',
                        choices=['bc', 'cmc'],
                        type=str,
                        help='For advanced crypto currency')
    parser.add_argument('--base',
                        type=str,
                        help='Base coin, default USD',
                        default='USD')
    parser.add_argument('quote',
                        type=str,
                        help='The quote coin')
    parser.add_argument('-v', '--value',
                        type=int,
                        help='Currency calculator, example: --base USD BTC -v 4',
                        default=1)
    parser.add_argument('--changes',
                        type=str,
                        choices=['1h', '24h', '7d'],
                        help='Show changes for 1h, 24h, 7d. Only for --crypto cmc',
                        default=False)
    parser.add_argument('--accuracy',
                        type=str,
                        choices=['0', '1', '2', '3', '4', '5', '6', '7', '8'],
                        help='Zeros after decimal point. 2 by default. Only for --crypto cmc',
                        default=False)
    args = parser.parse_args()

    fiat = args.fiat
    crypto = args.crypto
    base = (args.base).upper()
    quote = args.quote.upper()
    value = args.value
    changes = args.changes
    accuracy = args.accuracy

    if fiat is None and crypto is None or fiat == 'fcr':
        fiat = get_fiat_fcr(base=base, quote=quote, value=value)
        print(fiat)

    if crypto == 'bc':
        bc = get_crypto_bc(base=base, quote=quote, value=value)
        print(bc)

    # if crypto == 'cmc':
    #     cmc = get_crypto_cmc(base=base, quote=quote, value=value, changes=changes)
    #     print(cmc)

    if crypto == 'cmc':
        cmc = get_cmc_api_currency(symbol=quote, accuracy=accuracy, base=base, changes=changes)
        print(cmc)


if __name__ == "__main__":
    get_args()
