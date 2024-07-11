import random
import tkinter as tk
from tkinter import simpledialog, messagebox
from PIL import Image, ImageTk  # Pillow library for image handling

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
            color_code = "green"  # Green for price increase
        elif change_percentage < 0:
            color_code = "red"  # Red for price decrease
        else:
            color_code = "black"  # Default color for no change
        return f"{index}. {self.name}: ${self.current_price} ({change_percentage}% change from yesterday)", color_code

class Town:
    def __init__(self, name, products):
        self.name = name
        self.products = products

    def update_prices(self):
        for product in self.products:
            product.update_price()

    def display_products(self):
        product_info = []
        for i, product in enumerate(self.products):
            info, color = product.display_price_info(i + 1)
            product_info.append((info, color))
        return product_info

class Player:
    def __init__(self, starting_money=10000):
        self.money = starting_money
        self.inventory = {}

    def buy_product(self, product, quantity):
        total_cost = product.current_price * quantity
        if total_cost > self.money:
            return "Not enough money."
        else:
            self.money -= total_cost
            if product.name in self.inventory:
                self.inventory[product.name] += quantity
            else:
                self.inventory[product.name] = quantity
            return f"Bought {quantity} of {product.name}"

    def sell_product(self, product, quantity):
        if product.name not in self.inventory or self.inventory[product.name] < quantity:
            return "Not enough inventory."
        else:
            self.money += product.current_price * quantity
            self.inventory[product.name] -= quantity
            if self.inventory[product.name] == 0:
                del self.inventory[product.name]
            return f"Sold {quantity} of {product.name}"

    def display_inventory(self):
        inventory_info = ["Current inventory:"]
        for product, quantity in self.inventory.items():
            inventory_info.append(f"{product}: {quantity}")
        inventory_info.append(f"Current money: ${self.money:.2f}")
        return inventory_info

class Game:
    def __init__(self):
        self.root = tk.Tk()
        self.root.state('zoomed')  # Open the window maximized
        self.root.withdraw()
        self.user_name = simpledialog.askstring("Name", "Enter your name:")
        self.days_left = self.select_game_duration()
        messagebox.showinfo("Welcome", f"Welcome {self.user_name}! Make as much money as you can in the given time to win! The world is yours!")
        # Define custom product names
        product_names = ['Weed', 'Heroin', 'XTC', 'Acid', 'Cocaine', 'Fentynal', 'Xanax', 'Meth']
        # Initialize products with custom names and random base prices
        self.products = [Product(name, random.randint(5, 50)) for name in product_names]
        self.towns = [Town(name, self.products) for name in ["Atlanta", "Birmingham", "Miami", "Los Angeles"]]
        self.player = Player()
        self.current_town = self.towns[0]
        self.root.deiconify()
        self.root.title("Trading Game")
        self.create_widgets()
        self.update_display()

    def select_game_duration(self):
        durations = {"30 days": 30, "45 days": 45, "90 days": 90}
        duration = simpledialog.askstring("Duration", "Select the game duration (30 days, 45 days, 90 days):")
        return durations.get(duration, 45)

    def create_widgets(self):
        self.canvas = tk.Canvas(self.root, width=self.root.winfo_screenwidth(), height=self.root.winfo_screenheight())
        self.canvas.pack(fill="both", expand=True)
        
        # Load and display background image
        self.background_image = Image.open('images/background.png')
        self.background_image = self.background_image.resize((self.root.winfo_screenwidth(), self.root.winfo_screenheight()), Image.LANCZOS)
        self.bg_img = ImageTk.PhotoImage(self.background_image)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.bg_img)

        self.info_label = tk.Label(self.root, text="", justify="left", bg="white")
        self.info_label_window = self.canvas.create_window(10, 10, anchor="nw", window=self.info_label)

        self.action_label = tk.Label(self.root, text="Choose an action: travel, buy, sell, quit", bg="white")
        self.action_label_window = self.canvas.create_window(10, 500, anchor="nw", window=self.action_label)

        self.action_entry = tk.Entry(self.root)
        self.action_entry_window = self.canvas.create_window(10, 530, anchor="nw", window=self.action_entry)
        self.action_entry.bind("<Return>", self.process_action)

        self.action_button = tk.Button(self.root, text="Submit", command=self.process_action)
        self.action_button_window = self.canvas.create_window(210, 530, anchor="nw", window=self.action_button)

    def update_display(self):
        self.canvas.delete("price_info")  # Clear previous price info
        info_text = f"Current town: {self.current_town.name}\nDays left: {self.days_left}\n\n"
        products_info = self.current_town.display_products()
        y_offset = 10
        for info, color in products_info:
            label = tk.Label(self.root, text=info, fg=color, bg="white")
            self.canvas.create_window(10, y_offset, anchor="nw", window=label, tags="price_info")
            y_offset += 20

        inventory_info = self.player.display_inventory()
        for line in inventory_info:
            info_text += line + "\n"

        self.info_label.config(text=info_text)

    def process_action(self, event=None):
        action = self.action_entry.get().lower()
        if action == "travel":
            self.travel()
        elif action == "buy":
            self.buy()
        elif action == "sell":
            self.sell()
        elif action == "quit":
            self.root.quit()
        else:
            messagebox.showerror("Error", "Invalid action. Try again.")
        self.action_entry.delete(0, tk.END)
        self.days_left -= 1  # Decrease the number of days left
        self.current_town.update_prices()  # Update prices after each action
        if self.days_left <= 0:
            self.end_game()
        else:
            self.update_display()

    def travel(self):
        if self.random_encounter("police") or self.random_encounter("gang"):
            return
        
        towns = "\n".join([f"{i}: {town.name}" for i, town in enumerate(self.towns)])
        choice = simpledialog.askinteger("Travel", f"Choose a town to travel to:\n{towns}")
        if 0 <= choice < len(self.towns):
            self.current_town = self.towns[choice]
            messagebox.showinfo("Travel", f"Traveled to {self.current_town.name}")
        else:
            messagebox.showerror("Error", "Invalid choice.")

    def random_encounter(self, type):
        encounter_chance = random.random()
        if encounter_chance < 0.3:  # 30% chance of an encounter
            action = simpledialog.askstring("Encounter", f"You have encountered a {type}! Choose an action: fight, run, bribe:").lower()
            if action == "fight":
                if random.random() < 0.5:
                    messagebox.showinfo("Fight", f"You successfully fought off the {type}!")
                else:
                    messagebox.showerror("Caught", f"You were caught by the {type}!")
                    self.handle_failure()
                    return True
            elif action == "run":
                if random.random() < 0.5:
                    messagebox.showinfo("Run", f"You successfully ran away from the {type}!")
                else:
                    messagebox.showerror("Caught", f"You were caught by the {type}!")
                    self.handle_failure()
                    return True
            elif action == "bribe":
                bribe_amount = simpledialog.askinteger("Bribe", "Enter the amount to bribe:")
                if bribe_amount > self.player.money:
                    messagebox.showerror("Error", "Not enough money to bribe!")
                    self.handle_failure()
                    return True
                self.player.money -= bribe_amount
                if random.random() < 0.5:
                    messagebox.showinfo("Bribe", f"The {type} accepted your bribe!")
                else:
                    messagebox.showerror("Bribe", f"The {type} rejected your bribe!")
                    self.handle_failure()
                    return True
            else:
                messagebox.showerror("Caught", "Invalid action. You were caught!")
                self.handle_failure()
                return True
        return False

    def handle_failure(self):
        messagebox.showerror("Failure", "You lost some money and inventory.")
        loss_money = self.player.money * 0.1
        self.player.money -= loss_money
        messagebox.showinfo("Loss", f"You lost ${loss_money:.2f}.")
        for product in list(self.player.inventory.keys()):  # Use list to avoid runtime error
            loss_quantity = int(self.player.inventory[product] * 0.1)
            self.player.inventory[product] -= loss_quantity
            if self.player.inventory[product] == 0:
                del self.player.inventory[product]
            messagebox.showinfo("Loss", f"You lost {loss_quantity} of {product}.")

    def buy(self):
        products_info = "\n".join([f"{i + 1}. {self.products[i].name}" for i in range(len(self.products))])
        product_number = simpledialog.askinteger("Buy", f"Enter the product number to buy:\n{products_info}") - 1
        quantity = simpledialog.askinteger("Quantity", "Enter the quantity to buy:")
        if 0 <= product_number < len(self.current_town.products):
            product = self.current_town.products[product_number]
            result = self.player.buy_product(product, quantity)
            messagebox.showinfo("Buy", result)
        else:
            messagebox.showerror("Error", "Product not found.")

    def sell(self):
        inventory_info = "\n".join([f"{i + 1}. {self.products[i].name}" for i in range(len(self.products))])
        product_number = simpledialog.askinteger("Sell", f"Enter the product number to sell:\n{inventory_info}") - 1
        quantity = simpledialog.askinteger("Quantity", "Enter the quantity to sell:")
        if 0 <= product_number < len(self.current_town.products):
            product = self.current_town.products[product_number]
            result = self.player.sell_product(product, quantity)
            messagebox.showinfo("Sell", result)
        else:
            messagebox.showerror("Error", "Product not found.")

    def end_game(self):
        messagebox.showinfo("Game Over", f"Game over! {self.user_name}, you ended with ${self.player.money:.2f}.")
        self.root.quit()

if __name__ == "__main__":
    game = Game()
    game.root.mainloop()
