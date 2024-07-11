import random

class Product:
    def __init__(self, name, base_price):
        self.name = name
        self.base_price = base_price
        self.current_price = self.get_price()
        self.previous_price = self.current_price

    def get_price(self):
        fluctuation = random.uniform(0.8, 1.2)
        return round(self.base_price * fluctuation, 2)

    def update_price(self):
        self.previous_price = self.current_price
        self.current_price = self.get_price()

    def price_change_percentage(self):
        if self.previous_price == 0:
            return 0
        change = ((self.current_price - self.previous_price) / self.previous_price) * 100
        return round(change, 2)

    def display_price_info(self, index):
        change_percentage = self.price_change_percentage()
        if change_percentage > 0:
            color_code = "\033[92m"  # Green for price increase
        elif change_percentage < 0:
            color_code = "\033[91m"  # Red for price decrease
        else:
            color_code = "\033[0m"  # Default color for no change
        reset_code = "\033[0m"
        print(f"{index}. {self.name}: {color_code}${self.current_price} ({change_percentage}% change from yesterday){reset_code}")

class Town:
    def __init__(self, name, products):
        self.name = name
        self.products = products

    def update_prices(self):
        for product in self.products:
            product.update_price()

    def display_products(self):
        print(f"Products in {self.name}:")
        for i, product in enumerate(self.products):
            product.display_price_info(i + 1)
        print()

class Player:
    def __init__(self, starting_money=10000):
        self.money = starting_money
        self.inventory = {product: 0 for product in '12345678'}

    def buy_product(self, product, quantity):
        total_cost = product.current_price * quantity
        if total_cost > self.money:
            print("Not enough money.")
        else:
            self.money -= total_cost
            if product.name in self.inventory:
                self.inventory[product.name] += quantity
            else:
                self.inventory[product.name] = quantity
            print(f"Bought {quantity} of {product.name}")

    def sell_product(self, product, quantity):
        if product.name not in self.inventory or self.inventory[product.name] < quantity:
            print("Not enough inventory.")
        else:
            self.money += product.current_price * quantity
            self.inventory[product.name] -= quantity
            print(f"Sold {quantity} of {product.name}")

    def display_inventory(self):
        print("Current inventory:")
        for product, quantity in self.inventory.items():
            print(f"{product}: {quantity}")
        print(f"Current money: ${self.money}")
        print()

class Game:
    def __init__(self):
        self.user_name = input("Enter your name: ")
        self.days_left = self.select_game_duration()
        print(f"Welcome {self.user_name}! Make as much money as you can in the given time to win! The world is yours!")
        # Define custom product names
        product_names = ['Weed', 'Heroin', 'XTC', 'Acid', 'Cocaine', 'Fentynal', 'Xanax', 'Meth']
        # Initialize products with custom names and random base prices
        self.products = [Product(name, random.randint(5, 50)) for name in product_names]
        self.towns = [Town(name, self.products) for name in ["Atlanta", "Birmingham", "Miami", "Los Angeles"]]
        self.player = Player()
        self.current_town = self.towns[0]

    def select_game_duration(self):
        print("Select the game duration:")
        print("1. 30 days")
        print("2. 45 days")
        print("3. 90 days")
        choice = int(input("Enter the number of the choice: "))
        if choice == 1:
            return 30
        elif choice == 2:
            return 45
        elif choice == 3:
            return 90
        else:
            print("Invalid choice. Defaulting to 45 days.")
            return 45

    def start(self):
        print("Welcome to the game!")
        while self.days_left > 0:
            print(f"Current town: {self.current_town.name}")
            print(f"Days left: {self.days_left}")
            self.current_town.update_prices()
            self.current_town.display_products()
            self.player.display_inventory()
            action = input("Choose an action: travel, buy, sell, quit: ").lower()
            if action == "travel":
                self.travel()
            elif action == "buy":
                self.buy()
            elif action == "sell":
                self.sell()
            elif action == "quit":
                break
            else:
                print("Invalid action. Try again.")
            self.days_left -= 1  # Decrease the number of days left
        print(f"Game over! {self.user_name}, you ended with ${self.player.money:.2f}.")

    def travel(self):
        if self.random_encounter("police") or self.random_encounter("gang"):
            return
        
        print("Choose a town to travel to:")
        for i, town in enumerate(self.towns):
            print(f"{i}: {town.name}")
        choice = int(input("Enter the number of the town: "))
        if 0 <= choice < len(self.towns):
            self.current_town = self.towns[choice]
            print(f"Traveled to {self.current_town.name}")
        else:
            print("Invalid choice.")

    def random_encounter(self, type):
        encounter_chance = random.random()
        if encounter_chance < 0.3:  # 30% chance of an encounter
            print(f"You have encountered a {type}!")
            action = input("Choose an action: fight, run, bribe: ").lower()
            if action == "fight":
                if random.random() < 0.5:
                    print(f"You successfully fought off the {type}!")
                else:
                    print(f"You were caught by the {type}!")
                    self.handle_failure()
                    return True
            elif action == "run":
                if random.random() < 0.5:
                    print(f"You successfully ran away from the {type}!")
                else:
                    print(f"You were caught by the {type}!")
                    self.handle_failure()
                    return True
            elif action == "bribe":
                bribe_amount = int(input("Enter the amount to bribe: "))
                if bribe_amount > self.player.money:
                    print("Not enough money to bribe!")
                    self.handle_failure()
                    return True
                self.player.money -= bribe_amount
                if random.random() < 0.5:
                    print(f"The {type} accepted your bribe!")
                else:
                    print(f"The {type} rejected your bribe!")
                    self.handle_failure()
                    return True
            else:
                print("Invalid action. You were caught!")
                self.handle_failure()
                return True
        return False

    def handle_failure(self):
        print("You lost some money and inventory.")
        loss_money = self.player.money * 0.1
        self.player.money -= loss_money
        print(f"You lost ${loss_money:.2f}.")
        for product in self.player.inventory:
            loss_quantity = self.player.inventory[product] * 0.1
            self.player.inventory[product] -= int(loss_quantity)
            print(f"You lost {int(loss_quantity)} of {product}.")

    def buy(self):
        self.current_town.display_products()
        product_number = int(input("Enter the product number to buy: ")) - 1
        quantity = int(input("Enter the quantity to buy: "))
        if 0 <= product_number < len(self.current_town.products):
            product = self.current_town.products[product_number]
            self.player.buy_product(product, quantity)
        else:
            print("Product not found.")

    def sell(self):
        self.player.display_inventory()
        product_number = int(input("Enter the product number to sell: ")) - 1
        quantity = int(input("Enter the quantity to sell: "))
        if 0 <= product_number < len(self.current_town.products):
            product = self.current_town.products[product_number]
            self.player.sell_product(product, quantity)
        else:
            print("Product not found.")

if __name__ == "__main__":
    game = Game()
    game.start()
