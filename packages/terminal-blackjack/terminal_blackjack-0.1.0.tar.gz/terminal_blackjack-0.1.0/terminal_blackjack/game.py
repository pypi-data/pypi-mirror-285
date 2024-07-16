from . import cards

# Card Lists
deck = []
player_hand = []
dealer_hand = []

# Game Logic
## Initialization
def initialize_game():
    for initial_cards in range(2):
        cards.hit(deck, player_hand)
        cards.hit(deck, dealer_hand)
        

## User Interface
def ui():
    print('\n' * 100)
    print('Player Hand:')
    print(*player_hand, sep=', ')
    print('Dealer Hand:')
    print(*dealer_hand[1:], sep=', ')
    print('')
    print('Options:')
    print('1. Hit')
    print('2. Stand')

def input_screen():
    option = int(input('>> '))
    if option == 1:
        cards.hit(deck, player_hand)
    elif option == 2:
        None
    else:
        print('Invalid Input')
        return [True, option]
    return [False, option]

def print_values():
    print(f'Player hand\'s value: {cards.value(player_hand)}')
    print(f'Dealer hand\'s value: {cards.value(dealer_hand)}')

## Dealer Logic
def dealer_hit():
    if cards.value(dealer_hand) < 17:
        cards.hit(deck, dealer_hand)
        dealer_hit()

def dealer_end_check():
    dealer_hit()
    if cards.value(dealer_hand) < cards.value(player_hand) or cards.value(dealer_hand) > 21:
        print('You win!')
    else:
        print('You lose')

## Player Logic
def player_end_check(input):
    stand_status = False
    if input[1] == 2:
        stand_status = True
    if cards.value(player_hand) > 21:
        print('Bust!')
        print_values()
        return True
    if stand_status:
        print('Stand!')
        dealer_end_check()
        print_values()
        return True
    return False

# Game Loop
def main():
    cards.initialize(deck)
    initialize_game()
    while True:
        ui()
        input_loop = True
        while input_loop:
            input = input_screen()
            input_loop = input[0]
        if player_end_check(input):
            break
        del input

if __name__ == "__main__":
    main()