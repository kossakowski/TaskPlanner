"""
Main entry point for TaskPlanner application.
"""

from .gui import TaskPlannerApp


def main():
    """Main function to run the TaskPlanner application."""
    app = TaskPlannerApp()
    app.run()


if __name__ == "__main__":
    main()
