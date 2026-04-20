# Slot Booking System Documentation

## Overview
The Fitness AI Slot Booking System allows users to book yoga or gym slots for specific date ranges and time periods (morning/evening). Admins can approve or reject booking requests with proper reasons.

## Features

### User Features
1. **Book Slots**: Users can book slots by providing:
   - Username and Email
   - Membership Type (Yoga/Gym)
   - Date Range (From - To)
   - Time Slot (Morning/Evening)

2. **View Booking Status**: Users can check their booking status using their email
3. **Cancel Bookings**: Users can cancel pending bookings

### Admin Features
1. **View All Bookings**: See all bookings with filtering options
2. **View Pending Bookings**: Focus on bookings awaiting approval
3. **Approve Bookings**: Accept booking requests
4. **Reject Bookings**: Decline bookings with a mandatory rejection reason

## Database Schema

### TimeSlot Table
```sql
- id: Primary Key
- membership_type: ENUM('yoga', 'gym')
- date: DateTime
- time_slot: VARCHAR ('morning' or 'evening')
- start_time: VARCHAR (HH:MM format)
- end_time: VARCHAR (HH:MM format)
- capacity: INTEGER (default: 10)
- booked_count: INTEGER (default: 0)
- is_available: INTEGER (1 or 0)
- created_at: DateTime
```

### SlotBooking Table
```sql
- id: Primary Key
- user_id: Foreign Key (nullable for guest bookings)
- username: VARCHAR (required)
- email: VARCHAR (required)
- membership_type: ENUM('yoga', 'gym')
- date_from: DateTime (start date of booking period)
- date_to: DateTime (end date of booking period)
- time_slot: VARCHAR ('morning' or 'evening')
- status: ENUM('pending', 'approved', 'rejected', 'cancelled')
- rejection_reason: TEXT (nullable)
- approved_by: Foreign Key to User (admin)
- approved_at: DateTime
- created_at: DateTime
- updated_at: DateTime
```

## API Endpoints

### User Endpoints

#### 1. Create Booking
**POST** `/bookings`

Request Body:
```json
{
  "username": "John Doe",
  "email": "john@example.com",
  "membership_type": "yoga",
  "date_from": "2026-04-25",
  "date_to": "2026-05-25",
  "time_slot": "morning"
}
```

Response:
```json
{
  "id": 1,
  "username": "John Doe",
  "email": "john@example.com",
  "membership_type": "yoga",
  "date_from": "2026-04-25T00:00:00",
  "date_to": "2026-05-25T00:00:00",
  "time_slot": "morning",
  "status": "pending",
  "rejection_reason": null,
  "created_at": "2026-04-20T09:00:00"
}
```

#### 2. Get Bookings by Email
**GET** `/bookings/email/{email}`

Example: `/bookings/email/john@example.com`

Response: Array of booking objects

#### 3. Get Booking Status
**GET** `/bookings/status/{booking_id}`

Example: `/bookings/status/1`

Response: Single booking object

#### 4. Cancel Booking
**DELETE** `/bookings/{booking_id}?email={email}`

Example: `/bookings/1?email=john@example.com`

Response:
```json
{
  "message": "Booking cancelled successfully"
}
```

### Admin Endpoints

#### 1. Get All Bookings
**GET** `/admin/bookings?status_filter={status}&membership_type={type}`

Query Parameters (optional):
- `status_filter`: pending, approved, rejected, cancelled
- `membership_type`: yoga, gym

Response: Array of booking objects

#### 2. Get Pending Bookings
**GET** `/admin/bookings/pending`

Response: Array of pending booking objects

#### 3. Approve/Reject Booking
**POST** `/admin/bookings/approve?admin_id={admin_id}`

Request Body (Approve):
```json
{
  "booking_id": 1,
  "approved": true
}
```

Request Body (Reject):
```json
{
  "booking_id": 1,
  "approved": false,
  "rejection_reason": "Slot fully booked for this period"
}
```

Response:
```json
{
  "message": "Booking approved successfully",
  "booking": {
    "id": 1,
    "username": "John Doe",
    "email": "john@example.com",
    "status": "approved",
    "rejection_reason": null
  }
}
```

### Time Slot Management (Admin)

#### 1. Create Time Slot
**POST** `/admin/time-slots`

Request Body:
```json
{
  "membership_type": "yoga",
  "date": "2026-04-25",
  "time_slot": "morning",
  "start_time": "06:00",
  "end_time": "12:00",
  "capacity": 10
}
```

#### 2. Get Available Time Slots
**GET** `/time-slots?membership_type={type}&date={date}&time_slot={slot}`

Query Parameters (all optional):
- `membership_type`: yoga, gym
- `date`: YYYY-MM-DD format
- `time_slot`: morning, evening

## Booking Status Flow

```
PENDING → APPROVED (by admin)
        → REJECTED (by admin with reason)
        → CANCELLED (by user, only if pending)
```

## Business Rules

1. **Date Validation**:
   - `date_from` must be today or future date
   - `date_to` must be >= `date_from`

2. **Overlap Prevention**:
   - Users cannot book overlapping date ranges for the same membership type and time slot

3. **Status Restrictions**:
   - Only PENDING bookings can be cancelled by users
   - Only PENDING bookings can be approved/rejected by admins

4. **Rejection Reason**:
   - Mandatory when rejecting a booking

5. **Time Slots**:
   - Morning: 6:00 AM - 12:00 PM
   - Evening: 4:00 PM - 9:00 PM

## Dashboard Usage

### Access the Dashboard
Open `slot-booking-dashboard.html` in your browser after starting the backend server.

### For Users:
1. **Book a Slot**:
   - Go to "Book Slot" tab
   - Fill in your details (username, email)
   - Select membership type and time slot
   - Choose date range
   - Submit the form

2. **Check Your Bookings**:
   - Go to "My Bookings" tab
   - Enter your email
   - Click "Search"
   - View all your bookings with status

3. **Cancel a Booking**:
   - In "My Bookings", find the pending booking
   - Click "Cancel Booking" button

### For Admins:
1. **View Pending Requests**:
   - Go to "Admin Panel" tab
   - Enter your Admin ID
   - Click "Refresh Pending"

2. **Approve a Booking**:
   - Click "✅ Approve" button on the booking card

3. **Reject a Booking**:
   - Click "❌ Reject" button
   - Enter rejection reason in the prompt
   - Confirm rejection

4. **View All Bookings**:
   - Click "View All" button to see all bookings regardless of status

## Testing the System

### 1. Start the Backend Server
```bash
cd Fitness-AI-APP/backend
python -m uvicorn app.main:app --reload --port 8486
```

### 2. Open the Dashboard
Open `Fitness-AI-APP/frontend/slot-booking-dashboard.html` in your browser

### 3. Test User Flow
1. Create a booking with your details
2. Note the booking ID from the success message
3. Go to "My Bookings" and search with your email
4. Verify the booking appears with "PENDING" status

### 4. Test Admin Flow
1. Go to "Admin Panel"
2. Enter Admin ID (use 1 for testing)
3. Click "Refresh Pending"
4. Approve or reject the booking
5. Verify status changes

### 5. Test Cancellation
1. Create a new booking
2. In "My Bookings", find the pending booking
3. Click "Cancel Booking"
4. Verify status changes to "CANCELLED"

## Error Handling

The system handles various error scenarios:

1. **Invalid Date Range**: Returns error if date_to < date_from
2. **Overlapping Bookings**: Prevents double booking for same period
3. **Invalid Email**: Validates email format
4. **Missing Required Fields**: Returns validation errors
5. **Invalid Status Transitions**: Prevents invalid status changes
6. **Unauthorized Actions**: Validates admin permissions

## API Response Codes

- `200 OK`: Successful GET request
- `201 Created`: Successful POST request (resource created)
- `400 Bad Request`: Invalid input or business rule violation
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

## Future Enhancements

1. **Authentication**: Add JWT-based authentication
2. **Email Notifications**: Send emails on booking status changes
3. **Capacity Management**: Real-time slot availability tracking
4. **Payment Integration**: Add payment processing for bookings
5. **Recurring Bookings**: Support for weekly/monthly recurring slots
6. **Waitlist**: Queue system for fully booked slots
7. **Calendar View**: Visual calendar for slot selection
8. **Mobile App**: Native mobile application

## Support

For issues or questions:
- Check the API documentation at `http://localhost:8486/docs`
- Review error messages in the dashboard
- Check backend logs for detailed error information

---

**Made with Bob - Fitness AI Slot Booking System**