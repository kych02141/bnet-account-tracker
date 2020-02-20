#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Rename accounts.example.json to accounts.json
#
# Example format:
# 
# [
#     {
#         "email": "bnetplayer1@gmail.com",
#         "battletag": "bnetplayer1#11254",
#         "country": "United States",
#         "password": "X6K.qV:v^Fk43&2-"
#     },
#     {
#         "email": "bnetplayer2@gmail.com",
#         "battletag": "bnetplayer#1916",
#         "country": "Japan",
#         "password": "{FZAfrW)25kNU;P#"
#     }
# ]

# Windows Note:
# May need to change CMD code page to UTF-8 in Windows
# As well as set PYTHONIOENCODING=UTF-8

import json
import requests
import urllib.parse
from bs4 import BeautifulSoup
from prestige import PRESTIGE_BORDERS, PRESTIGE_STARS
from tabulate import tabulate
from threading import Thread


class Account:

    def __init__(self, email, battletag, country, password):
        self.email = email
        self.battletag = battletag
        self.country = country
        self.password = password
        self.level = None
        self.public = False
        self.tank_rating = None
        self.damage_rating = None
        self.support_rating = None


def get_accounts():
    accounts = []

    with open('accounts.json', encoding='utf-8') as json_file:
        data = json.load(json_file)
        for a in data:

            email = a['email']
            battletag = a['battletag']
            country = a['country']
            password = a['password']

            account = Account(email, battletag, country, password)
            accounts.append(account)

    return accounts


def get_prestige_level(level, border_hash, star_hash):
    prestige = 0

    if border_hash and border_hash in PRESTIGE_BORDERS:
        prestige += PRESTIGE_BORDERS.get(border_hash)

    if star_hash and star_hash in PRESTIGE_STARS:
        prestige += PRESTIGE_STARS.get(star_hash)

    return level + (prestige * 100)


def get_account_stats(account):

    x = account.battletag.split('#')
    name = urllib.parse.quote_plus(x[0])
    id = x[1]

    url = "https://playoverwatch.com/en-us/career/pc/%s-%s" % (name, id)

    profile_response = requests.get(url, timeout=5)
    soup = BeautifulSoup(profile_response.content, "html.parser")

    level_div = soup.find("div", {"class": "player-level"})
    level = int(level_div.text)
    border_hash = level_div['style'].rpartition('/')[-1][:-6]
    star_div = level_div.find('div', {"class": "player-rank"})

    if star_div:
        star_hash = star_div['style'].rpartition('/')[-1][:-6]
    else:
        star_hash = None

    account.level = get_prestige_level(level, border_hash, star_hash)

    tank_result = soup.find(
        "div", {"data-ow-tooltip-text": "Tank Skill Rating"})
    if tank_result:
        account.tank_rating = tank_result.nextSibling.text

    damage_result = soup.find(
        "div", {"data-ow-tooltip-text": "Damage Skill Rating"})
    if damage_result:
        account.damage_rating = damage_result.nextSibling.text

    support_result = soup.find(
        "div", {"data-ow-tooltip-text": "Support Skill Rating"})
    if support_result:
        account.support_rating = support_result.nextSibling.text


def get_avg_sr(accounts, role):
    placed_accts = 0
    total_sr = 0

    for account in accounts:
        sr = getattr(account, role + "_rating")
        if sr:
            placed_accts += 1
            total_sr += int(sr)

    return int(total_sr / placed_accts)


if __name__ == "__main__":

    print("Getting accounts...")

    accounts = get_accounts()

    threads = []

    for account in accounts:
        process = Thread(target=get_account_stats, args=[account])
        process.start()
        threads.append(process)

    for process in threads:
        process.join()

    data = []
    for account in accounts:
        data.append([account.email, account.battletag, account.country, account.level,
                     (account.tank_rating if account.tank_rating else '-'),
                     (account.damage_rating if account.damage_rating else '-'),
                     (account.support_rating if account.support_rating else '-')])

    tabulate.WIDE_CHARS_MODE = False

    print('')
    print(tabulate(data, headers=[
          'Email', 'BattleTag', 'Country', 'Level', 'Tank', 'Damage', 'Support'], showindex="always"))

    print('')
    print(tabulate([[sum(a.level for a in accounts), get_avg_sr(accounts, "tank"), get_avg_sr(accounts, "damage"), get_avg_sr(
        accounts, "support")]], headers=['Total Levels', 'Tank Avg', 'Damage Avg', 'Support Avg']))

    input()
