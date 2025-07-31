"""Real-time tracking service for Deliveroo parcels."""
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from server.models import Parcel, db
from server.services.sendgrid_service import SendGridService

class TrackingService:
    """Simulates real-time parcel tracking."""
    
    def __init__(self, app=None):
        self.app = app
        self.sendgrid_service = SendGridService()
        self.tracking_threads = {}
        self.location_sequence = {
            'pending': [
                'Warehouse - Sorting Center',
                'Loading Dock - Ready for Pickup',
                'Courier Assigned - En Route to Pickup'
            ],
            'in_transit': [
                'Picked up from sender',
                'In transit - Nairobi Central',
                'In transit - Thika Road',
                'In transit - Juja Junction',
                'In transit - Thika Town Center',
                'Approaching destination',
                'Out for delivery'
            ],
            'delivered': [
                'Delivered to recipient'
            ]
        }
        
    def start_tracking(self, parcel_id: int):
        """Start tracking a parcel with simulated movement."""
        if not self.app:
            print(f"Warning: Tracking service not initialized with app context for parcel {parcel_id}")
            return
            
        if parcel_id in self.tracking_threads:
            return  # Already tracking
            
        thread = threading.Thread(target=self._track_parcel, args=(parcel_id,))
        thread.daemon = True
        thread.start()
        self.tracking_threads[parcel_id] = thread
        
    def _track_parcel(self, parcel_id: int):
        """Simulate parcel movement through different locations."""
        # Create application context for database access
        with self.app.app_context():
            parcel = Parcel.query.get(parcel_id)
            if not parcel:
                return
                
            # Get user for email notifications
            user = parcel.user
            
            # Simulate movement through locations
            for status, locations in self.location_sequence.items():
                if status == 'pending':
                    # Quick updates for pending status
                    for location in locations:
                        self._update_location(parcel, location, status, user)
                        time.sleep(30)  # 30 seconds between updates
                        
                elif status == 'in_transit':
                    # Slower updates for in-transit
                    for location in locations:
                        self._update_location(parcel, location, status, user)
                        time.sleep(120)  # 2 minutes between updates
                        
                elif status == 'delivered':
                    # Final delivery
                    self._update_location(parcel, locations[0], status, user)
                
    def _update_location(self, parcel: Parcel, location: str, status: str, user):
        """Update parcel location and send notification."""
        try:
            with self.app.app_context():
                old_location = parcel.current_location
                old_status = parcel.status
                
                # Update parcel
                parcel.current_location = location
                parcel.status = status
                parcel.updated_at = datetime.now()
                
                # Save to database
                db.session.commit()
                
                # Send email notification if status changed (disabled due to SendGrid limits)
                # if old_status != status and user:
                #     try:
                #         self.sendgrid_service.send_status_update_email(
                #             user.email, 
                #             parcel.to_dict(), 
                #             old_status, 
                #             status
                #         )
                #     except Exception as e:
                #         print(f"Email notification failed: {str(e)}")
                
                # Send location update email (disabled due to SendGrid limits)
                # if old_location != location and user:
                #     try:
                #         self.sendgrid_service.send_location_update_email(
                #             user.email,
                #             parcel.to_dict(),
                #             old_location or 'Not set',
                #             location
                #         )
                #     except Exception as e:
                #         print(f"Email notification failed: {str(e)}")
                    
        except Exception as e:
            print(f"Error updating parcel {parcel.id}: {str(e)}")
            
    def get_tracking_info(self, parcel_id: int) -> Dict:
        """Get current tracking information for a parcel."""
        parcel = Parcel.query.get(parcel_id)
        if not parcel:
            return {}
            
        # Calculate estimated delivery time
        estimated_delivery = self._calculate_estimated_delivery(parcel)
        
        return {
            'parcel_id': parcel.id,
            'current_location': parcel.current_location,
            'status': parcel.status,
            'estimated_delivery': estimated_delivery,
            'is_tracking': parcel_id in self.tracking_threads,
            'last_updated': parcel.updated_at.isoformat() if parcel.updated_at else None
        }
        
    def _calculate_estimated_delivery(self, parcel: Parcel) -> str:
        """Calculate estimated delivery time based on current status."""
        now = datetime.now()
        
        if parcel.status == 'pending':
            return (now + timedelta(hours=2)).strftime('%Y-%m-%d %H:%M')
        elif parcel.status == 'in_transit':
            return (now + timedelta(hours=1)).strftime('%Y-%m-%d %H:%M')
        elif parcel.status == 'delivered':
            return 'Delivered'
        else:
            return (now + timedelta(hours=3)).strftime('%Y-%m-%d %H:%M')
            
    def stop_tracking(self, parcel_id: int):
        """Stop tracking a parcel."""
        if parcel_id in self.tracking_threads:
            del self.tracking_threads[parcel_id]

# Global tracking service instance
tracking_service = None

def init_tracking_service(app):
    """Initialize the global tracking service with the Flask app."""
    global tracking_service
    tracking_service = TrackingService(app) 