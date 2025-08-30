import streamlit as st
import json
import openai
import os
import re

# Replace this with your actual OpenAI API key or use environment variable
# Setup openai api key
openai.api_key = os.environ['OPENAI_API_KEY']


st.set_page_config(page_title="Smart Grocery AI", layout="centered")

# --- Function to generate grocery list + recipes ---
def generate_smart_grocery_list_and_recipes(grocery_items, user_goal=None, only_use_user_ingredients=True):
    prompt = f"""
    You are an AI nutritionist. Based on the following grocery items the user typically buys: {grocery_items}.
    {"The user is aiming for these health goals or diet preferences: " + user_goal if user_goal else ""}
    """

    if only_use_user_ingredients:
        prompt += """
        IMPORTANT: Only generate recipes using the ingredients listed above. Do NOT include or suggest any new ingredients.
        Do NOT assume pantry staples or make substitutions. ONLY use the ingredients exactly as provided.
        """
    else:
        prompt += """
        You may recommend additional ingredients if necessary for well-rounded recipes. Clearly mark any new suggested items in the output with (suggested).
        """

    prompt += """
    Generate:
    1. A section called **Grocery List:** — grouped by category  
    2. A section called **Recipes:** - Up to 5 recipe ideas.
    3. A summary of the ingredients used per recipe.
    """

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    return response.choices[0].message["content"]

# --- Session State Setup ---
if "user_items" not in st.session_state:
    st.session_state.user_items = None
if "page" not in st.session_state:
    st.session_state.page = "landing"
if "generated_response" not in st.session_state:
    st.session_state.generated_response = None

# --- Helper to switch pages ---
def go_to_main(user_input):
    # st.session_state.user_items = user_input.strip()
    st.session_state.page = "main"

# --- Landing Page ---
if st.session_state.page == "landing":
    st.title("🍎 Smart Grocery AI")
    st.subheader("Start by telling us what you usually buy")

    user_input = st.text_area("Enter your usual grocery items (comma-separated):", height=200)

    if st.button("Continue"):
        if user_input.strip():
            st.session_state.user_items = user_input.strip()
            go_to_main(user_input)
        else:
            st.warning("Please enter some grocery items.")

# --- Main App Page ---
elif st.session_state.page == "main":
    st.title("🧠 Personalized Grocery Plan + Recipes")

    # user_goal = st.text_input("What is your health goal or diet preference? (optional)")
    # Health Goals
    health_goals = st.multiselect(
        "Health Goals",
        ["High Protein", "Low Protein", "Low Carb", "High Fiber", "Low Sugar"]
    )

    # Allergies
    allergies = st.multiselect(
        "Allergies",
        ["Gluten-Free", "Dairy-Free / Lactose Intolerant"]
    )

    # Specific Diets
    specific_diets = st.multiselect(
        "Specific Diets",
        ["Paleo", "Kosher", "Halal", "Keto", "Pescatarian", "Plant-Based", "Vegan", "Vegetarian"]
    )

    # Ingredient usage toggle
    only_use_user_ingredients = st.checkbox("Only use ingredients I've listed", value=True)


    # Combine preferences into one string
    all_preferences = health_goals + allergies + specific_diets
    user_goal = ", ".join(all_preferences) if all_preferences else None

    if st.button("Generate Grocery Plan"):
        with st.spinner("Generating your custom grocery plan..."):
            # response = generate_smart_grocery_list_and_recipes(
            #     st.session_state.user_items,
            #     user_goal
            # )
            output = generate_smart_grocery_list_and_recipes(
            grocery_items=st.session_state.user_items,
            user_goal=all_preferences,
            only_use_user_ingredients=only_use_user_ingredients
        )
            # st.session_state.generated_response = response
        st.markdown("### Here's your personalized grocery list and recipe plan:")
        st.markdown(output)

    # if st.session_state.get("generated_response"):
    #     st.markdown("### 🍽️ Grocery List + Recipe Ideas")
    #     st.markdown(st.session_state.generated_response, unsafe_allow_html=True)
