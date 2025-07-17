from flask_mail import Message

class EmailService:
    def __init__(self, mail):
        self.mail = mail

    def send_created(self, parcel):
        msg = Message(
            subject=f"Parcel #{parcel.id} Created",
            recipients=[parcel.recipient_email],
            body=f"""
            New parcel created:
            ID: {parcel.id}
            From: {parcel.pickup}
            To: {parcel.destination}
            Price: ${parcel.price:.2f}
            """
        )
        self.mail.send(msg)