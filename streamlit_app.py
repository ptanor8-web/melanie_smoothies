# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col



# Write directly to the app
st.title(f":cup_with_straw: Customize Your Smoothie !:cup_with_straw: ")
st.write(
  """Choose the fruits you want in your custom Smoothie! """)



#import streamlit as st

name_on_order = st.text_input('Name on smoothie :')
st.write('The name on your smoothie will be :', name_on_order)

cnx = st.connection('snowflake')
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'),col('SEARCH_ON'))
#st.dataframe(data=my_dataframe, use_container_width=True)
#st.stop()


ingredients_list = st.multiselect(
    'Choose Up To 5 Ingredients:'
    ,my_dataframe
    ,max_selections=5
    )


if ingredients_list : 
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '


my_insert_stmt = (
    "INSERT INTO smoothies.public.orders(ingredients, name_on_order) "
    "VALUES ('" + ingredients_string + "', '" + name_on_order + "')"
)



time_to_insert = st.button('Submit Order')


if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(f'Your Smoothie is ordered, {name_on_order}!', icon="✅")

    



    
