import random

SUITS = ['♠', '♥', '♦', '♣']
RANKS = ['3', '4', '5', '6', '7', '8', '9', '10', 'Valet', 'Dame', 'Roi', 'A', '2']

class Card:
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank
        self.value = RANKS.index(rank)

    def __str__(self):
        return f"{self.rank} de {self.suit}"

    def __lt__(self, other):
        return self.value < other.value

class Player:
    def __init__(self, name):
        self.name = name
        self.hand = []

    def sort_hand(self):
        self.hand.sort()

    def play_card(self, top_card=None, force_value=None, force_index=None, current_index=None, force_count=1):
        hand_by_value = {}
        for card in self.hand:
            hand_by_value.setdefault(card.value, []).append(card)
        # Si contrainte de valeur ET de nombre de cartes (force_count > 1 seulement si la pile a été lancée ainsi)
        if force_value is not None and current_index == force_index:
            cards = hand_by_value.get(force_value, [])
            if len(cards) >= force_count:
                to_play = cards[:force_count]
                for c in to_play:
                    self.hand.remove(c)
                return to_play
            else:
                return None
        # Si on est en mode simple (force_count == 1), le joueur peut choisir de lancer une série (simple/double/triple/quadruple) UNIQUEMENT s'il commence le tour (pile vide)
        elif force_value is None and force_count == 1:
            # Si la pile est vide, le joueur peut lancer une série du plus grand nombre possible (max 4)
            if top_card is None:
                best_group = []
                for value in sorted(hand_by_value):
                    cards = hand_by_value[value]
                    if len(cards) > len(best_group):
                        best_group = cards
                if best_group:
                    to_play = best_group[:4]
                    for c in to_play:
                        self.hand.remove(c)
                    return to_play
            else:
                # Sinon, il ne peut jouer qu'une seule carte (la plus petite possible >= top_card)
                best_card = None
                for value in sorted(hand_by_value):
                    cards = hand_by_value[value]
                    if value >= top_card.value:
                        best_card = cards[0]
                        break
                if best_card:
                    self.hand.remove(best_card)
                    return [best_card]
        # Sinon, si on est en mode double/triple/quadruple, on ne peut jouer que force_count cartes, pas plus ni moins
        elif force_value is None and force_count > 1:
            for value in sorted(hand_by_value):
                cards = hand_by_value[value]
                if len(cards) >= force_count:
                    if top_card is None or value >= top_card.value:
                        to_play = cards[:force_count]
                        for c in to_play:
                            self.hand.remove(c)
                        return to_play
        return None

# Utility functions

def create_deck():
    return [Card(suit, rank) for suit in SUITS for rank in RANKS]

def deal_cards(players, deck):
    random.shuffle(deck)
    while deck:
        for player in players:
            if deck:
                player.hand.append(deck.pop())

def dame_de_coeur(players):
    for i, player in enumerate(players):
        for card in player.hand:
            if card.rank == 'Dame' and card.suit == '♥':
                print(f"{player.name} a la Dame de Coeur !")
                return players[i:] + players[:i]
    return players

def check_four_of_a_kind(pile):
    if len(pile) < 4:
        return False
    last_rank = pile[-1].rank
    return all(card.rank == last_rank for card in pile[-4:])

# Main round logic

def play_round(players, top_card=None, pile=None, force_count=1):
    n = len(players)
    passed = [False] * n
    force_value = None
    force_index = None
    last_player_played = None
    new_turn_cause_2 = False

    i = 0
    passes_in_row = 0

    while passes_in_row < n - 1:
        player = players[i]
        if passed[i]:
            i = (i + 1) % n
            continue

        player.sort_hand()
        print(f"{player.name} a {[str(card) for card in player.hand]}")

        # Correction : la contrainte de valeur ne s'applique que pour les simples
        if force_count == 1 and force_value is not None and i != force_index:
            print(f"{player.name} passe (contrainte {RANKS[force_value]} x{force_count})")
            passed[i] = True
            passes_in_row += 1
            i = (i + 1) % n
            continue

        cards = player.play_card(top_card, force_value if force_count == 1 else None, force_index, i, force_count)
        if cards:
            if not isinstance(cards, list):
                cards = [cards]
            print(f"{player.name} joue {' / '.join(str(card) for card in cards)}")
            pile.extend(cards)
            last_player_played = player
            top_card = cards[0]
            passes_in_row = 0

            # Gestion des contraintes
            if force_count == 1:
                # Cas simple : on peut activer la contrainte de valeur
                if force_value is not None and force_index == i:
                    if pile and len(pile) > force_count and all(c.value == pile[-force_count-1].value for c in cards):
                        force_value = cards[0].value
                        force_index = (i + 1) % n
                        print(f"‼️ {player.name} a égalé la carte précédente ! Le prochain ({players[force_index].name}) doit jouer {force_count}x {cards[0].rank}")
                    else:
                        force_value = None
                        force_index = None
                        force_count = len(cards)
                elif force_value is None and pile and len(pile) > force_count and all(c.value == pile[-force_count-1].value for c in cards):
                    force_value = cards[0].value
                    force_index = (i + 1) % n
                    force_count = len(cards)
                    print(f"‼️ {player.name} a égalé la carte précédente ! Le prochain ({players[force_index].name}) doit jouer {force_count}x {cards[0].rank}")
                else:
                    force_count = len(cards)
            else:
                # Pour double/triple/quadruple, on n'impose que le nombre de cartes, pas la valeur
                force_value = None
                force_index = None
                force_count = len(cards)

            # Fin de tour sur 2
            if any(card.rank == '2' for card in cards):
                print(f"{player.name} a joué un 2 ! Le tour est terminé.")
                new_turn_cause_2 = True
                break

            # Carré
            if check_four_of_a_kind(pile):
                print(f"🔥 {player.name} a complété un carré de {cards[0].rank} ! Le tas est coupé.")
                return None, last_player_played, True

            passed = [False] * n
            passed[i] = False
        else:
            print(f"{player.name} passe")
            passed[i] = True
            passes_in_row += 1
            if force_index == i:
                force_value = None
                force_index = None

        i = (i + 1) % n

    print("---Tous les joueurs ont passé, le tour est terminé.---")
    print("---Nouveau tour !---")
    return None, last_player_played, True

# Game loop

def play_game(players):
    classement = []
    top_card = None
    current_players = players.copy()
    starting_index = 0
    pile = []

    print("=== Début du jeu ===")
    deal_cards(current_players, create_deck())
    print("Cartes distribuées !")
    current_players = dame_de_coeur(current_players)

    while len(current_players) > 1:
        current_players = current_players[starting_index:] + current_players[:starting_index]
        top_card, last_player, reset_pile = play_round(current_players, top_card, pile)

        for player in current_players[:]:
            if not player.hand:
                print(f"{player.name} a terminé ses cartes !")
                classement.append(player.name)
                current_players.remove(player)

        if last_player and last_player in current_players:
            starting_index = current_players.index(last_player)
        else:
            starting_index = 0

        if reset_pile:
            print("Le tas de cartes est réinitialisé.")
            top_card = None
            pile = []

    classement.append(current_players[0].name)
    print("\n=== Fin de la partie ===")
    print("Classement :")
    for idx, name in enumerate(classement, 1):
        print(f"{idx}. {name}")

# Test
players = [Player("Elias"), Player("Axel"), Player("Tito")]
play_game(players)
players = [Player("Elias"), Player("Axel"), Player("Tito")]
play_game(players)
play_game(players)
players = [Player("Elias"), Player("Axel"), Player("Tito")]
play_game(players)
play_game(players)
play_game(players)
players = [Player("Elias"), Player("Axel"), Player("Tito")]
play_game(players)
