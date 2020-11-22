#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import pyperclip
import time
from account import Account, BanStatus
from console import clear
from profilescraper import *
from tabulate import tabulate
from threading import Thread

LEGEND_BAN_SEASONAL = '†'
LEGEND_BAN_PERMANENT = '††'

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

            account = Account(
                account_index,
                a['email'],
                a['battletag'],
                a['country'],
                a['password'],
                a['created'],
                a['sms_protected'],
                BanStatus(a['ban_status']['banned'],
                a['ban_status']['permanent'],
                a['ban_status']['seasonal'],
                a['ban_status']['expires']))
            accounts.append(account)
            account_index = account_index + 1

    return accounts

def get_avg_sr(accounts, role):
    placed_accts = 0
    total_sr = 0

    for account in accounts:
        sr = getattr(account, role + "_rating")
        if sr:
            placed_accts += 1
            total_sr += int(sr)

    if placed_accts > 0:
        return int(total_sr / placed_accts)
    else:
        return '-'


def print_account_table():

    headers = ['']

    if config['columns']['email']:
        headers.append('Email')
    if config['columns']['battletag']:
        headers.append('BattleTag')
    if config['columns']['country']:
        headers.append('Country')
    if config['columns']['created']:
        headers.append('Created')
    if config['columns']['sms']:
        headers.append('SMS')
    if config['columns']['banned']:
        headers.append('Banned')
    if config['columns']['level']:
        headers.append('Level')
    if config['columns']['tank']:
        headers.append('Tank')
    if config['columns']['damage']:
        headers.append('Damage')
    if config['columns']['support']:
        headers.append('Support')

    table_data = []
    for account in accounts:

        row_data = []

        row_data.append(account.id)

        if config['columns']['email']:
            row_data.append(mask_email(account.email) if config['mask_emails'] else account.email)
        if config['columns']['battletag']:
            row_data.append(mask_battletag(account.battletag) if config['mask_battletags'] else account.battletag)
        if config['columns']['country']:
            row_data.append(account.country)
        if config['columns']['created']:
            row_data.append(account.created)
        if config['columns']['sms']:
            row_data.append('Yes' if account.sms_protected else 'No')
        if config['columns']['banned']:
            msg = 'Yes' if account.ban_status.banned else 'No'
            if account.ban_status.banned:
                if account.ban_status.seasonal:
                    msg = "%s%s" % (msg, LEGEND_BAN_SEASONAL)
                elif account.ban_status.permanent:
                    msg = "%s%s" % (msg, LEGEND_BAN_PERMANENT)
                else:
                    msg = "%s (%s)" % (msg, account.ban_status.get_expiration().strftime(config['date_format']))
            row_data.append(msg)
        if config['columns']['level']:
            row_data.append(account.level)
        if config['columns']['tank']:
            row_data.append(account.tank_rating if account.tank_rating else '-')
        if config['columns']['damage']:
            row_data.append(account.damage_rating if account.damage_rating else '-')
        if config['columns']['support']:
            row_data.append(account.support_rating if account.support_rating else '-')

        clear()
        table_data.append(row_data)

    tabulate.WIDE_CHARS_MODE = False
    print(tabulate(table_data, headers=headers))

def print_stats():
    print(tabulate([[sum(a.level if a.level is not None else 0 for a in accounts),
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

def print_legend():
    print("%s Seasonal Ban" % (LEGEND_BAN_SEASONAL))
    print("%s Permanent Ban" % (LEGEND_BAN_PERMANENT))


def prompt_action():
    value = input("\nSelect an account by the ID: ")
    if value == '': # enter, refresh list
        print_account_table()
    else:
        try:
            id = int()
            account = accounts[id - 1]
            prompt_account_actions(account)    
        except IndexError:
            pass
        except ValueError:
            pass 

def prompt_account_actions(account):
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


def load_config():
    config = None
    with open('config/config.json') as json_file:
        config = json.load(json_file)
    return config

def update_account_stats(accounts):
    for i in range (0, len(accounts)):  
        print("Getting accounts%s" % ("." * i), end="\r")
        time.sleep(1.5)

    threads = []

    for account in accounts:
        process = Thread(target=get_account_stats, args=[account])
        process.start()
        threads.append(process)

    for process in threads:
        process.join()


if __name__ == "__main__":

    config = load_config()
    accounts = get_accounts()
    update_account_stats(accounts)

    while True:
        print_account_table()
        print('')
        print_legend()
        print('')
        print_stats()
        time.sleep(0.5)
        prompt_action()

