# 💪 Fitness AI App

An AI-powered fitness and nutrition planning application that provides personalized workout plans and diet recommendations based on your goals and fitness level.

## Features

- 🏋️ **Personalized Workout Plans** - AI-generated workout routines based on your fitness level and goals
- 🥗 **Custom Diet Plans** - Tailored meal plans with macro calculations
- 📊 **Fitness Metrics** - Calculate BMI, BMR, TDEE, and target calories
- 👤 **User Profiles** - Track your progress and preferences
- 🎯 **Goal-Oriented** - Support for weight loss, maintenance, and muscle gain

## Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - SQL toolkit and ORM
- **SQLite** - Database (easily switchable to PostgreSQL)
- **Pydantic** - Data validation
- **Passlib** - Password hashing

### Frontend
- **HTML5/CSS3** - Modern, responsive UI
- **Vanilla JavaScript** - No framework dependencies
- **Fetch API** - RESTful API communication

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file (optional, uses SQLite by default):
```bash
cp .env.example .env
```

4. Run the application:
```bash
python -m app.main
```

Or using uvicorn directly:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. Open `frontend/index.html` in your web browser
   - You can simply double-click the file
   - Or use a local server (recommended):

Using Python:
```bash
cd frontend
python -m http.server 3000
```

Then open `http://localhost:3000` in your browser

## Usage

### 1. Create an Account
- Go to the "Register" tab
- Enter your email, username, and password
- Note your User ID from the success message

### 2. Create Your Profile
- Go to the "Create Profile" tab
- Enter your User ID
- Fill in your personal information:
  - Age, gender, height, weight
  - Activity level
  - Fitness goal (lose weight, maintain, gain muscle)
- Submit to calculate your metrics

### 3. View Your Metrics
- Go to the "View Metrics" tab
- Enter your User ID
- See your BMI, BMR, TDEE, and recommended macros

### 4. Generate Workout Plan
- Go to the "Generate Workout" tab
- Enter your User ID
- Choose duration (4-16 weeks)
- Get a personalized workout plan with:
  - Weekly schedule
  - Exercise details (sets, reps, rest)
  - Progression guidelines
  - Tips and recommendations

### 5. Generate Diet Plan
- Go to the "Generate Diet Plan" tab
- Enter your User ID
- Get a personalized diet plan with:
  - Daily calorie target
  - Macro breakdown
  - Meal options for breakfast, lunch, dinner, and snacks
  - Meal timing recommendations
  - Nutrition tips

## API Documentation

Once the backend is running, visit:
- **Interactive API Docs**: `http://localhost:8000/docs`
- **Alternative Docs**: `http://localhost:8000/redoc`

### Main Endpoints

#### Users
- `POST /users` - Create new user
- `GET /users/{user_id}` - Get user details

#### Profile
- `POST /profile/{user_id}` - Create user profile
- `GET /profile/{user_id}` - Get user profile
- `PUT /profile/{user_id}` - Update user profile

#### Metrics
- `GET /metrics/{user_id}` - Get calculated fitness metrics

#### Workout Plans
- `POST /workout/{user_id}` - Generate workout plan
- `GET /workout/{user_id}/latest` - Get latest workout plan
- `GET /workout/{user_id}/all` - Get all workout plans

#### Diet Plans
- `POST /diet/{user_id}` - Generate diet plan
- `GET /diet/{user_id}/latest` - Get latest diet plan
- `GET /diet/{user_id}/all` - Get all diet plans

## Project Structure

```
fitness-ai-app/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI application
│   │   ├── models.py            # Database models
│   │   ├── database.py          # Database configuration
│   │   ├── calculator.py        # Fitness calculations
│   │   ├── workout_generator.py # Workout plan generation
│   │   └── diet_generator.py    # Diet plan generation
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   └── index.html               # Web interface
└── README.md
```

## Fitness Calculations

### BMI (Body Mass Index)
```
BMI = weight(kg) / (height(m))²
```

### BMR (Basal Metabolic Rate) - Mifflin-St Jeor Equation
```
Men: BMR = (10 × weight) + (6.25 × height) - (5 × age) + 5
Women: BMR = (10 × weight) + (6.25 × height) - (5 × age) - 161
```

### TDEE (Total Daily Energy Expenditure)
```
TDEE = BMR × Activity Multiplier
```

Activity Multipliers:
- Sedentary: 1.2
- Lightly Active: 1.375
- Moderately Active: 1.55
- Very Active: 1.725
- Extremely Active: 1.9

### Target Calories
- **Weight Loss**: TDEE - 500 cal
- **Maintenance**: TDEE
- **Muscle Gain**: TDEE + 300 cal

## Database

The application uses SQLite by default, which creates a `fitness_ai.db` file in the backend directory.

To use PostgreSQL instead:
1. Install PostgreSQL
2. Create a database
3. Update the `DATABASE_URL` in `.env`:
```
DATABASE_URL=postgresql://user:password@localhost/fitness_ai
```

## Development

### Running Tests
```bash
cd backend
pytest
```

### Code Style
The project follows PEP 8 guidelines for Python code.

## Future Enhancements

- [ ] User authentication with JWT tokens
- [ ] Progress tracking and analytics
- [ ] Exercise video demonstrations
- [ ] Meal prep instructions
- [ ] Mobile app (React Native)
- [ ] Social features (share workouts, challenges)
- [ ] Integration with fitness trackers
- [ ] AI chatbot for fitness advice
- [ ] Recipe database with nutritional info
- [ ] Workout history and statistics

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the MIT License.

## Support

For issues, questions, or suggestions, please open an issue on the project repository.

---

**Built with ❤️ for fitness enthusiasts**