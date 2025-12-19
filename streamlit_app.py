
# Import python packages
import streamlit as st
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col
import requests
import pandas as pd

# --- UI Header ---
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want to customize your Smoothie!")

# --- Name input ---
name_on_order = st.text_input("Name on Smoothie:")
if name_on_order:
    st.write("The name on your Smoothie will be:", name_on_order)

# --- Snowpark session & fruit options ---
session = get_active_session()

# Load fruit options (FRUIT_NAME + FRUIT_ID)
sp_df = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME"), col("FRUIT_ID"))
pd_df = sp_df.to_pandas()

# --- Ingredient selection (list of strings, not a Snowpark DF) ---
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    pd_df["FRUIT_NAME"].tolist(),
    max_selections=5
)

# --- Show nutrition info for selected ingredients and build the ingredients string ---
ingredients_string = ""
if ingredients_list:
    for fruit in ingredients_list:
        ingredients_string += fruit + " "
        # Lookup FRUIT_ID from the Pandas DF
        fruit_id = pd_df.loc[pd_df["FRUIT_NAME"] == fruit, "FRUIT_ID"].iloc[0]

        st.subheader(f"{fruit} — Nutrition Information")
        api_url = f"https://my.smoothiefroot.com/api/fruit/{fruit_id}"
        try:
            resp = requests.get(api_url, timeout=10)
            if resp.status_code == 200:
                st.json(resp.json())
            else:
                st.warning(f"Could not fetch nutrition info for {fruit} (HTTP {resp.status_code}).")
        except requests.RequestException as e:
            st.error(f"Error fetching data for {fruit}: {e}")

# --- Insert order (button) ---
time_to_insert = st.button("Submit Order")

if time_to_insert:
    # Minimal validation
    if not name_on_order.strip():
        st.error("Please enter a name for your Smoothie before submitting.")
    elif not ingredients_list:
        st.error("Please select at least one ingredient before submitting.")
    else:
        # Escape single quotes to avoid breaking SQL
        safe_ing = ingredients_string.strip().replace("'", "''")
        safe_name = name_on_order.strip().replace("'", "''")

        my_insert_stmt = (
            "INSERT INTO smoothies.public.orders (ingredients, name_on_order) "
            "VALUES ('" + safe_ing + "', '" + safe_name + "')"
        )

        try:
            session.sql(my_insert_stmt).collect()
            st.success(f"Your Smoothie is ordered, {name_on_order}!", icon="✅")
        except Exception as e:
            st.error(f"Order failed: {e}")
