from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

db=SQLAlchemy()
class ChatMessage(db.Model):
    __tablename__ ="chat_messages"
    id = db.Column(db.Integer, primary_key=True)
    user_message = db.Column(db.Text, nullable=False)
    bot_response = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    def to_dict(self):
        return{
            'id':self.id,
            'user_message':self.user_message,
            'bot_response':self.bot_response,
            'timestamp':self.timestamp.isoformat()
        }