import sys
import re
from collections import defaultdict

card_id_to_n_cards = defaultdict(lambda: 1)
n_cards = 0
for line in sys.stdin:
    line = line.strip()
    if line:
        card, tickets = line.split(": ")
        card_id = int(card.removeprefix("Card "))
        my_cards = card_id_to_n_cards[card_id]
        n_cards += my_cards
        winning, mine = [
            {int(num) for num in re.split(r'\s+', part.strip())}
            for part in tickets.split(" | ")
        ]
        n_winning = len(winning & mine)
        for i in range(1, 1+n_winning):
            card_id_to_n_cards[card_id + i] += my_cards
print(n_cards)
