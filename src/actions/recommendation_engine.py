# recommendation_engine.py
import sys
import json
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer
import pymongo
from bson import ObjectId

def scaling(dataframe):
    scaler = StandardScaler()
    # Using consistent column indices for nutritional values
    nutritional_columns = [
        'Calories', 'FatContent', 'SaturatedFatContent', 
        'CholesterolContent', 'SodiumContent', 'CarbohydrateContent', 
        'FiberContent', 'SugarContent', 'ProteinContent'
    ]
    prep_data = scaler.fit_transform(dataframe[nutritional_columns].to_numpy())
    return prep_data, scaler

def nn_predictor(prep_data):
    neigh = NearestNeighbors(metric='cosine', algorithm='brute')
    neigh.fit(prep_data)
    return neigh

def build_pipeline(neigh, scaler, params):
    transformer = FunctionTransformer(neigh.kneighbors, kw_args=params)
    pipeline = Pipeline([('std_scaler', scaler), ('NN', transformer)])
    return pipeline

def extract_data(dataframe, ingredient_filter, max_nutritional_values):
    extracted_data = dataframe.copy()
    nutritional_columns = [
        'Calories', 'FatContent', 'SaturatedFatContent', 
        'CholesterolContent', 'SodiumContent', 'CarbohydrateContent', 
        'FiberContent', 'SugarContent', 'ProteinContent'
    ]
    
    for column, maximum in zip(nutritional_columns, max_nutritional_values):
        extracted_data = extracted_data[extracted_data[column] < maximum]
    
    if ingredient_filter is not None:
        for ingredient in ingredient_filter:
            # Handle both string and list formats for RecipeIngredientParts
            extracted_data = extracted_data[
                extracted_data['RecipeIngredientParts'].apply(
                    lambda x: isinstance(x, str) and ingredient.lower() in x.lower() or 
                            isinstance(x, list) and any(ingredient.lower() in ing.lower() for ing in x)
                )
            ]
    
    return extracted_data

def apply_pipeline(pipeline, _input, extracted_data):
    indices = pipeline.transform(_input)[0]
    return extracted_data.iloc[indices]

def recommend(dataframe, _input, max_nutritional_values, ingredient_filter=None, params={'n_neighbors': 10, 'return_distance': False}):
    extracted_data = extract_data(dataframe, ingredient_filter, max_nutritional_values)
    
    # Check if we have enough data after filtering
    if len(extracted_data) < params.get('n_neighbors', 10):
        # If not enough data, reduce filtering constraints
        params['n_neighbors'] = min(len(extracted_data), 5)
        if len(extracted_data) == 0:
            return pd.DataFrame()  # Return empty DataFrame if no data left
    
    prep_data, scaler = scaling(extracted_data)
    neigh = nn_predictor(prep_data)
    pipeline = build_pipeline(neigh, scaler, params)
    
    try:
        result = apply_pipeline(pipeline, _input, extracted_data)
        return result
    except Exception as e:
        print(f"Error in recommendation: {e}", file=sys.stderr)
        return pd.DataFrame()

def main():
    try:
        # Get input from Node.js
        input_json = sys.argv[1]
        input_data = json.loads(input_json)
        
        recipe_id = input_data.get('recipeId')
        ingredient_filter = input_data.get('ingredientFilter')
        max_nutritional_values = input_data.get('maxNutritionValues')
        
        # Connect to MongoDB
        client = pymongo.MongoClient("mongodb://localhost:27017/")
        db = client["food_recommendation"]
        collection = db["recipes"]
        
        # Get all recipes as DataFrame
        all_recipes = pd.DataFrame(list(collection.find()))
        
        # Find the selected recipe
        selected_recipe = all_recipes[all_recipes['RecipeId'] == recipe_id]
        
        if selected_recipe.empty:
            print(json.dumps([]), file=sys.stdout)
            sys.exit(1)
        
        # Prepare input data for KNN
        nutritional_columns = [
            'Calories', 'FatContent', 'SaturatedFatContent', 
            'CholesterolContent', 'SodiumContent', 'CarbohydrateContent', 
            'FiberContent', 'SugarContent', 'ProteinContent'
        ]
        input_nutritional = selected_recipe[nutritional_columns].to_numpy()
        
        # Get recommendations
        recommendations = recommend(
            all_recipes,
            input_nutritional,
            max_nutritional_values,
            ingredient_filter,
            {'n_neighbors': 11, 'return_distance': False}  # 11 to include the input recipe itself
        )
        
        # Remove the input recipe from recommendations if present
        recommendations = recommendations[recommendations['RecipeId'] != recipe_id]
        
        # Take top 10 recommendations
        top_recommendations = recommendations.head(10)
        recommended_ids = top_recommendations['RecipeId'].tolist()
        
        # Return recipe IDs as JSON
        print(json.dumps(recommended_ids), file=sys.stdout)
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        print(json.dumps([]), file=sys.stdout)
        sys.exit(1)

if __name__ == "__main__":
    main()