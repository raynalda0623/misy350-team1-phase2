import uuid
import time
from openai import OpenAI

# service layer - handles business logic
# no streamlit code goes here

class User:
    def __init__(self, username, password, role):
        self.username = username
        self.password = password
        self.role = role

    def is_owner(self):
        if self.role == "Owner":
            return True
        return False

    def is_employee(self):
        if self.role == "Employee":
            return True
        return False

class Owner(User):
    def __init__(self, username, password):
        super().__init__(username, password, "Owner")

class Employee(User):
    def __init__(self, username, password):
        super().__init__(username, password, "Employee")


# finds a user by username and password
def find_user(users, username, password):
    for u in users:
        if u["username"] == username and u["password"] == password:
            found_user = User(u["username"], u["password"], u["role"])
            return found_user
    return None


def username_taken(users, username):
    for u in users:
        if u["username"] == username:
            return True
    return False


def register_user(users, username, password, confirm):
    if username == "" or password == "" or confirm == "":
        return None, "Please fill in all fields."
    if password != confirm:
        return None, "Passwords do not match."
    if len(password) < 4:
        return None, "Password must be at least 4 characters."
    if username_taken(users, username):
        return None, "That username is already taken."

    new_user = {"username": username, "password": password, "role": "Employee"}
    users.append(new_user)
    return new_user, "Account created successfully."


# finds an inventory item by its id
def find_item_by_id(inventory, item_id):
    for item in inventory:
        if item["item_id"] == item_id:
            return item
    return None


def add_item(inventory, name, price, stock, category):
    if name == "":
        return None, "Please enter a product name."

    # check if name already exists
    for item in inventory:
        if item["name"].lower() == name.lower():
            return None, "A product with that name already exists."

    # get the next id
    if len(inventory) == 0:
        new_id = 1
    else:
        new_id = max(item["item_id"] for item in inventory) + 1

    new_item = {
        "item_id": new_id,
        "name": name,
        "price": round(price, 2),
        "stock": stock,
        "category": category,
        "flagged": False
    }
    inventory.append(new_item)
    return new_item, "Product added."


def update_item(inventory, item_id, price, add_stock, category):
    item = find_item_by_id(inventory, item_id)
    if item is None:
        return False, "Item not found."

    item["price"] = round(price, 2)
    item["stock"] = item["stock"] + add_stock
    item["category"] = category

    # unflag the item if it has enough stock now
    if item["stock"] >= 5:
        item["flagged"] = False

    return True, item["name"] + " updated."


def delete_item(inventory, item_id):
    item = find_item_by_id(inventory, item_id)
    if item is None:
        return False, "Item not found."

    inventory.remove(item)
    return True, "Product removed."


def toggle_flag(inventory, item_id):
    item = find_item_by_id(inventory, item_id)
    if item is None:
        return False
    if item["flagged"] == True:
        item["flagged"] = False
    else:
        item["flagged"] = True
    return True


def place_sale(inventory, sales, item_id, quantity, username):
    item = find_item_by_id(inventory, item_id)
    if item is None:
        return None, "Item not found."
    if item["stock"] < quantity:
        return None, "Not enough stock. Only " + str(item["stock"]) + " available."

    item["stock"] = item["stock"] - quantity

    if item["stock"] < 5:
        item["flagged"] = True

    total = round(item["price"] * quantity, 2)

    new_sale = {
        "sale_id": str(uuid.uuid4())[:8].upper(),
        "item": item["name"],
        "item_id": item_id,
        "quantity": quantity,
        "unit_price": item["price"],
        "total": total,
        "logged_by": username,
        "date": time.strftime("%Y-%m-%d %H:%M")
    }
    sales.append(new_sale)
    return new_sale, "Sale recorded."


def get_low_stock_items(inventory):
    low_items = []
    for item in inventory:
        if item["stock"] < 5:
            low_items.append(item)
    return low_items


def get_total_inventory_value(inventory):
    total = 0
    for item in inventory:
        total = total + (item["price"] * item["stock"])
    return round(total, 2)


def get_sales_by_employee(sales, username):
    my_sales = []
    for sale in sales:
        if sale["logged_by"] == username:
            my_sales.append(sale)
    return my_sales


# AI assistant class
class ShopAssistantBot:
    def __init__(self, api_key, inventory_context):
        self.client = OpenAI(api_key=api_key)
        self.inventory_context = inventory_context

    def build_ai_prompt(self):
        prompt = "You are a helpful shop assistant for a bakery shop inventory portal.\n"
        prompt = prompt + "Answer user questions based on the shop data provided below.\n"
        prompt = prompt + "If the answer is not in the data, say you do not have enough information.\n\n"
        prompt = prompt + "SHOP DATA:\n" + self.inventory_context
        return prompt

    def get_ai_response(self, chat_history):
        ai_prompt = self.build_ai_prompt()
        ai_prompt_message = [{"role": "system", "content": ai_prompt}]
        messages = ai_prompt_message + chat_history

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.2
        )
        return response.choices[0].message.content