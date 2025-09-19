import streamlit as st
from datetime import datetime
from typing import List, Dict, Optional

class Task:
    """Represents a single task in the to-do list"""
    
    def __init__(self, title: str, description: str = "", status: str = "pending"):
        self.id = self._generate_id()
        self.title = title
        self.description = description
        self.status = status
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
    
    def _generate_id(self) -> int:
        """Generate unique task ID"""
        return len(st.session_state.get('tasks', [])) + 1
    
    def to_dict(self) -> Dict:
        """Convert task to dictionary"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict):
        """Create task from dictionary"""
        task = cls(data["title"], data["description"], data["status"])
        task.id = data["id"]
        task.created_at = data["created_at"]
        task.updated_at = data["updated_at"]
        return task

class TaskManager:
    """Manages tasks using Streamlit session state for persistence"""
    
    def __init__(self):
        self.tasks: List[Task] = []
        self._load_tasks()
    
    def _load_tasks(self):
        """Load tasks from session state"""
        if 'tasks' not in st.session_state:
            st.session_state.tasks = []
        self.tasks = [Task.from_dict(task) for task in st.session_state.tasks]
    
    def _save_tasks(self):
        """Save tasks to session state"""
        st.session_state.tasks = [task.to_dict() for task in self.tasks]
    
    def add_task(self, title: str, description: str = "") -> Task:
        """Add a new task"""
        task = Task(title, description)
        self.tasks.append(task)
        self._save_tasks()
        return task
    
    def get_task_by_id(self, task_id: int) -> Optional[Task]:
        """Get task by ID"""
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None
    
    def update_task(self, task_id: int, **kwargs) -> bool:
        """Update task properties"""
        task = self.get_task_by_id(task_id)
        if task:
            for key, value in kwargs.items():
                if hasattr(task, key):
                    setattr(task, key, value)
            task.updated_at = datetime.now().isoformat()
            self._save_tasks()
            return True
        return False
    
    def delete_task(self, task_id: int) -> bool:
        """Delete task by ID"""
        task = self.get_task_by_id(task_id)
        if task:
            self.tasks.remove(task)
            self._save_tasks()
            return True
        return False
    
    def get_all_tasks(self, status_filter: str = None) -> List[Task]:
        """Get all tasks with optional status filter"""
        if status_filter:
            return [task for task in self.tasks if task.status == status_filter]
        return self.tasks[:]
    
    def get_stats(self) -> Dict:
        """Generate task statistics"""
        total = len(self.tasks)
        pending = len([t for t in self.tasks if t.status == "pending"])
        completed = len([t for t in self.tasks if t.status == "completed"])
        return {
            "total": total,
            "pending": pending,
            "completed": completed,
            "completion_rate": (completed / total * 100) if total > 0 else 0
        }

# Streamlit App UI
st.title("📝 Python To-Do List App")
st.subheader("Built for Data Analysts | Track Tasks & Metrics")

manager = TaskManager()

# Tabs for better UX
tab1, tab2, tab3 = st.tabs(["➕ Add Task", "📋 View Tasks", "📊 Stats"])

with tab1:
    st.header("Add New Task")
    title = st.text_input("Task Title")
    description = st.text_area("Description (optional)")
    if st.button("Add Task"):
        if title:
            manager.add_task(title, description)
            st.success(f"Task '{title}' added!")
        else:
            st.error("Title cannot be empty!")

with tab2:
    st.header("All Tasks")
    tasks = manager.get_all_tasks()
    if not tasks:
        st.info("No tasks yet. Add some!")
    else:
        for task in tasks:
            col1, col2, col3 = st.columns([1, 4, 1])
            with col1:
                st.checkbox("", value=task.status == "completed", key=f"check_{task.id}", on_change=manager.update_task, args=(task.id,), kwargs={"status": "completed" if not task.status == "completed" else "pending"})
            with col2:
                st.write(f"**{task.title}** (ID: {task.id}) - {task.description}")
                st.caption(f"Created: {datetime.fromisoformat(task.created_at).strftime('%Y-%m-%d %H:%M')}")
            with col3:
                if st.button("🗑️", key=f"del_{task.id}"):
                    manager.delete_task(task.id)
                    st.rerun()  # Refresh UI

    st.subheader("Pending Tasks")
    pending = manager.get_all_tasks("pending")
    if pending:
        for task in pending:
            st.write(f"- {task.title} (ID: {task.id})")

with tab3:
    st.header("Task Statistics")
    stats = manager.get_stats()
    st.metric("Total Tasks", stats['total'])
    st.metric("Pending", stats['pending'])
    st.metric("Completed", stats['completed'])
    st.metric("Completion Rate", f"{stats['completion_rate']:.1f}%")
    
    # Progress bar
    st.progress(stats['completion_rate'] / 100)
    
    # For BI: Export to CSV
    if st.button("Export Tasks to CSV"):
        import pandas as pd
        df = pd.DataFrame([t.to_dict() for t in tasks])
        st.download_button("Download CSV", df.to_csv(index=False), "tasks.csv", "text/csv")
