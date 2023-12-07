import sys
import functools
from collections import Counter

def hand_to_ints(hand):
    return [
        int(c) if c.isdigit() else {
            'A': 14,
            'K': 13,
            'Q': 12,
            'J': 11,
            'T': 10,
        }[c]
        for c in hand
    ]

hands_and_bids = []
with open(sys.argv[1], "r") as f:
    for line in f:
        line = line.strip()
        if line:
            hand, bid = line.split(" ")
            hand = hand_to_ints(hand)
            bid = int(bid)
            hands_and_bids.append((hand, bid))

def hand_classifier(hand):
    counts = Counter(hand)
    counts_present = set(counts.values())
    inverse_counts = Counter(counts.values())
    max_count = max(counts_present)
    if max_count == 5:
        return 7
    elif max_count == 4:
        return 6
    elif {3, 2} == counts_present:  # full house
        return 5
    elif max_count == 3:
        return 4
    elif inverse_counts[2] == 2:  # 2 pair
        return 2
    elif max_count == 2:
        return 1
    else:
        return 0
    
def hand_comparator(hand1, hand2):
    if hand1 == hand2:
        assert False, "Underspecified"
        return 0
    hand1_class = hand_classifier(hand1)
    hand2_class = hand_classifier(hand2)
    if hand1_class > hand2_class:
        return -1
    elif hand1_class < hand2_class:
        return 1
    elif hand1 > hand2:
        return -1
    elif hand2 > hand1:
        return 1
    else:
        assert False
    
hand_key = functools.cmp_to_key(hand_comparator)
sorted_hands = sorted(hands_and_bids, key=lambda pair: hand_key(pair[0]), reverse=True)
print(sum((i+1)*bid for i, (_, bid) in enumerate(sorted_hands)))
