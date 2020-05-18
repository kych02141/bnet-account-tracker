#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import pyperclip
import requests
import time
import urllib.parse
from bs4 import BeautifulSoup
from account import Account
from prestige import PRESTIGE_BORDERS, PRESTIGE_STARS
from tabulate import tabulate
from threading import Thread

config = None
with open('config/config.json') as json_file:
    config = json.load(json_file)


def mask_battletag(battletag):
    split = battletag.split('#')
    name = split[0]
    id = split[1]
    return "%s#%s%s%s" % (name, id[0][:1], '*' * (len(id) - 2), id[-1:])


def mask_email(email):
    split = email.split('@')
    username = split[0]
    domain = split[1]
    return "%s%s%s@%s" % (username[0][:1],
                          '*' * (len(username) - 2),
                          username[-1:],
                          domain)

def get_accounts():
    accounts = []

    with open('config/accounts.json', encoding='utf-8') as json_file:
        data = json.load(json_file)
        account_index = 1
        for a in data:

            email = a['email']
            battletag = a['battletag']
            country = a['country']
            password = a['password']
            created = a['created']

            account = Account(
                account_index,
                email,
                battletag,
                country,
                password,
                created)
            accounts.append(account)
            account_index = account_index + 1

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


def print_table():
    print('')
    print(
        tabulate(
            data,
            headers=[
                '',
                'Email',
                'BattleTag',
                'Country',
                'Level',
                'Tank',
                'Damage',
                'Support']))

    print('')
    print(tabulate([[sum(a.level for a in accounts),
                     get_avg_sr(accounts,
                                "tank"),
                     get_avg_sr(accounts,
                                "damage"),
                     get_avg_sr(accounts,
                                "support")]],
                   headers=['Total Levels',
                            'Tank Avg',
                            'Damage Avg',
                            'Support Avg']))


def prompt_action():
    valid_id = False
    while not valid_id:
        try:
            id = int(input("\nSelect an account by the ID: "))
            account = accounts[id - 1]
            valid_id = True
        except IndexError:
            pass
        except ValueError:
            pass

    actions = [
        "[1] Copy email to clipboard",
        "[2] Copy password to clipboard",
        "[3] Copy battletag to clipboard",
        "[4] Go back"
    ]

    for a in actions:
        print(a)
    print()

    valid_action = False
    while not valid_action:
        try:
            action = int(
                input("What would you like to do with this account: "))
            actions[action - 1]
            valid_action = True
        except IndexError:
            pass
        except ValueError:
            pass

    if action == 1:
        pyperclip.copy(account.email)
        print("Email copied to clipboard!")
    if action == 2:
        pyperclip.copy(account.password)
        print("Password copied to clipboard!")
    if action == 3:
        pyperclip.copy(account.battletag)
        print("Battletag copied to clipboard!")
    if action == 4:
        pass

    print("Returning to accounts...")
    time.sleep(0.5)


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
        data.append(
            [
                account.id,
                mask_email(
                    account.email) if config['mask_emails'] else account.email,
                mask_battletag(
                    account.battletag) if config['mask_battletags'] else account.battletag,
                account.country,
                account.level,
                (account.tank_rating if account.tank_rating else '-'),
                (account.damage_rating if account.damage_rating else '-'),
                (account.support_rating if account.support_rating else '-')])

    tabulate.WIDE_CHARS_MODE = False

    while True:
        print_table()
        time.sleep(0.5)
        prompt_action()
