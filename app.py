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

@app.route('/ask/', methods=['POST', 'GET'])
def ask():
    if request.method == 'GET':
        return render_template('ask.html')
    else:
        try:
            return render_template('ask.html', name=request.form['name'], student=request.form['student'])
        except:
            return render_template('ask.html')

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


@app.route('/receipe_page/')
def receipe_page():
    return render_template('receipe_page.html')

@app.route('/receipe_page/<name>')
def receipe_page_name(name):
    return render_template('receipe_page.html', name=name)

#######
# Request object: https://flask.palletsprojects.com/en/.1.x/api/#flask.Request
@app.route('/submit-basic/', methods=['POST', 'GET'])
def submit_basic():
    if request.method == 'GET':
        return render_template('submit-basic.html')
    else:
        try:
            # this is how you can access the uploaded file
            # img = request.files['image']
            return render_template('submit-basic.html', thanks=True)
        except:
            return render_template('submit-basic.html', error=True)


# matplotlib: https://matplotlib.org/3.5.0/gallery/user_interfaces/web_application_server_sgskip.html
# plotly: https://towardsdatascience.com/web-visualization-with-plotly-and-flask-3660abf9c946
@app.route('/submit-advanced/', methods=['POST', 'GET'])
def submit():
    if request.method == 'GET':
        return render_template('submit.html')
    else:
        try:            
            '''
            1. Access the image
            2. Load the pickled ML model
            3. Run the ML model on the image
            4. Store the ML model's prediction in some Python variable
            5. Show the image on the template
            6. Print the prediction and some message on the template
            '''
            # 1
            img = request.files['image'] # file object 144.txt 
            img = np.loadtxt(img) # numpy array with the pixel values

            x = img.reshape(1, 64)
            
            # 2
            model = pickle.load(open('mnist-model/model.pkl', 'rb'))
            
            # 3, 4
            digit = model.predict(x)[0]

            # 5 
            fig = Figure(figsize=(3, 3))
            ax = fig.add_subplot(1, 1, 1,)
            ax.imshow(img, cmap='binary')
            ax.axis("off")

            # weird part of 5
            pngImage = io.BytesIO()
            FigureCanvas(fig).print_png(pngImage) # convert the pyplot figure object to a PNG image

            # encode the PNG image to base64 string
            pngImageB64String = "data:image/png;base64,"
            pngImageB64String += base64.b64encode(pngImage.getvalue()).decode('utf8')

            return render_template('submit.html',
             image=pngImageB64String, digit=digit)
        except:
            return render_template('submit.html', error=True)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

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
    ingredients = None  # Modify as needed, depending on your application's functionality

    recommended_recipes = gen_recipe(cuisine, ingredients)
    recipes_data = recommended_recipes.to_dict(orient='records')
    
    # Render the recipe_results.html template, passing the recipes data
    return render_template('recipe_results.html', recipes=recipes_data)

@app.route('/')
def index():
    # Render your main page here
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
    
@app.route('/recipe_results', methods=['GET', 'POST'])
def recipe_results(ingredients=None):
    if request.method == 'POST':
        cuisine = request.form.get('cuisine')
        # ingredients = None  # Adjust as necessary
        recommended_recipes = gen_recipe(cuisine, ingredients)
        recipes_data = recommended_recipes.to_dict(orient='records')
        print(recipes_data)  # Debugging line to check data
        return render_template('recipe_results.html', recipes=recipes_data)
    else:
        message = "Please select a cuisine to view recipes."
        return render_template('recipe_results.html', message=message)
if __name__ == '__main__':
    app.run(debug=True)
