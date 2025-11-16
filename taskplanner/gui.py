"""
GUI module for TaskPlanner application using Tkinter.

This module contains the main application window and all GUI components.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from typing import Optional, List, Tuple
from .core import Task, TaskManager, save_tasks_to_json, load_tasks_from_json, is_valid_date


class TaskPlannerApp:
    """
    Main application class for TaskPlanner GUI.
    
    This class manages the Tkinter interface and coordinates between
    the GUI components and the core task management logic.
    """
    
    def __init__(self, root: Optional[tk.Tk] = None):
        """
        Initialize the TaskPlanner application.
        
        Args:
            root: Optional Tk root window (creates one if not provided)
        """
        if root is None:
            self.root = tk.Tk()
        else:
            self.root = root
        
        self.root.title("TaskPlanner")
        self.root.geometry("1000x700")
        
        # Initialize task manager and load tasks
        self.task_manager = TaskManager()
        self.current_selected_index: Optional[int] = None
        self.current_sort_mode: str = "none"  # "none", "deadline", "title", "completion"
        self.current_filter_completed: Optional[bool] = None
        
        try:
            tasks = load_tasks_from_json()
            for task in tasks:
                self.task_manager.add_task(task)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load tasks: {e}")
        
        # Create GUI components
        self._create_widgets()
        
        # Refresh the task list display
        self._refresh_task_list()
    
    def _create_widgets(self):
        """Create and layout all GUI widgets."""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Left panel: Input/Edit section
        input_frame = ttk.LabelFrame(main_frame, text="Task Input/Edit", padding="10")
        input_frame.grid(row=0, column=0, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        input_frame.columnconfigure(1, weight=1)
        
        # Title field
        ttk.Label(input_frame, text="Title *:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.title_entry = ttk.Entry(input_frame, width=30)
        self.title_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        
        # Deadline field
        ttk.Label(input_frame, text="Deadline (DD-MM-YYYY) *:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.deadline_entry = ttk.Entry(input_frame, width=30)
        self.deadline_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        
        # Estimated time field
        ttk.Label(input_frame, text="Estimated time (minutes) *:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.time_entry = ttk.Entry(input_frame, width=30)
        self.time_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        
        # Notes field
        ttk.Label(input_frame, text="Notes / Hints:").grid(row=3, column=0, sticky=(tk.W, tk.N), pady=5)
        self.notes_text = scrolledtext.ScrolledText(input_frame, width=30, height=6, wrap=tk.WORD)
        self.notes_text.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        
        # Completion status checkbox
        self.completed_var = tk.BooleanVar()
        self.completed_checkbox = ttk.Checkbutton(
            input_frame,
            text="Mark as completed",
            variable=self.completed_var
        )
        self.completed_checkbox.grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Buttons frame
        buttons_frame = ttk.Frame(input_frame)
        buttons_frame.grid(row=5, column=0, columnspan=2, pady=10)
        
        ttk.Button(buttons_frame, text="Add Task", command=self._add_task).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Update Task", command=self._update_task).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Delete Task", command=self._delete_task).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Clear Form", command=self._clear_form).pack(side=tk.LEFT, padx=5)
        
        # Right panel: Task list and controls
        list_frame = ttk.LabelFrame(main_frame, text="Task List", padding="10")
        list_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(1, weight=1)
        
        # Search and filter section
        search_frame = ttk.Frame(list_frame)
        search_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        search_frame.columnconfigure(1, weight=1)
        
        ttk.Label(search_frame, text="Search:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.search_entry = ttk.Entry(search_frame)
        self.search_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        self.search_entry.bind('<KeyRelease>', lambda e: self._search_tasks())
        
        ttk.Button(search_frame, text="Search", command=self._search_tasks).grid(row=0, column=2, padx=5)
        
        # Sort and filter buttons
        sort_filter_frame = ttk.Frame(list_frame)
        sort_filter_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(sort_filter_frame, text="Sort:").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(sort_filter_frame, text="By Deadline", command=lambda: self._sort_tasks("deadline")).pack(side=tk.LEFT, padx=2)
        ttk.Button(sort_filter_frame, text="By Title", command=lambda: self._sort_tasks("title")).pack(side=tk.LEFT, padx=2)
        ttk.Button(sort_filter_frame, text="By Status", command=lambda: self._sort_tasks("completion")).pack(side=tk.LEFT, padx=2)
        ttk.Button(sort_filter_frame, text="Reset Sort", command=lambda: self._sort_tasks("none")).pack(side=tk.LEFT, padx=2)
        
        ttk.Label(sort_filter_frame, text="Filter:").pack(side=tk.LEFT, padx=(10, 5))
        ttk.Button(sort_filter_frame, text="All", command=lambda: self._filter_tasks(None)).pack(side=tk.LEFT, padx=2)
        ttk.Button(sort_filter_frame, text="Completed", command=lambda: self._filter_tasks(True)).pack(side=tk.LEFT, padx=2)
        ttk.Button(sort_filter_frame, text="Not Completed", command=lambda: self._filter_tasks(False)).pack(side=tk.LEFT, padx=2)
        
        # Task list treeview
        tree_frame = ttk.Frame(list_frame)
        tree_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        # Create treeview with columns
        columns = ("Title", "Deadline", "Estimated Time", "Status")
        self.task_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
        
        # Configure column headings
        self.task_tree.heading("Title", text="Title")
        self.task_tree.heading("Deadline", text="Deadline")
        self.task_tree.heading("Estimated Time", text="Estimated Time (min)")
        self.task_tree.heading("Status", text="Status")
        
        # Configure column widths
        self.task_tree.column("Title", width=200)
        self.task_tree.column("Deadline", width=120)
        self.task_tree.column("Estimated Time", width=150)
        self.task_tree.column("Status", width=100)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.task_tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.task_tree.xview)
        self.task_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid treeview and scrollbars
        self.task_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Bind selection event
        self.task_tree.bind('<<TreeviewSelect>>', self._on_task_select)
        
        # Mark complete button
        action_frame = ttk.Frame(list_frame)
        action_frame.grid(row=3, column=0, pady=(10, 0))
        
        ttk.Button(action_frame, text="Toggle Completion", command=self._toggle_completion).pack(side=tk.LEFT, padx=5)
    
    def _get_form_data(self) -> dict:
        """
        Get data from the input form.
        
        Returns:
            Dictionary with form data
        """
        return {
            "title": self.title_entry.get().strip(),
            "deadline": self.deadline_entry.get().strip(),
            "estimated_time": self.time_entry.get().strip(),
            "notes": self.notes_text.get("1.0", tk.END).strip(),
            "completed": self.completed_var.get()
        }
    
    def _clear_form(self):
        """Clear all input fields."""
        self.title_entry.delete(0, tk.END)
        self.deadline_entry.delete(0, tk.END)
        self.time_entry.delete(0, tk.END)
        self.notes_text.delete("1.0", tk.END)
        self.completed_var.set(False)
        self.current_selected_index = None
        self.task_tree.selection_remove(self.task_tree.selection())
    
    def _validate_form(self) -> Tuple[bool, str]:
        """
        Validate form data.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        data = self._get_form_data()
        
        if not data["title"]:
            return False, "Title is required"
        
        if not data["deadline"]:
            return False, "Deadline is required"
        
        if not is_valid_date(data["deadline"]):
            return False, f"Invalid deadline format. Please use DD-MM-YYYY format (e.g., 25-12-2025)"
        
        if not data["estimated_time"]:
            return False, "Estimated time is required"
        
        try:
            time_value = int(data["estimated_time"])
            if time_value < 0:
                return False, "Estimated time must be a non-negative number"
        except ValueError:
            return False, "Estimated time must be a valid integer (minutes)"
        
        return True, ""
    
    def _add_task(self):
        """Add a new task."""
        is_valid, error_msg = self._validate_form()
        if not is_valid:
            messagebox.showerror("Validation Error", error_msg)
            return
        
        data = self._get_form_data()
        
        try:
            task = Task(
                title=data["title"],
                deadline=data["deadline"],
                estimated_time=int(data["estimated_time"]),
                notes=data["notes"],
                completed=data["completed"]
            )
            
            self.task_manager.add_task(task)
            self._save_tasks()
            self._clear_form()
            self._refresh_task_list()
            messagebox.showinfo("Success", "Task added successfully!")
        
        except ValueError as e:
            messagebox.showerror("Error", str(e))
    
    def _update_task(self):
        """Update the currently selected task."""
        if self.current_selected_index is None:
            messagebox.showwarning("No Selection", "Please select a task to update.")
            return
        
        is_valid, error_msg = self._validate_form()
        if not is_valid:
            messagebox.showerror("Validation Error", error_msg)
            return
        
        data = self._get_form_data()
        
        try:
            task = Task(
                title=data["title"],
                deadline=data["deadline"],
                estimated_time=int(data["estimated_time"]),
                notes=data["notes"],
                completed=data["completed"]
            )
            
            self.task_manager.update_task(self.current_selected_index, task)
            self._save_tasks()
            self._refresh_task_list()
            messagebox.showinfo("Success", "Task updated successfully!")
        
        except (ValueError, IndexError) as e:
            messagebox.showerror("Error", str(e))
    
    def _delete_task(self):
        """Delete the currently selected task."""
        if self.current_selected_index is None:
            messagebox.showwarning("No Selection", "Please select a task to delete.")
            return
        
        # Confirm deletion
        if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this task?"):
            return
        
        try:
            self.task_manager.delete_task(self.current_selected_index)
            self._save_tasks()
            self._clear_form()
            self._refresh_task_list()
            messagebox.showinfo("Success", "Task deleted successfully!")
        
        except IndexError as e:
            messagebox.showerror("Error", str(e))
    
    def _toggle_completion(self):
        """Toggle completion status of the selected task."""
        if self.current_selected_index is None:
            messagebox.showwarning("No Selection", "Please select a task to toggle completion.")
            return
        
        try:
            self.task_manager.toggle_completion(self.current_selected_index)
            self._save_tasks()
            self._refresh_task_list()
            
            # Update form checkbox
            task = self.task_manager.get_task(self.current_selected_index)
            self.completed_var.set(task.completed)
        
        except IndexError as e:
            messagebox.showerror("Error", str(e))
    
    def _on_task_select(self, event):
        """Handle task selection in the treeview."""
        selection = self.task_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        # Get the index from the item tags or store it in the item
        # We'll use the item's index in the displayed list
        values = self.task_tree.item(item, 'values')
        if not values:
            return
        
        # Find the task in the current display list
        title = values[0]
        deadline = values[1]
        
        # Find matching task index in the manager
        all_tasks = self._get_displayed_tasks()
        for idx, task in enumerate(all_tasks):
            if task.title == title and task.deadline == deadline:
                self.current_selected_index = self._get_actual_index(idx)
                self._load_task_to_form(task)
                break
    
    def _get_displayed_tasks(self) -> List[Task]:
        """Get the list of tasks currently displayed (after search/filter/sort)."""
        tasks = self.task_manager.get_all_tasks()
        
        # Apply search
        search_query = self.search_entry.get().strip()
        if search_query:
            tasks = self.task_manager.search_by_title(search_query)
        
        # Apply filter
        if self.current_filter_completed is not None:
            tasks = [t for t in tasks if t.completed == self.current_filter_completed]
        
        # Apply sort
        if self.current_sort_mode == "deadline":
            tasks = self.task_manager.sort_by_deadline()
            # Re-apply search and filter after sort
            if search_query:
                tasks = [t for t in tasks if search_query.lower() in t.title.lower()]
            if self.current_filter_completed is not None:
                tasks = [t for t in tasks if t.completed == self.current_filter_completed]
        elif self.current_sort_mode == "title":
            tasks = self.task_manager.sort_by_title()
            if search_query:
                tasks = [t for t in tasks if search_query.lower() in t.title.lower()]
            if self.current_filter_completed is not None:
                tasks = [t for t in tasks if t.completed == self.current_filter_completed]
        elif self.current_sort_mode == "completion":
            tasks = self.task_manager.sort_by_completion(completed_first=True)
            if search_query:
                tasks = [t for t in tasks if search_query.lower() in t.title.lower()]
            if self.current_filter_completed is not None:
                tasks = [t for t in tasks if t.completed == self.current_filter_completed]
        
        return tasks
    
    def _get_actual_index(self, display_index: int) -> int:
        """
        Convert display index to actual task manager index.
        
        Args:
            display_index: Index in the displayed/filtered list
            
        Returns:
            Actual index in task manager
        """
        displayed_tasks = self._get_displayed_tasks()
        if display_index >= len(displayed_tasks):
            return -1
        
        displayed_task = displayed_tasks[display_index]
        all_tasks = self.task_manager.get_all_tasks()
        
        for idx, task in enumerate(all_tasks):
            if (task.title == displayed_task.title and 
                task.deadline == displayed_task.deadline and
                task.estimated_time == displayed_task.estimated_time):
                return idx
        
        return -1
    
    def _load_task_to_form(self, task: Task):
        """Load a task's data into the input form."""
        self.title_entry.delete(0, tk.END)
        self.title_entry.insert(0, task.title)
        
        self.deadline_entry.delete(0, tk.END)
        self.deadline_entry.insert(0, task.deadline)
        
        self.time_entry.delete(0, tk.END)
        self.time_entry.insert(0, str(task.estimated_time))
        
        self.notes_text.delete("1.0", tk.END)
        self.notes_text.insert("1.0", task.notes)
        
        self.completed_var.set(task.completed)
    
    def _refresh_task_list(self):
        """Refresh the task list display."""
        # Clear existing items
        for item in self.task_tree.get_children():
            self.task_tree.delete(item)
        
        # Get tasks to display
        tasks = self._get_displayed_tasks()
        
        # Add tasks to treeview
        for task in tasks:
            status = "Done" if task.completed else "Not done"
            item = self.task_tree.insert(
                "",
                tk.END,
                values=(task.title, task.deadline, task.estimated_time, status),
                tags=("completed" if task.completed else "not_completed",)
            )
        
        # Configure tags for visual distinction
        self.task_tree.tag_configure("completed", foreground="gray")
        self.task_tree.tag_configure("not_completed", foreground="black")
    
    def _search_tasks(self):
        """Perform search and refresh the task list."""
        self._refresh_task_list()
    
    def _sort_tasks(self, mode: str):
        """Sort tasks by the specified mode."""
        self.current_sort_mode = mode
        self.current_selected_index = None  # Clear selection when sorting
        self._refresh_task_list()
    
    def _filter_tasks(self, completed: Optional[bool]):
        """Filter tasks by completion status."""
        self.current_filter_completed = completed
        self.current_selected_index = None  # Clear selection when filtering
        self._refresh_task_list()
    
    def _save_tasks(self):
        """Save tasks to JSON file."""
        try:
            save_tasks_to_json(self.task_manager.get_all_tasks())
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save tasks: {e}")
    
    def run(self):
        """Start the application main loop."""
        self.root.mainloop()

