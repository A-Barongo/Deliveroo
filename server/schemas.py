# this file has schemas for turning database stuff to json and checking data
# we use marshmallow for this
from marshmallow import Schema, fields

# this is the schema for parcel
class ParcelSchema(Schema):
    id = fields.Integer(dump_only=True) # id only when sending data
    description = fields.String() # what is in the parcel
    weight = fields.Float() # how heavy
    status = fields.String(dump_only=True) # status only when sending
    sender_name = fields.String() # who sends
    sender_phone_number = fields.String() # sender phone
    pickup_location_text = fields.String() # where to pick up
    destination_location_text = fields.String() # where to deliver
    pick_up_longitude = fields.Float() # pickup longitude
    pick_up_latitude = fields.Float() # pickup latitude
    destination_longitude = fields.Float() # destination longitude
    destination_latitude = fields.Float() # destination latitude
    current_location_longitude = fields.Float(allow_none=True) # where is parcel now longitude
    current_location_latitude = fields.Float(allow_none=True) # where is parcel now latitude
    distance = fields.Float(allow_none=True) # how far
    cost = fields.Float(dump_only=True) # how much to deliver only when sending
    created_at = fields.DateTime(dump_only=True) # when made only when sending
    updated_at = fields.DateTime(dump_only=True) # when changed only when sending
    recipient_name = fields.String() # who gets parcel
    recipient_phone_number = fields.String() # recipient phone
    courier_id = fields.Integer(allow_none=True) # who delivers
    user_id = fields.Integer(dump_only=True) # who owns parcel only when sending 