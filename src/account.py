import dateutil.parser
from datetime import datetime

class Account:

    def __init__(self, id, email, battletag, country, password, created, sms_protected, ban_status):
        self.id = id
        self.email = email
        self.battletag = battletag
        self.country = country
        self.password = password
        self.created = created
        self.sms_protected = sms_protected
        self.ban_status = ban_status
        self.level = None
        self.public = False
        self.tank_rating = None
        self.damage_rating = None
        self.support_rating = None

class BanStatus:

    def __init__(self, banned, permanent, expires):
        self.banned = banned
        self.permanent = permanent
        self.expires = expires

    def get_expiration(self):
        if self.expires:
            return dateutil.parser.parse(self.expires)