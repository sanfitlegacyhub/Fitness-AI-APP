import json
from typing import Dict, List
from app.models import GoalEnum, ActivityLevelEnum

class WorkoutGenerator:
    """Generate personalized workout plans"""
    
    # Exercise database organized by muscle group and difficulty
    EXERCISES = {
        "chest": {
            "beginner": ["Push-ups", "Incline Push-ups", "Chest Press Machine"],
            "intermediate": ["Bench Press", "Dumbbell Flyes", "Cable Crossovers"],
            "advanced": ["Barbell Bench Press", "Weighted Dips", "Decline Bench Press"]
        },
        "back": {
            "beginner": ["Assisted Pull-ups", "Lat Pulldown", "Seated Cable Row"],
            "intermediate": ["Pull-ups", "Barbell Rows", "T-Bar Rows"],
            "advanced": ["Weighted Pull-ups", "Deadlifts", "Pendlay Rows"]
        },
        "legs": {
            "beginner": ["Bodyweight Squats", "Leg Press", "Leg Curls"],
            "intermediate": ["Barbell Squats", "Lunges", "Romanian Deadlifts"],
            "advanced": ["Front Squats", "Bulgarian Split Squats", "Barbell Hip Thrusts"]
        },
        "shoulders": {
            "beginner": ["Dumbbell Shoulder Press", "Lateral Raises", "Front Raises"],
            "intermediate": ["Military Press", "Arnold Press", "Face Pulls"],
            "advanced": ["Overhead Press", "Handstand Push-ups", "Heavy Lateral Raises"]
        },
        "arms": {
            "beginner": ["Dumbbell Curls", "Tricep Pushdowns", "Hammer Curls"],
            "intermediate": ["Barbell Curls", "Skull Crushers", "Preacher Curls"],
            "advanced": ["Weighted Chin-ups", "Close-Grip Bench Press", "Cable Curls"]
        },
        "core": {
            "beginner": ["Planks", "Crunches", "Leg Raises"],
            "intermediate": ["Hanging Leg Raises", "Russian Twists", "Ab Wheel"],
            "advanced": ["Dragon Flags", "Weighted Planks", "L-Sits"]
        },
        "cardio": {
            "beginner": ["Walking", "Light Jogging", "Cycling"],
            "intermediate": ["Running", "HIIT", "Jump Rope"],
            "advanced": ["Sprints", "Advanced HIIT", "Burpees"]
        }
    }
    
    @staticmethod
    def determine_difficulty(activity_level: ActivityLevelEnum, goal: GoalEnum) -> str:
        """Determine workout difficulty based on activity level and goal"""
        if activity_level in [ActivityLevelEnum.SEDENTARY, ActivityLevelEnum.LIGHTLY_ACTIVE]:
            return "beginner"
        elif activity_level in [ActivityLevelEnum.MODERATELY_ACTIVE, ActivityLevelEnum.VERY_ACTIVE]:
            return "intermediate"
        else:
            return "advanced"
    
    @staticmethod
    def generate_workout_split(goal: GoalEnum, difficulty: str) -> Dict[str, List[str]]:
        """Generate workout split based on goal"""
        if goal == GoalEnum.LOSE_WEIGHT:
            # More cardio-focused with full body workouts
            return {
                "Monday": ["Full Body Strength", "Cardio"],
                "Tuesday": ["Cardio", "Core"],
                "Wednesday": ["Rest"],
                "Thursday": ["Full Body Strength", "Cardio"],
                "Friday": ["Cardio", "Core"],
                "Saturday": ["Active Recovery"],
                "Sunday": ["Rest"]
            }
        elif goal == GoalEnum.GAIN_MUSCLE:
            # Traditional bodybuilding split
            return {
                "Monday": ["Chest", "Triceps"],
                "Tuesday": ["Back", "Biceps"],
                "Wednesday": ["Legs"],
                "Thursday": ["Shoulders", "Core"],
                "Friday": ["Chest", "Back"],
                "Saturday": ["Arms", "Core"],
                "Sunday": ["Rest"]
            }
        else:  # MAINTAIN
            # Balanced approach
            return {
                "Monday": ["Upper Body", "Core"],
                "Tuesday": ["Lower Body", "Cardio"],
                "Wednesday": ["Rest"],
                "Thursday": ["Full Body", "Core"],
                "Friday": ["Cardio"],
                "Saturday": ["Active Recovery"],
                "Sunday": ["Rest"]
            }
    
    @staticmethod
    def create_exercise_details(muscle_group: str, difficulty: str, sets: int, reps: str) -> List[Dict]:
        """Create detailed exercise list for a muscle group"""
        exercises = WorkoutGenerator.EXERCISES.get(muscle_group.lower(), {}).get(difficulty, [])
        
        exercise_details = []
        for exercise in exercises[:3]:  # Take top 3 exercises
            exercise_details.append({
                "name": exercise,
                "sets": sets,
                "reps": reps,
                "rest": "60-90 seconds"
            })
        
        return exercise_details
    
    @staticmethod
    def generate_workout_plan(
        goal: GoalEnum,
        activity_level: ActivityLevelEnum,
        duration_weeks: int = 8
    ) -> Dict:
        """
        Generate a complete workout plan
        Args:
            goal: Fitness goal
            activity_level: Current activity level
            duration_weeks: Duration of the plan in weeks
        Returns:
            Complete workout plan dictionary
        """
        difficulty = WorkoutGenerator.determine_difficulty(activity_level, goal)
        workout_split = WorkoutGenerator.generate_workout_split(goal, difficulty)
        
        # Determine sets and reps based on goal
        if goal == GoalEnum.LOSE_WEIGHT:
            sets, reps = 3, "12-15"
        elif goal == GoalEnum.GAIN_MUSCLE:
            sets, reps = 4, "8-12"
        else:
            sets, reps = 3, "10-12"
        
        # Create detailed weekly plan
        weekly_plan = {}
        for day, muscle_groups in workout_split.items():
            day_exercises = []
            
            for muscle_group in muscle_groups:
                if muscle_group not in ["Rest", "Active Recovery"]:
                    exercises = WorkoutGenerator.create_exercise_details(
                        muscle_group, difficulty, sets, reps
                    )
                    day_exercises.extend(exercises)
            
            weekly_plan[day] = {
                "focus": muscle_groups,
                "exercises": day_exercises if day_exercises else [{"name": muscle_groups[0], "description": "Light activity or complete rest"}]
            }
        
        # Create the complete plan
        plan = {
            "title": f"{goal.value.replace('_', ' ').title()} Workout Plan",
            "difficulty": difficulty.title(),
            "duration_weeks": duration_weeks,
            "goal": goal.value,
            "weekly_schedule": weekly_plan,
            "tips": WorkoutGenerator.get_workout_tips(goal, difficulty),
            "progression": f"Increase weight by 5-10% every 2 weeks or when you can complete all sets with good form"
        }
        
        return plan
    
    @staticmethod
    def get_workout_tips(goal: GoalEnum, difficulty: str) -> List[str]:
        """Get workout tips based on goal and difficulty"""
        tips = [
            "Always warm up for 5-10 minutes before starting",
            "Focus on proper form over heavy weights",
            "Stay hydrated throughout your workout",
            "Get adequate rest between workouts"
        ]
        
        if goal == GoalEnum.LOSE_WEIGHT:
            tips.extend([
                "Combine strength training with cardio for best results",
                "Keep rest periods shorter (30-60 seconds) to maintain heart rate",
                "Consider adding HIIT sessions for maximum calorie burn"
            ])
        elif goal == GoalEnum.GAIN_MUSCLE:
            tips.extend([
                "Progressive overload is key - gradually increase weight",
                "Ensure adequate protein intake (1.6-2.2g per kg bodyweight)",
                "Get 7-9 hours of sleep for optimal recovery"
            ])
        
        if difficulty == "beginner":
            tips.append("Start with lighter weights to master form before progressing")
        
        return tips

