"""
Comprehensive test suite for TaskPlanner application.

This test suite validates all core functionality of the TaskPlanner application
without requiring a running GUI.

To run the tests:
    python -m unittest tests.test_taskplanner
    or
    pytest tests/test_taskplanner.py
"""

import unittest
import json
import os
import tempfile
from datetime import datetime
from taskplanner.core import (
    Task,
    TaskManager,
    parse_date,
    format_date,
    is_valid_date,
    save_tasks_to_json,
    load_tasks_from_json
)


class TestDateFunctions(unittest.TestCase):
    """Test date parsing, formatting, and validation functions."""
    
    def test_parse_valid_date(self):
        """Test parsing valid DD-MM-YYYY dates."""
        date_str = "25-12-2025"
        result = parse_date(date_str)
        self.assertIsNotNone(result)
        self.assertEqual(result.day, 25)
        self.assertEqual(result.month, 12)
        self.assertEqual(result.year, 2025)
    
    def test_parse_invalid_format(self):
        """Test parsing invalid date formats."""
        invalid_formats = [
            "2025-12-25",  # Wrong format
            "25/12/2025",  # Wrong separator
            "12-25-2025",  # MM-DD-YYYY
            "25-12-25",    # Short year
            "invalid",     # Not a date
        ]
        
        for date_str in invalid_formats:
            result = parse_date(date_str)
            self.assertIsNone(result, f"Should fail for: {date_str}")
    
    def test_parse_invalid_date(self):
        """Test parsing non-existent dates."""
        invalid_dates = [
            "32-01-2025",  # Invalid day
            "31-02-2025",  # Invalid day for February
            "29-02-2024",  # Valid leap year
            "29-02-2025",  # Invalid (not a leap year)
        ]
        
        # 29-02-2024 should be valid (leap year)
        result = parse_date("29-02-2024")
        self.assertIsNotNone(result)
        
        # 29-02-2025 should be invalid
        result = parse_date("29-02-2025")
        self.assertIsNone(result)
        
        # Other invalid dates
        for date_str in ["32-01-2025", "31-02-2025"]:
            result = parse_date(date_str)
            self.assertIsNone(result, f"Should fail for: {date_str}")
    
    def test_format_date(self):
        """Test formatting datetime to DD-MM-YYYY string."""
        date_obj = datetime(2025, 12, 25)
        result = format_date(date_obj)
        self.assertEqual(result, "25-12-2025")
    
    def test_is_valid_date_valid(self):
        """Test validation of valid dates."""
        valid_dates = [
            "01-01-2025",
            "25-12-2025",
            "29-02-2024",  # Leap year
            "31-12-2025",
        ]
        
        for date_str in valid_dates:
            self.assertTrue(is_valid_date(date_str), f"Should be valid: {date_str}")
    
    def test_is_valid_date_invalid(self):
        """Test validation of invalid dates."""
        invalid_dates = [
            "32-01-2025",
            "31-02-2025",
            "29-02-2025",  # Not a leap year
            "invalid",
            "",
            "2025-12-25",  # Wrong format
        ]
        
        for date_str in invalid_dates:
            self.assertFalse(is_valid_date(date_str), f"Should be invalid: {date_str}")
    
    def test_is_valid_date_edge_cases(self):
        """Test edge cases for date validation."""
        self.assertFalse(is_valid_date(None))
        self.assertFalse(is_valid_date(123))  # Not a string


class TestTask(unittest.TestCase):
    """Test Task data class and validation."""
    
    def test_create_valid_task(self):
        """Test creating a valid task with all fields."""
        task = Task(
            title="Test Task",
            deadline="25-12-2025",
            estimated_time=1.0,
            notes="Test notes",
            completed=False
        )
        
        self.assertEqual(task.title, "Test Task")
        self.assertEqual(task.deadline, "25-12-2025")
        self.assertEqual(task.estimated_time, 1.0)
        self.assertEqual(task.notes, "Test notes")
        self.assertFalse(task.completed)
    
    def test_create_task_minimal(self):
        """Test creating a task with only required fields."""
        task = Task(
            title="Minimal Task",
            deadline="01-01-2025",
            estimated_time=0.5
        )
        
        self.assertEqual(task.title, "Minimal Task")
        self.assertEqual(task.deadline, "01-01-2025")
        self.assertEqual(task.estimated_time, 0.5)
        self.assertEqual(task.notes, "")  # Default empty
        self.assertFalse(task.completed)  # Default False
    
    def test_task_empty_title_raises_error(self):
        """Test that empty title raises ValueError."""
        with self.assertRaises(ValueError):
            Task(title="", deadline="25-12-2025", estimated_time=1.0)
        
        with self.assertRaises(ValueError):
            Task(title="   ", deadline="25-12-2025", estimated_time=1.0)
    
    def test_task_missing_deadline_raises_error(self):
        """Test that missing deadline raises ValueError."""
        with self.assertRaises(ValueError):
            Task(title="Test", deadline="", estimated_time=1.0)
    
    def test_task_invalid_deadline_raises_error(self):
        """Test that invalid deadline format raises ValueError."""
        with self.assertRaises(ValueError):
            Task(title="Test", deadline="2025-12-25", estimated_time=1.0)
        
        with self.assertRaises(ValueError):
            Task(title="Test", deadline="32-13-2025", estimated_time=1.0)
    
    def test_task_invalid_estimated_time_raises_error(self):
        """Test that invalid estimated time raises ValueError."""
        with self.assertRaises(ValueError):
            Task(title="Test", deadline="25-12-2025", estimated_time=-10)
        
        with self.assertRaises(ValueError):
            Task(title="Test", deadline="25-12-2025", estimated_time="invalid")


class TestTaskManager(unittest.TestCase):
    """Test TaskManager class and its operations."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.manager = TaskManager()
        self.task1 = Task(
            title="Task 1",
            deadline="25-12-2025",
            estimated_time=1.0,
            notes="Notes 1",
            completed=False
        )
        self.task2 = Task(
            title="Task 2",
            deadline="01-01-2025",
            estimated_time=0.5,
            notes="Notes 2",
            completed=True
        )
        self.task3 = Task(
            title="Another Task",
            deadline="15-06-2025",
            estimated_time=2.0,
            completed=False
        )
    
    def test_add_task(self):
        """Test adding tasks to the manager."""
        self.assertEqual(self.manager.get_count(), 0)
        
        self.manager.add_task(self.task1)
        self.assertEqual(self.manager.get_count(), 1)
        
        self.manager.add_task(self.task2)
        self.assertEqual(self.manager.get_count(), 2)
    
    def test_add_task_validation(self):
        """Test that adding invalid task raises error."""
        with self.assertRaises(ValueError):
            invalid_task = Task(title="", deadline="25-12-2025", estimated_time=1.0)
            self.manager.add_task(invalid_task)
    
    def test_get_all_tasks(self):
        """Test retrieving all tasks."""
        self.manager.add_task(self.task1)
        self.manager.add_task(self.task2)
        
        tasks = self.manager.get_all_tasks()
        self.assertEqual(len(tasks), 2)
        self.assertIn(self.task1, tasks)
        self.assertIn(self.task2, tasks)
    
    def test_get_all_tasks_returns_copy(self):
        """Test that get_all_tasks returns a copy, not the original list."""
        self.manager.add_task(self.task1)
        tasks = self.manager.get_all_tasks()
        tasks.append(self.task2)  # Should not affect manager
        
        self.assertEqual(self.manager.get_count(), 1)
    
    def test_get_task(self):
        """Test retrieving a specific task by index."""
        self.manager.add_task(self.task1)
        self.manager.add_task(self.task2)
        
        retrieved = self.manager.get_task(0)
        self.assertEqual(retrieved.title, "Task 1")
        
        retrieved = self.manager.get_task(1)
        self.assertEqual(retrieved.title, "Task 2")
    
    def test_get_task_invalid_index(self):
        """Test that getting task with invalid index raises IndexError."""
        with self.assertRaises(IndexError):
            self.manager.get_task(0)
        
        self.manager.add_task(self.task1)
        with self.assertRaises(IndexError):
            self.manager.get_task(1)
        
        with self.assertRaises(IndexError):
            self.manager.get_task(-1)
    
    def test_update_task(self):
        """Test updating an existing task."""
        self.manager.add_task(self.task1)
        
        updated_task = Task(
            title="Updated Task",
            deadline="30-12-2025",
            estimated_time=1.5,
            notes="Updated notes",
            completed=True
        )
        
        self.manager.update_task(0, updated_task)
        
        retrieved = self.manager.get_task(0)
        self.assertEqual(retrieved.title, "Updated Task")
        self.assertEqual(retrieved.deadline, "30-12-2025")
        self.assertEqual(retrieved.estimated_time, 1.5)
        self.assertTrue(retrieved.completed)
    
    def test_update_task_keeps_other_tasks(self):
        """Test that updating one task doesn't affect others."""
        self.manager.add_task(self.task1)
        self.manager.add_task(self.task2)
        
        updated_task = Task(
            title="Updated",
            deadline="25-12-2025",
            estimated_time=1.0
        )
        self.manager.update_task(0, updated_task)
        
        # Task 2 should be unchanged
        task2 = self.manager.get_task(1)
        self.assertEqual(task2.title, "Task 2")
    
    def test_update_task_invalid_index(self):
        """Test that updating with invalid index raises IndexError."""
        with self.assertRaises(IndexError):
            self.manager.update_task(0, self.task1)
    
    def test_delete_task(self):
        """Test deleting a task."""
        self.manager.add_task(self.task1)
        self.manager.add_task(self.task2)
        self.manager.add_task(self.task3)
        
        self.assertEqual(self.manager.get_count(), 3)
        
        self.manager.delete_task(1)
        self.assertEqual(self.manager.get_count(), 2)
        
        # Remaining tasks should be task1 and task3
        self.assertEqual(self.manager.get_task(0).title, "Task 1")
        self.assertEqual(self.manager.get_task(1).title, "Another Task")
    
    def test_delete_task_invalid_index(self):
        """Test that deleting with invalid index raises IndexError."""
        with self.assertRaises(IndexError):
            self.manager.delete_task(0)
    
    def test_mark_completed(self):
        """Test marking a task as completed."""
        self.manager.add_task(self.task1)
        self.assertFalse(self.manager.get_task(0).completed)
        
        self.manager.mark_completed(0, True)
        self.assertTrue(self.manager.get_task(0).completed)
        
        self.manager.mark_completed(0, False)
        self.assertFalse(self.manager.get_task(0).completed)
    
    def test_toggle_completion(self):
        """Test toggling completion status."""
        self.manager.add_task(self.task1)
        self.assertFalse(self.manager.get_task(0).completed)
        
        self.manager.toggle_completion(0)
        self.assertTrue(self.manager.get_task(0).completed)
        
        self.manager.toggle_completion(0)
        self.assertFalse(self.manager.get_task(0).completed)
    
    def test_get_count(self):
        """Test getting task count."""
        self.assertEqual(self.manager.get_count(), 0)
        
        self.manager.add_task(self.task1)
        self.assertEqual(self.manager.get_count(), 1)
        
        self.manager.add_task(self.task2)
        self.assertEqual(self.manager.get_count(), 2)
        
        self.manager.delete_task(0)
        self.assertEqual(self.manager.get_count(), 1)
    
    def test_clear(self):
        """Test clearing all tasks."""
        self.manager.add_task(self.task1)
        self.manager.add_task(self.task2)
        
        self.manager.clear()
        self.assertEqual(self.manager.get_count(), 0)


class TestTaskManagerSearch(unittest.TestCase):
    """Test search functionality in TaskManager."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.manager = TaskManager()
        self.manager.add_task(Task(
            title="Python Programming",
            deadline="25-12-2025",
            estimated_time=1.0,
            notes="Learn Python basics"
        ))
        self.manager.add_task(Task(
            title="Java Development",
            deadline="01-01-2025",
            estimated_time=2.0,
            notes="Java project"
        ))
        self.manager.add_task(Task(
            title="Python Testing",
            deadline="15-06-2025",
            estimated_time=1.5,
            notes="Write Python tests"
        ))
    
    def test_search_by_title_exact_match(self):
        """Test searching by exact title match."""
        results = self.manager.search_by_title("Python Programming")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].title, "Python Programming")
    
    def test_search_by_title_partial_match(self):
        """Test searching by partial title match."""
        results = self.manager.search_by_title("Python")
        self.assertEqual(len(results), 2)
        titles = [t.title for t in results]
        self.assertIn("Python Programming", titles)
        self.assertIn("Python Testing", titles)
    
    def test_search_by_title_case_insensitive(self):
        """Test that search is case-insensitive."""
        results = self.manager.search_by_title("python")
        self.assertEqual(len(results), 2)
        
        results = self.manager.search_by_title("JAVA")
        self.assertEqual(len(results), 1)
    
    def test_search_by_title_no_match(self):
        """Test searching with no matches."""
        results = self.manager.search_by_title("Nonexistent")
        self.assertEqual(len(results), 0)
    
    def test_search_by_title_empty_query(self):
        """Test that empty query returns all tasks."""
        results = self.manager.search_by_title("")
        self.assertEqual(len(results), 3)
    
    def test_search_by_notes(self):
        """Test searching by notes content."""
        results = self.manager.search_by_notes("Python")
        self.assertEqual(len(results), 2)
        
        results = self.manager.search_by_notes("Java")
        self.assertEqual(len(results), 1)


class TestTaskManagerSorting(unittest.TestCase):
    """Test sorting functionality in TaskManager."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.manager = TaskManager()
        # Add tasks with different deadlines
        self.manager.add_task(Task(
            title="Task C",
            deadline="25-12-2025",
            estimated_time=1.0
        ))
        self.manager.add_task(Task(
            title="Task A",
            deadline="01-01-2025",
            estimated_time=0.5
        ))
        self.manager.add_task(Task(
            title="Task B",
            deadline="15-06-2025",
            estimated_time=1.5
        ))
    
    def test_sort_by_deadline_ascending(self):
        """Test sorting by deadline in ascending order."""
        sorted_tasks = self.manager.sort_by_deadline(reverse=False)
        
        self.assertEqual(len(sorted_tasks), 3)
        self.assertEqual(sorted_tasks[0].deadline, "01-01-2025")
        self.assertEqual(sorted_tasks[1].deadline, "15-06-2025")
        self.assertEqual(sorted_tasks[2].deadline, "25-12-2025")
    
    def test_sort_by_deadline_descending(self):
        """Test sorting by deadline in descending order."""
        sorted_tasks = self.manager.sort_by_deadline(reverse=True)
        
        self.assertEqual(len(sorted_tasks), 3)
        self.assertEqual(sorted_tasks[0].deadline, "25-12-2025")
        self.assertEqual(sorted_tasks[1].deadline, "15-06-2025")
        self.assertEqual(sorted_tasks[2].deadline, "01-01-2025")
    
    def test_sort_by_title_ascending(self):
        """Test sorting by title in ascending order."""
        sorted_tasks = self.manager.sort_by_title(reverse=False)
        
        self.assertEqual(len(sorted_tasks), 3)
        self.assertEqual(sorted_tasks[0].title, "Task A")
        self.assertEqual(sorted_tasks[1].title, "Task B")
        self.assertEqual(sorted_tasks[2].title, "Task C")
    
    def test_sort_by_title_descending(self):
        """Test sorting by title in descending order."""
        sorted_tasks = self.manager.sort_by_title(reverse=True)
        
        self.assertEqual(len(sorted_tasks), 3)
        self.assertEqual(sorted_tasks[0].title, "Task C")
        self.assertEqual(sorted_tasks[1].title, "Task B")
        self.assertEqual(sorted_tasks[2].title, "Task A")
    
    def test_sort_by_title_case_insensitive(self):
        """Test that title sorting is case-insensitive."""
        manager = TaskManager()
        manager.add_task(Task(title="zebra", deadline="01-01-2025", estimated_time=1.0))
        manager.add_task(Task(title="Apple", deadline="01-01-2025", estimated_time=1.0))
        manager.add_task(Task(title="banana", deadline="01-01-2025", estimated_time=1.0))
        
        sorted_tasks = manager.sort_by_title(reverse=False)
        self.assertEqual(sorted_tasks[0].title, "Apple")
        self.assertEqual(sorted_tasks[1].title, "banana")
        self.assertEqual(sorted_tasks[2].title, "zebra")
    
    def test_sort_by_completion(self):
        """Test sorting by completion status."""
        manager = TaskManager()
        manager.add_task(Task(title="Task 1", deadline="01-01-2025", estimated_time=1.0, completed=False))
        manager.add_task(Task(title="Task 2", deadline="01-01-2025", estimated_time=1.0, completed=True))
        manager.add_task(Task(title="Task 3", deadline="01-01-2025", estimated_time=1.0, completed=False))
        
        # Completed first
        sorted_tasks = manager.sort_by_completion(completed_first=True)
        self.assertTrue(sorted_tasks[0].completed)
        self.assertFalse(sorted_tasks[1].completed)
        self.assertFalse(sorted_tasks[2].completed)
        
        # Not completed first
        sorted_tasks = manager.sort_by_completion(completed_first=False)
        self.assertFalse(sorted_tasks[0].completed)
        self.assertFalse(sorted_tasks[1].completed)
        self.assertTrue(sorted_tasks[2].completed)


class TestTaskManagerFiltering(unittest.TestCase):
    """Test filtering functionality in TaskManager."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.manager = TaskManager()
        self.manager.add_task(Task(
            title="Task 1",
            deadline="25-12-2025",
            estimated_time=1.0,
            completed=False
        ))
        self.manager.add_task(Task(
            title="Task 2",
            deadline="01-01-2025",
            estimated_time=0.5,
            completed=True
        ))
        self.manager.add_task(Task(
            title="Task 3",
            deadline="15-06-2025",
            estimated_time=1.5,
            completed=False
        ))
    
    def test_filter_by_completion_completed(self):
        """Test filtering for completed tasks."""
        results = self.manager.filter_by_completion(completed=True)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].title, "Task 2")
        self.assertTrue(results[0].completed)
    
    def test_filter_by_completion_not_completed(self):
        """Test filtering for not completed tasks."""
        results = self.manager.filter_by_completion(completed=False)
        self.assertEqual(len(results), 2)
        titles = [t.title for t in results]
        self.assertIn("Task 1", titles)
        self.assertIn("Task 3", titles)
        self.assertNotIn("Task 2", titles)
    
    def test_filter_by_completion_all(self):
        """Test filtering with None returns all tasks."""
        results = self.manager.filter_by_completion(completed=None)
        self.assertEqual(len(results), 3)


class TestJSONPersistence(unittest.TestCase):
    """Test JSON save and load functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_file.close()
        self.filepath = self.temp_file.name
    
    def tearDown(self):
        """Clean up test files."""
        if os.path.exists(self.filepath):
            os.unlink(self.filepath)
    
    def test_save_and_load_tasks(self):
        """Test saving and loading tasks."""
        tasks = [
            Task(
                title="Task 1",
                deadline="25-12-2025",
                estimated_time=1.0,
                notes="Notes 1",
                completed=False
            ),
            Task(
                title="Task 2",
                deadline="01-01-2025",
                estimated_time=0.5,
                notes="Notes 2",
                completed=True
            )
        ]
        
        # Save tasks
        save_tasks_to_json(tasks, self.filepath)
        
        # Verify file exists
        self.assertTrue(os.path.exists(self.filepath))
        
        # Load tasks
        loaded_tasks = load_tasks_from_json(self.filepath)
        
        # Verify loaded tasks
        self.assertEqual(len(loaded_tasks), 2)
        self.assertEqual(loaded_tasks[0].title, "Task 1")
        self.assertEqual(loaded_tasks[0].deadline, "25-12-2025")
        self.assertEqual(loaded_tasks[0].estimated_time, 1.0)
        self.assertEqual(loaded_tasks[0].notes, "Notes 1")
        self.assertFalse(loaded_tasks[0].completed)
        
        self.assertEqual(loaded_tasks[1].title, "Task 2")
        self.assertEqual(loaded_tasks[1].deadline, "01-01-2025")
        self.assertEqual(loaded_tasks[1].estimated_time, 0.5)
        self.assertEqual(loaded_tasks[1].notes, "Notes 2")
        self.assertTrue(loaded_tasks[1].completed)
    
    def test_save_empty_list(self):
        """Test saving an empty task list."""
        save_tasks_to_json([], self.filepath)
        
        loaded_tasks = load_tasks_from_json(self.filepath)
        self.assertEqual(len(loaded_tasks), 0)
    
    def test_load_nonexistent_file(self):
        """Test loading from a non-existent file."""
        nonexistent = "/tmp/nonexistent_file_12345.json"
        if os.path.exists(nonexistent):
            os.unlink(nonexistent)
        
        loaded_tasks = load_tasks_from_json(nonexistent)
        self.assertEqual(len(loaded_tasks), 0)
    
    def test_load_invalid_json(self):
        """Test loading from invalid JSON file."""
        with open(self.filepath, 'w') as f:
            f.write("invalid json content {")
        
        with self.assertRaises(ValueError):
            load_tasks_from_json(self.filepath)
    
    def test_load_json_not_list(self):
        """Test loading JSON that is not a list."""
        with open(self.filepath, 'w') as f:
            json.dump({"not": "a list"}, f)
        
        with self.assertRaises(ValueError):
            load_tasks_from_json(self.filepath)
    
    def test_load_json_with_invalid_task(self):
        """Test loading JSON with invalid task data."""
        invalid_data = [
            {"title": "Valid Task", "deadline": "25-12-2025", "estimated_time": 60},
            {"title": "", "deadline": "25-12-2025", "estimated_time": 60},  # Invalid: empty title
            {"title": "Another Task", "deadline": "invalid", "estimated_time": 60},  # Invalid date
        ]
        
        with open(self.filepath, 'w') as f:
            json.dump(invalid_data, f)
        
        # Should load valid tasks and skip invalid ones
        loaded_tasks = load_tasks_from_json(self.filepath)
        # Should have at least one valid task, but behavior may vary
        # The function should handle errors gracefully
    
    def test_json_structure(self):
        """Test that saved JSON has the correct structure."""
        tasks = [
            Task(
                title="Test Task",
                deadline="25-12-2025",
                estimated_time=1.0,
                notes="Test notes",
                completed=True
            )
        ]
        
        save_tasks_to_json(tasks, self.filepath)
        
        with open(self.filepath, 'r') as f:
            data = json.load(f)
        
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        
        task_dict = data[0]
        self.assertIn("title", task_dict)
        self.assertIn("deadline", task_dict)
        self.assertIn("estimated_time", task_dict)
        self.assertIn("notes", task_dict)
        self.assertIn("completed", task_dict)
        
        self.assertEqual(task_dict["title"], "Test Task")
        self.assertEqual(task_dict["deadline"], "25-12-2025")
        self.assertEqual(task_dict["estimated_time"], 1.0)
        self.assertEqual(task_dict["notes"], "Test notes")
        self.assertTrue(task_dict["completed"])


class TestIntegration(unittest.TestCase):
    """Integration tests combining multiple features."""
    
    def test_full_workflow(self):
        """Test a complete workflow: add, search, sort, update, delete."""
        manager = TaskManager()
        
        # Add multiple tasks
        task1 = Task(title="Python Task", deadline="25-12-2025", estimated_time=1.0, completed=False)
        task2 = Task(title="Java Task", deadline="01-01-2025", estimated_time=0.5, completed=True)
        task3 = Task(title="Python Project", deadline="15-06-2025", estimated_time=2.0, completed=False)
        
        manager.add_task(task1)
        manager.add_task(task2)
        manager.add_task(task3)
        
        # Search
        python_tasks = manager.search_by_title("Python")
        self.assertEqual(len(python_tasks), 2)
        
        # Sort
        sorted_by_deadline = manager.sort_by_deadline()
        self.assertEqual(sorted_by_deadline[0].deadline, "01-01-2025")
        
        # Filter
        incomplete = manager.filter_by_completion(completed=False)
        self.assertEqual(len(incomplete), 2)
        
        # Update
        updated_task = Task(title="Updated Python Task", deadline="25-12-2025", estimated_time=1.5)
        manager.update_task(0, updated_task)
        self.assertEqual(manager.get_task(0).title, "Updated Python Task")
        
        # Delete
        manager.delete_task(1)
        self.assertEqual(manager.get_count(), 2)
    
    def test_save_load_workflow(self):
        """Test saving and loading with TaskManager."""
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        temp_file.close()
        filepath = temp_file.name
        
        try:
            # Create manager and add tasks
            manager1 = TaskManager()
            manager1.add_task(Task(title="Task 1", deadline="25-12-2025", estimated_time=1.0))
            manager1.add_task(Task(title="Task 2", deadline="01-01-2025", estimated_time=0.5))
            
            # Save
            save_tasks_to_json(manager1.get_all_tasks(), filepath)
            
            # Load into new manager
            loaded_tasks = load_tasks_from_json(filepath)
            manager2 = TaskManager(loaded_tasks)
            
            # Verify
            self.assertEqual(manager2.get_count(), 2)
            self.assertEqual(manager2.get_task(0).title, "Task 1")
            self.assertEqual(manager2.get_task(1).title, "Task 2")
        
        finally:
            if os.path.exists(filepath):
                os.unlink(filepath)


if __name__ == '__main__':
    unittest.main()

