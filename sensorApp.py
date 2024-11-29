import tkinter as tk
from tkinter import messagebox, filedialog
import psycopg2
import subprocess
import threading

class LoginApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Login Window")
        self.set_window_center(300, 200)  # Center the window with width=300, height=200

        # Username label and entry
        tk.Label(root, text="Username:").pack(pady=5)
        self.username_entry = tk.Entry(root)
        self.username_entry.pack(pady=5)
        self.username_entry.focus()  # Set focus to the username entry field

        # Password label and entry
        tk.Label(root, text="Password:").pack(pady=5)
        self.password_entry = tk.Entry(root, show="*")
        self.password_entry.pack(pady=5)
        self.password_entry.bind("<Return>", lambda event: self.login())  # Bind Enter key to login

        # Login button
        tk.Button(root, text="Login", command=self.login).pack(pady=10)

    def set_window_center(self, width, height):
        """Centers the window on the screen."""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        x = (screen_width - width) // 2
        y = (screen_height - height) // 2

        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        # Check credentials
        if username == "admin" and password == "password":  # Example credentials
            messagebox.showinfo("Login Successful", "Welcome to the App!")
            self.open_main_window()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")

    def authenticate(self, username, password):
        """Authenticates the user by checking the database."""
        try:
            # Connect to PostgreSQL database
            conn = psycopg2.connect(
                dbname="sensor_data_db",
                user="postgres",
                password="GOD$postgres2024",
                host="localhost",  # Adjust to your database server
                port="5432"        # Adjust if you're using a different port
            )
            cursor = conn.cursor()
            # Query to check user credentials
            cursor.execute(
                "SELECT * FROM users WHERE username = %s AND password = %s",
                (username, password)
            )
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            # If result is not None, credentials are valid
            return result is not None
        except Exception as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")
            return False

    def open_main_window(self):
        # Close the login window
        self.root.destroy()

        # Open main window
        main_window = tk.Tk()
        main_window.title("Main Window")
        main_window.state('zoomed')  # Maximize the main window

        # Create main menu
        self.create_menu(main_window)

        # Create toolbar
        self.create_toolbar(main_window)

        # Create left sidebar
        self.create_left_sidebar(main_window)

        # Create status bar
        self.create_status_bar(main_window)

        # Add some main content
        tk.Label(main_window, text="Welcome to the Main Window!", font=("Arial", 20)).pack(pady=50)
        
        # Add content to the main window
        self.create_ping_section(main_window)

        main_window.mainloop()
 
    def create_ping_section(self, window):
        """Creates a section in the main window to display continuous ping results."""
        frame = tk.Frame(window, pady=20)
        frame.pack()

        tk.Label(frame, text="Ping Results", font=("Arial", 14)).pack(pady=5)

        self.result_box = tk.Text(frame, height=20, width=100, wrap=tk.WORD)
        self.result_box.pack(pady=10)

        self.start_ping_button = tk.Button(frame, text="Start Ping 127.0.0.1 -t", command=self.start_ping)
        self.start_ping_button.pack(side=tk.LEFT, padx=10)

        self.stop_ping_button = tk.Button(frame, text="Stop Ping", command=self.stop_ping, state=tk.DISABLED)
        self.stop_ping_button.pack(side=tk.LEFT, padx=10)

        self.save_button = tk.Button(frame, text="Save Results", command=self.save_results, state=tk.DISABLED)
        self.save_button.pack(side=tk.LEFT, padx=10)

        self.ping_process = None  # To manage the subprocess
        self.running = False  # To track if the ping is running
        
    def start_ping(self):
        """Starts the ping process in a new thread."""
        if not self.running:
            self.running = True
            self.start_ping_button.config(state=tk.DISABLED)
            self.stop_ping_button.config(state=tk.NORMAL)
            self.save_button.config(state=tk.DISABLED) 
            
            # Start the ping in a separate thread
            threading.Thread(target=self.run_ping, daemon=True).start()

    def stop_ping(self):
        """Stops the ping process."""
        self.running = False
        if self.ping_process:
            self.ping_process.terminate()
            self.ping_process = None
        self.start_ping_button.config(state=tk.NORMAL)
        self.stop_ping_button.config(state=tk.DISABLED)
        self.save_button.config(state=tk.NORMAL) 

    def run_ping(self):
        """Runs the ping command and displays the output in real-time."""
        try:
            # Run the ping command
            self.ping_process = subprocess.Popen(
                ["ping", "127.0.0.1", "-t"],  # Windows continuous ping
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Read the output line by line
            for line in iter(self.ping_process.stdout.readline, ''):
                if not self.running:  # Stop if the ping is stopped
                    break
                self.result_box.insert(tk.END, line)
                self.result_box.see(tk.END)  # Auto-scroll to the latest line
            self.ping_process.stdout.close()

        except Exception as e:
            messagebox.showerror("Ping Error", f"An error occurred: {e}")
        finally:
            self.stop_ping()  # Ensure cleanup when the process stops
    
    def save_results(self):
        """Saves the content of the result box to a file."""
        try:
            # Open a file dialog to select where to save the file
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
                title="Save Ping Results"
            )
            if file_path:
                # Get the content of the result box
                content = self.result_box.get(1.0, tk.END).strip()

                # Write the content to the file
                with open(file_path, "w") as file:
                    file.write(content)
                
                messagebox.showinfo("Success", f"Results saved to {file_path}")
                self.save_button.config(state=tk.DISABLED)
        except Exception as e:
            messagebox.showerror("Save Error", f"An error occurred while saving: {e}")    
                            
    def create_menu(self, window):
        """Creates a main menu bar."""
        menu_bar = tk.Menu(window)

        # File menu
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="New")
        file_menu.add_command(label="Open")
        file_menu.add_command(label="Save")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=window.destroy)
        menu_bar.add_cascade(label="File", menu=file_menu)

        # Edit menu
        edit_menu = tk.Menu(menu_bar, tearoff=0)
        edit_menu.add_command(label="Undo")
        edit_menu.add_command(label="Redo")
        menu_bar.add_cascade(label="Edit", menu=edit_menu)

        # Help menu
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="About", command=lambda: messagebox.showinfo("About", "This is a sample application."))
        menu_bar.add_cascade(label="Help", menu=help_menu)

        # Attach menu bar to window
        window.config(menu=menu_bar)

    def create_toolbar(self, window):
        """Creates a toolbar."""
        toolbar = tk.Frame(window, bd=1, relief=tk.RAISED)
        
        tk.Button(toolbar, text="New", command=lambda: messagebox.showinfo("Toolbar", "New File")).pack(side=tk.LEFT, padx=2, pady=2)
        tk.Button(toolbar, text="Open", command=lambda: messagebox.showinfo("Toolbar", "Open File")).pack(side=tk.LEFT, padx=2, pady=2)
        tk.Button(toolbar, text="Save", command=lambda: messagebox.showinfo("Toolbar", "Save File")).pack(side=tk.LEFT, padx=2, pady=2)
        tk.Button(toolbar, text="Exit", command=window.destroy).pack(side=tk.RIGHT, padx=2, pady=2)
        
        toolbar.pack(side=tk.TOP, fill=tk.X)

    def create_left_sidebar(self, window):
        """Creates a left sidebar."""
        sidebar = tk.Frame(window, width=200, bg="lightgrey", relief=tk.SUNKEN, bd=2)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)

        tk.Button(sidebar, text="Option 1", command=lambda: messagebox.showinfo("Sidebar", "Option 1 Selected")).pack(pady=10)
        tk.Button(sidebar, text="Option 2", command=lambda: messagebox.showinfo("Sidebar", "Option 2 Selected")).pack(pady=10)
        tk.Button(sidebar, text="Option 3", command=lambda: messagebox.showinfo("Sidebar", "Option 3 Selected")).pack(pady=10)

    def create_status_bar(self, window):
        """Creates a status bar."""
        status_bar = tk.Label(window, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

# Run the app
if __name__ == "__main__":
    root = tk.Tk()
    app = LoginApp(root)
    root.mainloop()
