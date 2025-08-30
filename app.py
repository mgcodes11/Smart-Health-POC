import streamlit as st
import json
import openai
import os
import re

# Replace this with your actual OpenAI API key or use environment variable
# Setup openai api key
openai.api_key = os.environ['OPENAI_API_KEY']

# Load past grocery lists from file
def load_grocery_lists(filepath='C:/Users/MehakGanju/Documents/Python Scripts/SmartHeath POC/grocery_lists.json'):
    with open(filepath, 'r') as f:
        return json.load(f)

# Generate smart grocery list + recipes using GPT
def generate_smart_grocery_list_and_recipes(past_grocery_lists, user_goal=None):
    all_items = [item for week in past_grocery_lists for item in week]
    input_str = ", ".join(sorted(set(all_items)))

    goal_instruction = f"Please tailor everything to a '{user_goal}' diet." if user_goal else ""

    prompt = f"""
You are an AI nutritionist and meal planner. Based on this user's previous 30 grocery lists:

{input_str}

goal_instruction = f"Please tailor everything to the following dietary preferences: {user_goal}." if user_goal else ""

Please return the following:

1. A section called **Recipes:** — list 5 meal ideas with titles and short one-line summaries  
2. A section called **Grocery List:** — grouped by category  
3. A section called **Full Recipes:** — each recipe should include:
    - Ingredients (as a list)
    - Step-by-step instructions (as numbered list)
4. The full recipe section should read like a cook book level instruction with ingredient measurments and temperatures depending on what is needed for the recipe

Format example:

Recipes:
- Recipe 1: Grilled Salmon with Mixed Salad: A heart-healthy salmon fillet seasoned to perfection, grilled and served over a fresh, crunchy salad.
...

Grocery List:
Vegetables:
- Bell Peppers
...

Full Recipes:
- Grilled Salmon with Mixed Salad:
  Ingredients:
    - 1 Salmon fillet
    - 2 cups Lettuce
    ...
  Instructions:
    1. Preheat grill to medium heat.
    2. Season salmon with salt and pepper.
    ...
"""

# 1. Suggest 3 meal recipes they might be making regularly.
# 2. Create a smart grocery list for the upcoming week that includes all the ingredients needed for those recipes, avoids duplicates from long-lasting pantry items (like oats, peanut butter), and includes reasonable variety.
# 3. Make sure the grocery list order makes sense so group things like veggies, fruits or breads like they would be in a grocery store next to each other.
# 4. Keep the grocery list between 20 and 30 items.
# 5. At the end give full recipe descriptions with instructions like in a cook book for each recipe 
# 6. Output the results in this format:


# Recipes:
# - Recipe 1: [name]
# - Recipe 2: ...

# Grocery List:
# - item 1
# - item 2
# ...

# Full Recipes:
# - Grilled Salmon with Mixed Salad:
#   Ingredients:
#     - 1 Salmon fillet
#     - 2 cups Lettuce
#     ...
#   Instructions:
#     1. Preheat grill to medium heat.
#     2. Season salmon with salt and pepper.
#     ...
#     """

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful AI nutritionist."},
            {"role": "user", "content": prompt}
        ]
    )

    # return response.choices[0].message.content

    full_output = response.choices[0].message.content

    # Optional: store the full original output
    summary_text = full_output.split("Full Recipes:")[0].strip()

    # Extract and parse full recipes
    recipe_section = full_output.split("Full Recipes:")[1].strip()
    recipe_blocks = re.findall(r"- (.*?):\n(.*?)\n(?=- |\Z)", recipe_section, re.DOTALL)
    recipes = {title.strip(): content.strip() for title, content in recipe_blocks}

    return summary_text, recipes
    
# ---- STREAMLIT UI ----
st.set_page_config(page_title="AI Nutritionist", layout="centered")

st.title("🥗 Smart Grocery & Recipe Planner")

st.subheader("🍽️ Optional Dietary Preferences")


# Diet goal selection
# goal = st.selectbox(
#     "Choose a nutrition goal (optional):",
#     ["None", "High protein", "Vegetarian", "Low carb", "Budget-friendly"]
# )


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

# Button to generate the result
# if st.button("Generate Grocery List and Recipes"):
#     with st.spinner("Thinking like a nutritionist..."):
#         try:
#             grocery_lists = load_grocery_lists()
#             # user_goal = None if goal == "None" else goal
#             preferences = health_goals + allergies + specific_diets
#             user_goal = ", ".join(preferences) if preferences else None
#             output = generate_smart_grocery_list_and_recipes(grocery_lists, user_goal)
#             st.text_area("📋 Result", value=output, height=500)
#         except Exception as e:
#             st.error(f"Error: {str(e)}")



if st.button("Generate Grocery List and Recipes"):
    with st.spinner("Cooking up ideas..."):
        try:
            grocery_lists = load_grocery_lists()
            preferences = health_goals + allergies + specific_diets
            user_goal = ", ".join(preferences) if preferences else None

            summary_text, recipes = generate_smart_grocery_list_and_recipes(
                grocery_lists, user_goal
            )

            # ✨ Show the raw summary output from GPT (with recipe names + grocery list)
            st.subheader("📋 Smart Grocery Plan")
            st.markdown(summary_text)

            # 🔽 Expandable full recipes
            st.subheader("🍽️ Full Recipes")
            for name, content in recipes.items():
                with st.expander(name):
                    st.markdown(content)
        except Exception as e:
            st.error(f"Error: {str(e)}")