import pandas as pd, os, json
from difflib import get_close_matches

#reading csv files.
data_dir = "data"
nutrition_df = pd.read_csv(os.path.join(data_dir, "nutrition_values.csv"))
units_df = pd.read_csv(os.path.join(data_dir, "unit_measurements.csv"))
categories_df = pd.read_csv(os.path.join(data_dir, "food_categories.csv"))
log = [] #logs

# extracting first name of the ingredient.
def normalize_name(name):
    return name.lower().strip().split("(")[0].split(",")[0]

nutrition_df["normalized_name"] = nutrition_df["food_name"].apply(normalize_name)

# unit conversions(hardcoded)  (implement with AI Integration)
unit_to_grams = {
    "tbsp": {
        "Butter": 14,
        "Oil": 13,
        "Cream": 15,
        "default": 15
    },
    "tsp": {
        "Mixed Spices": 2,
        "default": 5
    },
    "medium": {
        "Onion": 100,
        "Tomato": 75,
        "default": 100
    },
    "small": {
        "default": 50
    },
    "large": {
        "default": 150
    }
}

#extracting ingredient details(simulation) (get details through llm integration.)
def get_ingredients_from_ai(dish_name):
    if dish_name.lower() == "paneer butter masala":
        return [
            {"name": "Paneer", "quantity": 100, "unit": "g"},
            {"name": "Butter", "quantity": 1, "unit": "tbsp"},
            {"name": "Onion", "quantity": 1, "unit": "medium"},
            {"name": "Tomato", "quantity": 2, "unit": "medium"},
            {"name": "Oil", "quantity": 1, "unit": "tbsp"},
            {"name": "Cream", "quantity": 2, "unit": "tbsp"},
            {"name": "Mixed Spices", "quantity": 1, "unit": "tsp"},
        ]
    else:
        log.append(f"no ingredients found for dish: {dish_name}.")
        return []

#function to perform unit conversions.
def convert_to_grams(ingredient):
    name = ingredient.get("name")
    qty = ingredient.get("quantity")
    unit = ingredient.get("unit")

    if qty is None:
        log.append(f"missing quantity for '{name}', skipping.")
        return None

    if unit == "g":
        return qty

    if unit in unit_to_grams:
        unit_data = unit_to_grams[unit]
        if name in unit_data:
            return qty * unit_data[name]
        elif "default" in unit_data:
            defualt_grams = qty * unit_data["default"]
            log.append(f"used default conversion for unit '{unit}' of '{name}': {defualt_grams}g assumed.")
            return defualt_grams

    log.append(f"no conversion rule for unit '{unit}' of '{name}'. skipping.")
    return None

#finding the best for ingrediant from nutrition database
def find_best_match(name):
    all_names = nutrition_df["normalized_name"].unique()
    matches = get_close_matches(name, all_names, n=1, cutoff=0.7)
    if matches:
        result = nutrition_df[nutrition_df["normalized_name"] == matches[0]]
        if len(result) > 1:
            log.append(f"multiple nutrition matches found for '{name}'. Using first match: {result.iloc[0]['food_name']}") # selecting the first row if multiple rows are matched
        return result
    return pd.DataFrame()

#user input
dish_name = input("Enter the dish name: ")
print(f"\nUser Input: {dish_name}")
ingredients = get_ingredients_from_ai(dish_name)
print("\nIngredients Fetched:")
for ing in ingredients:
    print(f"- {ing['quantity']} {ing['unit']} {ing['name']}")

#nutrition json object.
nutrition_summary = {
    "energy_kcal": 0,
    "carb_g": 0,
    "protein_g": 0,
    "fat_g": 0,
    "fibre_g": 0
}

#main function(to process and find nutrition)
for ing in ingredients:
    ing_name = normalize_name(ing["name"])
    ing["grams"] = convert_to_grams(ing)

    if not ing["grams"]:
        log.append(f"Skipping '{ing['name']}', could not convert to grams.")
        continue

    match = find_best_match(ing_name)
    if match.empty:
        log.append(f"no nutrition match found for '{ing_name}', may be a synonym or missing entry.")
        continue

    row = match.iloc[0]
    factor = ing["grams"] / 100  #given nutrition values are per 100g in assignment.

    nutrition_summary["energy_kcal"] += row["energy_kcal"] * factor
    nutrition_summary["carb_g"] += row["carb_g"] * factor
    nutrition_summary["protein_g"] += row["protein_g"] * factor
    nutrition_summary["fat_g"] += row["fat_g"] * factor
    nutrition_summary["fibre_g"] += row["fibre_g"] * factor

    log.append(f"Mapped '{ing['name']}' to '{row['food_name']}' with {ing['grams']}g.")
    print(f"\n{ing['name']} → {row['food_name']} | {ing['grams']}g contributes:")
    print(f"  Energy: {row['energy_kcal'] * factor:.2f} kcal")
    print(f"  Protein: {row['protein_g'] * factor:.2f}g | Fat: {row['fat_g'] * factor:.2f}g")
    print(f"  Carbs: {row['carb_g'] * factor:.2f}g | Fibre: {row['fibre_g'] * factor:.2f}g")

#final calculation
total_weight = sum([ing["grams"] for ing in ingredients if ing.get("grams")])
scale_factor = 150 / total_weight if total_weight else 0    # 1 katori = 150g
per_katori_nutrition = {k: round(v * scale_factor, 2) for k, v in nutrition_summary.items()}

#output json object
output = {
    "dish": dish_name,
    "total_cooked_weight": total_weight,
    "nutrition_per_katori_150g": per_katori_nutrition,
    "log": log
}

print("\ntotal Cooked Weight:", total_weight, "g")
print("nutrition per 150g serving:")
for k, v in per_katori_nutrition.items():
    print(f"  {k}: {v}")

with open("output.json", "w") as f:
    json.dump(output, f, indent=2)

with open("debug-log.txt", "w") as f:
    f.write("\n".join(log))

print("\nlogs have been saved in debug-log.txt and Output saved to output.json")
