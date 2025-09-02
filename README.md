# Personal Planner API
[![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=fff)](https://www.python.org/)
[![PyCharm](https://img.shields.io/badge/PyCharm-000?logo=pycharm&logoColor=fff)](https://www.jetbrains.com/pycharm/)
[![Flask](https://img.shields.io/badge/Flask-000?logo=flask&logoColor=fff)](https://flask.palletsprojects.com/)
[![Postgres](https://img.shields.io/badge/Postgres-%23316192.svg?logo=postgresql&logoColor=white)](https://www.postgresql.org/)


This is a Flask-based backend application for a personal planner. It provides a RESTful API for managing tasks, events, and journal entries, with support for recurring tasks and other features to help you organize your life.

---

## Features

-   **Task Management**: Create, retrieve, update, and delete tasks.
-   **Recurring Tasks**: Set up tasks that repeat daily or weekly.
-   **Event Scheduling**: Manage your calendar with endpoints for creating, retrieving, updating, and deleting events.
-   **Journaling**: Keep a log of your thoughts, meals, or moods with a flexible journaling system.
-   **Database Integration**: Uses SQLAlchemy and Flask-Migrate to manage a postgresSQL database.

---

## Getting Started

### Prerequisites

-   Python 3.10 or later
-   pip

### Dependencies

-   Flask~=3.1.2
-   flask-cors~=6.0.1
-   Flask-Migrate~=4.1.0
-   alembic~=1.16.5
-   SQLAlchemy~=2.0.43

### Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/ericbrown589/personal-planner.git](https://github.com/ericbrown589/personal-planner.git)
    cd personal-planner
    ```
2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate   # macOS/Linux
    .venv\Scripts\activate      # Windows
    ```
3. **Configure the Database:**
  * Create a new PostgreSQL database (e.g., personal_planner).
  * Create a config.py file in the root of the project. This file is ignored by Git, so your credentials will be safe.
  * Add the following to your config.py, replacing the user, password, and database name with your own credentials:
    ```python
    from urllib.parse import quote_plus

    class Config:
      # Replace with your actual PostgreSQL credentials
      raw_password = 'your_super_secret_password'
      encoded_password = quote_plus(raw_password)
      SQLALCHEMY_DATABASE_URI = f'postgresql://user:{encoded_password}@localhost:5432/personal_planner'
      SQLALCHEMY_TRACK_MODIFICATIONS = False
    ```
4.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
5.  **Initialize the database:**
    ```bash
    flask db init
    flask db migrate -m "Initial migration."
    flask db upgrade
    ```
6.  **Run the application:**
    ```bash
    flask run
    ```

---

## Project Structure

```
.
├── app.py
├── models.py
├── config.py
├── Migrations
├── requirements.txt
└── README.md
```

---

## API Endpoints

### Tasks

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/tasks` | Retrieve a list of all tasks. |
| `POST` | `/tasks` | Create a new task. Supports recurring tasks. |
| `PUT` | `/tasks/<int:task_id>` | Update an existing task. |
| `DELETE` | `/tasks/<int:task_id>` | Delete a task. Can also delete all future recurring tasks. |

### Events

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/events` | Retrieve a list of all events. |
| `POST` | `/events` | Create a new event. |
| `PUT` | `/events/<int:event_id>` | Update an existing event. |
| `DELETE` | `/events/<int:event_id>` | Delete an event. |

### Journal Entries

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/journal` | Retrieve all journal entries. |
| `POST` | `/journal` | Create a new journal entry. |
| `PUT` | `/journal/<int:entry_id>` | Update an existing journal entry. |
| `DELETE` | `/journal/<int:entry_id>` | Delete a journal entry. |

---

## Database Models

### Task

| Field | Type | Description |
| :--- | :--- | :--- |
| `id` | Integer | Primary key. |
| `title` | String | The title of the task. |
| `description` | Text | A description of the task. |
| `is_recurring`| Boolean | Whether the task is recurring. |
| `is_completed`| Boolean | Whether the task is completed. |
| `due_date` | Date | The due date of the task. |
| `start_time` | DateTime | The start time of the task. |
| `end_time` | DateTime | The end time of the task. |
| `time_tracked_seconds` | Integer | The time tracked for the task in seconds. |
| `created_at` | DateTime | The creation timestamp of the task. |
| `recurrence_type` | String | The recurrence type (e.g., 'daily', 'weekly'). |
| `recurrence_group_id`| String | A unique ID to group recurring tasks. |

### Event

| Field | Type | Description |
| :--- | :--- | :--- |
| `id` | Integer | Primary key. |
| `title` | String | The title of the event. |
| `description` | Text | A description of the event. |
| `start_time` | DateTime | The start time of the event. |
| `end_time` | DateTime | The end time of the event. |
| `created_at` | DateTime | The creation timestamp of the event. |

### JournalEntry

| Field | Type | Description |
| :--- | :--- | :--- |
| `id` | Integer | Primary key. |
| `entry_type` | String | The type of journal entry (e.g., 'meal', 'mood'). |
| `content` | JSON | The content of the journal entry. |
| `timestamp` | DateTime | The timestamp of the journal entry. |

---

## Future Work / Roadmap
Planned improvement and features include:

* Adding authorization and authenitcation to allow multiple users
* Advanced Recurrence Logic (e.g., "monthly on the 15th", "every other Tuesday")

---

## Status

🚧 This is a capstone project and currently a work in progress. 🚧  
Features and API are subject to change as development continues.

---
