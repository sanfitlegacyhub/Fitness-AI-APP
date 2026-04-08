# 🔄 Fitness AI App - Complete Code Flow Documentation

## 📋 Quick Navigation
- [Architecture Overview](#architecture-overview)
- [User Journey](#user-journey-flow)
- [Backend Details](#backend-flow-detailed)
- [Frontend Details](#frontend-flow-detailed)
- [Data Flow](#data-flow-diagram)
- [Key Concepts](#key-concepts)

---

## 🏗️ Architecture Overview

The Fitness AI app follows a client-server architecture with three main layers:

1. **Frontend (Client)** - HTML/CSS/JavaScript in browser
2. **Backend (Server)** - FastAPI Python application
3. **Database** - SQLite for data persistence

### Technology Stack

**Backend:**
- FastAPI - Modern Python web framework
- SQLAlchemy - ORM for database operations
- SQLite - Lightweight database
- Pydantic - Data validation

**Frontend:**
- HTML5/CSS3 - Structure and styling
- Vanilla JavaScript - Logic and interactivity
- Fetch API - HTTP requests

---

## 👤 User Journey Flow

### Complete User Flow from Start to Finish:

```
1. User opens app (dashboard.html)
   ↓
2. Sees Login/Register page
   ↓
3. Registers new account
   - Enters email, username, password
   - Backend creates user with hashed password
   - Returns user ID
   ↓
4. Logs in with credentials
   - Backend verifies password
   - Returns user data
   - Stored in localStorage
   ↓
5. Dashboard displays
   - Shows welcome message
   - Displays 4 action cards
   ↓
6. Clicks "Set Your Goal"
   - Fills profile form (age, gender, height, weight, activity, goal)
   - Backend calculates BMI, BMR, TDEE, target calories
   - Generates workout plan
   - Generates diet plan
   - Returns complete fitness plan
   ↓
7. Views results
   - Sees metrics (BMI, BMR, TDEE, calories)
   - Sees workout preview
   - Sees diet preview
   ↓
8. Clicks "Workout Plan" card
   - Fetches latest workout from database
   - Displays weekly schedule with exercises
   ↓
9. Clicks "Diet Plan" card
   - Fetches latest diet from database
   - Displays meal plan with options
```

---

## 🔧 Backend Flow (Detailed)

### File Structure:
```
backend/
├── app/
│   ├── main.py              # FastAPI app & routes
│   ├── models.py            # Database models
│   ├── database.py          # Database connection
│   ├── calculator.py        # Fitness calculations
│   ├── workout_generator.py # Workout plan generation
│   └── diet_generator.py    # Diet plan generation
```

### 1. Application Initialization

**File:** `main.py`

```python
# Create FastAPI app
app = FastAPI(title="Fitness AI API")

# Add CORS middleware
app.add_middleware(CORSMiddleware, allow_origins=["*"])

# Startup: Create database tables
@app.on_event("startup")
def startup_event():
    create_tables()
```

### 2. User Registration

**Endpoint:** `POST /users`

**Flow:**
1. Receive user data (email, username, password)
2. Check if user already exists
3. Hash password using SHA-256
4. Create User object
5. Save to database
6. Return user data (without password)

**Code:**
```python
def create_user(user: UserCreate, db: Session):
    # Check existing user
    existing = db.query(User).filter(
        (User.email == user.email) | (User.username == user.username)
    ).first()
    
    if existing:
        raise HTTPException(400, "User already exists")
    
    # Hash password
    hashed = hashlib.sha256(user.password.encode()).hexdigest()
    
    # Create and save
    db_user = User(email=user.email, username=user.username, hashed_password=hashed)
    db.add(db_user)
    db.commit()
    
    return db_user
```

### 3. User Login

**Endpoint:** `POST /login`

**Flow:**
1. Receive credentials (username, password)
2. Find user by username
3. Verify password hash
4. Return user data if valid

### 4. Profile Creation & Metrics

**Endpoint:** `POST /users/{user_id}/profile`

**Flow:**
1. Validate user exists
2. Convert string inputs to enums
3. Calculate fitness metrics:
   - **BMI** = weight / (height/100)²
   - **BMR** = Mifflin-St Jeor equation
   - **TDEE** = BMR × activity multiplier
   - **Target Calories** = TDEE ± adjustment for goal
   - **Macros** = Protein/Carbs/Fats distribution
4. Save profile with metrics
5. Return profile data

**Calculations:**

```python
# BMI
bmi = weight / ((height / 100) ** 2)

# BMR (Mifflin-St Jeor)
if gender == "male":
    bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
else:
    bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161

# TDEE
activity_multipliers = {
    "sedentary": 1.2,
    "lightly_active": 1.375,
    "moderately_active": 1.55,
    "very_active": 1.725,
    "extremely_active": 1.9
}
tdee = bmr * activity_multipliers[activity_level]

# Target Calories
if goal == "lose_weight":
    target = tdee - 500
elif goal == "maintain":
    target = tdee
else:  # gain_muscle
    target = tdee + 300

# Macros (example for weight loss)
protein_grams = (target * 0.40) / 4  # 40% protein, 4 cal/g
carbs_grams = (target * 0.30) / 4    # 30% carbs, 4 cal/g
fats_grams = (target * 0.30) / 9     # 30% fats, 9 cal/g
```

### 5. Workout Generation

**Endpoint:** `POST /users/{user_id}/workout`

**Flow:**
1. Get user profile
2. Determine difficulty based on activity level
3. Select workout template based on goal
4. Create weekly schedule with exercises
5. Save to database as JSON
6. Return workout data

**Logic:**
```python
# Difficulty mapping
difficulty = {
    "sedentary": "Beginner",
    "lightly_active": "Beginner",
    "moderately_active": "Intermediate",
    "very_active": "Advanced",
    "extremely_active": "Advanced"
}[activity_level]

# Goal-based templates
if goal == "lose_weight":
    # Focus: Cardio + HIIT
    schedule = {
        "Monday": {"focus": ["Cardio"], "exercises": [...]},
        "Tuesday": {"focus": ["Core"], "exercises": [...]},
        ...
    }
elif goal == "gain_muscle":
    # Focus: Strength training
    schedule = {
        "Monday": {"focus": ["Chest", "Triceps"], "exercises": [...]},
        ...
    }
```

### 6. Diet Generation

**Endpoint:** `POST /users/{user_id}/diet`

**Flow:**
1. Get user profile
2. Calculate macros
3. Distribute calories across meals (25% breakfast, 35% lunch, 30% dinner, 10% snacks)
4. Generate meal options for each meal type
5. Add meal timing and tips
6. Save to database as JSON
7. Return diet data

---

## 💻 Frontend Flow (Detailed)

### File: `frontend/dashboard.html`

### 1. Page Load

```javascript
const API_URL = 'http://localhost:8486';
let currentUser = null;

window.onload = function() {
    const user = localStorage.getItem('fitnessAI_user');
    if (user) {
        currentUser = JSON.parse(user);
        showDashboard();
    }
}
```

### 2. Registration

```javascript
async function handleRegister(event) {
    event.preventDefault();
    
    const data = {
        email: document.getElementById('register-email').value,
        username: document.getElementById('register-username').value,
        password: document.getElementById('register-password').value
    };
    
    const response = await fetch(`${API_URL}/users`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
    });
    
    if (response.ok) {
        showAlert('success', 'Account created!');
    }
}
```

### 3. Login

```javascript
async function handleLogin(event) {
    event.preventDefault();
    
    const credentials = {
        username: document.getElementById('login-username').value,
        password: document.getElementById('login-password').value
    };
    
    const response = await fetch(`${API_URL}/login`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(credentials)
    });
    
    if (response.ok) {
        const result = await response.json();
        currentUser = result;
        localStorage.setItem('fitnessAI_user', JSON.stringify(result));
        showDashboard();
    }
}
```

### 4. Goal Setting

```javascript
async function handleGoalSubmit(event) {
    event.preventDefault();
    
    // Collect form data
    const formData = {
        age: parseInt(document.getElementById('age').value),
        gender: document.getElementById('gender').value,
        height: parseFloat(document.getElementById('height').value),
        weight: parseFloat(document.getElementById('weight').value),
        activity_level: document.getElementById('activity_level').value,
        goal: document.getElementById('goal').value
    };
    
    // Create profile
    await fetch(`${API_URL}/users/${currentUser.id}/profile`, {
        method: 'POST',
        body: JSON.stringify(formData)
    });
    
    // Get metrics
    const metrics = await fetch(`${API_URL}/metrics/${currentUser.id}`);
    
    // Generate workout
    const workout = await fetch(`${API_URL}/users/${currentUser.id}/workout`, {
        method: 'POST'
    });
    
    // Generate diet
    const diet = await fetch(`${API_URL}/users/${currentUser.id}/diet`, {
        method: 'POST'
    });
    
    // Display results
    displayGoalResults(formData, metrics, workout, diet);
}
```

### 5. View Workout

```javascript
async function loadWorkout() {
    const response = await fetch(`${API_URL}/workout/${currentUser.id}/latest`);
    const data = await response.json();
    displayWorkoutPlan(data.plan);
}

function displayWorkoutPlan(plan) {
    let html = '<div>';
    
    for (const [day, details] of Object.entries(plan.weekly_schedule)) {
        html += `<h4>${day}</h4>`;
        html += `<p>Focus: ${details.focus.join(', ')}</p>`;
        
        details.exercises.forEach(exercise => {
            html += `
                <div>
                    <strong>${exercise.name}</strong>
                    <p>Sets: ${exercise.sets} | Reps: ${exercise.reps}</p>
                </div>
            `;
        });
    }
    
    html += '</div>';
    document.getElementById('workout-result').innerHTML = html;
}
```

### 6. View Diet

```javascript
async function loadDiet() {
    const response = await fetch(`${API_URL}/diet/${currentUser.id}/latest`);
    const data = await response.json();
    displayDietPlan(data.plan);
}

function displayDietPlan(plan) {
    let html = '<div>';
    
    for (const [mealType, details] of Object.entries(plan.meal_plan)) {
        html += `<h4>${mealType}</h4>`;
        html += `<p>Target: ${details.target_calories} cal</p>`;
        
        details.meal_options.forEach((option, idx) => {
            html += `
                <div>
                    <strong>Option ${idx + 1}: ${option.name}</strong>
                    <p>${option.calories} cal | P: ${option.protein}g | 
                       C: ${option.carbs}g | F: ${option.fats}g</p>
                </div>
            `;
        });
    }
    
    html += '</div>';
    document.getElementById('diet-result').innerHTML = html;
}
```

---

## 📊 Data Flow Diagram

```
USER BROWSER
    ↓ (HTTP Requests)
FRONTEND (dashboard.html)
    ↓ (Fetch API)
BACKEND API (main.py)
    ↓ (SQLAlchemy)
DATABASE (SQLite)
    ↑ (Query Results)
BACKEND API
    ↑ (JSON Response)
FRONTEND
    ↑ (Display)
USER BROWSER
```

### Request/Response Flow:

```
1. User Action (Click button)
   ↓
2. JavaScript function triggered
   ↓
3. Fetch API sends HTTP request
   ↓
4. FastAPI route receives request
   ↓
5. Route function processes data
   ↓
6. Database query/update (if needed)
   ↓
7. Calculations performed (if needed)
   ↓
8. JSON response created
   ↓
9. Response sent to frontend
   ↓
10. JavaScript receives response
    ↓
11. DOM updated with new data
    ↓
12. User sees results
```

---

## 🔑 Key Concepts

### 1. Authentication
- **Storage**: SQLite database
- **Password**: SHA-256 hashed
- **Session**: localStorage in browser
- **No JWT**: Simplified for demo

### 2. Fitness Calculations

**BMI (Body Mass Index):**
- Formula: weight(kg) / height(m)²
- Categories: Underweight (<18.5), Normal (18.5-24.9), Overweight (25-29.9), Obese (≥30)

**BMR (Basal Metabolic Rate):**
- Mifflin-St Jeor Equation
- Men: (10×weight) + (6.25×height) - (5×age) + 5
- Women: (10×weight) + (6.25×height) - (5×age) - 161

**TDEE (Total Daily Energy Expenditure):**
- Formula: BMR × Activity Multiplier
- Sedentary: 1.2, Lightly Active: 1.375, Moderately Active: 1.55, Very Active: 1.725, Extremely Active: 1.9

**Target Calories:**
- Weight Loss: TDEE - 500 cal
- Maintenance: TDEE
- Muscle Gain: TDEE + 300 cal

**Macros:**
- Protein: 4 cal/gram
- Carbs: 4 cal/gram
- Fats: 9 cal/gram

### 3. Data Persistence

**Database Tables:**
- `users`: id, email, username, hashed_password, created_at
- `user_profiles`: id, user_id, age, gender, height, weight, activity_level, goal, bmi, bmr, tdee, target_calories
- `workout_plans`: id, user_id, title, description, duration_weeks, difficulty_level, plan_data (JSON), created_at
- `diet_plans`: id, user_id, title, description, daily_calories, protein_grams, carbs_grams, fats_grams, plan_data (JSON), created_at

**JSON Storage:**
- Complex data (workout schedules, meal plans) stored as JSON strings
- Parsed when retrieved
- Allows flexible structure without schema changes

### 4. API Design

**RESTful Endpoints:**
- `POST /users` - Create user
- `POST /login` - Authenticate
- `POST /users/{id}/profile` - Create/update profile
- `GET /metrics/{id}` - Get fitness metrics
- `POST /users/{id}/workout` - Generate workout
- `POST /users/{id}/diet` - Generate diet
- `GET /workout/{id}/latest` - Get latest workout
- `GET /diet/{id}/latest` - Get latest diet

**Response Format:**
```json
{
    "id": 1,
    "data": {...},
    "message": "Success"
}
```

---

## 🎯 Summary

The Fitness AI app follows a simple but effective architecture:

1. **Frontend** handles user interaction and display
2. **Backend** processes requests and performs calculations
3. **Database** stores all user data persistently

The flow is straightforward:
- User interacts → Frontend sends request → Backend processes → Database stores/retrieves → Backend responds → Frontend displays

All fitness calculations are based on established formulas (Mifflin-St Jeor for BMR, standard macro distributions, etc.), and the workout/diet generation uses rule-based logic to create personalized plans.

---

**End of Documentation** 📚