"""
Core logic for TaskPlanner application.

This module contains the data model and business logic for task management,
separated from the GUI to enable unit testing.
"""

import json
import os
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List, Optional, Callable


@dataclass
class Task:
    """
    Represents a single task.
    
    Fields:
        title: Task title (required, string)
        deadline: Deadline date in DD-MM-YYYY format (required, string)
        estimated_time: Estimated time in hours (required, float)
            Examples: 1.0 (1 hour), 1.25 (1 hour 15 minutes), 2.5 (2 hours 30 minutes)
        notes: Additional notes or hints (optional, string)
        completed: Completion status (boolean)
    """
    title: str
    deadline: str  # DD-MM-YYYY format
    estimated_time: float  # hours (e.g., 1.25 = 1 hour 15 minutes)
    notes: str = ""
    completed: bool = False

    def __post_init__(self):
        """Validate task data after initialization."""
        if not self.title or not self.title.strip():
            raise ValueError("Task title is required and cannot be empty")
        if not self.deadline:
            raise ValueError("Deadline is required")
        if not isinstance(self.estimated_time, (int, float)) or self.estimated_time < 0:
            raise ValueError("Estimated time must be a non-negative number (hours)")
        
        # Validate deadline format
        if not is_valid_date(self.deadline):
            raise ValueError(f"Invalid deadline format or date: {self.deadline}. Expected DD-MM-YYYY format.")


def parse_date(date_str: str) -> Optional[datetime]:
    """
    Parse a date string in DD-MM-YYYY format to a datetime object.
    
    Args:
        date_str: Date string in DD-MM-YYYY format
        
    Returns:
        datetime object if valid, None otherwise
    """
    try:
        return datetime.strptime(date_str.strip(), "%d-%m-%Y")
    except (ValueError, AttributeError):
        return None


def format_date(date_obj: datetime) -> str:
    """
    Format a datetime object to DD-MM-YYYY string format.
    
    Args:
        date_obj: datetime object
        
    Returns:
        Date string in DD-MM-YYYY format
    """
    return date_obj.strftime("%d-%m-%Y")


def is_valid_date(date_str: str) -> bool:
    """
    Validate if a date string is in DD-MM-YYYY format and represents a valid date.
    
    Args:
        date_str: Date string to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not date_str or not isinstance(date_str, str):
        return False
    
    parsed = parse_date(date_str)
    return parsed is not None


class TaskManager:
    """
    Manages a collection of tasks with CRUD operations, searching, sorting, and filtering.
    
    This class handles all business logic for task management, independent of the GUI.
    """
    
    def __init__(self, tasks: Optional[List[Task]] = None):
        """
        Initialize TaskManager with an optional list of tasks.
        
        Args:
            tasks: Optional initial list of tasks
        """
        self._tasks: List[Task] = tasks if tasks is not None else []
    
    def add_task(self, task: Task) -> None:
        """
        Add a new task to the collection.
        
        Args:
            task: Task object to add
            
        Raises:
            ValueError: If task validation fails
        """
        # Validation is done in Task.__post_init__
        self._tasks.append(task)
    
    def update_task(self, index: int, task: Task) -> None:
        """
        Update an existing task at the given index.
        
        Args:
            index: Index of the task to update
            task: Updated task object
            
        Raises:
            IndexError: If index is out of range
            ValueError: If task validation fails
        """
        if index < 0 or index >= len(self._tasks):
            raise IndexError(f"Task index {index} is out of range")
        
        # Validation is done in Task.__post_init__
        self._tasks[index] = task
    
    def delete_task(self, index: int) -> None:
        """
        Delete a task at the given index.
        
        Args:
            index: Index of the task to delete
            
        Raises:
            IndexError: If index is out of range
        """
        if index < 0 or index >= len(self._tasks):
            raise IndexError(f"Task index {index} is out of range")
        
        del self._tasks[index]
    
    def get_task(self, index: int) -> Task:
        """
        Get a task at the given index.
        
        Args:
            index: Index of the task to retrieve
            
        Returns:
            Task object
            
        Raises:
            IndexError: If index is out of range
        """
        if index < 0 or index >= len(self._tasks):
            raise IndexError(f"Task index {index} is out of range")
        
        return self._tasks[index]
    
    def get_all_tasks(self) -> List[Task]:
        """
        Get all tasks.
        
        Returns:
            List of all tasks
        """
        return self._tasks.copy()
    
    def mark_completed(self, index: int, completed: bool = True) -> None:
        """
        Mark a task as completed or not completed.
        
        Args:
            index: Index of the task
            completed: True to mark as completed, False to mark as not completed
            
        Raises:
            IndexError: If index is out of range
        """
        if index < 0 or index >= len(self._tasks):
            raise IndexError(f"Task index {index} is out of range")
        
        self._tasks[index].completed = completed
    
    def toggle_completion(self, index: int) -> None:
        """
        Toggle the completion status of a task.
        
        Args:
            index: Index of the task
            
        Raises:
            IndexError: If index is out of range
        """
        if index < 0 or index >= len(self._tasks):
            raise IndexError(f"Task index {index} is out of range")
        
        self._tasks[index].completed = not self._tasks[index].completed
    
    def search_by_title(self, query: str) -> List[Task]:
        """
        Search tasks by title (case-insensitive partial match).
        
        Args:
            query: Search query string
            
        Returns:
            List of matching tasks
        """
        if not query:
            return self.get_all_tasks()
        
        query_lower = query.lower().strip()
        return [task for task in self._tasks if query_lower in task.title.lower()]
    
    def search_by_notes(self, query: str) -> List[Task]:
        """
        Search tasks by notes content (case-insensitive partial match).
        
        Args:
            query: Search query string
            
        Returns:
            List of matching tasks
        """
        if not query:
            return self.get_all_tasks()
        
        query_lower = query.lower().strip()
        return [task for task in self._tasks if query_lower in task.notes.lower()]
    
    def filter_by_completion(self, completed: Optional[bool] = None) -> List[Task]:
        """
        Filter tasks by completion status.
        
        Args:
            completed: True for completed tasks, False for incomplete, None for all
            
        Returns:
            List of filtered tasks
        """
        if completed is None:
            return self.get_all_tasks()
        
        return [task for task in self._tasks if task.completed == completed]
    
    def sort_by_deadline(self, reverse: bool = False) -> List[Task]:
        """
        Get tasks sorted by deadline date.
        
        Args:
            reverse: If True, sort in descending order (latest first)
            
        Returns:
            List of tasks sorted by deadline
        """
        def get_deadline_date(task: Task) -> datetime:
            parsed = parse_date(task.deadline)
            if parsed is None:
                # Invalid dates go to the end
                return datetime.max
            return parsed
        
        sorted_tasks = sorted(self._tasks, key=get_deadline_date, reverse=reverse)
        return sorted_tasks
    
    def sort_by_title(self, reverse: bool = False) -> List[Task]:
        """
        Get tasks sorted by title (case-insensitive).
        
        Args:
            reverse: If True, sort in descending order (Z to A)
            
        Returns:
            List of tasks sorted by title
        """
        sorted_tasks = sorted(self._tasks, key=lambda t: t.title.lower(), reverse=reverse)
        return sorted_tasks
    
    def sort_by_completion(self, completed_first: bool = False) -> List[Task]:
        """
        Get tasks sorted by completion status.
        
        Args:
            completed_first: If True, completed tasks appear first
            
        Returns:
            List of tasks sorted by completion status
        """
        sorted_tasks = sorted(self._tasks, key=lambda t: t.completed, reverse=completed_first)
        return sorted_tasks
    
    def get_count(self) -> int:
        """
        Get the total number of tasks.
        
        Returns:
            Number of tasks
        """
        return len(self._tasks)
    
    def clear(self) -> None:
        """Clear all tasks."""
        self._tasks.clear()


def save_tasks_to_json(tasks: List[Task], filepath: str = "tasks.json") -> None:
    """
    Save a list of tasks to a JSON file.
    
    Args:
        tasks: List of Task objects to save
        filepath: Path to the JSON file
    """
    tasks_data = [asdict(task) for task in tasks]
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(tasks_data, f, indent=2, ensure_ascii=False)


def load_tasks_from_json(filepath: str = "tasks.json") -> List[Task]:
    """
    Load tasks from a JSON file.
    
    Args:
        filepath: Path to the JSON file
        
    Returns:
        List of Task objects
        
    Raises:
        json.JSONDecodeError: If JSON is invalid
        ValueError: If task data is invalid
    """
    if not os.path.exists(filepath):
        return []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            tasks_data = json.load(f)
        
        if not isinstance(tasks_data, list):
            raise ValueError("JSON file must contain a list of tasks")
        
        tasks = []
        for task_dict in tasks_data:
            try:
                task = Task(**task_dict)
                tasks.append(task)
            except (TypeError, ValueError) as e:
                # Skip invalid tasks but continue loading others
                print(f"Warning: Skipping invalid task: {e}")
                continue
        
        return tasks
    
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON file: {e}")

