import tkinter
import customtkinter as ctk
from sh_gen import ScheduleGenerator
import tkinter.messagebox as messagebox
import re

class ScheduleApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- Window Setup ---
        self.title("Schedule Generator")
        self.geometry("900x750")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")

        # --- Data & Validation ---
        self.appointment_frames = []
        self.goal_frames = []
        self.vcmd = (self.register(self._validate_numeric_input), '%P')

        # --- Main Layout ---
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.scrollable_frame = ctk.CTkScrollableFrame(self, label_text="Your Weekly Schedule Setup")
        self.scrollable_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.scrollable_frame.grid_columnconfigure(0, weight=1)
        
        # --- Create UI Sections ---
        self._create_core_habits_frame()
        self._create_appointments_frame()
        self._create_goals_frame()
        self._create_entertainment_frame()

        # --- Generate Button ---
        generate_button = ctk.CTkButton(self, text="✨ Generate My Schedule ✨", font=("Arial", 18, "bold"), height=50, command=self.run_schedule_generation)
        generate_button.grid(row=1, column=0, pady=(0, 20), padx=10, sticky="ew")

    def _validate_numeric_input(self, value_if_allowed):
        """Allows only integers or floats."""
        if value_if_allowed == "":
            return True
        try:
            float(value_if_allowed)
            return True
        except ValueError:
            return False

    def _validate_time_format(self, time_str):
        """Validate time format and return standardized format"""
        if not time_str or time_str.strip() == "":
            raise ValueError("Time cannot be empty")
        
        time_str = time_str.strip()
        
        # Check for valid time formats: HH:MM, H:MM, HH, H
        if ':' in time_str:
            parts = time_str.split(':')
            if len(parts) != 2:
                raise ValueError(f"Invalid time format: {time_str}. Use HH:MM or H:MM")
            try:
                hours, minutes = int(parts[0]), int(parts[1])
            except ValueError:
                raise ValueError(f"Invalid time format: {time_str}. Hours and minutes must be numbers")
        else:
            try:
                hours = int(time_str)
                minutes = 0
            except ValueError:
                raise ValueError(f"Invalid time format: {time_str}. Use HH:MM, H:MM, or just H")
        
        if not (0 <= hours <= 23):
            raise ValueError(f"Invalid hour: {hours}. Must be between 0-23")
        if not (0 <= minutes <= 59):
            raise ValueError(f"Invalid minutes: {minutes}. Must be between 0-59")
        
        return f"{hours:02d}:{minutes:02d}"

    def _create_spinbox(self, parent, initial_value=0.0, step=0.5):
        """Creates a custom spinbox with an entry and +/- buttons."""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        entry = ctk.CTkEntry(frame, width=80, validate="key", validatecommand=self.vcmd)
        entry.insert(0, str(initial_value))
        
        def increment():
            try:
                val = float(entry.get() or "0") + step
                entry.delete(0, "end")
                entry.insert(0, str(round(val, 2)))
            except ValueError:
                entry.delete(0, "end")
                entry.insert(0, str(initial_value))

        def decrement():
            try:
                val = max(0, float(entry.get() or "0") - step)
                entry.delete(0, "end")
                entry.insert(0, str(round(val, 2)))
            except ValueError:
                entry.delete(0, "end")
                entry.insert(0, str(initial_value))

        plus_button = ctk.CTkButton(frame, text="+", width=30, command=increment)
        minus_button = ctk.CTkButton(frame, text="-", width=30, command=decrement)

        entry.pack(side="left", fill="x", expand=True)
        minus_button.pack(side="left", padx=(5, 2))
        plus_button.pack(side="left")
        return frame, entry

    def _create_core_habits_frame(self):
        frame = ctk.CTkFrame(self.scrollable_frame)
        frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(frame, text="🌙 Sleep Hours:", font=("Arial", 14)).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.sleep_label = ctk.CTkLabel(frame, text="8.0", font=("Arial", 14, "bold"))
        self.sleep_label.grid(row=0, column=2, padx=10)
        self.sleep_slider = ctk.CTkSlider(frame, from_=4, to=12, number_of_steps=16, command=lambda v: self.sleep_label.configure(text=f"{v:.1f}"))
        self.sleep_slider.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        self.sleep_slider.set(8)

        ctk.CTkLabel(frame, text="Wake Up Time:", font=("Arial", 14)).grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.wake_up_entry = ctk.CTkEntry(frame, placeholder_text="e.g., 06:30 or 7")
        self.wake_up_entry.grid(row=1, column=1, columnspan=2, padx=10, pady=10, sticky="ew")

        self.cook_dinner_check = ctk.CTkCheckBox(frame, text="I cook dinner daily", font=("Arial", 14))
        self.cook_dinner_check.grid(row=2, column=0, padx=10, pady=10, sticky="w")
        
        ctk.CTkLabel(frame, text="Cooking Time (hrs):", font=("Arial", 14)).grid(row=3, column=0, padx=10, pady=10, sticky="w")
        self.cooking_time_entry = ctk.CTkEntry(frame, placeholder_text="e.g., 1.5", validate="key", validatecommand=self.vcmd)
        self.cooking_time_entry.grid(row=3, column=1, columnspan=2, padx=10, pady=10, sticky="ew")

    def _create_appointments_frame(self):
        frame = ctk.CTkFrame(self.scrollable_frame)
        frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(frame, text="Fixed Classes & Appointments", font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=10)
        self.appointments_container = ctk.CTkFrame(frame, fg_color="transparent")
        self.appointments_container.grid(row=1, column=0, sticky="ew")
        
        add_button = ctk.CTkButton(frame, text="+ Add Appointment", command=self.add_appointment_fields)
        add_button.grid(row=2, column=0, pady=10)

    def _create_goals_frame(self):
        frame = ctk.CTkFrame(self.scrollable_frame)
        frame.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
        frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(frame, text="Learning Goals", font=("Arial", 16, "bold")).grid(row=0, column=0, pady=10)
        self.goals_container = ctk.CTkFrame(frame, fg_color="transparent")
        self.goals_container.grid(row=1, column=0, sticky="ew")
        
        add_button = ctk.CTkButton(frame, text="+ Add Learning Goal", command=self.add_goal_fields)
        add_button.grid(row=2, column=0, pady=10)

    def _create_entertainment_frame(self):
        frame = ctk.CTkFrame(self.scrollable_frame)
        frame.grid(row=3, column=0, sticky="ew", padx=10, pady=10)
        frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(frame, text="Weekly Free Time (hrs):", font=("Arial", 14)).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.entertainment_label = ctk.CTkLabel(frame, text="10.0", font=("Arial", 14, "bold"))
        self.entertainment_label.grid(row=0, column=2, padx=10)
        self.entertainment_slider = ctk.CTkSlider(frame, from_=0, to=40, number_of_steps=80, command=lambda v: self.entertainment_label.configure(text=f"{v:.1f}"))
        self.entertainment_slider.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        self.entertainment_slider.set(10)

    def add_appointment_fields(self):
        container = ctk.CTkFrame(self.appointments_container)
        container.pack(fill="x", padx=5, pady=5, expand=True)
        container.grid_columnconfigure(1, weight=1)
        
        name_entry = ctk.CTkEntry(container, placeholder_text=f"Appointment #{len(self.appointment_frames) + 1} Name")
        name_entry.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

        days_frame = ctk.CTkFrame(container)
        days_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        days_vars = {day: tkinter.BooleanVar() for day in ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']}
        for i, day in enumerate(days_vars):
            ctk.CTkCheckBox(days_frame, text=day, variable=days_vars[day]).grid(row=0, column=i, padx=4, pady=4)

        start_entry = ctk.CTkEntry(container, placeholder_text="Start Time (16:00)")
        start_entry.grid(row=2, column=0, padx=5, pady=5, sticky="ew")
        end_entry = ctk.CTkEntry(container, placeholder_text="End Time (17:30)")
        end_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        
        ctk.CTkLabel(container, text="Prep Time (hrs):").grid(row=3, column=0, padx=5, sticky="e")
        prep_spinbox, prep_entry = self._create_spinbox(container)
        prep_spinbox.grid(row=3, column=1, padx=5, pady=5, sticky="w")

        ctk.CTkLabel(container, text="Recovery Time (hrs):").grid(row=4, column=0, padx=5, sticky="e")
        post_spinbox, post_entry = self._create_spinbox(container)
        post_spinbox.grid(row=4, column=1, padx=5, pady=5, sticky="w")
        
        def remove_appointment():
            self.appointment_frames = [f for f in self.appointment_frames if f["container"] != container]
            container.destroy()
        
        remove_button = ctk.CTkButton(container, text="Remove", fg_color="#D32F2F", hover_color="#B71C1C", command=remove_appointment)
        remove_button.grid(row=5, column=0, columnspan=2, padx=5, pady=10)
        
        self.appointment_frames.append({
            "container": container, "name": name_entry, "days": days_vars,
            "start": start_entry, "end": end_entry, "prep": prep_entry, "post": post_entry
        })

    def add_goal_fields(self):
        container = ctk.CTkFrame(self.goals_container)
        container.pack(fill="x", padx=5, pady=5, expand=True)
        container.grid_columnconfigure(1, weight=1)
        
        name_entry = ctk.CTkEntry(container, placeholder_text=f"Goal #{len(self.goal_frames) + 1} Name")
        name_entry.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        
        ctk.CTkLabel(container, text="Weekly Hours:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        hours_entry = ctk.CTkEntry(container, validate="key", validatecommand=self.vcmd)
        hours_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
        ctk.CTkLabel(container, text="Priority (1-10):").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        priority_frame = ctk.CTkFrame(container, fg_color="transparent")
        priority_frame.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        priority_frame.grid_columnconfigure(0, weight=1)
        priority_label = ctk.CTkLabel(priority_frame, text="5", font=("Arial", 12, "bold"))
        priority_label.grid(row=0, column=1, padx=5)
        priority_slider = ctk.CTkSlider(priority_frame, from_=1, to=10, number_of_steps=9, command=lambda v: priority_label.configure(text=f"{int(v)}"))
        priority_slider.set(5)
        priority_slider.grid(row=0, column=0, sticky="ew")

        ctk.CTkLabel(container, text="Preferred Time:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        time_combo = ctk.CTkComboBox(container, values=["anytime", "morning", "afternoon", "evening"])
        time_combo.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

        ctk.CTkLabel(container, text="Min Session (hrs):").grid(row=4, column=0, padx=5, pady=5, sticky="e")
        min_spin, min_entry = self._create_spinbox(container, initial_value=0.5, step=0.25)
        min_spin.grid(row=4, column=1, padx=5, pady=5, sticky="w")

        ctk.CTkLabel(container, text="Max Session (hrs):").grid(row=5, column=0, padx=5, pady=5, sticky="e")
        max_spin, max_entry = self._create_spinbox(container, initial_value=2.0, step=0.5)
        max_spin.grid(row=5, column=1, padx=5, pady=5, sticky="w")
        
        def remove_goal():
            self.goal_frames = [f for f in self.goal_frames if f["container"] != container]
            container.destroy()
        
        remove_button = ctk.CTkButton(container, text="Remove", fg_color="#D32F2F", hover_color="#B71C1C", command=remove_goal)
        remove_button.grid(row=6, column=0, columnspan=2, padx=5, pady=10)

        self.goal_frames.append({
            "container": container, "name": name_entry, "hours": hours_entry, "priority": priority_slider,
            "preferred_time": time_combo, "min_session": min_entry, "max_session": max_entry
        })

    def validate_all_inputs(self):
        """Comprehensive validation of all user inputs"""
        errors = []
        
        # Validate wake up time
        try:
            wake_time = self.wake_up_entry.get().strip()
            if not wake_time:
                errors.append("Wake up time is required")
            else:
                self._validate_time_format(wake_time)
        except ValueError as e:
            errors.append(f"Wake up time error: {e}")
        
        # Validate cooking time if cooking is enabled
        if self.cook_dinner_check.get():
            try:
                cooking_time_str = self.cooking_time_entry.get().strip()
                if not cooking_time_str:
                    errors.append("Cooking time is required when cooking is enabled")
                else:
                    cooking_time = float(cooking_time_str)
                    if cooking_time <= 0:
                        errors.append("Cooking time must be greater than 0")
                    elif cooking_time > 12:
                        errors.append("Cooking time cannot exceed 12 hours")
            except ValueError:
                errors.append("Cooking time must be a valid number")
        
        # Validate appointments
        active_appointments = [f for f in self.appointment_frames if f["container"].winfo_exists()]
        for i, frame in enumerate(active_appointments):
            appointment_num = i + 1
            
            # Check name
            if not frame["name"].get().strip():
                errors.append(f"Appointment {appointment_num}: Name is required")
            
            # Check if at least one day is selected
            selected_days = [day for day, var in frame["days"].items() if var.get()]
            if not selected_days:
                errors.append(f"Appointment {appointment_num}: At least one day must be selected")
            
            # Validate start and end times
            try:
                start_time = frame["start"].get().strip()
                if not start_time:
                    errors.append(f"Appointment {appointment_num}: Start time is required")
                else:
                    start_formatted = self._validate_time_format(start_time)
                    
                end_time = frame["end"].get().strip()
                if not end_time:
                    errors.append(f"Appointment {appointment_num}: End time is required")
                else:
                    end_formatted = self._validate_time_format(end_time)
                    
                    # Check if end time is after start time
                    if start_time and end_time:
                        start_mins = self._time_to_minutes(start_formatted)
                        end_mins = self._time_to_minutes(end_formatted)
                        if end_mins <= start_mins:
                            errors.append(f"Appointment {appointment_num}: End time must be after start time")
                            
            except ValueError as e:
                errors.append(f"Appointment {appointment_num}: {e}")
            
            # Validate prep and post times
            try:
                prep_time = float(frame["prep"].get() or "0")
                if prep_time < 0 or prep_time > 12:
                    errors.append(f"Appointment {appointment_num}: Prep time must be between 0-12 hours")
            except ValueError:
                errors.append(f"Appointment {appointment_num}: Prep time must be a valid number")
            
            try:
                post_time = float(frame["post"].get() or "0")
                if post_time < 0 or post_time > 12:
                    errors.append(f"Appointment {appointment_num}: Recovery time must be between 0-12 hours")
            except ValueError:
                errors.append(f"Appointment {appointment_num}: Recovery time must be a valid number")
        
        # Validate learning goals
        active_goals = [f for f in self.goal_frames if f["container"].winfo_exists()]
        if not active_goals:
            errors.append("At least one learning goal is required")
        
        for i, frame in enumerate(active_goals):
            goal_num = i + 1
            
            if not frame["name"].get().strip():
                errors.append(f"Learning Goal {goal_num}: Name is required")
            
            # Validate weekly hours
            try:
                hours_str = frame["hours"].get().strip()
                if not hours_str:
                    errors.append(f"Learning Goal {goal_num}: Weekly hours is required")
                else:
                    hours = float(hours_str)
                    if hours <= 0:
                        errors.append(f"Learning Goal {goal_num}: Weekly hours must be greater than 0")
                    elif hours > 168:  # More than 24*7 hours
                        errors.append(f"Learning Goal {goal_num}: Weekly hours cannot exceed 168 (24h/day * 7 days)")
            except ValueError:
                errors.append(f"Learning Goal {goal_num}: Weekly hours must be a valid number")
            
            # Validate session times
            try:
                min_session = float(frame["min_session"].get() or "0")
                max_session = float(frame["max_session"].get() or "0")
                
                if min_session <= 0:
                    errors.append(f"Learning Goal {goal_num}: Minimum session time must be greater than 0")
                elif min_session > 24:
                    errors.append(f"Learning Goal {goal_num}: Minimum session time cannot exceed 24 hours")
                
                if max_session <= 0:
                    errors.append(f"Learning Goal {goal_num}: Maximum session time must be greater than 0")
                elif max_session > 24:
                    errors.append(f"Learning Goal {goal_num}: Maximum session time cannot exceed 24 hours")
                
                if min_session > max_session:
                    errors.append(f"Learning Goal {goal_num}: Minimum session time cannot be greater than maximum")
                    
            except ValueError:
                errors.append(f"Learning Goal {goal_num}: Session times must be valid numbers")
        
        # Check total weekly hours don't exceed reasonable limits
        try:
            total_goal_hours = sum(float(frame["hours"].get() or "0") for frame in active_goals if frame["name"].get().strip())
            sleep_hours = float(self.sleep_slider.get()) * 7
            cooking_hours = (float(self.cooking_time_entry.get() or "0") * 7) if self.cook_dinner_check.get() else 0
            entertainment_hours = float(self.entertainment_slider.get())
            
            # Calculate approximate appointment hours (rough estimate)
            appointment_hours = 0
            for frame in active_appointments:
                try:
                    if frame["start"].get() and frame["end"].get():
                        start_mins = self._time_to_minutes(self._validate_time_format(frame["start"].get()))
                        end_mins = self._time_to_minutes(self._validate_time_format(frame["end"].get()))
                        duration = (end_mins - start_mins) / 60
                        prep_time = float(frame["prep"].get() or "0")
                        post_time = float(frame["post"].get() or "0")
                        total_duration = duration + prep_time + post_time
                        days_count = sum(1 for var in frame["days"].values() if var.get())
                        appointment_hours += total_duration * days_count
                except:
                    pass
            
            total_committed_hours = sleep_hours + cooking_hours + entertainment_hours + appointment_hours + total_goal_hours
            
            if total_committed_hours > 168:
                excess = total_committed_hours - 168
                errors.append(f"Schedule overbooked by {excess:.1f} hours per week. Reduce learning goals, entertainment time, or appointments.")
                
        except ValueError:
            pass
        
        return errors

    def _time_to_minutes(self, time_str):
        """Helper method to convert time to minutes"""
        hours, minutes = map(int, time_str.split(':'))
        return hours * 60 + minutes

    def run_schedule_generation(self):
        # Validate all inputs first
        errors = self.validate_all_inputs()
        if errors:
            error_message = "Please fix the following errors:\n\n"
            for i, error in enumerate(errors[:10], 1):  # Show max 10 errors
                error_message += f"{i}. {error}\n"
            if len(errors) > 10:
                error_message += f"\n... and {len(errors) - 10} more errors."
            
            self.display_error(error_message)
            return

        user_data = {}
        day_map = {'Mon':'Monday', 'Tue':'Tuesday', 'Wed':'Wednesday', 'Thu':'Thursday', 'Fri':'Friday', 'Sat':'Saturday', 'Sun':'Sunday'}

        try:
            # --- Collect data from GUI ---
            user_data['sleep_duration'] = float(self.sleep_slider.get())
            user_data['wake_up_time'] = self._validate_time_format(self.wake_up_entry.get())
            user_data['cook_dinner'] = bool(self.cook_dinner_check.get())
            user_data['cooking_time'] = float(self.cooking_time_entry.get() or 0) if user_data['cook_dinner'] else 0
            user_data['entertainment_hours'] = float(self.entertainment_slider.get())
            
            # Process appointments
            user_data['fixed_classes'] = []
            active_appointments = [f for f in self.appointment_frames if f["container"].winfo_exists()]
            for frame in active_appointments:
                name = frame["name"].get().strip()
                if name:  # Only add appointments with names
                    selected_days = [day_map[day] for day, var in frame["days"].items() if var.get()]
                    if selected_days:  # Only add if at least one day is selected
                        appointment = {
                            "name": name,
                            "days": selected_days,
                            "start_time": self._validate_time_format(frame["start"].get()),
                            "end_time": self._validate_time_format(frame["end"].get()),
                            "prep_time": float(frame["prep"].get() or 0),
                            "post_time": float(frame["post"].get() or 0)
                        }
                        user_data['fixed_classes'].append(appointment)
            
            # Process learning goals
            user_data['learning_goals'] = []
            active_goals = [f for f in self.goal_frames if f["container"].winfo_exists()]
            for frame in active_goals:
                name = frame["name"].get().strip()
                if name:  # Only add goals with names
                    goal = {
                        "name": name,
                        "weekly_hours": float(frame["hours"].get() or 0),
                        "priority": int(frame["priority"].get()),
                        "preferred_time": frame["preferred_time"].get(),
                        "min_session": float(frame["min_session"].get() or 0.5),
                        "max_session": float(frame["max_session"].get() or 2.0)
                    }
                    user_data['learning_goals'].append(goal)

            # --- Run Backend Logic ---
            scheduler = ScheduleGenerator()
            scheduler.user_data = user_data
            scheduler.user_data['learning_goals'].sort(key=lambda x: x['priority'], reverse=True)
            
            # Initialize and generate schedule
            scheduler.schedule = {day: [] for day in scheduler.days}
            scheduler.add_fixed_commitments()
            scheduler.add_routine_tasks()
            scheduler.schedule_flexible_tasks(scheduler.user_data['learning_goals'], 'learning')
            scheduler.schedule_entertainment()

            self.display_schedule_window(scheduler)

        except ValueError as ve:
            self.display_error(f"Input Error: {ve}\n\nPlease check your input values and try again.")
        except Exception as e:
            self.display_error(f"Unexpected Error: {e}\n\nPlease check all fields are filled correctly and try again.")

    def display_schedule_window(self, scheduler):
        schedule_window = ctk.CTkToplevel(self)
        schedule_window.title("Your Generated Schedule")
        schedule_window.geometry("800x700")
        schedule_window.transient(self)
        
        schedule_window.deiconify()
        schedule_window.lift()
        schedule_window.focus_force()
        
        try:
            schedule_window.after(100, lambda: schedule_window.grab_set())
        except:
            pass

        main_frame = ctk.CTkFrame(schedule_window)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        title_label = ctk.CTkLabel(main_frame, text="📅 Your Personalized Weekly Schedule", 
                                 font=("Arial", 20, "bold"))
        title_label.pack(pady=(10, 20))

        output_text = ""
        total_scheduled_hours = {goal['name']: 0 for goal in scheduler.user_data['learning_goals']}
        
        for day in scheduler.days:
            output_text += f"\n{'='*50}\n"
            output_text += f"{day.upper():^50}\n"
            output_text += f"{'='*50}\n"
            
            day_schedule = sorted(scheduler.schedule.get(day, []), key=lambda x: scheduler.time_to_minutes(x['start']))

            if not day_schedule:
                output_text += "No activities scheduled.\n"
            else:
                for item in day_schedule:
                    # Skip duplicate sleep entries
                    if item.get('task') == 'Sleep' and item.get('start') == '00:00':
                        continue
                    
                    start_time = item.get('start', '')
                    end_time = item.get('end', '')
                    task_name = item.get('task', '')
                    
                    # Calculate duration for learning goals
                    if item.get('type') == 'learning':
                        try:
                            start_mins = scheduler.time_to_minutes(start_time)
                            end_mins = scheduler.time_to_minutes(end_time)
                            duration_hours = (end_mins - start_mins) / 60
                            total_scheduled_hours[task_name] += duration_hours
                        except:
                            pass
                    
                    output_text += f"{start_time:>5} - {end_time:<5} │ {task_name}\n"

        output_text += f"\n\n{'='*50}\n"
        output_text += f"{'WEEKLY SUMMARY':^50}\n"
        output_text += f"{'='*50}\n"
        
        output_text += f"Sleep: {scheduler.user_data['sleep_duration']} hours/night\n"
        output_text += f"Entertainment: {scheduler.user_data['entertainment_hours']} hours/week\n"
        if scheduler.user_data['cook_dinner']:
            output_text += f"Cooking: {scheduler.user_data['cooking_time']} hours/day\n"
        
        output_text += f"\nLEARNING GOALS PROGRESS:\n"
        output_text += f"{'-'*30}\n"
        for goal in scheduler.user_data['learning_goals']:
            target = goal['weekly_hours']
            scheduled = total_scheduled_hours.get(goal['name'], 0)
            percentage = (scheduled / target * 100) if target > 0 else 0
            output_text += f"{goal['name']}: {scheduled:.1f}h / {target:.1f}h ({percentage:.0f}%)\n"

        schedule_textbox = ctk.CTkTextbox(main_frame, font=("Courier New", 12), wrap="word")
        schedule_textbox.pack(expand=True, fill="both", padx=10, pady=10)
        schedule_textbox.insert("0.0", output_text)
        schedule_textbox.configure(state="disabled")

        buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        buttons_frame.pack(fill="x", pady=10)

        def save_and_notify():
            try:
                scheduler.save_schedule()
                messagebox.showinfo("Success", "Schedule has been saved to 'my_schedule.yaml' successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save schedule: {e}")

        def export_to_text():
            try:
                with open("my_schedule.txt", "w", encoding="utf-8") as f:
                    f.write(output_text)
                messagebox.showinfo("Success", "Schedule exported to 'my_schedule.txt' successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export schedule: {e}")

        save_button = ctk.CTkButton(buttons_frame, text="💾 Save YAML", command=save_and_notify)
        save_button.pack(side="left", padx=(0, 10))

        export_button = ctk.CTkButton(buttons_frame, text="📄 Export Text", command=export_to_text)
        export_button.pack(side="left", padx=10)

        close_button = ctk.CTkButton(buttons_frame, text="✖ Close", command=schedule_window.destroy)
        close_button.pack(side="right")

    def display_error(self, message):
        error_window = ctk.CTkToplevel(self)
        error_window.title("Input Validation Error")
        error_window.geometry("500x400")
        error_window.transient(self)
        
        error_window.update_idletasks()
        x = (error_window.winfo_screenwidth() // 2) - (500 // 2)
        y = (error_window.winfo_screenheight() // 2) - (400 // 2)
        error_window.geometry(f"500x400+{x}+{y}")
        
        error_window.deiconify()
        error_window.lift()
        error_window.focus_force()
        
        # Set grab after window is fully visible
        try:
            error_window.after(100, lambda: error_window.grab_set())
        except:
            pass

        main_frame = ctk.CTkFrame(error_window)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        title_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        title_frame.pack(fill="x", pady=(0, 20))

        error_label = ctk.CTkLabel(title_frame, text="⚠️ Please Fix These Issues", 
                                 font=("Arial", 18, "bold"), text_color="#FF6B6B")
        error_label.pack()

        error_textbox = ctk.CTkTextbox(main_frame, font=("Arial", 12), wrap="word")
        error_textbox.pack(expand=True, fill="both", pady=(0, 20))
        error_textbox.insert("0.0", message)
        error_textbox.configure(state="disabled")

        ok_button = ctk.CTkButton(main_frame, text="OK, I'll Fix These", 
                                command=error_window.destroy, width=200, height=40)
        ok_button.pack()

if __name__ == "__main__":
    app = ScheduleApp()
    app.mainloop()