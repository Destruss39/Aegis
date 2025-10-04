import webview
import os

class Api:
    """
    This class exposes methods that can be called from JavaScript.
    """

    def encrypt(self, master_key):
        """
        Opens a file dialog to select multiple files for encryption.
        """
        window.evaluate_js('updateMessage("Encrypting...")')

        if not master_key:
            print("Master key is empty.")
            window.evaluate_js('updateMessage("Error: Master key cannot be empty.")')
            return

        print(f"Starting encryption with master key: {master_key}")

        # --- File Selection Logic (Updated to fix deprecation warning) ---
        # To select MULTIPLE FILES, use webview.FileDialog.OPEN
        file_paths = window.create_file_dialog(
            webview.FileDialog.OPEN,  # <-- This line is updated
            allow_multiple=True,
            file_types=('All files (*.*)',)
        )

        # --- Folder Selection (Alternative, also updated) ---
        # To select a FOLDER instead, comment out the above and uncomment below.
        # file_paths = []
        # folder_path_tuple = window.create_file_dialog(webview.FileDialog.FOLDER) # <-- This line is updated
        # if folder_path_tuple:
        #     # The result of a folder dialog is a tuple with one element
        #     folder_path = folder_path_tuple[0]
        #     # Walk through the directory and collect all file paths
        #     for root, _, files in os.walk(folder_path):
        #         for file in files:
        #             file_paths.append(os.path.join(root, file))


        if not file_paths:
            print("No files selected.")
            window.evaluate_js('updateMessage("Operation cancelled: No files were selected.")')
            return

        print("Selected files for encryption:")
        for path in file_paths:
            print(path)

        # Here you would add your actual file encryption logic
        # For this example, we'll just confirm the action.

        # Update the frontend with the result
        message = f"Successfully selected {len(file_paths)} file(s) for encryption."
        window.evaluate_js(f'updateMessage("{message}")')


    def decrypt(self, master_key):
        """
        Opens a file dialog to select multiple files for decryption.
        """
        window.evaluate_js('updateMessage("Decrypting...")')

        if not master_key:
            print("Master key is empty.")
            window.evaluate_js('updateMessage("Error: Master key cannot be empty.")')
            return

        print(f"Starting decryption with master key: {master_key}")

        # --- File Selection Logic (Updated to fix deprecation warning) ---
        file_paths = window.create_file_dialog(
            webview.FileDialog.OPEN,  # <-- This line is updated
            allow_multiple=True,
            file_types=('All files (*.*)',)
        )

        if not file_paths:
            print("No files selected.")
            window.evaluate_js('updateMessage("Operation cancelled: No files were selected.")')
            return

        print("Selected files for decryption:")
        for path in file_paths:
            print(path)

        # Here you would add your actual file decryption logic

        # Update the frontend with the result
        message = f"Successfully selected {len(file_paths)} file(s) for decryption."
        window.evaluate_js(f'updateMessage("{message}")')


if __name__ == '__main__':
    api = Api()
    # Create the window and expose the API object.
    window = webview.create_window(
        'Aegis',
        'index.html',
        js_api=api,
        width=700,
        height=500,
        resizable=False
    )
    webview.start()