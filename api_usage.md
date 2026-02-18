# Farm Equipment Sharing Service API Documentation

Base URL: `http://127.0.0.1:8000`

## Authentication (Hackathon Mode)
Authentication is **disabled**.
- By default, you are logged in as a "Hackathon User" (Role: `OWNER`).
- **Simulate specific user**: Add header `X-User-Phone: <phone_number>`.
    - Owner Example: `X-User-Phone: 9876543210`
    - Renter Example: `X-User-Phone: 9123456780`

---

## 1. Authentication & User

### Register User
Create a new user (Owner or Renter).
- **Endpoint**: `POST /register`
- **Body**:
```json
{
  "name": "John Doe",
  "phone": "9876543210",
  "role": "owner",
  "location": {
    "type": "Point",
    "coordinates": [76.2673, 9.9312]
  },
  "password": "any_password"
}
```

### Get Current User Profile
- **Endpoint**: `GET /users/me`
- **Header (Optional)**: `X-User-Phone: 9876543210`

---

## 2. Equipment Service

### Register Equipment
List a new tractor or tool (Requires user role `owner`).
- **Endpoint**: `POST /uber/equipment/register`
- **Header**: `X-User-Phone: 9876543210` (Must be an owner)
- **Body**:
```json
{
  "equipment_type": "Tractor",
  "description": "Mahindra 575 DI Power Plus",
  "hourly_price": 500,
  "daily_price": 4000,
  "location_lat": 9.9312,
  "location_long": 76.2673,
  "images": ["http://image-url.com/tractor.jpg"]
}
```

### Find Nearby Equipment
Search for available equipment near a location.
- **Endpoint**: `GET /uber/equipment/nearby`
- **Query Params**:
  - `lat`: Latitude (e.g., `9.9312`)
  - `long`: Longitude (e.g., `76.2673`)
  - `radius_km` (optional): Search radius (default `10`)
- **Example**: `/uber/equipment/nearby?lat=9.9312&long=76.2673`

### Get Equipment Details
- **Endpoint**: `GET /uber/equipment/{id}`
- **Path Param**: `id` (The equipment ID returned from search)
- **Note**: The `images` field will contain Base64 encoded strings (Data URIs).

---

## 3. Booking Service

### Create Booking
Book equipment for a specific time range.
- **Endpoint**: `POST /uber/booking/create`
- **Header**: `X-User-Phone: 9123456780` (Renter)
- **Body**:
```json
{
  "equipment_id": "PREVIOUS_EQUIPMENT_ID",
  "start_time": "2023-10-27T10:00:00",
  "end_time": "2023-10-27T14:00:00"
}
```
*Note: Returns 400 error if equipment is already booked for these times.*

### Get My Bookings
List all bookings made by the current user.
- **Endpoint**: `GET /uber/booking`
- **Header**: `X-User-Phone: 9123456780`

### Update Booking Status
Confirm or cancel a booking.
- **Endpoint**: `PATCH /uber/booking/status/{booking_id}`
- **Query Param**: `status` (`confirmed`, `cancelled`, `completed`)
- **Example**: `/uber/booking/status/BOOKING_ID?status=confirmed`

### Create Booking by Mobile (Agent/Offline)
Book equipment using a mobile number. If the user doesn't exist, a **Guest** user is automatically created.
- **Endpoint**: `POST /uber/booking/create-by-mobile`
- **Body**:
```json
{
  "equipment_id": "EQUIPMENT_ID",
  "start_time": "2023-10-27T10:00:00",
  "end_time": "2023-10-27T14:00:00",
  "mobile_number": "9876543210"
}
```

### List All Booked Equipment
List all equipment currently booked (pending or confirmed).
- **Endpoint**: `GET /uber/booking/list-booked`
- **Response**: List of booking objects.

---

## 4. Review Service

### Add Review
Rate equipment after a completed booking.
- **Endpoint**: `POST /uber/review/add`
- **Body**:
```json
{
  "booking_id": "COMPLETED_BOOKING_ID",
  "rating": 5,
  "review_text": "Excellent service and machine condition."
}
```
