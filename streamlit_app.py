# Import python packages
import streamlit as st
import requests
import pandas as pd

from snowflake.snowpark.functions import col

# Write directly to the app
st.title(":cup_with_straw: Customize your Smoothie :cup_with_straw:")
st.write("Choose the Fruits for your Custom Smoothie")

cnx = st.connection("snowflake")
session = cnx.session()

my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))
# st.dataframe(data=my_dataframe, use_container_width=True)
pd_df = my_dataframe.to_pandas()



ingredient_string = ""

name_on_order = st.text_input("Name on Smoothie:")
st.write(f'The name on the smoothie will be: {name_on_order}')
ingredient_list = st.multiselect('Choose up to 5 ingredients.',
                                my_dataframe,
                                max_selections=5)

if ingredient_list:
    # st.write(ingredient_list)
    st.text(ingredient_list)

    for fruit in ingredient_list:
        ingredient_string += fruit + " "

        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit, 'SEARCH_ON'].iloc[0]
        st.write('The search value for ', fruit,' is ', search_on, '.')

        st.subheader(fruit + ' Nutrition Infromation')
        fruityvice_response = requests.get("https://fruityvice.com/api/fruit/" + fruit)
        fv_df = st.dataframe(data=fruityvice_response.json(), use_container_width=True)

    my_insert_smt = f"""
    insert into smoothies.public.orders(ingredients, name_on_order)
    values('{ingredient_string}', '{name_on_order}')
    """
    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        session.sql(my_insert_smt).collect()
        st.success('Your smoothie is ordered!', icon="✅")
