# Smart Nutrition Estimator (CLI Version)

**Smart Nutrition Estimator** is a Python command-line tool that estimates nutritional values of Indian dishes using a pre-built database and ingredient-to-gram conversion logic.

---

## Features

- Estimates energy, carbs, protein, fat, and fiber
- Converts common units like tbsp, tsp, medium into grams
- Outputs nutrition per 150g serving (standard katori)
- Logs mapping steps and issues to a debug file
- Extendable with AI, OCR, or NLP modules in the future

---

## Folder Structure
```
smart-nutrition-estimator/
├── main.py 
├── requirements.txt 
├── output.json  
├── debug-log.txt
└── data/
    ├── nutrition_values.csv
    ├── unit_measurements.csv
    └── food_categories.csv
```

## How to Run

### 1. Clone the repository
```
git clone https://github.com/your-username/smart-nutrition-estimator.git
cd smart-nutrition-estimator
```
### 2. Set up a virtual environment

```
python -m venv venv
venv\Scripts\activate       # On Windows
# or
source venv/bin/activate    # On macOS/Linux
```
### 3. Install required packages
```
pip install -r requirements.txt
```
### 4. Run the estimator
```
python main.py
```

## Output
- output.json → structured result with per-serving nutrition
- debug-log.txt → shows fallback conversions, matched food items, etc.

## Notes
- Currently supports paneer butter masala only (customize in get_ingredients_from_ai()).
- Ingredient-to-gram conversion is hardcoded with default fallbacks.
- Nutrition values are based on 100g servings from CSV data.

