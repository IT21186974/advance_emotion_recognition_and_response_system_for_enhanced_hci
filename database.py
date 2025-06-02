from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
# import datetime
from typing import List
from datetime import datetime, time
from sqlalchemy import func, cast, Date

engine = create_engine("sqlite:///chat.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    sender = Column(String)
    text = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

    # New columns to store detected emotion and distortion
    emotion = Column(String, nullable=True)
    distortion = Column(String, nullable=True)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_user(username):
    session = SessionLocal()
    try:
        user = session.query(User).filter(User.username == username).first()
        return user
    except Exception as e:
        print(f"DB error in get_user: {e}")
        return None
    finally:
        session.close()

def create_user(username, hashed_password):
    session = SessionLocal()
    try:
        user = User(username=username, hashed_password=hashed_password)
        session.add(user)
        session.commit()
    except Exception as e:
        print(f"DB error in create_user: {e}")
    finally:
        session.close()

# Updated save_message to save emotion and distortion
def save_message(username, sender, text, emotion=None, distortion=None):
    session = SessionLocal()
    try:
        msg = ChatMessage(
            username=username,
            sender=sender,
            text=text,
            emotion=emotion,
            distortion=distortion
        )
        session.add(msg)
        session.commit()
    except Exception as e:
        print(f"DB error in save_message: {e}")
    finally:
        session.close()

def get_messages(username):
    session = SessionLocal()
    try:
        msgs = session.query(ChatMessage).filter(ChatMessage.username == username).order_by(ChatMessage.timestamp).all()
        return msgs
    except Exception as e:
        print(f"DB error in get_messages: {e}")
        return []
    finally:
        session.close()


#functions for emotional dependency

#For total prompts per user
def get_total_user_prompts(username):
    session = SessionLocal()
    try:
        count = session.query(ChatMessage).filter(
            ChatMessage.username == username,
            ChatMessage.sender == "user"
        ).count()
        return count
    except Exception as e:
        print(f"DB error in get_total_user_prompts: {e}")
        return 0
    finally:
        session.close()

#For day wise total prompts per user visualization
def get_daily_user_prompts(username):
    session = SessionLocal()
    try:
        # Use func.date to extract date part in SQLite
        results = (
            session.query(
                func.date(ChatMessage.timestamp).label("date"),
                func.count(ChatMessage.id).label("prompt_count")
            )
            .filter(ChatMessage.username == username, ChatMessage.sender == "user")
            .group_by(func.date(ChatMessage.timestamp))
            .order_by(func.date(ChatMessage.timestamp))
            .all()
        )
        
        return [{"date": r.date, "prompt_count": r.prompt_count} for r in results]
    except Exception as e:
        print(f"DB error in get_daily_user_prompts: {e}")
        return []
    finally:
        session.close()


#Late night prompts count
def get_late_night_conversations(username):
    session = SessionLocal()
    try:
        # Filter messages by username and timestamp time after 22:00 (10 PM)
        late_msgs_count = session.query(func.count(ChatMessage.id)) \
            .filter(ChatMessage.username == username) \
            .filter(func.strftime('%H', ChatMessage.timestamp) >= '22') \
            .scalar()
        return late_msgs_count or 0
    except Exception as e:
        print(f"DB error in get_late_night_conversations: {e}")
        return 0
    finally:
        session.close()



# Max consecutive days
def max_consecutive_days(dates: List[str]) -> int:
    if not dates:
        return 0
    
    # Convert strings to datetime.date objects
    date_objs = [datetime.strptime(date_str, "%Y-%m-%d").date() for date_str in dates]
    
    # Sort dates
    sorted_dates = sorted(date_objs)
    
    max_streak = 1
    current_streak = 1
    
    for i in range(1, len(sorted_dates)):
        delta = (sorted_dates[i] - sorted_dates[i - 1]).days
        if delta == 1:
            current_streak += 1
        elif delta > 1:
            max_streak = max(max_streak, current_streak)
            current_streak = 1
    
    max_streak = max(max_streak, current_streak)
    return max_streak



# Has late night negative emotions

negative_emotions = ['anger', 'sadness', 'fear', 'disapproval', 'disgust', 'disappointment', 'remorse']

def has_late_night_negative(messages: List[dict]) -> int:
    """
    Returns 1 if the user has at least one message sent after 10 PM with a negative emotion.
    Otherwise, returns 0.

    Args:
        messages (List[dict]): List of message dicts, each with keys:
            - 'timestamp' (datetime)
            - 'emotion' (str)

    Returns:
        int: 1 if condition met, else 0
    """
    late_night_threshold = time(22, 0)  # 10 PM

    for msg in messages:
        timestamp = msg.get('timestamp')
        emotion = msg.get('emotion', '').lower()

        if not timestamp or not emotion:
            continue

        if timestamp.time() >= late_night_threshold and emotion in negative_emotions:
            return 1

    return 0

def total_negative_emotion_count(messages: List[dict]) -> int:
    """
    Counts total messages with negative emotions from a list of messages.

    Args:
        messages (List[dict]): List of message dicts, each with key:
            - 'emotion' (str)

    Returns:
        int: Number of messages with negative emotions
    """
    count = 0
    print(messages)
    for msg in messages:
        emotion = msg.get('emotion', '').lower()
        if emotion in negative_emotions:
            count += 1
    return count
