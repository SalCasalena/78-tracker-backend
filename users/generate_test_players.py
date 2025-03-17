import random
import string
from users.models import User

def generate_random_username():
    return "Player" + "".join(random.choices(string.digits, k=3))

def generate_random_email(username):
    return f"{username.lower()}@example.com"

def create_random_players(num_players=8):
    players = []
    for _ in range(num_players):
        username = generate_random_username()
        email = generate_random_email(username)

        player, created = User.objects.get_or_create(username=username, email=email)
        if created:
            print(f"Created user: {username} ({email})")
        else:
            print(f"User already exists: {username} ({email})")

        players.append(player)
    return players

# Run the script
if __name__ == "__main__":
    create_random_players()
