from flask import Flask, render_template, request, redirect, url_for 
import numpy as np
import pandas as pd 
import os
import torch
from torchvision import transforms
from dataset_maker import preprocess
from PIL import Image
from resnet import resnet14, resnet18, resnet34, resnet50

import io
import base64

### stuff from last class
app = Flask(__name__)

@app.route('/')
def main():
    return render_template('main_better.html')

@app.route('/generate/', methods=['POST', 'GET'])
def generate():
    if request.method == 'GET':
        return render_template('generate2.html')
    else:
        classes = ['beans', 'bell_pepper', 'potato', 'tomato']
        model = resnet18(4, 3)
        model.load_state_dict(torch.load('model/model_logs/Ingredients8.pth', map_location='cpu'))

        model.eval()
        try:
            files = request.files.getlist('images')
            transform = transforms.Compose([
                transforms.RandomHorizontalFlip(),
                transforms.RandomResizedCrop(32),
                transforms.ToTensor(),
                transforms.Normalize((0.38046584, 0.10854615, -0.13485776), (0.5249659, 0.59474176, 0.6634378))
            ])  
            ingredients = []
            images = []
            for file in files:
                try:
                    image = Image.open(file)
                    if image is not None:
                        if image.mode != 'RGB':
                            image = image.convert('RGB')
                        image = image.resize((150,150))
                        images.append(image)
                except Exception as e:
                    print(f'Error reading file {file}: {e}')

            images = np.array(images)
            images = preprocess(images)
            images = transform(images)

            # classify each image
            for image in images:
                with torch.no_grad():
                    outputs = model(image)
                    _, pred_class = torch.max(outputs, 1)
                    ingredient = classes[pred_class]
                    ingredients.append(ingredient)

            # send list of ingredients to recipe_results function
            return redirect(url_for('recipe_results', ingredients=ingredients))
        
        except:
            return render_template('generate2.html', error=True)

@app.route('/generate/<name>')
def generate_name(name):
    return render_template('generate2.html', name=name)

@app.route('/receipe_page')
def receipe_page():
    return render_template('receipe_page.html')

@app.route('/receipe_page/<name>')
def receipe_page_name(name):
    return render_template('receipe_page.html', name=name)

# was unable to call the function from the recipegen.py due to a computer issue so I had to bring in the function again 
def gen_recipe(cuisine, list_of_ingredients=None):
  '''
  - Generates recipe recommendations from the recipe dataset based off of the
    detected ingredients from user input images and prefered cuisine.
  - Input: cuisine, list of ingredients
  - Output: dataframe of recomended recipes
  '''
  link = 'https://raw.githubusercontent.com/Nkannan12/Project-16B-GNN/main/Recipes_cleaned.csv'
  df = pd.read_csv(link)

  if list_of_ingredients == None:
    cuisine_df = df[df["Cuisine"] == cuisine].copy()
    return cuisine_df
  else:
    cuisine_df = df[df["Cuisine"] == cuisine].copy()
    # Create a new column to count matching ingredients
    cuisine_df['Matched Ingredients'] = cuisine_df['key_ingredients'].apply(lambda x: sum(1 for ingredient in list_of_ingredients if ingredient in x))
    if len(list_of_ingredients) > 2:
      cuisine_df = cuisine_df[cuisine_df['Matched Ingredients'] >= 2]
    else:
      cuisine_df = cuisine_df[cuisine_df['Matched Ingredients'] >= 1]
    # Sort dataframe based on the number of matched ingredients in descending order
    cuisine_df = cuisine_df.sort_values(by='Matched Ingredients', ascending=False)

    # Reset index
    cuisine_df.reset_index(drop=True, inplace=True)

    return cuisine_df 
 
@app.route('/filter-recipes', methods=['POST'])
def filter_recipes():
    cuisine = request.form.get('cuisine')
    ingredients = None 

    recommended_recipes = gen_recipe(cuisine, ingredients)
    recipes_data = recommended_recipes.to_dict(orient='records')
    
    # Render the recipe_results.html template, passing the recipes data
    return render_template('recipe_results.html', recipes=recipes_data)
    
@app.route('/recipe_results', methods=['GET', 'POST'])
def recipe_results(ingredients=None):
    if request.method == 'GET':
        message = "Please select a cuisine to view recipes."
        return render_template('recipe_results.html', message=message)
    else:
        cuisine = request.form.get('cuisine')
        # ingredients = None
        recommended_recipes = gen_recipe(cuisine, ingredients)
        recipes_data = recommended_recipes.to_dict(orient='records')
        print(recipes_data)  # Debugging line to check data
        return render_template('recipe_results.html', recipes=recipes_data)

if __name__ == '__main__':
    app.run(debug=True)