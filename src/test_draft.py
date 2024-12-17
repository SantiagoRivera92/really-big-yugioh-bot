from drafting.draft_manager import DraftManager
from card.card_collection import CardCollection

players = [
    {"name":"Ashlee", "id":1},
    {"name":"Santi", "id":2},
    {"name":"Cathal", "id":3},
    {"name":"Graf", "id":4}
]

player_count = 4
pack_size = 15
pack_amount = 4

card_collection = CardCollection()
manager = DraftManager(1234)
print(manager.init_cube_draft(6338, player_count, pack_size, pack_amount).message)
for player in players:
    manager.join_cube_draft(player["name"], player["id"])

for i in range(pack_size*pack_amount):
    
    draft_data = manager.load_draft_data()
    
    for player in draft_data["players_data"]:
        manager.pick(player["id"], player["current_pack"]["pack"][0])

draft_data = manager.load_draft_data()

for player in draft_data["players_data"]:
    print(f"\n{player["name"]}'s pool:\n")
    for card_id in player["picked_cards"]:
        print(card_collection.get_card_name_from_id(card_id))