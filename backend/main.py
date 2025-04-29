# backend/main.py
from flask import Flask, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import random


# CONNECTING TO FLASK AND FRONTEND AND SOCKETIO AND CORS AND SERVER 


app = Flask(__name__)
CORS(app) # So React can talk to here (Flask)
socketio = SocketIO(app, cors_allowed_origins="*")


print("What is up? Its working!")
print("Flask is running on port 5000")


# ACTUAL GAME LOGIC


suits = ['Hearts', 'Diamonds', 'Spades', 'Clubs']
ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace']

def create_deck():
    deck = []
    for suit in suits:
        for rank in ranks:
            deck.append((rank, suit))
    random.shuffle(deck)
    return deck

    # Creates a deck of cards with 52 cards then shuffles it
    # Returns a list of tuples (rank, suit)

def deal_card(deck):
    return deck.pop(random.randint(0, len(deck) - 1))

    # Deals a card from the deck of 52 cards
    # Removes the card using pop() after dealing it
    # Returns a tuple (rank, suit) of the card dealt

def calculate_score(hand):
    score = 0
    aces = 0

    for card in hand:
        rank = card[0]                  # First element of the card tuple is the rank
        if rank in ['Jack', 'Queen', 'King']:
            score += 10
        elif rank == 'Ace':
            aces += 1
            score += 11
        else:
            score += int(rank)
    while score > 21 and aces:           # If score is over 21 and there are aces in the hand
        score -= 10                      # Ace correction logic
        aces -= 1
    return score


players = {

}



# FOR CONNECTION OF CLIENTS TO SERVER AND SOCKETIO
# This is where the socketio events are defined

@app.route('/')
def index():
    return "Black Jack Server is running"

@socketio.on('connect')
def handle_connect():
    print("Client Connected")

@socketio.on('disconnect')
def handle_disconnect():
    print("Client Disconnected")


# MORE GAME LOGIC WITH SERVER SIDE

@socketio.on('join_game')
def handle_join():
    deck = create_deck()
    player_hand = [deal_card(deck), deal_card(deck)]
    dealer_hand = [deal_card(deck)]

    players[request.sid] = {
        'deck': deck,
        'player_hand': player_hand,
        'dealer_hand': dealer_hand,
        'stand': False,
        'game_over': False,
    }

    emit('game_joined', {
        'playerHand': player_hand,
        'dealerHand': dealer_hand,
        'playerScore': calculate_score(player_hand),
        'dealerScore': calculate_score(dealer_hand),
    })

@socketio.on('hit')
def handle_hit():
    print("Hit received from client:", request.sid)
    sid = request.sid
    if sid in players:
        game = players[sid]
        if not game['game_over']:
            card = deal_card(game['deck'])
            game['player_hand'].append(card)
            game['player_score'] = calculate_score(game['player_hand'])

            if game['player_score'] > 21:
                game['game_over'] = True
                emit('game_over', {
                    'playerHand': game['player_hand'],
                    'dealerHand': game['dealer_hand'],
                    'playerScore': game['player_score'],
                    'dealerScore': game['dealer_score'],
                    'message': 'You busted! Dealer wins.'
                }, to=sid)
            else:
                emit('update', {
                    'playerHand': game['player_hand'],
                    'playerScore': game['player_score']
                }, to=sid)


@socketio.on('stand')
def handle_stand():
    player = players.get(request.sid)
    if not player:
        return

    player['stand'] = True
    while calculate_score(player['dealer_hand']) < 17:            # Dealer must have 17 or higher or else must keep hitting
        player['dealer_hand'].append(deal_card(player['deck']))   

    player_score = calculate_score(player['player_hand'])
    dealer_score = calculate_score(player['dealer_hand'])

    if dealer_score > 21 or player_score > dealer_score:
        result = "You win!"
    elif dealer_score == player_score:
        result = "Break! It's a tie!"
    else:
        result = "Dealer wins!"

    emit('game_over', {
        'playerHand': player['player_hand'],
        'dealerHand': player['dealer_hand'],
        'playerScore': player_score,
        'dealerScore': dealer_score,
        'message': result
    })

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)