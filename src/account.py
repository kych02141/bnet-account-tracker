class Account:

    def __init__(self, id, email, battletag, country, password, created):
        self.id = id
        self.email = email
        self.battletag = battletag
        self.country = country
        self.password = password
        self.created = created
        self.level = None
        self.public = False
        self.tank_rating = None
        self.damage_rating = None
        self.support_rating = None