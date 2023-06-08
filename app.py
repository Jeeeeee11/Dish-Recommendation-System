import streamlit as st
import openai
import requests
import re

# Set up your OpenAI API credentials
openai.api_key = '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'

# Edamam API credentials
edamam_app_id = 'b0676972'
edamam_app_key = 'f0125506ff24f7a645dc0f6771731116'

def generate_dishes(ingredients):
    # Convert portions to a consistent unit, e.g., grams
    converted_ingredients = convert_portions_to_grams(ingredients)

    prompt = "You have:\n"
    for ingredient in converted_ingredients:
        prompt += f"- {ingredient['amount']} {ingredient['unit']} of {ingredient['name']}\n"
    prompt += "\nGenerate three different dishes using these ingredients:\n1. "

    # Generate recipe suggestions using OpenAI API
    response = openai.Completion.create(
        engine="davinci",
        prompt=prompt,
        temperature=0.7,
        max_tokens=200,
        n=3,
        stop=None,
        echo=True
    )

    dishes = []

    # Parse the generated text to extract the recipe suggestions
    for choice in response.choices:
        choice_text = choice.text.strip().split('\n')
        dish = choice_text[0].split('1. ')[1]
        directions = '\n'.join(choice_text[1:])
        dishes.append((dish, directions))

    return dishes

def convert_portions_to_grams(ingredients):
    converted_ingredients = []

    for ingredient in ingredients:
        amount, unit, name = extract_amount_unit_name(ingredient)
        amount_in_grams = convert_to_grams(amount, unit)
        converted_ingredients.append({'amount': amount_in_grams, 'unit': 'grams', 'name': name})

    return converted_ingredients

def extract_amount_unit_name(ingredient):
    amount_matches = re.findall(r'\d+', ingredient)
    if amount_matches:
        amount = amount_matches[0]
    else:
        amount = ""
    unit = re.findall(r'\b(?:piece|pieces|cloves)\b', ingredient)
    if unit:
        unit = unit[0]
    else:
        unit = ""
    name = re.sub(r'\d+|\b(?:piece|pieces|cloves)\b', '', ingredient).strip()
    return amount, unit, name

def convert_to_grams(amount, unit):
    try:
        grams = float(amount)
    except ValueError:
        grams = 0.0

    # Implement your own conversion logic here
    if unit == 'pieces':
        grams *= 100  # Assuming a piece is approximately 100 grams
    elif unit == 'cloves':
        grams *= 4  # Assuming a clove is approximately 4 grams

    return grams

def get_recipe_image(title):
    # Make a request to Edamam API to retrieve recipe details
    response = requests.get(f"https://api.edamam.com/api/recipes/v2?type=public&q={title}&app_id={edamam_app_id}&app_key={edamam_app_key}")

    # Parse the response to extract the image URL
    data = response.json()
    if 'hits' in data and data['hits']:
        recipe = data['hits'][0]['recipe']
        if 'image' in recipe:
            return recipe['image']

    return None

# Streamlit web app
def main():
    st.title("Recipe Generator")
    st.write("Enter a list of ingredients and generate three different dishes!")

    ingredients_text = st.text_area("Enter the ingredients (separated by commas)")
    ingredients = [ingredient.strip() for ingredient in ingredients_text.split(",")]

    if st.button("Generate Recipes"):
        suggested_dishes = generate_dishes(ingredients)

        st.subheader("Inputted Ingredients:")
        for ingredient in ingredients:
            st.write("- " + ingredient)
        
        st.subheader("Suggested dishes:")
        for i, dish in enumerate(suggested_dishes):
            st.write(f"\n{i+1}. {dish[0]}:")
            st.write(dish[1])
            image_url = get_recipe_image(dish[0])
            if image_url:
                st.image(image_url, use_column_width=True)
            else:
                st.write("No image available.")

if __name__ == "__main__":
    main()
