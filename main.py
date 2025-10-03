# main.py

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow

# Import the generated UI class from the ui_main_window.py file.
from ui_main_window import Ui_MainWindow

# Import the conversion function from our logic.py file.
from logic import convert_celsius_to_fahrenheit

class TemperatureConverterApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # Initialize the UI from the generated class.
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Set the window title.
        self.setWindowTitle("Celsius to Fahrenheit Converter")

        # --- SIGNAL AND SLOT CONNECTION ---
        # This is the core of the application's interactivity.
        # Connect the 'clicked' signal of the convert_button widget
        # to the 'perform_conversion' method (our slot).
        self.ui.convert_button.clicked.connect(self.perform_conversion)

    def perform_conversion(self):
        """
        This method (the "slot") is executed when the convert_button is clicked.
        """
        # 1. Get the text from the celsius_input line edit widget.
        celsius_text = self.ui.celsius_input.text()

        # 2. Call the logic function to perform the calculation.
        result_string = convert_celsius_to_fahrenheit(celsius_text)

        # 3. Set the text of the result_label to the string returned by our logic.
        self.ui.result_label.setText(result_string)


# The standard Python entry point.
if __name__ == "__main__":
    # Create the application instance.
    app = QApplication(sys.argv)

    # Create an instance of our main window and show it.
    window = TemperatureConverterApp()
    window.show()

    # Start the application's event loop.
    sys.exit(app.exec())