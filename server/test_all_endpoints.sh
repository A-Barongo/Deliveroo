#!/bin/bash

# Test Deliveroo API endpoints on localhost:5000
# NOTE: Insert your JWT tokens where indicated for protected endpoints.

BASE_URL="http://127.0.0.1:5000"

# 1. Signup
printf "\n--- Signup ---\n"
curl -s -X POST $BASE_URL/signup \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"testpass","phone_number":"1234567890"}' | jq

# 2. Login
printf "\n--- Login ---\n"
LOGIN_RESPONSE=$(curl -s -X POST $BASE_URL/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"testpass"}')
echo "$LOGIN_RESPONSE" | jq
ACCESS_TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.access_token')

# 3. Profile (requires JWT)
printf "\n--- Profile ---\n"
curl -s -X GET $BASE_URL/profile \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq

# 4. Logout (requires JWT)
printf "\n--- Logout ---\n"
curl -s -X POST $BASE_URL/logout \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq

# 5. List Parcels
printf "\n--- List Parcels ---\n"
curl -s -X GET $BASE_URL/parcels | jq

# 6. Create Parcel
printf "\n--- Create Parcel ---\n"
CREATE_PARCEL_RESPONSE=$(curl -s -X POST $BASE_URL/parcels \
  -H "Content-Type: application/json" \
  -d '{"description":"Box","weight":2.5,"sender_name":"Alice","sender_phone_number":"1234567890","pickup_location_text":"Origin","destination_location_text":"Destination","pick_up_longitude":36.8,"pick_up_latitude":-1.2,"destination_longitude":36.9,"destination_latitude":-1.3,"recipient_name":"Bob","recipient_phone_number":"9876543210","user_id":1}')
echo "$CREATE_PARCEL_RESPONSE" | jq
PARCEL_ID=$(echo "$CREATE_PARCEL_RESPONSE" | jq -r '.id')

# 7. Get Parcel by ID
printf "\n--- Get Parcel by ID ---\n"
curl -s -X GET $BASE_URL/parcels/$PARCEL_ID | jq

# 8. Cancel Parcel (requires JWT)
printf "\n--- Cancel Parcel ---\n"
curl -s -X PATCH $BASE_URL/parcels/$PARCEL_ID/cancel \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq

# 9. Update Parcel Destination
printf "\n--- Update Parcel Destination ---\n"
curl -s -X PATCH $BASE_URL/parcels/$PARCEL_ID/destination \
  -H "Content-Type: application/json" \
  -d '{"destination_location_text":"New Address","destination_longitude":37.0,"destination_latitude":-1.4}' | jq

# 10. Update Parcel Status
printf "\n--- Update Parcel Status ---\n"
curl -s -X PATCH $BASE_URL/parcels/$PARCEL_ID/status \
  -H "Content-Type: application/json" \
  -d '{"status":"in-transit"}' | jq

# --- Admin Endpoints ---
# NOTE: You must manually set ADMIN_ACCESS_TOKEN below for admin endpoints.
ADMIN_ACCESS_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc1Mjc4NDA0MSwianRpIjoiZGQ3YjE5ZjgtMWNjYy00OThmLTgzNzEtMTI3NmE2MjMyZTI5IiwidHlwZSI6ImFjY2VzcyIsInN1YiI6MTIsIm5iZiI6MTc1Mjc4NDA0MSwiY3NyZiI6IjEwM2U5MWEwLWU0MjctNDNjYy05YzY1LTU5OWM4NGQ0MzQwNSIsImV4cCI6MTc1Mjc4NzY0MX0.qpchiZVTrymiVGFx_tX-5cfy3SJz37WpCdZciyji7GY"

# 11. List All Parcels (admin)
printf "\n--- Admin: List All Parcels ---\n"
curl -s -X GET $BASE_URL/admin/parcels \
  -H "Authorization: Bearer $ADMIN_ACCESS_TOKEN" | jq

# 12. Update Parcel Status (admin)
printf "\n--- Admin: Update Parcel Status ---\n"
curl -s -X PATCH $BASE_URL/admin/parcels/$PARCEL_ID/status \
  -H "Authorization: Bearer $ADMIN_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status":"delivered"}' | jq

# 13. Update Parcel Location (admin)
printf "\n--- Admin: Update Parcel Location ---\n"
curl -s -X PATCH $BASE_URL/admin/parcels/$PARCEL_ID/location \
  -H "Authorization: Bearer $ADMIN_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"present_location":"Warehouse"}' | jq

# 14. List All Parcel Histories (admin)
printf "\n--- Admin: List All Parcel Histories ---\n"
curl -s -X GET $BASE_URL/admin/histories \
  -H "Authorization: Bearer $ADMIN_ACCESS_TOKEN" | jq

# 15. Get Specific Parcel History (admin)
printf "\n--- Admin: Get Specific Parcel History ---\n"
curl -s -X GET $BASE_URL/admin/histories/1 \
  -H "Authorization: Bearer $ADMIN_ACCESS_TOKEN" | jq

printf "\nAll endpoint tests complete.\n" 