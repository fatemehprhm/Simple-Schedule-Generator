import tkinter
import customtkinter as ctk
from sh_gen import ScheduleGenerator

class ScheduleApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- Window Setup ---
        self.title("Advanced Schedule Generator")
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

    def _create_spinbox(self, parent, initial_value=0.0, step=0.5):
        """Creates a custom spinbox with an entry and +/- buttons."""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        entry = ctk.CTkEntry(frame, width=80, validate="key", validatecommand=self.vcmd)
        entry.insert(0, str(initial_value))
        
        def increment():
            try:
                val = float(entry.get()) + step
                entry.delete(0, "end")
                entry.insert(0, str(round(val, 2)))
            except ValueError:
                pass

        def decrement():
            try:
                val = max(0, float(entry.get()) - step)
                entry.delete(0, "end")
                entry.insert(0, str(round(val, 2)))
            except ValueError:
                pass

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
        
        remove_button = ctk.CTkButton(container, text="Remove", fg_color="#D32F2F", hover_color="#B71C1C", command=container.destroy)
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
        
        remove_button = ctk.CTkButton(container, text="Remove", fg_color="#D32F2F", hover_color="#B71C1C", command=container.destroy)
        remove_button.grid(row=6, column=0, columnspan=2, padx=5, pady=10)

        self.goal_frames.append({
            "container": container, "name": name_entry, "hours": hours_entry, "priority": priority_slider,
            "preferred_time": time_combo, "min_session": min_entry, "max_session": max_entry
        })

    def run_schedule_generation(self):
        user_data = {}
        day_map = {'Mon':'Monday', 'Tue':'Tuesday', 'Wed':'Wednesday', 'Thu':'Thursday', 'Fri':'Friday', 'Sat':'Saturday', 'Sun':'Sunday'}

        try:
            # --- Collect data from GUI ---
            user_data['sleep_duration'] = float(self.sleep_slider.get())
            user_data['wake_up_time'] = self.wake_up_entry.get()
            user_data['cook_dinner'] = bool(self.cook_dinner_check.get())
            user_data['cooking_time'] = float(self.cooking_time_entry.get() or 0)
            user_data['entertainment_hours'] = float(self.entertainment_slider.get())
            
            user_data['fixed_classes'] = [
                {
                    "name": frame["name"].get(),
                    "days": [day_map[day] for day, var in frame["days"].items() if var.get()],
                    "start_time": frame["start"].get(), "end_time": frame["end"].get(),
                    "prep_time": float(frame["prep"].get() or 0),
                    "post_time": float(frame["post"].get() or 0)
                }
                for frame in self.appointment_frames if frame["container"].winfo_exists() and frame["name"].get()
            ]
            
            user_data['learning_goals'] = [
                {
                    "name": frame["name"].get(),
                    "weekly_hours": float(frame["hours"].get() or 0),
                    "priority": int(frame["priority"].get()),
                    "preferred_time": frame["preferred_time"].get(),
                    "min_session": float(frame["min_session"].get() or 0),
                    "max_session": float(frame["max_session"].get() or 0)
                }
                for frame in self.goal_frames if frame["container"].winfo_exists() and frame["name"].get()
            ]

            # --- Run Backend Logic ---
            scheduler = ScheduleGenerator()
            scheduler.user_data = user_data
            scheduler.user_data['learning_goals'].sort(key=lambda x: x['priority'], reverse=True)
            
            scheduler.schedule = {day: [] for day in scheduler.days} # Reset
            scheduler.add_fixed_commitments()
            scheduler.add_routine_tasks()
            scheduler.schedule_flexible_tasks(scheduler.user_data['learning_goals'], 'learning')
            scheduler.schedule_entertainment()

            self.display_schedule_window(scheduler)

        except Exception as e:
            self.display_error(f"An error occurred: {e}\nPlease check all fields are filled correctly.")

    def display_schedule_window(self, scheduler):
        schedule_window = ctk.CTkToplevel(self)
        schedule_window.title("Your Generated Schedule")
        schedule_window.geometry("700x600")

        output_text = ""
        for day in scheduler.days:
            output_text += f"{day.upper()}\n" + "-" * 20 + "\n"
            day_schedule = sorted(scheduler.schedule.get(day, []), key=lambda x: scheduler.time_to_minutes(x['start']))
            
            if not day_schedule:
                output_text += "No activities scheduled.\n"
            else:
                for item in day_schedule:
                    if item.get('task') == 'Sleep' and item.get('start') == '00:00': continue
                    output_text += f"{item.get('start', '')}-{item.get('end', '')} | {item.get('task', '')}\n"
            output_text += "\n"

        schedule_textbox = ctk.CTkTextbox(schedule_window, font=("Courier", 13), wrap="word")
        schedule_textbox.pack(expand=True, fill="both", padx=10, pady=10)
        schedule_textbox.insert("0.0", output_text)
        schedule_textbox.configure(state="disabled")

        save_button = ctk.CTkButton(schedule_window, text="Save to File", command=scheduler.save_schedule)
        save_button.pack(pady=10, padx=10)

    def display_error(self, message):
        error_window = ctk.CTkToplevel(self)
        error_window.title("Error")
        error_window.transient(self)
        error_window.grab_set()
        ctk.CTkLabel(error_window, text=message, wraplength=380, font=("Arial", 14), text_color="#E57373").pack(expand=True, padx=20, pady=20)
        ctk.CTkButton(error_window, text="OK", command=error_window.destroy, width=100).pack(pady=10)

if __name__ == "__main__":
    app = ScheduleApp()
    app.mainloop()