default_pokemon_stats = {
    "level": 0,
    "energies": 0,
    "evolves_from": None,
    "can_evolve": False,
    "item_card": False,
}

bench_positions = [(230, 1220), (460, 1220), (700, 1220)]

card_offset_mapping = {
    2: 92,
    3: 92,  # ok
    4: 78,  # ok
    5: 65,  # ok
    6: 55,  # ok
    7: 47,  # ok
    8: 45,  # changed from 40 because 40 failed in 3 card testing
}

ZOOM_CARD_REGION = (80, 255, 740, 1020)
NUMBER_OF_CARDS_REGION = (790, 1325, 60, 50)