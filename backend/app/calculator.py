from typing import Dict, Any
from app.models import ActivityLevelEnum, GoalEnum, GenderEnum

class FitnessCalculator:
    """Calculate various fitness metrics"""
    
    # Activity level multipliers for TDEE
    ACTIVITY_MULTIPLIERS = {
        ActivityLevelEnum.SEDENTARY: 1.2,
        ActivityLevelEnum.LIGHTLY_ACTIVE: 1.375,
        ActivityLevelEnum.MODERATELY_ACTIVE: 1.55,
        ActivityLevelEnum.VERY_ACTIVE: 1.725,
        ActivityLevelEnum.EXTREMELY_ACTIVE: 1.9
    }
    
    # Calorie adjustment for goals
    GOAL_ADJUSTMENTS = {
        GoalEnum.LOSE_WEIGHT: -500,  # 500 calorie deficit
        GoalEnum.MAINTAIN: 0,
        GoalEnum.GAIN_MUSCLE: 300    # 300 calorie surplus
    }
    
    @staticmethod
    def calculate_bmi(weight: float, height: float) -> float:
        """
        Calculate Body Mass Index
        Args:
            weight: Weight in kg
            height: Height in cm
        Returns:
            BMI value
        """
        height_m = height / 100
        return round(weight / (height_m ** 2), 2)
    
    @staticmethod
    def calculate_bmr(weight: float, height: float, age: int, gender: GenderEnum) -> float:
        """
        Calculate Basal Metabolic Rate using Mifflin-St Jeor Equation
        Args:
            weight: Weight in kg
            height: Height in cm
            age: Age in years
            gender: Gender
        Returns:
            BMR in calories
        """
        if gender == GenderEnum.MALE:
            bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
        else:  # FEMALE or OTHER
            bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161
        
        return round(bmr, 2)
    
    @staticmethod
    def calculate_tdee(bmr: float, activity_level: ActivityLevelEnum) -> float:
        """
        Calculate Total Daily Energy Expenditure
        Args:
            bmr: Basal Metabolic Rate
            activity_level: Activity level
        Returns:
            TDEE in calories
        """
        multiplier = FitnessCalculator.ACTIVITY_MULTIPLIERS[activity_level]
        return round(bmr * multiplier, 2)
    
    @staticmethod
    def calculate_target_calories(tdee: float, goal: GoalEnum) -> float:
        """
        Calculate target daily calories based on goal
        Args:
            tdee: Total Daily Energy Expenditure
            goal: Fitness goal
        Returns:
            Target calories
        """
        adjustment = FitnessCalculator.GOAL_ADJUSTMENTS[goal]
        return round(tdee + adjustment, 2)
    
    @staticmethod
    def calculate_macros(target_calories: float, goal: GoalEnum) -> Dict[str, float]:
        """
        Calculate macronutrient distribution
        Args:
            target_calories: Target daily calories
            goal: Fitness goal
        Returns:
            Dictionary with protein, carbs, and fats in grams
        """
        if goal == GoalEnum.LOSE_WEIGHT:
            # Higher protein for weight loss: 40% protein, 30% carbs, 30% fats
            protein_ratio = 0.40
            carbs_ratio = 0.30
            fats_ratio = 0.30
        elif goal == GoalEnum.GAIN_MUSCLE:
            # Balanced for muscle gain: 30% protein, 40% carbs, 30% fats
            protein_ratio = 0.30
            carbs_ratio = 0.40
            fats_ratio = 0.30
        else:  # MAINTAIN
            # Balanced: 30% protein, 40% carbs, 30% fats
            protein_ratio = 0.30
            carbs_ratio = 0.40
            fats_ratio = 0.30
        
        # Calculate grams (protein: 4 cal/g, carbs: 4 cal/g, fats: 9 cal/g)
        protein_grams = round((target_calories * protein_ratio) / 4, 2)
        carbs_grams = round((target_calories * carbs_ratio) / 4, 2)
        fats_grams = round((target_calories * fats_ratio) / 9, 2)
        
        return {
            "protein": protein_grams,
            "carbs": carbs_grams,
            "fats": fats_grams
        }
    
    @staticmethod
    def get_bmi_category(bmi: float) -> str:
        """Get BMI category"""
        if bmi < 18.5:
            return "Underweight"
        elif bmi < 25:
            return "Normal weight"
        elif bmi < 30:
            return "Overweight"
        else:
            return "Obese"
    
    @staticmethod
    def calculate_all_metrics(
        weight: float,
        height: float,
        age: int,
        gender: GenderEnum,
        activity_level: ActivityLevelEnum,
        goal: GoalEnum
    ) -> Dict[str, Any]:
        """
        Calculate all fitness metrics at once
        Returns:
            Dictionary with all calculated metrics
        """
        bmi = FitnessCalculator.calculate_bmi(weight, height)
        bmr = FitnessCalculator.calculate_bmr(weight, height, age, gender)
        tdee = FitnessCalculator.calculate_tdee(bmr, activity_level)
        target_calories = FitnessCalculator.calculate_target_calories(tdee, goal)
        macros = FitnessCalculator.calculate_macros(target_calories, goal)
        
        return {
            "bmi": bmi,
            "bmi_category": FitnessCalculator.get_bmi_category(bmi),
            "bmr": bmr,
            "tdee": tdee,
            "target_calories": target_calories,
            "macros": macros
        }

