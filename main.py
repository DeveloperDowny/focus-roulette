import random
import json
import os
import tkinter as tk
from tkinter import messagebox, simpledialog
from datetime import datetime, timedelta

class AdaptiveWeightedTaskSelector:
    def __init__(self, tasks_file="tasks.json"):
        self.tasks_file = tasks_file
        self.tasks = {}  # {task_name: {"base_weight": float, "current_weight": float, "cooldown": int}}
        self.history = []
        self.load_tasks()
    
    def load_tasks(self):
        if os.path.exists(self.tasks_file):
            try:
                with open(self.tasks_file, 'r') as f:
                    data = json.load(f)
                    self.tasks = data.get('tasks', {})
                    self.history = data.get('history', [])
            except (json.JSONDecodeError, FileNotFoundError):
                # If file is corrupted or not found, start with empty data
                self.tasks = {}
                self.history = []
        else:
            # File doesn't exist, initialize with empty data
            self.tasks = {}
            self.history = []
    
    def save_tasks(self):
        data = {
            "tasks": self.tasks,
            "history": self.history
        }
        
        with open(self.tasks_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def add_task(self, task_name, base_weight, cooldown_days=3):
        self.tasks[task_name] = {
            "base_weight": base_weight,
            "current_weight": base_weight,
            "cooldown": cooldown_days,
            "last_selected": None
        }
        self.save_tasks()
    
    def remove_task(self, task_name):
        if task_name in self.tasks:
            del self.tasks[task_name]
            self.save_tasks()
            return True
        return False
    
    def update_weight(self, task_name, new_base_weight):
        if task_name in self.tasks:
            task = self.tasks[task_name]
            
            # Calculate the ratio between old and new weight
            ratio = new_base_weight / task["base_weight"] if task["base_weight"] > 0 else 1
            
            # Update base weight
            task["base_weight"] = new_base_weight
            
            # Update current weight proportionally
            task["current_weight"] = task["current_weight"] * ratio
            
            self.save_tasks()
            return True
        return False
    
    def update_cooldown(self, task_name, new_cooldown):
        if task_name in self.tasks:
            self.tasks[task_name]["cooldown"] = new_cooldown
            self.save_tasks()
            return True
        return False
    
    def reset_weights(self):
        """Reset all tasks to their base weights"""
        for task_name in self.tasks:
            self.tasks[task_name]["current_weight"] = self.tasks[task_name]["base_weight"]
        self.save_tasks()
    
    def _adjust_weights(self):
        """Adjust weights based on time since last selection"""
        now = datetime.now()
        
        for task_name, task_data in self.tasks.items():
            last_selected_str = task_data.get("last_selected")
            cooldown_days = task_data.get("cooldown", 3)
            
            if last_selected_str:
                last_selected = datetime.fromisoformat(last_selected_str)
                days_since = (now - last_selected).days
                
                # Calculate recovery percentage (0 to 1)
                recovery = min(1.0, days_since / cooldown_days)
                
                # Gradually restore weight based on time passed
                base_weight = task_data["base_weight"]
                min_weight = base_weight * 0.1  # Minimum weight is 10% of base
                
                # Linear interpolation between min_weight and base_weight
                task_data["current_weight"] = min_weight + recovery * (base_weight - min_weight)
            else:
                # If never selected, use base weight
                task_data["current_weight"] = task_data["base_weight"]
    
    def get_random_task(self):
        if not self.tasks:
            return None
        
        # First adjust all weights based on time since last selection
        self._adjust_weights()
            
        tasks = list(self.tasks.keys())
        weights = [self.tasks[task]["current_weight"] for task in tasks]
        
        # Ensure all weights are positive
        if all(w <= 0 for w in weights):
            # If all weights are zero or negative, reset to base weights
            for task_name in tasks:
                self.tasks[task_name]["current_weight"] = self.tasks[task_name]["base_weight"]
            weights = [self.tasks[task]["current_weight"] for task in tasks]
        
        try:
            selected = random.choices(tasks, weights=weights, k=1)[0]
            
            # Update last selected time
            self.tasks[selected]["last_selected"] = datetime.now().isoformat()
            
            # Reduce the weight temporarily to make it less likely to be selected again soon
            self.tasks[selected]["current_weight"] = self.tasks[selected]["base_weight"] * 0.1
            
            # Record selection
            self.history.append({
                "task": selected,
                "timestamp": datetime.now().isoformat(),
                "weight_used": weights[tasks.index(selected)]
            })
            
            self.save_tasks()
            return selected
        except ValueError as e:
            print(f"Error in selection: {e}")
            print(f"Tasks: {tasks}")
            print(f"Weights: {weights}")
            return None
    
    def get_task_history(self, limit=10):
        return self.history[-limit:]
    
    def get_task_weights(self):
        """Return current weights for UI display"""
        results = {}
        for task_name, task_data in self.tasks.items():
            results[task_name] = {
                "base_weight": task_data["base_weight"],
                "current_weight": task_data["current_weight"],
                "cooldown": task_data["cooldown"],
                "last_selected": task_data.get("last_selected")
            }
        return results


class TaskSelectorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Adaptive Weighted Task Selector")
        self.root.geometry("700x600")
        self.root.resizable(True, True)
        
        self.selector = AdaptiveWeightedTaskSelector()
        
        # Main frame
        self.main_frame = tk.Frame(root, padx=20, pady=20)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Task list frame
        self.task_list_frame = tk.LabelFrame(self.main_frame, text="Tasks & Weights", padx=10, pady=10)
        self.task_list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Task listbox
        self.task_listbox = tk.Listbox(self.task_list_frame, height=10, width=60, font=("Helvetica", 10))
        self.task_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar for task listbox
        self.scrollbar = tk.Scrollbar(self.task_list_frame)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Connect scrollbar to listbox
        self.task_listbox.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.task_listbox.yview)
        
        # Button frame
        self.button_frame = tk.Frame(self.main_frame)
        self.button_frame.pack(fill=tk.X, pady=10)
        
        # Buttons
        self.add_button = tk.Button(self.button_frame, text="Add Task", command=self.add_task)
        self.add_button.pack(side=tk.LEFT, padx=5)
        
        self.remove_button = tk.Button(self.button_frame, text="Remove Task", command=self.remove_task)
        self.remove_button.pack(side=tk.LEFT, padx=5)
        
        self.update_weight_button = tk.Button(self.button_frame, text="Update Weight", command=self.update_weight)
        self.update_weight_button.pack(side=tk.LEFT, padx=5)
        
        self.update_cooldown_button = tk.Button(self.button_frame, text="Update Cooldown", command=self.update_cooldown)
        self.update_cooldown_button.pack(side=tk.LEFT, padx=5)
        
        self.reset_button = tk.Button(self.button_frame, text="Reset All Weights", command=self.reset_weights)
        self.reset_button.pack(side=tk.LEFT, padx=5)
        
        # Random task selection frame
        self.selection_frame = tk.LabelFrame(self.main_frame, text="Random Task Selection", padx=10, pady=10)
        self.selection_frame.pack(fill=tk.BOTH, expand=True)
        
        # Selected task display
        self.selected_task_var = tk.StringVar()
        self.selected_task_var.set("No task selected yet")
        self.selected_task_label = tk.Label(self.selection_frame, textvariable=self.selected_task_var, font=("Helvetica", 14, "bold"))
        self.selected_task_label.pack(pady=10)
        
        # Cooldown info display
        self.cooldown_info_var = tk.StringVar()
        self.cooldown_info_var.set("")
        self.cooldown_info_label = tk.Label(self.selection_frame, textvariable=self.cooldown_info_var)
        self.cooldown_info_label.pack(pady=5)
        
        # Select button
        self.select_button = tk.Button(self.selection_frame, text="Select Random Task", command=self.select_random_task, font=("Helvetica", 12, "bold"))
        self.select_button.pack(pady=10)
        
        # History frame
        self.history_frame = tk.LabelFrame(self.main_frame, text="Task History (Last 5)", padx=10, pady=10)
        self.history_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # History listbox
        self.history_listbox = tk.Listbox(self.history_frame, height=5, font=("Helvetica", 10))
        self.history_listbox.pack(fill=tk.BOTH, expand=True)
        
        # Initial update
        self.update_task_list()
        self.update_history()
    
    def update_task_list(self):
        self.task_listbox.delete(0, tk.END)
        task_weights = self.selector.get_task_weights()
        
        for task_name, data in task_weights.items():
            base_weight = data["base_weight"]
            current_weight = data["current_weight"]
            cooldown = data["cooldown"]
            last_selected = data["last_selected"]
            
            status = ""
            if last_selected:
                last_date = datetime.fromisoformat(last_selected)
                days_ago = (datetime.now() - last_date).days
                hours_ago = int((datetime.now() - last_date).total_seconds() / 3600)
                
                if days_ago > 0:
                    status = f" (selected {days_ago} days ago)"
                else:
                    status = f" (selected {hours_ago} hours ago)"
            
            self.task_listbox.insert(tk.END, f"{task_name} - Base: {base_weight:.1f}, Current: {current_weight:.1f}, Cooldown: {cooldown} days{status}")
    
    def update_history(self):
        self.history_listbox.delete(0, tk.END)
        history = self.selector.get_task_history(5)
        for entry in reversed(history):
            task = entry["task"]
            timestamp = datetime.fromisoformat(entry["timestamp"]).strftime("%Y-%m-%d %H:%M")
            weight = entry.get("weight_used", "N/A")
            self.history_listbox.insert(tk.END, f"{timestamp}: {task} (weight: {weight:.1f})")
    
    def add_task(self):
        task_name = simpledialog.askstring("Add Task", "Enter task name:")
        if task_name:
            try:
                weight = simpledialog.askfloat("Task Weight", "Enter base weight (higher = more frequent):", minvalue=0.1)
                if weight is not None:
                    cooldown = simpledialog.askinteger("Cooldown Period", "Enter cooldown period in days (how long until task returns to full weight):", minvalue=1, initialvalue=3)
                    if cooldown is not None:
                        self.selector.add_task(task_name, weight, cooldown)
                        self.update_task_list()
            except ValueError:
                messagebox.showerror("Invalid Input", "Weight must be a positive number")
    
    def remove_task(self):
        selected_index = self.task_listbox.curselection()
        if selected_index:
            task_entry = self.task_listbox.get(selected_index[0])
            task_name = task_entry.split(" - Base:")[0]
            
            if messagebox.askyesno("Confirm", f"Remove task '{task_name}'?"):
                if self.selector.remove_task(task_name):
                    self.update_task_list()
                else:
                    messagebox.showerror("Error", f"Could not remove task '{task_name}'")
        else:
            messagebox.showinfo("Selection Required", "Please select a task to remove")
    
    def update_weight(self):
        selected_index = self.task_listbox.curselection()
        if selected_index:
            task_entry = self.task_listbox.get(selected_index[0])
            task_name = task_entry.split(" - Base:")[0]
            
            try:
                new_weight = simpledialog.askfloat("Update Weight", 
                                                 f"Enter new base weight for '{task_name}':",
                                                 minvalue=0.1)
                if new_weight is not None:
                    if self.selector.update_weight(task_name, new_weight):
                        self.update_task_list()
                    else:
                        messagebox.showerror("Error", f"Could not update weight for '{task_name}'")
            except ValueError:
                messagebox.showerror("Invalid Input", "Weight must be a positive number")
        else:
            messagebox.showinfo("Selection Required", "Please select a task to update")
    
    def update_cooldown(self):
        selected_index = self.task_listbox.curselection()
        if selected_index:
            task_entry = self.task_listbox.get(selected_index[0])
            task_name = task_entry.split(" - Base:")[0]
            
            try:
                new_cooldown = simpledialog.askinteger("Update Cooldown", 
                                                    f"Enter new cooldown period (in days) for '{task_name}':",
                                                    minvalue=1)
                if new_cooldown is not None:
                    if self.selector.update_cooldown(task_name, new_cooldown):
                        self.update_task_list()
                    else:
                        messagebox.showerror("Error", f"Could not update cooldown for '{task_name}'")
            except ValueError:
                messagebox.showerror("Invalid Input", "Cooldown must be a positive integer")
        else:
            messagebox.showinfo("Selection Required", "Please select a task to update")
    
    def reset_weights(self):
        if messagebox.askyesno("Confirm Reset", "Reset all tasks to their base weights?"):
            self.selector.reset_weights()
            self.update_task_list()
    
    def select_random_task(self):
        task = self.selector.get_random_task()
        if task:
            self.selected_task_var.set(task)
            
            # Show cooldown info
            task_data = self.selector.get_task_weights()[task]
            cooldown_days = task_data["cooldown"]
            self.cooldown_info_var.set(f"This task will return to full weight after {cooldown_days} days")
            
            self.update_task_list()
            self.update_history()
        else:
            messagebox.showinfo("No Tasks", "Please add some tasks first")


if __name__ == "__main__":
    root = tk.Tk()
    app = TaskSelectorApp(root)
    root.mainloop()