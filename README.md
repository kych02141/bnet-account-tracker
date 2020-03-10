# BattleNet Account Tracker

Allows easy tracking of Overwatch accounts and their various account details (email, battletag) and stats (level, skill ratings).


Requirements:

```
pip install tabulate
pip install wcwidth
pip install pyperclip
```

Rename accounts.example.json to accounts.json

Example format:

    [
        {
            "email": "bnetplayer1@gmail.com",
            "battletag": "bnetplayer1#11254",
            "country": "United States",
            "password": "X6K.qV:v^Fk43&2-"
        },
        {
            "email": "bnetplayer2@gmail.com",
            "battletag": "bnetplayer#1916",
            "country": "Japan",
            "password": "{FZAfrW)25kNU;P#"
        }
    ]

Running via the command prompt might not display certain characters properly, so the Powershell script is recommended.

```
./run.ps1
```