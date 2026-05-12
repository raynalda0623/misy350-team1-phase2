import streamlit as st
import time
from pathlib import Path
from data_layer import save_data
import service_layer as service

INVENTORY_PATH = Path("inventory.json")
SALES_PATH = Path("sales.json")
USERS_PATH = Path("users.json")


# sidebar

def render_sidebar():
    with st.sidebar:
        st.title("Shop Portal")
        st.divider()

        if st.session_state["logged_in"] == True:
            user = st.session_state["user"]
            st.markdown("**User:** " + user.username)
            st.markdown("**Role:** " + user.role)
            st.divider()

            inventory = st.session_state["inventory"]
            total_units = 0
            for item in inventory:
                total_units = total_units + item["stock"]

            st.metric("Total Products", len(inventory))
            st.metric("Total Units", total_units)

            low_items = service.get_low_stock_items(inventory)
            if len(low_items) > 0:
                st.warning(str(len(low_items)) + " item(s) low on stock")
            else:
                st.success("Stock levels OK")

            st.divider()

            if st.button("Log Out", use_container_width=True, key="logout_btn"):
                st.session_state["logged_in"] = False
                st.session_state["user"] = None
                st.session_state["role"] = None
                st.session_state["page"] = "login"
                st.session_state["messages"] = [
                    {"role": "assistant", "content": "Hi! How can I help you today?"}
                ]
                st.rerun()
        else:
            st.caption("Please log in to continue.")

        st.divider()
        st.caption("Shop Inventory Portal v2")


# login page

def render_login_page():
    users = st.session_state["users"]

    st.title("Shop Inventory Portal")
    st.markdown("Log in or register to continue.")
    st.divider()

    with st.container(border=True):
        st.markdown("**Test Accounts**")
        st.caption("Owner: owner / owner123")
        st.caption("Employee: employee / employee123")

    st.divider()

    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        st.subheader("Login")
        with st.container(border=True):
            login_username = st.text_input("Username", key="login_username")
            login_password = st.text_input("Password", type="password", key="login_password")
            login_btn = st.button("Log In", type="primary", use_container_width=True, key="login_btn")

        if login_btn:
            if login_username == "" or login_password == "":
                st.warning("Please enter both username and password.")
            else:
                user_obj = service.find_user(users, login_username, login_password)
                if user_obj:
                    with st.spinner("Logging in..."):
                        st.session_state["logged_in"] = True
                        st.session_state["user"] = user_obj
                        st.session_state["role"] = user_obj.role
                        st.session_state["page"] = "home"
                        time.sleep(1)
                    st.rerun()
                else:
                    st.error("Invalid username or password.")

    with tab2:
        st.subheader("Register")
        with st.container(border=True):
            reg_username = st.text_input("Choose a Username", key="reg_username")
            reg_password = st.text_input("Choose a Password", type="password", key="reg_password")
            reg_confirm = st.text_input("Confirm Password", type="password", key="reg_confirm")
            st.markdown("**Role:** Employee (all new accounts are employees)")
            register_btn = st.button("Create Account", type="primary", use_container_width=True, key="register_btn")

        if register_btn:
            new_user, message = service.register_user(users, reg_username, reg_password, reg_confirm)
            if new_user:
                save_data(USERS_PATH, users)
                st.success(message)
            else:
                st.error(message)


# owner pages

def render_owner_home():
    inventory = st.session_state["inventory"]
    sales = st.session_state["sales"]
    user = st.session_state["user"]

    st.title("Owner Dashboard")
    st.markdown("Welcome back, " + user.username + ".")
    st.divider()

    total_units = 0
    for item in inventory:
        total_units = total_units + item["stock"]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Products", len(inventory))
    col2.metric("Total Units", total_units)
    col3.metric("Inventory Value", "$" + str(service.get_total_inventory_value(inventory)))
    col4.metric("Total Sales", len(sales))

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.markdown("### Catalog")
            st.caption("View and search all products.")
            if st.button("Open Catalog", use_container_width=True, key="go_catalog"):
                st.session_state["page"] = "catalog"
                st.rerun()

        with st.container(border=True):
            st.markdown("### Edit / Restock")
            st.caption("Update prices and stock levels.")
            if st.button("Open Editor", use_container_width=True, key="go_edit"):
                st.session_state["page"] = "edit"
                st.rerun()

    with col2:
        with st.container(border=True):
            st.markdown("### Add Product")
            st.caption("Add a new item to the catalog.")
            if st.button("Add Product", use_container_width=True, key="go_add"):
                st.session_state["page"] = "add"
                st.rerun()

        with st.container(border=True):
            st.markdown("### Remove Product")
            st.caption("Delete a product from the catalog.")
            if st.button("Remove Product", use_container_width=True, key="go_delete"):
                st.session_state["page"] = "delete"
                st.rerun()

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.markdown("### Sales Log")
            st.caption("Review all transactions.")
            if st.button("View Sales Log", use_container_width=True, key="go_sales"):
                st.session_state["page"] = "sales"
                st.rerun()

    with col2:
        with st.container(border=True):
            st.markdown("### Shop Assistant")
            st.caption("Ask the AI assistant questions.")
            if st.button("Open Assistant", use_container_width=True, key="go_ai_owner"):
                st.session_state["page"] = "assistant"
                st.rerun()

    # show low stock warnings at the bottom
    st.divider()
    low_items = service.get_low_stock_items(inventory)
    if len(low_items) > 0:
        st.markdown("**Low Stock Alerts**")
        for item in low_items:
            st.warning(item["name"] + " - " + str(item["stock"]) + " units remaining")


def render_owner_catalog():
    inventory = st.session_state["inventory"]

    if st.button("Back", key="catalog_back"):
        st.session_state["page"] = "home"
        st.rerun()

    st.header("Product Catalog")

    search = st.text_input("Search by name", key="owner_search")

    st.divider()

    total_units = 0
    for item in inventory:
        total_units = total_units + item["stock"]

    low_items = service.get_low_stock_items(inventory)

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Products", len(inventory))
    col2.metric("Total Units", total_units)
    col3.metric("Critically Low", len(low_items))
    st.divider()

    for item in inventory:
        # filter by search if something was typed
        if search != "":
            if search.lower() not in item["name"].lower():
                continue

        with st.container(border=True):
            c1, c2, c3, c4, c5 = st.columns([3, 2, 2, 2, 2])
            c1.markdown("**" + item["name"] + "**")
            c2.markdown(item.get("category", "Other"))
            c3.markdown("$" + str(item["price"]))
            c4.markdown("Stock: " + str(item["stock"]))

            if item["stock"] == 0:
                c5.error("Out of Stock")
            elif item["stock"] < 5:
                c5.warning("Low")
            else:
                c5.success("OK")


def render_owner_add():
    inventory = st.session_state["inventory"]

    if st.button("Back", key="add_back"):
        st.session_state["page"] = "home"
        st.rerun()

    st.header("Add a New Product")

    with st.container(border=True):
        st.subheader("Product Details")

        col1, col2 = st.columns(2)
        with col1:
            new_name = st.text_input("Product Name", key="new_product_name")
            new_price = st.number_input("Price ($)", min_value=0.01, value=1.00, step=0.25, key="new_product_price")
        with col2:
            new_stock = st.number_input("Initial Stock", min_value=0, value=10, step=1, key="new_product_stock")
            new_category = st.selectbox("Category", ["Bread", "Pastry", "Dessert", "Beverage", "Other"], key="new_product_category")

        add_btn = st.button("Add Product", type="primary", use_container_width=True, key="add_product_btn")

    if add_btn:
        new_item, message = service.add_item(inventory, new_name, new_price, new_stock, new_category)
        if new_item:
            with st.spinner("Adding product..."):
                save_data(INVENTORY_PATH, inventory)
                time.sleep(1)
            st.success(message)
            st.session_state["page"] = "home"
            st.rerun()
        else:
            st.error(message)


def render_owner_edit():
    inventory = st.session_state["inventory"]

    if st.button("Back", key="edit_back"):
        st.session_state["page"] = "home"
        st.rerun()

    st.header("Edit or Restock a Product")

    with st.container(border=True):
        st.subheader("Select a Product")

        edit_item = st.selectbox(
            "Choose product to edit",
            options=inventory,
            format_func=lambda x: x["name"] + " (Stock: " + str(x["stock"]) + ")",
            key="edit_item_select"
        )

        st.divider()
        st.subheader("Update Details")

        col1, col2 = st.columns(2)
        with col1:
            updated_price = st.number_input(
                "New Price ($)",
                min_value=0.01,
                value=float(edit_item["price"]),
                step=0.25,
                key="edit_price_" + str(edit_item["item_id"])
            )
            add_stock = st.number_input(
                "Units to Add to Stock",
                min_value=0,
                value=0,
                step=1,
                key="edit_stock_" + str(edit_item["item_id"])
            )
        with col2:
            categories = ["Bread", "Pastry", "Dessert", "Beverage", "Other"]
            current_cat = edit_item.get("category", "Other")
            if current_cat in categories:
                cat_index = categories.index(current_cat)
            else:
                cat_index = 0

            updated_category = st.selectbox(
                "Category",
                categories,
                index=cat_index,
                key="edit_cat_" + str(edit_item["item_id"])
            )
            st.markdown("**Current stock:** " + str(edit_item["stock"]) + " units")

        update_btn = st.button("Save Changes", type="primary", use_container_width=True, key="update_btn")

    if update_btn:
        success, message = service.update_item(inventory, edit_item["item_id"], updated_price, add_stock, updated_category)
        if success:
            with st.spinner("Saving..."):
                save_data(INVENTORY_PATH, inventory)
                time.sleep(1)
            st.success(message)
            st.session_state["page"] = "home"
            st.rerun()
        else:
            st.error(message)


def render_owner_delete():
    inventory = st.session_state["inventory"]

    if st.button("Back", key="delete_back"):
        st.session_state["page"] = "home"
        st.rerun()

    st.header("Remove a Product")

    with st.container(border=True):
        st.subheader("Select Product to Remove")

        delete_item = st.selectbox(
            "Choose product",
            options=inventory,
            format_func=lambda x: x["name"] + " (Stock: " + str(x["stock"]) + ")",
            key="delete_item_select"
        )

        col1, col2 = st.columns(2)
        col1.markdown("**Price:** $" + str(delete_item["price"]))
        col2.markdown("**Stock remaining:** " + str(delete_item["stock"]))

        st.warning("This will permanently remove " + delete_item["name"] + " from the catalog.")
        confirm = st.checkbox("I confirm I want to delete this product.", key="confirm_delete")
        delete_btn = st.button("Delete Product", type="primary", use_container_width=True, key="delete_btn")

    if delete_btn:
        if confirm == False:
            st.error("Please check the confirmation box first.")
        else:
            success, message = service.delete_item(inventory, delete_item["item_id"])
            if success:
                with st.spinner("Removing..."):
                    save_data(INVENTORY_PATH, inventory)
                    time.sleep(1)
                st.success(message)
                st.session_state["page"] = "home"
                st.rerun()
            else:
                st.error(message)


def render_owner_sales():
    sales = st.session_state["sales"]

    if st.button("Back", key="sales_back"):
        st.session_state["page"] = "home"
        st.rerun()

    st.header("Sales Log")

    if len(sales) == 0:
        st.info("No sales have been logged yet.")
        return

    total_revenue = 0
    for sale in sales:
        total_revenue = total_revenue + sale["total"]

    col1, col2 = st.columns(2)
    col1.metric("Total Transactions", len(sales))
    col2.metric("Total Revenue", "$" + str(round(total_revenue, 2)))
    st.divider()

    for sale in reversed(sales):
        with st.container(border=True):
            c1, c2, c3, c4 = st.columns([3, 2, 2, 3])
            c1.markdown("**" + sale["item"] + "**")
            c2.markdown("Qty: " + str(sale["quantity"]))
            c3.markdown("$" + str(sale["total"]))
            c4.markdown(sale["logged_by"] + " - " + sale["date"])


# employee pages

def render_employee_home():
    inventory = st.session_state["inventory"]
    sales = st.session_state["sales"]
    user = st.session_state["user"]

    st.title("Welcome, " + user.username + "!")
    st.markdown("What would you like to do today?")
    st.divider()

    my_sales = service.get_sales_by_employee(sales, user.username)

    my_revenue = 0
    for sale in my_sales:
        my_revenue = my_revenue + sale["total"]

    col1, col2 = st.columns(2)
    col1.metric("My Sales", len(my_sales))
    col2.metric("My Revenue", "$" + str(round(my_revenue, 2)))

    st.divider()

    col1, col2, col3 = st.columns(3)
    with col1:
        with st.container(border=True):
            st.markdown("### Log a Sale")
            st.caption("Record items sold and update stock.")
            if st.button("Log a Sale", use_container_width=True, key="go_log_sale"):
                st.session_state["page"] = "log_sale"
                st.rerun()

    with col2:
        with st.container(border=True):
            st.markdown("### View Catalog")
            st.caption("Browse products and flag low items.")
            if st.button("View Catalog", use_container_width=True, key="go_emp_catalog"):
                st.session_state["page"] = "emp_catalog"
                st.rerun()

    with col3:
        with st.container(border=True):
            st.markdown("### Shop Assistant")
            st.caption("Ask the AI assistant a question.")
            if st.button("Open Assistant", use_container_width=True, key="go_ai_emp"):
                st.session_state["page"] = "assistant"
                st.rerun()

    if len(my_sales) > 0:
        st.divider()
        st.markdown("**My Recent Sales**")
        # show last 5 sales
        recent = my_sales[-5:]
        for sale in reversed(recent):
            with st.container(border=True):
                c1, c2, c3 = st.columns([3, 2, 3])
                c1.markdown("**" + sale["item"] + "**")
                c2.markdown("$" + str(sale["total"]))
                c3.markdown(sale["date"])


def render_employee_log_sale():
    inventory = st.session_state["inventory"]
    sales = st.session_state["sales"]
    user = st.session_state["user"]

    if st.button("Back", key="log_sale_back"):
        st.session_state["page"] = "home"
        st.rerun()

    st.header("Log a Sale")

    # get items that are in stock
    available = []
    for item in inventory:
        if item["stock"] > 0:
            available.append(item)

    left_col, right_col = st.columns([1.4, 1])

    with left_col:
        if len(available) == 0:
            st.error("No items currently in stock.")
        else:
            with st.container(border=True):
                st.subheader("Sale Details")

                selected_item = st.selectbox(
                    "Select an Item",
                    options=available,
                    format_func=lambda x: x["name"] + " (Stock: " + str(x["stock"]) + ")",
                    key="sale_item_select"
                )
                quantity = st.number_input("Quantity", min_value=1, step=1, key="sale_quantity")

                st.markdown("**Unit price:** $" + str(selected_item["price"]))
                st.markdown("**Sale total:** $" + str(round(selected_item["price"] * quantity, 2)))

                if st.button("Create Order", type="primary", use_container_width=True, key="create_order_btn"):
                    new_sale, message = service.place_sale(
                        inventory, sales, selected_item["item_id"], quantity, user.username
                    )
                    if new_sale:
                        with st.spinner("Creating order..."):
                            save_data(INVENTORY_PATH, inventory)
                            save_data(SALES_PATH, sales)
                            time.sleep(1)
                        st.balloons()
                        time.sleep(2)
                        st.session_state["page"] = "home"
                        st.rerun()
                    else:
                        st.error(message)

    with right_col:
        st.subheader("Low Stock Items")
        low_items = service.get_low_stock_items(inventory)
        if len(low_items) == 0:
            st.success("All items stocked OK.")
        else:
            for item in low_items:
                st.warning(item["name"] + ": " + str(item["stock"]) + " left")


def render_employee_catalog():
    inventory = st.session_state["inventory"]

    if st.button("Back", key="emp_catalog_back"):
        st.session_state["page"] = "home"
        st.rerun()

    st.header("Current Catalog")

    search = st.text_input("Search by name", key="emp_search")

    st.divider()

    total_units = 0
    for item in inventory:
        total_units = total_units + item["stock"]

    low_items = service.get_low_stock_items(inventory)

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Products", len(inventory))
    col2.metric("Total Units", total_units)
    col3.metric("Low / Flagged", len(low_items))
    st.divider()

    for item in inventory:
        if search != "":
            if search.lower() not in item["name"].lower():
                continue

        with st.container(border=True):
            c1, c2, c3, c4, c5 = st.columns([3, 2, 2, 2, 2])
            c1.markdown("**" + item["name"] + "**")
            c2.markdown(item.get("category", "Other"))
            c3.markdown("$" + str(item["price"]))
            c4.markdown("Stock: " + str(item["stock"]))

            if item["stock"] == 0:
                c5.error("Out of Stock")
            elif item["stock"] < 5:
                c5.warning("Low")
            elif item.get("flagged") == True:
                c5.warning("Flagged")
            else:
                c5.success("OK")

            # flag button
            if item.get("flagged") == True:
                flag_label = "Unflag"
            else:
                flag_label = "Flag"

            if st.button(flag_label, key="flag_" + str(item["item_id"])):
                service.toggle_flag(inventory, item["item_id"])
                save_data(INVENTORY_PATH, inventory)
                st.rerun()


# assistant page

def render_assistant_page(bot):
    st.header("Shop Assistant")
    st.markdown("Ask me anything about the shop inventory or sales.")
    st.divider()

    with st.container(height=400, border=True):
        for message in st.session_state["messages"]:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    user_input = st.chat_input("Ask a question...")

    if user_input:
        st.session_state["messages"].append({"role": "user", "content": user_input})

        with st.spinner("Thinking..."):
            try:
                ai_response = bot.get_ai_response(st.session_state["messages"])
            except Exception as e:
                ai_response = "Sorry, I could not connect to the AI. Error: " + str(e)

        st.session_state["messages"].append({"role": "assistant", "content": ai_response})
        st.rerun()

    if st.button("Clear Chat", key="clear_chat_btn"):
        st.session_state["messages"] = [
            {"role": "assistant", "content": "Hi! How can I help you today?"}
        ]
        st.rerun()