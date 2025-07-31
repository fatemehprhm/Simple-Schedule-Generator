from datetime import datetime, timedelta
import yaml

class ScheduleGenerator:
    def __init__(self):
        self.days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        self.schedule = {day: [] for day in self.days}
        self.user_data = {}
        
    def collect_user_data(self):
        """Collect all user preferences and constraints"""
        print("=== Personal Schedule Generator ===\n")
        
        # Basic preferences
        self.user_data['sleep_duration'] = int(input("How many hours of sleep do you need per night? "))
        
        print("Time format examples: '07:30', '7:30', or just '7' for 7:00")
        self.user_data['wake_up_time'] = input("What time do you prefer to wake up? ")
        
        # Cooking preferences
        cook_dinner = input("Do you cook dinner daily? (y/n): ").lower() == 'y'
        self.user_data['cook_dinner'] = cook_dinner
        if cook_dinner:
            self.user_data['cooking_time'] = float(input("How many hours does cooking take? "))
        else:
            self.user_data['cooking_time'] = 0
            
        # Fixed classes/appointments
        self.user_data['fixed_classes'] = []
        while True:
            add_class = input("Do you have any fixed classes/appointments to add? (y/n): ").lower()
            if add_class != 'y':
                break
                
            class_info = {}
            class_info['name'] = input("Class/appointment name: ")
            class_info['days'] = input("Which days? (comma-separated, e.g., Monday,Wednesday,Friday): ").split(',')
            class_info['days'] = [day.strip() for day in class_info['days']]
            class_info['start_time'] = input("Start time (examples: '16:00', '16', '4:30'): ")
            class_info['end_time'] = input("End time (examples: '17:00', '17', '5:30'): ")
            
            needs_prep = input("Do you need preparation time before? (y/n): ").lower() == 'y'
            if needs_prep:
                class_info['prep_time'] = float(input("How many hours of prep time? "))
            else:
                class_info['prep_time'] = 0
                
            needs_post = input("Do you need recovery time after? (y/n): ").lower() == 'y'
            if needs_post:
                class_info['post_time'] = float(input("How many hours of recovery time? "))
            else:
                class_info['post_time'] = 0
                
            self.user_data['fixed_classes'].append(class_info)
        
        # Learning goals
        self.user_data['learning_goals'] = []
        while True:
            add_goal = input("Do you have learning goals to add? (y/n): ").lower()
            if add_goal != 'y':
                break
                
            goal = {}
            goal['name'] = input("Learning goal name: ")
            goal['weekly_hours'] = float(input("How many hours per week for this goal? "))
            goal['priority'] = int(input("Priority level (1-10, 10 being highest): "))
            goal['preferred_time'] = input("Preferred time of day (morning/afternoon/evening/anytime): ").lower()
            goal['min_session'] = float(input("Minimum session length in hours (e.g., 0.5): "))
            goal['max_session'] = float(input("Maximum session length in hours (e.g., 4): "))
            
            self.user_data['learning_goals'].append(goal)
        
        # Entertainment time
        self.user_data['entertainment_hours'] = float(input("How many hours of entertainment/free time do you want per week? "))
        
        # Sort learning goals by priority
        self.user_data['learning_goals'].sort(key=lambda x: x['priority'], reverse=True)
        
    def time_to_minutes(self, time_str):
        """Convert time string to minutes since midnight"""
        time_str = time_str.strip()
        
        # Handle different time formats
        if ':' in time_str:
            # Format: HH:MM or H:MM
            parts = time_str.split(':')
            if len(parts) == 2:
                hours, minutes = map(int, parts)
            else:
                raise ValueError(f"Invalid time format: {time_str}")
        else:
            # Format: just hour (e.g., "7" or "07")
            hours = int(time_str)
            minutes = 0
            
        # Validate time
        if not (0 <= hours <= 23 and 0 <= minutes <= 59):
            raise ValueError(f"Invalid time: {time_str}")
            
        return hours * 60 + minutes
    
    def minutes_to_time(self, minutes):
        """Convert minutes since midnight to HH:MM"""
        minutes = int(minutes)  # Ensure we have an integer
        hours = minutes // 60
        mins = minutes % 60
        return f"{hours:02d}:{mins:02d}"
    
    def add_fixed_commitments(self):
        """Add fixed classes and cooking to schedule"""
        # Add sleep
        wake_time = self.time_to_minutes(self.user_data['wake_up_time'])
        sleep_duration_mins = self.user_data['sleep_duration'] * 60
        sleep_time = (wake_time - sleep_duration_mins) % (24 * 60)
        
        for day in self.days:
            # Add sleep
            if sleep_time < wake_time:
                self.schedule[day].append({
                    'task': 'Sleep',
                    'start': self.minutes_to_time(sleep_time),
                    'end': self.user_data['wake_up_time'],
                    'type': 'fixed'
                })
            else:
                # Sleep crosses midnight
                self.schedule[day].append({
                    'task': 'Sleep',
                    'start': self.minutes_to_time(sleep_time),
                    'end': '23:59',
                    'type': 'fixed'
                })
                self.schedule[day].append({
                    'task': 'Sleep',
                    'start': '00:00',
                    'end': self.user_data['wake_up_time'],
                    'type': 'fixed'
                })
            
            # Add cooking
            if self.user_data['cook_dinner']:
                cooking_duration = int(self.user_data['cooking_time'] * 60)
                # Default dinner time 18:00-20:00, adjust based on cooking time
                dinner_start = 18 * 60  # 18:00
                self.schedule[day].append({
                    'task': 'Cooking Dinner',
                    'start': self.minutes_to_time(dinner_start),
                    'end': self.minutes_to_time(dinner_start + cooking_duration),
                    'type': 'fixed'
                })
                
                # Add dinner time (30 minutes after cooking)
                dinner_time = dinner_start + cooking_duration
                self.schedule[day].append({
                    'task': 'Dinner',
                    'start': self.minutes_to_time(dinner_time),
                    'end': self.minutes_to_time(dinner_time + 60),
                    'type': 'fixed'
                })
        
        # Add fixed classes
        for class_info in self.user_data['fixed_classes']:
            for day in class_info['days']:
                if day in self.days:
                    start_mins = self.time_to_minutes(class_info['start_time'])
                    end_mins = self.time_to_minutes(class_info['end_time'])
                    
                    # Add prep time
                    if class_info['prep_time'] > 0:
                        prep_duration = int(class_info['prep_time'] * 60)
                        prep_start = start_mins - prep_duration
                        self.schedule[day].append({
                            'task': f"{class_info['name']} - Preparation",
                            'start': self.minutes_to_time(prep_start),
                            'end': class_info['start_time'],
                            'type': 'fixed'
                        })
                    
                    # Add main class
                    self.schedule[day].append({
                        'task': class_info['name'],
                        'start': class_info['start_time'],
                        'end': class_info['end_time'],
                        'type': 'fixed'
                    })
                    
                    # Add recovery time
                    if class_info['post_time'] > 0:
                        post_duration = int(class_info['post_time'] * 60)
                        self.schedule[day].append({
                            'task': f"{class_info['name']} - Recovery",
                            'start': class_info['end_time'],
                            'end': self.minutes_to_time(end_mins + post_duration),
                            'type': 'fixed'
                        })
    
    def get_available_slots(self, day):
        """Get available time slots for a given day"""
        day_schedule = sorted(self.schedule[day], key=lambda x: self.time_to_minutes(x['start']))
        available_slots = []
        
        current_time = self.time_to_minutes(self.user_data['wake_up_time'])
        end_of_day = self.time_to_minutes(self.user_data['wake_up_time']) + 24 * 60 - self.user_data['sleep_duration'] * 60
        
        for item in day_schedule:
            if item['type'] == 'fixed':
                item_start = self.time_to_minutes(item['start'])
                if current_time < item_start:
                    available_slots.append((current_time, item_start))
                current_time = max(current_time, self.time_to_minutes(item['end']))
        
        # Add remaining time at end of day
        if current_time < end_of_day:
            available_slots.append((current_time, end_of_day))
        
        return available_slots
    
    def schedule_learning_goals(self):
        """Schedule learning goals based on priority and preferences"""
        # Calculate how much time each goal needs per day on average
        goal_daily_minutes = {}
        for goal in self.user_data['learning_goals']:
            goal_daily_minutes[goal['name']] = (goal['weekly_hours'] * 60) / 7
        
        # Track scheduled time for each goal
        scheduled_time = {goal['name']: 0 for goal in self.user_data['learning_goals']}
        
        # Schedule high-priority goals first
        for goal in self.user_data['learning_goals']:
            target_weekly_mins = goal['weekly_hours'] * 60
            min_session_mins = int(goal['min_session'] * 60)
            max_session_mins = int(goal['max_session'] * 60)
            
            for day in self.days:
                if scheduled_time[goal['name']] >= target_weekly_mins:
                    break
                    
                available_slots = self.get_available_slots(day)
                
                for start_mins, end_mins in available_slots:
                    slot_duration = end_mins - start_mins
                    
                    if slot_duration >= min_session_mins:
                        # Determine session length
                        needed_time = target_weekly_mins - scheduled_time[goal['name']]
                        session_length = min(slot_duration, max_session_mins, needed_time)
                        session_length = int(session_length)  # Ensure integer
                        
                        if session_length >= min_session_mins:
                            # Add to schedule
                            self.schedule[day].append({
                                'task': goal['name'],
                                'start': self.minutes_to_time(start_mins),
                                'end': self.minutes_to_time(start_mins + session_length),
                                'type': 'learning'
                            })
                            
                            scheduled_time[goal['name']] += session_length
                            break
    
    def add_routine_tasks(self):
        """Add routine tasks like meals and breaks"""
        for day in self.days:
            # Add lunch break if there's space around noon
            available_slots = self.get_available_slots(day)
            for start_mins, end_mins in available_slots:
                if 11 * 60 <= start_mins <= 14 * 60 and (end_mins - start_mins) >= 60:
                    self.schedule[day].append({
                        'task': 'Lunch Break',
                        'start': '12:30',
                        'end': '13:30',
                        'type': 'break'
                    })
                    break
    
    def schedule_flexible_tasks(self, tasks, task_type):
        """Generic method to schedule flexible tasks"""
        if task_type == 'learning':
            self.schedule_learning_goals()
    
    def schedule_entertainment(self):
        """Schedule entertainment time"""
        entertainment_per_day = (self.user_data['entertainment_hours'] * 60) / 7
        
        for day in self.days:
            available_slots = self.get_available_slots(day)
            for start_mins, end_mins in available_slots:
                slot_duration = end_mins - start_mins
                if slot_duration >= entertainment_per_day:
                    entertainment_duration = int(min(entertainment_per_day, 120))  # Max 2 hours per day
                    self.schedule[day].append({
                        'task': 'Entertainment/Free Time',
                        'start': self.minutes_to_time(start_mins),
                        'end': self.minutes_to_time(start_mins + entertainment_duration),
                        'type': 'entertainment'
                    })
                    break
    
    def add_breaks_and_entertainment(self):
        """Add breaks, meals, and entertainment time"""
        entertainment_per_day = (self.user_data['entertainment_hours'] * 60) / 7
        
        for day in self.days:
            available_slots = self.get_available_slots(day)
            
            # Add lunch break
            for start_mins, end_mins in available_slots:
                if 12 * 60 <= start_mins <= 14 * 60 and (end_mins - start_mins) >= 60:
                    self.schedule[day].append({
                        'task': 'Lunch Break',
                        'start': '12:30',
                        'end': '13:30',
                        'type': 'break'
                    })
                    break
            
            # Add entertainment time
            available_slots = self.get_available_slots(day)
            for start_mins, end_mins in available_slots:
                slot_duration = end_mins - start_mins
                if slot_duration >= entertainment_per_day:
                    entertainment_duration = int(min(entertainment_per_day, 120))  # Max 2 hours per day
                    self.schedule[day].append({
                        'task': 'Entertainment/Free Time',
                        'start': self.minutes_to_time(start_mins),
                        'end': self.minutes_to_time(start_mins + entertainment_duration),
                        'type': 'entertainment'
                    })
                    break
    
    def print_schedule(self):
        """Print the generated schedule"""
        print("\n" + "="*50)
        print("GENERATED WEEKLY SCHEDULE")
        print("="*50)
        
        for day in self.days:
            print(f"\n{day.upper()}:")
            print("-" * 30)
            
            day_schedule = sorted(self.schedule[day], key=lambda x: self.time_to_minutes(x['start']))
            
            for item in day_schedule:
                print(f"{item['start']}-{item['end']} | {item['task']}")
    
    def save_schedule(self, filename="my_schedule.yaml"):
        """Save schedule to YAML file"""
        with open(filename, 'w') as f:
            yaml.dump({
                'user_data': self.user_data,
                'schedule': self.schedule
            }, f, default_flow_style=False)
        print(f"\nSchedule saved to {filename}")
    
    def generate_schedule(self):
        """Main method to generate the complete schedule"""
        self.collect_user_data()
        print("\nGenerating your personalized schedule...")
        
        self.add_fixed_commitments()
        self.schedule_learning_goals()
        self.add_breaks_and_entertainment()
        
        self.print_schedule()
        
        # Calculate summary statistics
        total_learning_hours = 0
        for goal in self.user_data['learning_goals']:
            total_learning_hours += goal['weekly_hours']
        
        print(f"\n" + "="*50)
        print("SCHEDULE SUMMARY")
        print("="*50)
        print(f"Total learning hours per week: {total_learning_hours}")
        print(f"Entertainment hours per week: {self.user_data['entertainment_hours']}")
        print(f"Sleep hours per night: {self.user_data['sleep_duration']}")
        print(f"Cooking hours per week: {self.user_data['cooking_time'] * 7 if self.user_data['cook_dinner'] else 0}")
        
        save_option = input("\nWould you like to save this schedule to a file? (y/n): ")
        if save_option.lower() == 'y':
            self.save_schedule()

# Example usage
if __name__ == "__main__":
    scheduler = ScheduleGenerator()
    scheduler.generate_schedule()