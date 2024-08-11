import urllib.request as requests
import json
from datetime import datetime
from typing import List

header = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) '
                'AppleWebKit/537.11 (KHTML, like Gecko) '
                'Chrome/23.0.1271.64 Safari/537.11',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
    'Accept-Encoding': 'none',
    'Accept-Language': 'en-US,en;q=0.8',
    'Connection': 'keep-alive'
}

class Alias:
	def __init__(self):
		self.lists = [	
				[41356845,41356846],
				[86120752,86120751],
				[4280258,4280259],
				[6150044,6150045],
				[14558128,14558127],
				[81480460,81480461],
				[73580472,73580471],
				[23995346,23995347,23995348],
				[89631139,89631140,89631141,89631142,89631143,89631144,89631145,89631146],
				[31833038,31833039],
				[85289965,85289966],
				[78193832,78193831],
				[91152256,91152257,91152258],
				[55878038,55878039],
				[82044280,82044279],
				[57728570,57728571],
				[70095154,70095155],
				[10443957,10443958],
				[1546123,1546124],
				[46986414,46986415,46986416,46986417,46986418,46986419,46986420,46986421,36996508],
				[38033121,38033122,38033123,38033124,38033125,38033126],
				[43892408,43892409],
				[98502113,98502114,98502115],
				[16195942,16195943],
				[1861629,1861630],
				[83965310,83965311],
				[84257640,84257639],
				[46173680,46173681],
				[80193355,80193356],
				[94145021,94145022],
				[20366274,20366275],
				[94977269,94977270],
				[95440946,95440947],
				[21844576,21844577],
				[58932616,58932615],
				[89943723,89943724],
				[20721928,20721929],
				[40044918,40044919],
				[31887905,31887906],
				[68881649,68881650],
				[4376658,4376659],
				[40542825,40542826],
				[31764353,31764354],
				[78661338,78661339],
				[81172176,81172177],
				[73134081,73134082],
				[5043010,5043011,5043012],
				[99267150,99267151],
				[45231177,45231178],
				[15341822,15341823],
				[81439173,81439174],
				[6368038,6368039],
				[69140098,69140099],
				[73642296,73642297],
				[52038441,52038442],
				[59438930,59438931],
				[62015408,62015409],
				[60643553,60643554],
				[36354008,36354007],
				[78437364,78437365],
				[31122090,31122091],
				[18144506,18144507],
				[11050416,11050417,11050418,11050419],
				[65741786,65741787],
				[77585513,77585514],
				[38342336,38342335],
				[37390589,37390590],
				[40640057,40640058,40640059],
				[97590747,97590748],
				[60764582,60764583],
				[90330453,90330454],
				[87322377,87322378],
				[7852509,7852510],
				[68540058,68540059],
				[32012841,32012842],
				[83764718,83764719],
				[83011277,83011278],
				[32003338,32003339],
				[84013237,84013238],
				[90590304,90590303],
				[10000000,10000001,10000002],
				[16178681,16178682,16178683],
				[19230408,19230407],
				[29843092,29843093,29843094,14470846,14470847],
				[39751093,39751094],
				[61307542,61307543],
				[42035044,42035045],
				[27911549,27911550],
				[24433920,24433921],
				[27847700,24094653],
				[74677422,74677423,74677424,74677425,74677426,74677427],
				[64335804,64335805],
				[88264978,88264979],
				[14878872,14878871],
				[83555666,83555667],
				[41463181,41463182],
				[23401840,23401839],
				[73915052,73915053,73915054,73915055],
				[63288573,63288574],
				[10000020,10000021,10000022],
				[47852924,47852925],
				[18807108,18807109],
				[44508094,44508095],
				[41209827,41209828],
				[70781052,70781053,70781054,70781055],
				[90740329,90740330],
				[84080938,84080939],
				[10000010,10000011,10000012],
				[41462083,41462084],
				[49791928,49791927],
				[15259704,15259703],
				[10802915,10802916],
				[35686187,35686188],
				[32448765,32448766],
				[80604091,80604092],
				[56043446,56043447],
				[14898066,14898067],
				[56993276,56993277],
				[77754944,77754945],
				[57116033,57116034],
				[91998120,91998121,91998119]
		]

	def get_ids(self, n):
		for lst in self.lists:
			if n in lst:
				return lst
		return [n]

URL_COMMON_BANLISTS = "https://api.ygoprog.com/api/banlist/common"
URL_BANLIST = "https://api.ygoprog.com/api/banlist/public/%s"
URL_CARDS = "https://api.ygoprog.com/api/cards"
LABEL_BANLIST = "Tcg"
force_legal = []
force_unlimited = []

def generate_banlist() -> str:
    request = requests.Request(URL_COMMON_BANLISTS, None, header)
    with requests.urlopen(request) as response:
        banlists = json.loads(response.read().decode())
        advanced_id = next(obj for obj in banlists if obj['format'] == LABEL_BANLIST)['_id']

    request = requests.Request(URL_BANLIST % advanced_id, None, header)
    with requests.urlopen(request) as response:
        data = json.loads(response.read().decode())
        forbidden = data['forbidden']
        limited = data['limited']
        semi = data['semi_limited']

    request = requests.Request(URL_CARDS, None, header)
    with requests.urlopen(request) as response:
        cards: List = json.loads(response.read().decode())
        common_ids = [card['id'] for card in cards if any(card_set["set_rarity_code"] == "C" for card_set in card["card_sets"])]
    
    all_cards = []
    alias = Alias()
    
    for card in cards:
        cardid = card['id']
        ids = alias.get_ids(cardid)
        name = card['name']
        cardtype = card['type']
        status = -1
        is_common = False
        
        for card_id in ids:
            if card_id in common_ids:
                is_common = True
                status = 3

        if not is_common and cardid in force_legal:
            is_common = True
            status = 3
        elif cardid in force_legal:
            force_legal.remove(cardid)
        
        if cardtype not in ['Skill', 'Token'] and is_common:
            for card_id in ids:
                if name in force_unlimited:
                    status = 3
                    break
                if card_id in forbidden:
                    status = 0
                    break
                elif card_id in limited:
                    status = 1
                    break
                elif card_id in semi:
                    status = 2
                    break
            if status == -1:
                status = 3
        
        all_cards.append({
            "name": name,
            "ids": ids,
            "status": status
        })

    output = []
    date = datetime.now()
    output.append("#[Common Charity Format]")
    output.append(f"!Common Charity {date.month}.{date.year}\n")
    output.append("$whitelist")

    for card in sorted(all_cards, key=lambda x: x["name"].lower()):
        for cardid in card["ids"]:
            output.append(f"{cardid} {card['status']} -- {card['name']}")

    return '\n'.join(output)