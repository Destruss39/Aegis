# logic.py

def convert_celsius_to_fahrenheit(celsius_str):
    """
    Converts a string containing a Celsius temperature to Fahrenheit.

    Args:
        celsius_str (str): The temperature in Celsius, as a string.

    Returns:
        str: A string with the result or an error message.
    """
    # Use a try-except block to handle cases where the input is not a number.
    try:
        # Convert the input string to a floating-point number.
        celsius = float(celsius_str)
        
        # Apply the conversion formula.
        fahrenheit = (celsius * 9/5) + 32
        
        # Return the result as a nicely formatted string.
        # The :.2f formats the number to have exactly two decimal places.
        return f"{fahrenheit:.2f} °F"
        
    except ValueError:
        # If float() fails, it raises a ValueError. We catch it here.
        return "Error: Please enter a valid number."