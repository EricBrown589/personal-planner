"""
This module defines the main Flask application for the Personal Planner.

It sets up the Flask app, configures CORS and the database, and defines all
the RESTful API endpoints for managing tasks, events, and journal entries.
The endpoints support standard CRUD (Create, Read, Update, Delete) operations.
"""
import uuid
from datetime import datetime, timezone, timedelta
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_migrate import Migrate

from config import Config
from models import db, Task, Event, JournalEntry

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)
db.init_app(app)
migrate = Migrate(app, db)


# --- Helper Functions ---
def parse_date(date_str):
    """
    Parse a string into a date object.

    Handles both ISO formats with 'Z' and 'YYYY-MM-DD' format.

    Args:
        date_str (str): The date string to parse.

    Returns:
        datetime.date or None: The parsed date object, or None if input is empty.
    """
    if not date_str:
        return None
    try:
        return datetime.fromisoformat(date_str.replace('Z', '+00:00')).date()
    except ValueError:
        return datetime.strptime(date_str, '%Y-%m-%d').date()


def parse_datetime(datetime_str):
    """
    Parse an ISO 8601 datetime string into a datetime object.

    Args:
        datetime_str (str): The datetime string, potentially with 'Z' for UTC.

    Returns:
        datetime.datetime or None: The parsed datetime object, or None if input is empty.
    """
    if not datetime_str:
        return None
    return datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))


def _create_recurring_tasks(original_task):
    """
    Generate future instances of a recurring task.

    Based on the original task's recurrence_type, this function creates
    and adds new task instances to the database session.

    Args:
        original_task (Task): The first task in the recurring series.
    """
    if not original_task.is_recurring or not original_task.recurrence_type:
        return

    # Use a dictionary to avoid manually copying attributes
    task_data = original_task.to_dict()
    # Remove fields that should not be copied or will be recalculated for new tasks
    task_data.pop('id', None)
    task_data.pop('due_date', None)
    task_data.pop('is_completed', None)
    task_data.pop('time_tracked_seconds', None)
    task_data.pop('created_at', None)

    # Define recurrence periods for better clarity and maintainability
    recurrence_periods = {
        'daily': {'delta': timedelta(days=1), 'count': 90},  # Approx 3 months
        'weekly': {'delta': timedelta(weeks=1), 'count': 12},  # Approx 3 months
    }

    if config := recurrence_periods.get(original_task.recurrence_type):
        for i in range(1, config['count'] + 1):
            new_due_date = original_task.due_date + (config['delta'] * i)
            db.session.add(Task(**task_data, due_date=new_due_date))


# --- API Endpoints ---
@app.route('/tasks', methods=['GET'])
def get_tasks():
    """Retrieve a list of all tasks.

    Returns:
        Response: A JSON response containing a list of task objects.
    """
    tasks = Task.query.all()
    return jsonify([task.to_dict() for task in tasks])


@app.route('/tasks', methods=['POST'])
def create_task():
    """
    Create a new task from a JSON payload.

    Handles both single and recurring tasks. If 'is_recurring' is true,
    it generates future instances based on the 'recurrence_type'.

    Request Body (JSON):
        - title (str): The title of the task.
        - due_date (str): The due date in 'YYYY-MM-DD' or ISO format.
        - (and other optional Task fields)

    Returns:
        Response: The new task object with a 201 status code, or an error with a 400 status.
    """
    data = request.json
    due_date = parse_date(data.get('due_date'))
    if not data.get('title') or not due_date:
        return jsonify({'error': 'Title and due_date are required'}), 400

    is_recurring = data.get('is_recurring', False)
    recurrence_group_id = str(uuid.uuid4()) if is_recurring else None

    # Create the main task object
    new_task = Task(
        title=data.get('title'),
        description=data.get('description'),
        is_recurring=is_recurring,
        recurrence_type=data.get('recurrence_type'),
        recurrence_group_id=recurrence_group_id,
        due_date=due_date,
        start_time=parse_datetime(data.get('start_time')),
        end_time=parse_datetime(data.get('end_time'))
    )
    db.session.add(new_task)

    # Flush the session to the database. This populates new_task with db-generated
    # values like 'id' and 'created_at' before we use it.
    db.session.flush()

    # If the task is recurring, generate the future instances.
    _create_recurring_tasks(new_task)
    db.session.commit()
    return jsonify(new_task.to_dict()), 201


@app.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    """Update an existing task's details from a JSON payload.

    This endpoint is for modifying mutable fields of a single task instance,
    such as its title, description, or completion status.

    Args:
        task_id (int): The unique identifier for the task.

    Returns:
        Response: The updated task object.
    """
    task = Task.query.get_or_404(task_id)
    data = request.json
    task.title = data.get('title', task.title)
    task.description = data.get('description', task.description)
    task.is_completed = data.get('is_completed', task.is_completed)
    task.time_tracked_seconds = data.get('time_tracked_seconds', task.time_tracked_seconds)
    db.session.commit()
    return jsonify(task.to_dict())


@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """
    Delete a task instance.

    Supports deleting a single task or, for recurring tasks, all future
    instances by using the 'apply_to=all_future' query parameter.

    Args:
        task_id (int): The unique identifier for the task.

    Returns:
        Response: An empty response with a 204 status code.
    """
    task = Task.query.get_or_404(task_id)
    # Check for a query parameter to determine the scope of deletion.
    apply_to = request.args.get('apply_to')  # e.g., 'all_future'

    if apply_to == 'all_future' and task.recurrence_group_id:
        # Delete this task and all future tasks in the same recurring series.
        Task.query.filter(
            Task.recurrence_group_id == task.recurrence_group_id,
            Task.due_date >= task.due_date
        ).delete(synchronize_session=False)
    else:
        db.session.delete(task)

    db.session.commit()
    return '', 204


@app.route('/events', methods=['GET'])
def get_events():
    """Retrieve a list of all events.

    Returns:
        Response: A JSON response containing a list of event objects.
    """
    return jsonify([event.to_dict() for event in Event.query.all()])


@app.route('/events', methods=['POST'])
def create_event():
    """Create a new event from a JSON payload.

    Request Body (JSON):
        - title (str): The title of the event.
        - start_time (str): The start time in ISO format.
        - (and other optional Event fields)

    Returns:
        Response: The new event object with a 201 status code, or an error with a 400 status.
    """
    data = request.json
    if not data.get('title') or not data.get('start_time'):
        return jsonify({'error': 'Title and start_time are required'}), 400

    new_event = Event(
        title=data.get('title'),
        description=data.get('description'),
        start_time=parse_datetime(data.get('start_time')),
        end_time=parse_datetime(data.get('end_time'))
    )
    db.session.add(new_event)
    db.session.commit()
    return jsonify(new_event.to_dict()), 201


@app.route('/events/<int:event_id>', methods=['PUT'])
def update_event(event_id):
    """Update an existing event's details from a JSON payload.

    Args:
        event_id (int): The unique identifier for the event.

    Request Body (JSON):
        - optional fields to update, e.g., 'title', 'start_time'

    Returns:
        Response: The updated event object.
    """
    event = Event.query.get_or_404(event_id)
    data = request.json

    # Standard updates for simple fields
    event.title = data.get('title', event.title)
    event.description = data.get('description', event.description)

    # Update start_time only if a valid (non-null) value is provided,
    # as this field is required in the database.
    new_start_time = parse_datetime(data.get('start_time'))
    if new_start_time:
        event.start_time = new_start_time

    # For nullable fields like end_time, checking for the key's presence
    # allows clients to explicitly set the value to null.
    if 'end_time' in data:
        event.end_time = parse_datetime(data.get('end_time'))

    db.session.commit()
    return jsonify(event.to_dict())


@app.route('/events/<int:event_id>', methods=['DELETE'])
def delete_event(event_id):
    """Delete a specific event.

    Args:
        event_id (int): The unique identifier for the event.

    Returns:
        Response: An empty response with a 204 status code.
    """
    event = Event.query.get_or_404(event_id)
    db.session.delete(event)
    db.session.commit()
    return '', 204


@app.route('/journal', methods=['GET'])
def get_journal_entries():
    """Retrieve all journal entries, ordered by the most recent first.

    Returns:
        Response: A JSON response containing a list of journal entry objects.
    """
    return jsonify([entry.to_dict() for entry in JournalEntry.query.order_by(JournalEntry.timestamp.desc()).all()])


@app.route('/journal', methods=['POST'])
def create_journal_entry():
    """Create a new journal entry from a JSON payload.

    Request Body (JSON):
        - entry_type (str): The type of entry (e.g., 'meal', 'mood').
        - content (json): The data associated with the entry.

    Returns:
        Response: The new journal entry object with a 201 status code.
    """
    data = request.json
    if not data.get('entry_type') or not data.get('content'):
        return jsonify({'error': 'entry_type and content are required'}), 400

    new_entry = JournalEntry(
        entry_type=data.get('entry_type'),
        content=data.get('content'),
        # Use the provided timestamp or default to now.
        timestamp=parse_datetime(data.get('timestamp')) or datetime.now(timezone.utc)
    )
    db.session.add(new_entry)
    db.session.commit()
    return jsonify(new_entry.to_dict()), 201


@app.route('/journal/<int:entry_id>', methods=['PUT'])
def update_journal_entry(entry_id):
    """Update an existing journal entry from a JSON payload.

    Args:
        entry_id (int): The unique identifier for the journal entry.

    Request Body (JSON):
        - content (json): The data associated with the entry.
        - timestamp (str, optional): The timestamp in ISO format.

    Returns:
        Response: The updated journal entry object.
    """
    entry = JournalEntry.query.get_or_404(entry_id)
    data = request.json

    # Update the main content field
    entry.content = data.get('content', entry.content)

    # Update timestamp only if a valid (non-null) value is provided,
    # as this field is required in the database.
    new_timestamp = parse_datetime(data.get('timestamp'))
    if new_timestamp:
        entry.timestamp = new_timestamp

    db.session.commit()
    return jsonify(entry.to_dict())


@app.route('/journal/<int:entry_id>', methods=['DELETE'])
def delete_journal_entry(entry_id):
    """Delete a journal entry.

    Args:
        entry_id (int): The unique identifier for the journal entry.

    Returns:
        Response: An empty response with a 204 status code.
    """
    entry = JournalEntry.query.get_or_404(entry_id)
    db.session.delete(entry)
    db.session.commit()
    return '', 204


if __name__ == '__main__':
    # This block allows the Flask app to be run directly for development purposes.
    # The 'debug=True' flag enables features like auto-reloading on code changes
    # and an interactive debugger in the browser for unhandled exceptions.
    app.run(debug=True)
