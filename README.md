# TaskPlanner

A comprehensive desktop task management application built with Python and Tkinter.

## Description

TaskPlanner is a Python desktop application designed to help you organize and manage your tasks efficiently. It provides a clean, intuitive GUI for creating, editing, searching, sorting, and tracking tasks with deadlines and time estimates.

## Features

- **Task Management**: Add, edit, delete, and organize tasks
- **Deadline Tracking**: Set deadlines in DD-MM-YYYY format with validation
- **Time Estimation**: Track estimated time for each task (in minutes)
- **Notes/Hints**: Add detailed notes and hints for each task
- **Completion Status**: Mark tasks as completed or not completed
- **Search**: Search tasks by title (case-insensitive)
- **Sorting**: Sort tasks by deadline, title, or completion status
- **Filtering**: Filter tasks by completion status
- **Data Persistence**: Automatically save and load tasks from JSON file
- **Visual Distinction**: Completed tasks are visually distinguished in the task list

## Requirements

- Python 3.8 or higher
- Tkinter (usually included with Python)

No external dependencies are required - the application uses only Python standard library modules.

## Installation

1. Clone the repository:
```bash
git clone https://github.com/kossakowski/TaskPlanner.git
cd TaskPlanner
```

2. No additional installation is required - the application uses only Python standard library.

## Usage

### Running the Application

```bash
python -m taskplanner
```

Or:

```bash
python taskplanner/main.py
```

### Using TaskPlanner

1. **Adding a Task**:
   - Enter the task title (required)
   - Enter the deadline in DD-MM-YYYY format, e.g., `25-12-2025` (required)
   - Enter estimated time in minutes, e.g., `60` (required)
   - Optionally add notes/hints in the multi-line text field
   - Optionally check "Mark as completed"
   - Click "Add Task"

2. **Editing a Task**:
   - Select a task from the task list
   - The task data will be loaded into the input fields
   - Modify the fields as needed
   - Click "Update Task"

3. **Deleting a Task**:
   - Select a task from the task list
   - Click "Delete Task"
   - Confirm the deletion

4. **Marking Tasks as Completed**:
   - Select a task from the task list
   - Click "Toggle Completion" or use the checkbox in the input form

5. **Searching Tasks**:
   - Type in the search field
   - Tasks are filtered in real-time by title (case-insensitive)

6. **Sorting Tasks**:
   - Click "By Deadline" to sort by deadline date
   - Click "By Title" to sort alphabetically by title
   - Click "By Status" to sort by completion status
   - Click "Reset Sort" to remove sorting

7. **Filtering Tasks**:
   - Click "All" to show all tasks
   - Click "Completed" to show only completed tasks
   - Click "Not Completed" to show only incomplete tasks

## Data Storage

Tasks are automatically saved to `tasks.json` in the application directory. The file is created automatically when you add your first task and updated whenever you make changes.

## Running Tests

The application includes a comprehensive test suite covering all core functionality:

```bash
python -m unittest tests.test_taskplanner
```

Or using pytest:

```bash
pytest tests/test_taskplanner.py
```

The test suite includes:
- Date parsing and validation tests
- Task creation and validation tests
- TaskManager CRUD operation tests
- Search, sort, and filter functionality tests
- JSON persistence tests
- Integration tests

All 52 tests should pass successfully.

## Project Structure

```
TaskPlanner/
├── taskplanner/
│   ├── __init__.py       # Package initialization
│   ├── core.py           # Core logic (Task, TaskManager, date functions, JSON persistence)
│   ├── gui.py            # GUI application (Tkinter interface)
│   └── main.py           # Application entry point
├── tests/
│   ├── __init__.py
│   └── test_taskplanner.py  # Comprehensive test suite
├── tasks.json            # Task data file (created automatically)
├── README.md
├── requirements.txt
└── pyproject.toml
```

## Code Architecture

The application is designed with separation of concerns:

- **Core Logic** (`taskplanner/core.py`): Contains all business logic, data models, and persistence. This code is completely independent of the GUI and can be tested without Tkinter.

- **GUI** (`taskplanner/gui.py`): Contains the Tkinter interface that calls the core logic functions.

- **Tests** (`tests/test_taskplanner.py`): Comprehensive test suite that validates all core functionality without requiring a running GUI.

## Date Format

All dates must be entered and are displayed in **DD-MM-YYYY** format (e.g., `25-12-2025`). The application validates dates to ensure they are valid calendar dates.

## Estimated Time Format

Estimated time is entered and displayed as **minutes** (integer). For example:
- 60 minutes = 1 hour
- 120 minutes = 2 hours
- 30 minutes = 30 minutes

## License

This project is open source and available for use.

## Development

This application was built with:
- Clean, idiomatic Python 3 code
- Separation of concerns (core logic vs GUI)
- Comprehensive automated testing
- User-friendly error handling
- Data persistence with JSON

## Contributing

Contributions are welcome! Please ensure that:
- All tests pass
- Code follows Python style guidelines
- New features include appropriate tests
