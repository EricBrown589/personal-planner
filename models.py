"""
This module defines the SQLAlchemy database models for the Personal Planner.

It includes the following models:
- Task: Represents a to-do item, which can be recurring.
- Event: Represents a scheduled event with a start and end time.
- JournalEntry: Represents a generic log entry for things like meals or moods.
"""
from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class Task(db.Model):
    """Represents a to-do item or task."""

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    is_recurring = db.Column(db.Boolean, default=False)
    is_completed = db.Column(db.Boolean, default=False)
    due_date = db.Column(db.Date, nullable=True)
    start_time = db.Column(db.DateTime, nullable=True)
    end_time = db.Column(db.DateTime, nullable=True)
    time_tracked_seconds = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    recurrence_type = db.Column(db.String(50), nullable=True)  # e.g., 'daily', 'weekly'
    # A unique ID to group recurring tasks together.
    recurrence_group_id = db.Column(db.String(36), nullable=True, index=True)

    def to_dict(self):
        """Return a dictionary representation of the Task object."""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'is_recurring': self.is_recurring,
            'recurrence_type': self.recurrence_type,
            'is_completed': self.is_completed,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'time_tracked_seconds': self.time_tracked_seconds,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'recurrence_group_id': self.recurrence_group_id
        }


class Event(db.Model):
    """Represents a scheduled event with a specific start and end time."""

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=True)  # Events can have a start time without a defined end time.
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        """Return a dictionary representation of the Event object."""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,  # Gracefully handle nullable end_time.
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class JournalEntry(db.Model):
    """Represents a log entry, such as for meals, sleep, or mood."""

    id = db.Column(db.Integer, primary_key=True)
    entry_type = db.Column(db.String(50), nullable=False)  # 'meal', 'sleep', 'mood'
    content = db.Column(db.JSON, nullable=False)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    def to_dict(self):
        """Return a dictionary representation of the JournalEntry object."""
        return {
            'id': self.id,
            'entry_type': self.entry_type,
            'content': self.content,
            'timestamp': self.timestamp.isoformat()
        }
