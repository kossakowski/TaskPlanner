"""
Entry point for running TaskPlanner as a module: python -m taskplanner
"""

from .gui import TaskPlannerApp


if __name__ == "__main__":
    app = TaskPlannerApp()
    app.run()

