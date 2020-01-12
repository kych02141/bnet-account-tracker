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
    self.sr = None

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

    divs = soup.findAll("div", {"class": "competitive-rank"})

    if len(divs) > 0:
        account.sr = divs[0].text

if __name__ == "__main__":

    print "Getting accounts..."

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
            (account.sr if account.sr else 'N/A')])

    print ''
    print tabulate(data, headers=['Email', 'BattleTag', 'SR'])

    raw_input()