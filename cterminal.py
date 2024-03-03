import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QTextEdit, QLineEdit, QPushButton, QLabel, QComboBox, QDialog
from PyQt5.QtGui import QColor, QPalette
import subprocess
import time
import requests
import json
# Dictionary to hold custom commands
custom_commands = {}

# Add the 'add' command to the custom commands dictionary

# Function to add custom commands
def add_command(command_name, function):
    custom_commands[command_name] = function

# Sample custom command functions
def say_hello(args):
    main_window.output("Hello, " + ' '.join(args))

def calculate(args):
    try:
        result = eval(' '.join(args))
        main_window.output("Result: " + str(result))
    except Exception as e:
        main_window.output("Error: " + str(e), error=True)

# Define a function that returns help text
def help(args):
    help_message = """
    Welcome to cTerminal Dashboard!<br>
    Run command !info to get info about what this Terminal is for!<br><br>
    
    Commands:<br>
    <b>help;</b> gives useful info about how to use the terminal<br>
    <b>info;</b> gives info about what this Terminal is for<br>
    <b>echoback;</b> Used to return the argument as a echo test args[echo: str]<br>
    <b>sendDSM;</b> Used to send discord messages args [token: str, channel_id: str, message: str]<br>
    <b>ping;</b> Used to ping a ip/server args[ip: str]<br><br>
    
    Command Methods:<br>
    <b>--silent</b> Does not return anything but still runs the function<br>
    <b>--force</b> skips all confirmation on commands that require it<br>
    """
    main_window.output(help_message.strip(), bold=True)

def info(args):
    main_window.output("This Terminal is for providing custom command functionalities.")

def echoback(args):
    if args:
        main_window.output("Echo: " + args[0])
    else:
        main_window.output("No argument provided for echoback command.", error=True)

def sendDSM(args):
    if len(args) > 3:
        main_window.output("Sending message")
        message = ""
        for item in args[2:]:
            message += item + " "
        post = requests.post(f"https://discord.com/api/v9/channels/{str(args[1])}/messages", json={"content":message}, headers={"Authorization":str(args[0])})
        time.sleep(0.5)
        match post.status_code:
            case 200:
                main_window.output(f"Sent Message to Channel ID: {args[1]}, Status Code: {post.status_code}", color="green")
            case _: 
                main_window.output(f"Failed to send Message to Channel ID: {args[1]}, Status Code: {post.status_code}", error=True)
    else:
        main_window.output("Invalid number of arguments. Usage: sendDSM <token> <channel_id> <message>", error=True)

def ping(args):
    silent = False
    if "--silent" in args:
        silent = True
        args.remove("--silent")  # Remove the --silent flag from the arguments

    if args:
        target = args[0]
        try:
            # Execute the ping command and capture the output
            result = subprocess.run(['ping', '-c', '4', target], capture_output=True, text=True, timeout=10)
            # Check if the ping was successful
            if result.returncode == 0 and not silent:
                main_window.output(result.stdout)
            elif result.returncode != 0 and not silent:
                main_window.output("Ping failed: " + result.stderr, error=True)
        except subprocess.TimeoutExpired:
            if not silent:
                main_window.output("Ping timed out.", error=True)
        except Exception as e:
            if not silent:
                main_window.output("An error occurred while pinging: " + str(e), error=True)
    else:
        main_window.output("No IP address provided for ping command.", error=True)


# Add the commands to the custom_commands dictionary
add_command("info", info)
add_command("echoback", echoback)
add_command("sendDSM", sendDSM)
add_command("ping", ping)
add_command("hello", say_hello)
add_command("calculate", calculate)
add_command("help", help)

# Function to process input command
def process_command(command):
    parts = command.split()
    silent = False
    if "--silent" in parts:
        silent = True
        parts.remove("--silent")  # Remove the --silent flag from the command

    if parts[0] in custom_commands:
        if silent:
            # If --silent flag is present, execute the command silently
            custom_commands[parts[0]](parts[1:])
        else:
            # Otherwise, execute the command normally and display output
            custom_commands[parts[0]](parts[1:])
    else:
        main_window.output("Command not found", error=True)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Custom Command Line Interface")
        self.setGeometry(100, 100, 600, 400)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # Add settings button
        self.settings_button = QPushButton("Settings", self)
        self.settings_button.clicked.connect(self.show_settings)
        layout.addWidget(self.settings_button)

        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)  # Set QTextEdit widget to read-only
        layout.addWidget(self.output_text)

        self.input_line = QLineEdit()
        self.input_line.returnPressed.connect(self.process_input)
        layout.addWidget(self.input_line)

        # Default color theme
        self.color_palette = self.palette()

    def process_input(self):
        command = self.input_line.text()
        self.input_line.clear()
        process_command(command)

    def output(self, text, bold=False, color=None, error=False):
        # Start with empty HTML string
        html_text = ''

        # Apply bold formatting if requested
        if bold:
            html_text += '<b>'

        # Add text content
        html_text += text

        # Close bold formatting if applied
        if bold:
            html_text += '</b>'

        # Set color if provided
        if color:
            html_text = '<font color="' + color + '">' + html_text + '</font>'

        # Use HTML formatting to display errors in red
        if error:
            html_text = '<font color="red">' + html_text + '</font>'

        # Append to QTextEdit widget
        self.output_text.append(html_text)

    def show_settings(self):
        settings_window = SettingsWindow(self)
        settings_window.exec_()

    def set_color_theme(self, theme):
        with open("settings.json", "r") as f: 
            settings_json = json.loads(f.read())

        settings_json["color-theme"] = theme

        with open("settings.json", "w") as f:
            f.write(json.dumps(settings_json))

        if theme == "Bright":
            self.setPalette(self.color_palette)
            self.settings_button.setStyleSheet("color: black;")
            self.input_line.setStyleSheet("color: black;")
        elif theme == "Dark":
            dark_palette = self.palette()
            dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
            dark_palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
            dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
            dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
            dark_palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 220))
            dark_palette.setColor(QPalette.ToolTipText, QColor(255, 255, 255))
            dark_palette.setColor(QPalette.Text, QColor(255, 255, 255))
            dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
            dark_palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
            dark_palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
            dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
            dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
            dark_palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
            self.setPalette(dark_palette)
            self.settings_button.setStyleSheet("color: black;")
            self.input_line.setStyleSheet("color: black;")
        elif theme == "System":
            self.setPalette(self.color_palette)
            self.settings_button.setStyleSheet("")
            self.input_line.setStyleSheet("")

class SettingsWindow(QDialog):
    def __init__(self, main_window):
        super().__init__()

        self.setWindowTitle("Settings")
        self.setGeometry(200, 200, 300, 200)

        self.main_window = main_window

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.color_label = QLabel("Color Theme:")
        layout.addWidget(self.color_label)

        self.color_combo = QComboBox()
        self.color_combo.addItem("Bright")
        self.color_combo.addItem("Dark")
        self.color_combo.addItem("System")
        self.color_combo.currentIndexChanged.connect(self.apply_settings)
        layout.addWidget(self.color_combo)

        apply_button = QPushButton("Apply", self)
        apply_button.clicked.connect(self.apply_settings)
        layout.addWidget(apply_button)

    def apply_settings(self):
        color_theme = self.color_combo.currentText()
        self.main_window.set_color_theme(color_theme)

if __name__ == "__main__":
    with open("settings.json", "r") as f: 
        settings_json = f.read()
    theme = json.loads(settings_json)["color-theme"]
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    MainWindow.set_color_theme(main_window, theme)
    sys.exit(app.exec_())