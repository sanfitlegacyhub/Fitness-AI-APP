import json
from typing import Dict, List
from app.models import GoalEnum

class DietGenerator:
    """Generate personalized diet plans"""
    
    # Meal templates organized by meal type
    MEAL_DATABASE = {
        "breakfast": {
            "high_protein": [
                {"name": "Greek Yogurt Parfait", "protein": 25, "carbs": 35, "fats": 8, "calories": 310},
                {"name": "Scrambled Eggs with Avocado", "protein": 24, "carbs": 12, "fats": 22, "calories": 340},
                {"name": "Protein Oatmeal", "protein": 30, "carbs": 45, "fats": 10, "calories": 390},
                {"name": "Egg White Omelet", "protein": 28, "carbs": 15, "fats": 8, "calories": 248}
            ],
            "balanced": [
                {"name": "Whole Grain Toast with Peanut Butter", "protein": 12, "carbs": 40, "fats": 16, "calories": 340},
                {"name": "Smoothie Bowl", "protein": 15, "carbs": 50, "fats": 12, "calories": 368},
                {"name": "Overnight Oats", "protein": 18, "carbs": 55, "fats": 14, "calories": 418}
            ],
            "low_carb": [
                {"name": "Keto Egg Muffins", "protein": 20, "carbs": 8, "fats": 18, "calories": 278},
                {"name": "Avocado Egg Boats", "protein": 16, "carbs": 10, "fats": 24, "calories": 320},
                {"name": "Cheese and Veggie Omelet", "protein": 22, "carbs": 6, "fats": 20, "calories": 298}
            ]
        },
        "lunch": {
            "high_protein": [
                {"name": "Grilled Chicken Salad", "protein": 40, "carbs": 20, "fats": 15, "calories": 385},
                {"name": "Tuna Quinoa Bowl", "protein": 38, "carbs": 35, "fats": 12, "calories": 410},
                {"name": "Turkey Wrap", "protein": 35, "carbs": 30, "fats": 14, "calories": 394},
                {"name": "Salmon with Vegetables", "protein": 42, "carbs": 18, "fats": 20, "calories": 440}
            ],
            "balanced": [
                {"name": "Chicken Rice Bowl", "protein": 30, "carbs": 50, "fats": 15, "calories": 465},
                {"name": "Pasta with Lean Meat", "protein": 28, "carbs": 55, "fats": 18, "calories": 494},
                {"name": "Burrito Bowl", "protein": 32, "carbs": 48, "fats": 16, "calories": 472}
            ],
            "low_carb": [
                {"name": "Steak with Broccoli", "protein": 45, "carbs": 12, "fats": 25, "calories": 477},
                {"name": "Chicken Caesar Salad", "protein": 38, "carbs": 10, "fats": 22, "calories": 410},
                {"name": "Grilled Fish with Asparagus", "protein": 40, "carbs": 8, "fats": 18, "calories": 370}
            ]
        },
        "dinner": {
            "high_protein": [
                {"name": "Lean Beef Stir-fry", "protein": 45, "carbs": 25, "fats": 18, "calories": 458},
                {"name": "Baked Chicken Breast", "protein": 48, "carbs": 20, "fats": 12, "calories": 396},
                {"name": "Grilled Salmon", "protein": 42, "carbs": 15, "fats": 22, "calories": 442},
                {"name": "Turkey Meatballs", "protein": 40, "carbs": 22, "fats": 16, "calories": 408}
            ],
            "balanced": [
                {"name": "Chicken with Sweet Potato", "protein": 35, "carbs": 45, "fats": 14, "calories": 454},
                {"name": "Fish Tacos", "protein": 32, "carbs": 40, "fats": 18, "calories": 450},
                {"name": "Beef and Rice", "protein": 38, "carbs": 50, "fats": 16, "calories": 504}
            ],
            "low_carb": [
                {"name": "Ribeye with Cauliflower", "protein": 50, "carbs": 10, "fats": 30, "calories": 550},
                {"name": "Pork Chops with Green Beans", "protein": 42, "carbs": 12, "fats": 24, "calories": 456},
                {"name": "Chicken Thighs with Zucchini", "protein": 38, "carbs": 8, "fats": 26, "calories": 434}
            ]
        },
        "snacks": {
            "high_protein": [
                {"name": "Protein Shake", "protein": 25, "carbs": 10, "fats": 3, "calories": 165},
                {"name": "Cottage Cheese", "protein": 20, "carbs": 8, "fats": 5, "calories": 161},
                {"name": "Hard Boiled Eggs", "protein": 12, "carbs": 2, "fats": 10, "calories": 154}
            ],
            "balanced": [
                {"name": "Apple with Almond Butter", "protein": 6, "carbs": 25, "fats": 12, "calories": 232},
                {"name": "Trail Mix", "protein": 8, "carbs": 20, "fats": 15, "calories": 252},
                {"name": "Protein Bar", "protein": 15, "carbs": 22, "fats": 8, "calories": 220}
            ],
            "low_carb": [
                {"name": "Cheese and Nuts", "protein": 12, "carbs": 6, "fats": 18, "calories": 234},
                {"name": "Beef Jerky", "protein": 15, "carbs": 4, "fats": 8, "calories": 148},
                {"name": "Celery with Cream Cheese", "protein": 6, "carbs": 5, "fats": 12, "calories": 150}
            ]
        }
    }
    
    @staticmethod
    def determine_meal_style(goal: GoalEnum) -> str:
        """Determine meal style based on goal"""
        if goal == GoalEnum.LOSE_WEIGHT:
            return "high_protein"
        elif goal == GoalEnum.GAIN_MUSCLE:
            return "balanced"
        else:
            return "balanced"
    
    @staticmethod
    def select_meals(meal_type: str, meal_style: str, count: int = 3) -> List[Dict]:
        """Select meals from database"""
        meals = DietGenerator.MEAL_DATABASE.get(meal_type, {}).get(meal_style, [])
        return meals[:count] if meals else []
    
    @staticmethod
    def calculate_meal_distribution(
        target_calories: float,
        protein_grams: float,
        carbs_grams: float,
        fats_grams: float
    ) -> Dict[str, Dict]:
        """Calculate how to distribute macros across meals"""
        # Standard distribution: 25% breakfast, 35% lunch, 35% dinner, 5% snacks
        distribution = {
            "breakfast": {
                "calories": target_calories * 0.25,
                "protein": protein_grams * 0.25,
                "carbs": carbs_grams * 0.25,
                "fats": fats_grams * 0.25
            },
            "lunch": {
                "calories": target_calories * 0.35,
                "protein": protein_grams * 0.35,
                "carbs": carbs_grams * 0.35,
                "fats": fats_grams * 0.35
            },
            "dinner": {
                "calories": target_calories * 0.35,
                "protein": protein_grams * 0.35,
                "carbs": carbs_grams * 0.35,
                "fats": fats_grams * 0.35
            },
            "snacks": {
                "calories": target_calories * 0.05,
                "protein": protein_grams * 0.05,
                "carbs": carbs_grams * 0.05,
                "fats": fats_grams * 0.05
            }
        }
        
        return distribution
    
    @staticmethod
    def generate_diet_plan(
        target_calories: float,
        protein_grams: float,
        carbs_grams: float,
        fats_grams: float,
        goal: GoalEnum
    ) -> Dict:
        """
        Generate a complete diet plan
        Args:
            target_calories: Target daily calories
            protein_grams: Target protein in grams
            carbs_grams: Target carbs in grams
            fats_grams: Target fats in grams
            goal: Fitness goal
        Returns:
            Complete diet plan dictionary
        """
        meal_style = DietGenerator.determine_meal_style(goal)
        meal_distribution = DietGenerator.calculate_meal_distribution(
            target_calories, protein_grams, carbs_grams, fats_grams
        )
        
        # Generate meal options for each meal type
        daily_plan = {}
        for meal_type in ["breakfast", "lunch", "dinner", "snacks"]:
            meal_options = DietGenerator.select_meals(meal_type, meal_style, count=3)
            target_macros = meal_distribution[meal_type]
            
            daily_plan[meal_type] = {
                "target_calories": round(target_macros["calories"], 0),
                "target_protein": round(target_macros["protein"], 1),
                "target_carbs": round(target_macros["carbs"], 1),
                "target_fats": round(target_macros["fats"], 1),
                "meal_options": meal_options
            }
        
        # Create the complete plan
        plan = {
            "title": f"{goal.value.replace('_', ' ').title()} Diet Plan",
            "daily_calories": target_calories,
            "daily_macros": {
                "protein": protein_grams,
                "carbs": carbs_grams,
                "fats": fats_grams
            },
            "meal_plan": daily_plan,
            "hydration": "Drink at least 8-10 glasses (2-3 liters) of water daily",
            "tips": DietGenerator.get_diet_tips(goal),
            "meal_timing": {
                "breakfast": "7:00 AM - 9:00 AM",
                "lunch": "12:00 PM - 2:00 PM",
                "dinner": "6:00 PM - 8:00 PM",
                "snacks": "Between meals as needed"
            }
        }
        
        return plan
    
    @staticmethod
    def get_diet_tips(goal: GoalEnum) -> List[str]:
        """Get diet tips based on goal"""
        tips = [
            "Eat whole, unprocessed foods whenever possible",
            "Prepare meals in advance to stay on track",
            "Track your food intake for the first few weeks",
            "Listen to your body's hunger and fullness cues"
        ]
        
        if goal == GoalEnum.LOSE_WEIGHT:
            tips.extend([
                "Create a moderate calorie deficit (500 calories/day)",
                "Prioritize protein to preserve muscle mass",
                "Include plenty of vegetables for volume and nutrients",
                "Avoid liquid calories (sodas, juices)",
                "Practice portion control"
            ])
        elif goal == GoalEnum.GAIN_MUSCLE:
            tips.extend([
                "Eat in a slight calorie surplus (300 calories/day)",
                "Consume protein with every meal (aim for 1.6-2.2g/kg)",
                "Time protein intake around workouts",
                "Don't neglect carbs - they fuel your workouts",
                "Be consistent with meal timing"
            ])
        else:  # MAINTAIN
            tips.extend([
                "Focus on nutrient-dense foods",
                "Maintain consistent eating patterns",
                "Balance your macronutrients",
                "Allow flexibility for social occasions"
            ])
        
        return tips

