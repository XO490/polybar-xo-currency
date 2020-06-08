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
    except EnvironmentError as e:
        print(f'[Err] get_coinmarketcap_data:\n     \--{e}')
    else:
        save_json({'coins': coins}, 'coinmarketcap.json')
        return True


def get_fiat_fcr(base, quote, value):
    filename_saveopen_json = f'{quote}_{base}.json'
    try:
        resp = get_response(BASE_URL.format(quote, base, value)).json()
    except:
        print('ISO currency code error')
    else:
        if resp is not None:
            save_json(resp, filename_saveopen_json)
            exchange_rate = round(resp[quote], 2)
            # print(f'{exchange_rate}')
            return f'{exchange_rate}'
        else:
            resp = open_json(filename_saveopen_json)
            if resp is None:
                # print('!')
                return '!'
            else:
                exchange_rate = round(resp[quote], 2)
                # print(f'{exchange_rate}!')
                return f'{exchange_rate}!'


def get_crypto_bc(base, quote, value):
    filename_saveopen_json = f'{base}.json'
    try:
        resp = get_response(BASE_URL_BC.format(base)).json()
    except:
        print('ISO currency code error')
    else:
        if resp is not None:
            save_json(resp, filename_saveopen_json)
            if resp.get(quote):
                exchange_rate = resp[quote]['last']
            else:
                exchange_rate = f'ISO currency({quote}) code error'
            print(f'{exchange_rate}')
        else:
            resp = open_json(filename_saveopen_json)
            if resp is None:
                print('!')
            else:
                if resp.get(quote):
                    exchange_rate = resp[quote]['last']
                else:
                    exchange_rate = f'ISO currency({quote}) code error'
                print(f'{exchange_rate}!')


def get_crypto_cmc(base, quote, value, changes):

    def get_price():
        try:
            if base != 'USD':
                another_quote = get_fiat_fcr('USD', quote, value)
                coin = open_json('coinmarketcap.json')['coins'][base]
                price = round(float(coin['price']) * float(another_quote), 6)
            else:
                coin = open_json('coinmarketcap.json')['coins'][quote]
                price = coin['price']
            hour = coin['hour']
            day = coin['day']
            week = coin['week']
        except EnvironmentError as e:
            print(f'[Err] get_crypto_cmc> get_price:\n     \-{e}')
        else:
            if changes:
                if changes == 'all':
                    return f'{price} {hour} {day} {week}'
                else:
                    return f'{price} {coin[changes]}'
            else:
                return price

    resp = get_coinmarketcap_data(get_response(BASE_URL_CMC))
    price = get_price()
    if resp:
        print(price)
    else:
        print(f'{price}!')


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
                        choices=['all', 'hour', 'day', 'week'],
                        help='Show changes for 1h, 24h, 7d. Only for --crypto cmc',
                        default=False)
    args = parser.parse_args()

    fiat = args.fiat
    crypto = args.crypto
    base = (args.base).upper()
    quote = args.quote.upper()
    value = args.value
    changes = args.changes

    if fiat is None and crypto is None or fiat == 'fcr':
        fiat = get_fiat_fcr(base=base, quote=quote, value=value)
        print(fiat)

    if crypto == 'bc':
        get_crypto_bc(base=base, quote=quote, value=value)

    if crypto == 'cmc':
        get_crypto_cmc(base=base, quote=quote, value=value, changes=changes)


if __name__ == "__main__":
    get_args()
