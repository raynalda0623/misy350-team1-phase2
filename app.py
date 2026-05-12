import os
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv

from data_layer import load_data
from service_layer import ShopAssistantBot
import ui_layer

load_dotenv()

st.set_page_config(
    page_title="Shop Inventory Portal",
    layout="centered",
    initial_sidebar_state="expanded"
)

INVENTORY_PATH = Path("inventory.json")
SALES_PATH = Path("sales.json")
USERS_PATH = Path("users.json")

# initialize session state

if "inventory" not in st.session_state:
    st.session_state["inventory"] = load_data(INVENTORY_PATH)

if "sales" not in st.session_state:
    st.session_state["sales"] = load_data(SALES_PATH)

if "users" not in st.session_state:
    st.session_state["users"] = load_data(USERS_PATH)

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if "user" not in st.session_state:
    st.session_state["user"] = None

if "role" not in st.session_state:
    st.session_state["role"] = None

if "page" not in st.session_state:
    st.session_state["page"] = "login"

if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "Hi! How can I help you today?"}
    ]


# build the context string to pass to the AI
def build_inventory_context():
    inventory = st.session_state["inventory"]
    sales = st.session_state["sales"]

    context = "INVENTORY:\n"
    for item in inventory:
        context = context + "- " + item["name"] + " | $" + str(item["price"])
        context = context + " | Stock: " + str(item["stock"])
        context = context + " | Category: " + item["category"]
        context = context + " | Flagged: " + str(item.get("flagged", False)) + "\n"

    total_value = 0
    for item in inventory:
        total_value = total_value + (item["price"] * item["stock"])

    context = context + "\nTotal inventory value: $" + str(round(total_value, 2)) + "\n"
    context = context + "Total products: " + str(len(inventory)) + "\n"

    context = context + "\nRECENT SALES:\n"
    recent_sales = sales[-10:]
    for sale in recent_sales:
        context = context + "- " + sale["item"] + " x" + str(sale["quantity"])
        context = context + " | $" + str(sale["total"])
        context = context + " | by " + sale["logged_by"] + " on " + sale["date"] + "\n"

    total_revenue = 0
    for sale in sales:
        total_revenue = total_revenue + sale["total"]

    context = context + "\nTotal revenue: $" + str(round(total_revenue, 2))
    context = context + " across " + str(len(sales)) + " transactions"

    return context


# set up the AI bot
api_key = os.getenv("OPENAI_API_KEY")

if api_key:
    bot = ShopAssistantBot(api_key=api_key, inventory_context=build_inventory_context())
else:
    bot = None

# render the sidebar
ui_layer.render_sidebar()

# page routing
role = st.session_state["role"]
page = st.session_state["page"]

if st.session_state["logged_in"] == False:
    ui_layer.render_login_page()

elif page == "assistant":
    ui_layer.render_assistant_page(bot)

elif role == "Owner":
    if page == "home":
        ui_layer.render_owner_home()
    elif page == "catalog":
        ui_layer.render_owner_catalog()
    elif page == "add":
        ui_layer.render_owner_add()
    elif page == "edit":
        ui_layer.render_owner_edit()
    elif page == "delete":
        ui_layer.render_owner_delete()
    elif page == "sales":
        ui_layer.render_owner_sales()
    else:
        st.session_state["page"] = "home"
        st.rerun()

elif role == "Employee":
    if page == "home":
        ui_layer.render_employee_home()
    elif page == "log_sale":
        ui_layer.render_employee_log_sale()
    elif page == "emp_catalog":
        ui_layer.render_employee_catalog()
    else:
        st.session_state["page"] = "home"
        st.rerun()