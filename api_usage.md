# Farmora Backend API Documentation

## Authentication Endpoints

### 1. Register User
Registers a new user with just their mobile number.
- **URL**: `/register`
- **Method**: `POST`
- **Body**:
  ```json
  {
    "mobile_number": "1234567890"
  }
  ```
- **Response**: User object

### 2. Update Profile
Update user profile details. Requires `X-User-Phone` header.
- **URL**: `/updateprofile`
- **Method**: `POST`
- **Body**:
  ```json
  {
    "name": "Farmer John",
    "acres_land": 5.5,
    "years_experience": 10
  }
  ```
- **Response**: Updated User object

### 3. Update Crops
Update the user's current crop rotation. Requires `X-User-Phone` header.
- **URL**: `/updatecrops`
- **Method**: `POST`
- **Body**:
  ```json
  {
    "crops_rotation": ["Wheat", "Rice", "Corn"]
  }
  ```
- **Response**: Updated User object

### 4. Get Current User
Get details of the currently authenticated user. Requires `X-User-Phone` header.
- **URL**: `/users/me`
- **Method**: `GET`
- **Response**: User object

---

## Harvest Prediction Endpoints

### 1. Predict Harvest
Get harvest recommendations based on crop data and weather.
- **URL**: `/api/harvest-predict`
- **Method**: `POST`
- **Body**:
  ```json
  {
    "crop_type": "Wheat",
    "sowing_date": "2023-11-01",
    "location": "Punjab, India" 
  }
  ```
  *(Note: Location can be city name or "lat,long")*
- **Response**: Harvest prediction and weather risk analysis

---

## Equipment Endpoints (Uber-for-Tractors)
Base URL Prefix: `/uber/equipment`

### 1. Register Equipment (Authenticated)
Register new equipment. Requires `X-User-Phone` header (Owner only).
- **URL**: `/uber/equipment/register`
- **Method**: `POST`
- **Body**:
  ```json
  {
    "name": "John Deere 5050",
    "equipment_type": "Tractor",
    "description": "50HP Tractor with Rotavator",
    "hourly_price": 500,
    "daily_price": 4000,
    "location_lat": 30.7333,
    "location_long": 76.7794,
    "images": ["url1", "url2"]
  }
  ```

### 2. Register Equipment (By Mobile)
Register equipment for guest/quick users.
- **URL**: `/uber/equipment/register-by-mobile`
- **Method**: `POST`
- **Body**: Similar to register but includes `mobile_number`.

### 3. Get Nearby Equipment
Find equipment near a location.
- **URL**: `/uber/equipment/nearby`
- **Method**: `GET`
- **Query Params**:
  - `lat`: Latitude
  - `long`: Longitude
  - `radius_km`: Search radius (default 10)
  - `equipment_type`: Filter by type (optional)
- **Response**: List of equipment

### 4. Get My Listings
Get equipment listed by a specific mobile number.
- **URL**: `/uber/equipment/my-listings`
- **Method**: `GET`
- **Query Params**:
  - `mobile_number`: User's mobile number
- **Response**: List of equipment

### 5. Get Equipment Details
- **URL**: `/uber/equipment/{id}`
- **Method**: `GET`

### 6. Delete Equipment
Delete a listing.
- **URL**: `/uber/equipment/{id}`
- **Method**: `DELETE`
- **Query Params**:
  - `mobile_number`: Owner's mobile number for verification

---

## Booking Endpoints
Base URL Prefix: `/uber/booking`

### 1. Create Booking (Authenticated)
Book equipment. Requires `X-User-Phone` header.
- **URL**: `/uber/booking/create`
- **Method**: `POST`
- **Body**:
  ```json
  {
    "equipment_id": "equipment_obj_id",
    "start_time": "2023-12-01T08:00:00",
    "end_time": "2023-12-01T17:00:00"
  }
  ```

### 2. Create Booking (By Mobile)
Book equipment as a guest/quick user.
- **URL**: `/uber/booking/create-by-mobile`
- **Method**: `POST`
- **Body**: Similar to create but includes `mobile_number`.

### 3. Get User Bookings
Get bookings for the authenticated user.
- **URL**: `/uber/booking/user`
- **Method**: `GET`
- **Response**: List of bookings

### 4. Update Booking Status
Update status (e.g., cancel, confirm).
- **URL**: `/uber/booking/status/{booking_id}`
- **Method**: `PATCH`
- **Query Params**:
  - `status`: New status (pending, confirmed, completed, cancelled)

### 5. Get Incoming Bookings (Owner)
Get bookings for equipment owned by a user.
- **URL**: `/uber/booking/incoming`
- **Method**: `GET`
- **Query Params**:
  - `mobile_number`: Owner's mobile number

---

## Review Endpoints
Base URL Prefix: `/uber/review`

### 1. Add Review
Add a review for a completed booking.
- **URL**: `/uber/review/add`
- **Method**: `POST`
- **Body**:
  ```json
  {
    "booking_id": "booking_obj_id",
    "rating": 5,
    "comment": "Great machine!"
  }
  ```
