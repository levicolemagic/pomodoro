import rumps

class PomodoroApp(object):
    def __init__(self):
        self.config = {
            "app_name": "Pomodoro",
            "start": "Start Timer",
            "pause": "Pause Timer",
            "continue": "Continue Timer",
            "stop": "Stop Timer",
            "pomodoro_interval": 1500,
            "short_break_interval": 300,
            "long_break_interval": 900,
            "break_message": "Time is up! Take a break :)",
            "work_message": "Break's over! Back to work :)"
        }

        self.statistics = {
            'completed_pomodoros': 0,
            'breaks_taken': 0,
            'total_time': 0
        }
        self.tasks_log = []

        self.app = rumps.App(self.config["app_name"])
        self.timer = rumps.Timer(self.on_tick, 1)
        self.set_up_menu()

    def set_up_menu(self):
        if hasattr(self, 'timer') and self.timer is not None:
            self.timer.stop()

        self.app.menu.clear()

        self.start_pause_button = rumps.MenuItem(title=self.config["start"], callback=self.start_timer)
        self.stop_button = rumps.MenuItem(title=self.config["stop"], callback=self.stop_timer)
        self.toggle_transition_button = rumps.MenuItem(title="Auto Transition: ON", callback=self.toggle_transition)
        self.stats_button = rumps.MenuItem(title="Show Statistics", callback=self.show_statistics)
        self.skip_button = rumps.MenuItem(title="Skip", callback=self.skip_phase)
        self.settings_button = rumps.MenuItem(title="Settings", callback=self.get_user_input)
        
        self.app.menu = [self.start_pause_button, self.stop_button, self.toggle_transition_button, self.stats_button, self.skip_button, self.settings_button]
        
        self.mode = "pomodoro"
        self.auto_transition = True

    def show_statistics(self, _):
        stats_message = f"Completed Pomodoros: {self.statistics['completed_pomodoros']}\n" \
                        f"Breaks Taken: {self.statistics['breaks_taken']}\n" \
                        f"Total Time (mins): {self.statistics['total_time'] // 60}"
        rumps.alert("Statistics", stats_message)

    def log_task(self):
        task_window = rumps.Window(message='What are you working on?', default_input="")
        task_response = task_window.run()
        if task_response.clicked:
            self.tasks_log.append(task_response.text)

    def skip_phase(self, _):
        # If in Pomodoro phase, switch to break, and vice versa.
        if self.mode == "pomodoro":
            if self.pomodoro_counter % 4 == 0:
                self.start_break("long")
            else:
                self.start_break("short")
        else:
            self.start_pomodoro()

    
    def start_timer(self, sender):
        if self.mode == "pomodoro":
            self.log_task()
        self.app = rumps.App(self.config["app_name"])
        self.timer = rumps.Timer(self.on_tick, 1)

        self.settings_button = rumps.MenuItem(title="Settings", callback=self.get_user_input)
        self.app.menu.add(self.settings_button)
        
        self.interval = self.config["pomodoro_interval"]
        
        self.start_pause_button = rumps.MenuItem(title=self.config["start"], callback=self.start_timer)
        self.stop_button = rumps.MenuItem(title=self.config["stop"], callback=self.stop_timer)
        self.toggle_transition_button = rumps.MenuItem(title="Auto Transition: ON", callback=self.toggle_transition)
        
        self.app.menu = [self.start_pause_button, self.stop_button, self.toggle_transition_button]
        self.set_up_menu()

    def get_user_input(self):
        pomodoro_window = rumps.Window(message='Set Pomodoro Duration (in minutes):', default_input=str(self.config["pomodoro_interval"] // 60))
        pomodoro_response = pomodoro_window.run()

        short_break_window = rumps.Window(message='Set Short Break Duration (in minutes):', default_input=str(self.config["short_break_interval"] // 60))
        short_break_response = short_break_window.run()

        long_break_window = rumps.Window(message='Set Long Break Duration (in minutes):', default_input=str(self.config["long_break_interval"] // 60))
        long_break_response = long_break_window.run()

        if pomodoro_response.clicked and short_break_response.clicked and long_break_response.clicked:
            try:
                self.config["pomodoro_interval"] = int(pomodoro_response.text) * 60
                self.config["short_break_interval"] = int(short_break_response.text) * 60
                self.config["long_break_interval"] = int(long_break_response.text) * 60
            except ValueError:
                rumps.alert("Please enter valid numbers!")
    def set_up_menu(self):
        self.timer.stop()
        self.timer.count = 0
        self.app.title = "🍅"
        self.pomodoro_counter = 0
        self.mode = "pomodoro"
        self.auto_transition = True

    def start_timer(self, sender):
        if sender.title.lower().startswith(("start", "continue")):
            if sender.title == self.config["start"]:
                self.timer.count = 0
                if self.mode == "pomodoro":
                    self.timer.end = self.config["pomodoro_interval"]
                elif self.mode == "break":
                    if self.pomodoro_counter % 4 == 0:
                        self.timer.end = self.config["long_break_interval"]
                    else:
                        self.timer.end = self.config["short_break_interval"]
            sender.title = self.config["pause"]
            self.timer.start()
        else:
            sender.title = self.config["continue"]
            self.timer.stop()

    def on_tick(self, sender):
        time_left = sender.end - sender.count
        # Add the progress bar code here
        progress_percentage = (sender.count / sender.end)
        progress_blocks = int(progress_percentage * 10)
        progress_bar = '▓' * progress_blocks + '░' * (10 - progress_blocks)
        self.app.title = progress_bar + ' {:2d}:{:02d}'.format(mins, secs)

        mins = time_left // 60 if time_left >= 0 else time_left // 60 + 1
        secs = time_left % 60 if time_left >= 0 else (-1 * time_left) % 60
        self.statistics['total_time'] += 1
        if mins == 0 and time_left < 0:
            if self.mode == "pomodoro":
                self.statistics['completed_pomodoros'] += 1
            else:
                self.statistics['breaks_taken'] += 1
            self.pomodoro_counter += 1 if self.mode == "pomodoro" else 0
            if self.auto_transition:
                if self.mode == "pomodoro":
                    if self.pomodoro_counter % 4 == 0:
                        self.start_break("long")
                    else:
                        self.start_break("short")
                else:
                    self.start_pomodoro()
        else:
            self.stop_button.set_callback(self.stop_timer)
            self.app.title = '{:2d}:{:02d}'.format(mins, secs)
        sender.count += 1

    def start_break(self, break_type):
        if break_type == "short":
            self.timer.end = self.config["short_break_interval"]
        elif break_type == "long":
            self.timer.end = self.config["long_break_interval"]
        self.mode = "break"
        rumps.notification(title=self.config["app_name"],
                           subtitle=self.config["break_message"],
                           message='')
        self.timer.count = 0
        self.timer.start()

    def start_pomodoro(self):
        self.timer.end = self.config["pomodoro_interval"]
        self.mode = "pomodoro"
        rumps.notification(title=self.config["app_name"],
                           subtitle=self.config["work_message"],
                           message='')
        self.timer.count = 0
        self.timer.start()

    def toggle_transition(self, sender):
        self.auto_transition = not self.auto_transition
        sender.title = "Auto Transition: ON" if self.auto_transition else "Auto Transition: OFF"


    def stop_timer(self, sender):
        self.set_up_menu()
        self.stop_button.set_callback(None)
        self.start_pause_button.title = self.config["start"]

    def run(self):
        self.app.run()


if __name__ == '__main__':
    app = PomodoroApp()
    app.run()
