import requests
import urllib.parse
from bs4 import BeautifulSoup
from prestige import PRESTIGE_BORDERS, PRESTIGE_STARS
from profile import CareerProfile

def get_prestige_level(level, border_hash, star_hash):
    prestige = 0

    if border_hash and border_hash in PRESTIGE_BORDERS:
        prestige += PRESTIGE_BORDERS.get(border_hash)

    if star_hash and star_hash in PRESTIGE_STARS:
        prestige += PRESTIGE_STARS.get(star_hash)

    return level + (prestige * 100)


def get_career_profile(account):

    account.profile = CareerProfile()
    
    x = account.battletag.split('#')
    name = urllib.parse.quote_plus(x[0])
    id = x[1]

    url = "https://playoverwatch.com/en-us/career/pc/%s-%s" % (name, id)

    profile_response = requests.get(url, timeout=5)
    
    soup = BeautifulSoup(profile_response.content, "html.parser")

    if not soup.findAll(text="Profile Not Found"):
        level_div = soup.find("div", {"class": "player-level"})

        level = int(level_div.text)
        border_hash = level_div['style'].rpartition('/')[-1][:-6]
        star_div = level_div.find('div', {"class": "player-rank"})

        if star_div:
            star_hash = star_div['style'].rpartition('/')[-1][:-6]
        else:
            star_hash = None

        account.profile.level = get_prestige_level(level, border_hash, star_hash)

        tank_result = soup.find(
            "div", {"data-ow-tooltip-text": "Tank Skill Rating"})
        if tank_result:
            account.profile.tank_rating = tank_result.nextSibling.text

        damage_result = soup.find(
            "div", {"data-ow-tooltip-text": "Damage Skill Rating"})
        if damage_result:
            account.profile.damage_rating = damage_result.nextSibling.text

        support_result = soup.find(
            "div", {"data-ow-tooltip-text": "Support Skill Rating"})
        if support_result:
            account.profile.support_rating = support_result.nextSibling.text