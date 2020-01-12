#!/usr/bin/env python
# -*- coding: utf-8 -*- 

# Create accounts.txt file and enter account information, one per line
# ex: email@gmail.com:Syntack#11114

# Windows Note:
# May need to change CMD code page to UTF-8 in Windows
# As well as set PYTHONIOENCODING=UTF-8

import io
import requests
from bs4 import BeautifulSoup
from tabulate import tabulate
from threading import Thread

class Account:

  def __init__(self, email, battletag):
    self.email = email
    self.battletag = battletag
    self.tank_rating = None
    self.damage_rating = None
    self.support_rating = None

def get_accounts():
    accounts = []

    with io.open('accounts.txt','r', encoding='utf-8') as f:
        for line in f:
            x = line.split(':')
            email = x[0]
            btag = x[1]
            account = Account(email, btag)
            accounts.append(account)

    return accounts

def get_current_sr(account):

    x = account.battletag.split('#')
    name = x[0]
    id = x[1]

    url = "https://playoverwatch.com/en-us/career/pc/%s-%s" % (name, id)

    profile_response = requests.get(url, timeout=5)
    soup = BeautifulSoup(profile_response.content, "html.parser")

    tank_result = soup.find("div", {"data-ow-tooltip-text" : "Tank Skill Rating"})
    if tank_result:
        account.tank_rating = tank_result.nextSibling.text

    damage_result = soup.find("div", {"data-ow-tooltip-text" : "Damage Skill Rating"})
    if damage_result:
        account.damage_rating = damage_result.nextSibling.text

    support_result = soup.find("div", {"data-ow-tooltip-text" : "Support Skill Rating"})
    if support_result:
        account.support_rating = support_result.nextSibling.text

if __name__ == "__main__":

    print("Getting accounts...")

    accounts = get_accounts()

    threads = []

    for account in accounts:
        process = Thread(target=get_current_sr, args=[account])
        process.start()
        threads.append(process)

    for process in threads:
        process.join()

    data = []
    for account in accounts:
        data.append([account.email, account.battletag,
        (account.tank_rating if account.tank_rating else 'N/A'),
        (account.damage_rating if account.damage_rating else 'N/A'),
        (account.support_rating if account.support_rating else 'N/A')])

    print ('')
    print (tabulate(data, headers=['Email', 'BattleTag', 'Tank', 'Damage', 'Support']))

    input()