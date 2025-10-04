import webview

class Api:
    """
    This class exposes methods that can be called from JavaScript.
    """
    def greet(self, name):
        """
        A function that can be called from JavaScript.
        It receives a name, prints a message, and updates the UI.
        """
        print(f"Python was greeted by: {name}")
        # Call a JS function to update the frontend
        window.evaluate_js(f'updateMessage("Hello from Python, {name}!")')
        return f"Hello {name}, I am Python!"

if __name__ == '__main__':
    api = Api()
    # Create the window and expose the API object
    window = webview.create_window(
        'JS Communication App',
        'index.html',
        js_api=api
    )
    webview.start()