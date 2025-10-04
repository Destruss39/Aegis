import ctypes
import os
import webview
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidTag

# --- Constants for Encryption ---
# Parameter to generate a unquie salt for each file.
SALT_SIZE = 16
TAG_SIZE = 16
NONCE_SIZE = 12
KEY_SIZE = 32 # For AES-256
ITERATIONS = 100_000 # Number of iterations for PBKDF2

class Api:
    """
    This class exposes methods that can be called from JavaScript.
    """

    def _derive_key(self, master_key: str, salt: bytes) -> bytes:
        """Derives a 32-byte key from the master key and a salt using PBKDF2."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=KEY_SIZE,
            salt=salt,
            iterations=ITERATIONS,
            backend=default_backend()
        )
        return kdf.derive(master_key.encode('utf-8'))

    def encrypt(self, master_key):
        """
        Opens a file dialog, reads selected files as bytes, and encrypts them.
        """
        window.evaluate_js('updateMessage("Starting encryption...")')

        if not master_key:
            window.evaluate_js('updateMessage("Error: Master key cannot be empty.")')
            return

        file_paths = window.create_file_dialog(
            webview.FileDialog.OPEN,
            allow_multiple=True
        )

        if not file_paths:
            window.evaluate_js('updateMessage("Operation cancelled: No files selected.")')
            return

        encrypted_count = 0
        for file_path in file_paths:
            try:
                # 1. Get original file extension
                _, original_ext = os.path.splitext(file_path)
                original_ext_bytes = original_ext.encode('utf-8')

                # 2. Read the file content
                with open(file_path, 'rb') as f:
                    file_data = f.read()

                # 3. Generate a random salt for each file
                salt = os.urandom(SALT_SIZE)

                # 4. Derive the encryption key from the master key and salt
                key = self._derive_key(master_key, salt)

                # 5. Encrypt using AES-GCM
                aesgcm = AESGCM(key)
                nonce = os.urandom(NONCE_SIZE)
                encrypted_data = aesgcm.encrypt(nonce, file_data, None) # tag is generated automatically

                # 6. Define the new file path (without original extension)
                encrypted_file_path = os.path.splitext(file_path)[0]

                # 7. Write the encrypted file with metadata
                # Format: [salt][nonce][original_ext_len (1 byte)][original_ext][encrypted_data]
                with open(encrypted_file_path, 'wb') as f:
                    f.write(salt)
                    f.write(nonce)
                    f.write(len(original_ext_bytes).to_bytes(1, 'big'))
                    f.write(original_ext_bytes)
                    f.write(encrypted_data)
                
                encrypted_count += 1
                print(f"Successfully encrypted: {file_path}")

            except Exception as e:
                error_message = f"Failed to encrypt {os.path.basename(file_path)}: {e}"
                print(error_message)
                window.evaluate_js(f'updateMessage("{error_message}")')
                # Stop on first error
                return

        message = f"Successfully encrypted {encrypted_count} of {len(file_paths)} file(s)."
        window.evaluate_js(f'updateMessage("{message}")')


    def decrypt(self, master_key):
        """
        Opens a file dialog, reads selected files, and decrypts them.
        """
        window.evaluate_js('updateMessage("Starting decryption...")')

        if not master_key:
            window.evaluate_js('updateMessage("Error: Master key cannot be empty.")')
            return

        file_paths = window.create_file_dialog(
            webview.FileDialog.OPEN,
            allow_multiple=True
        )

        if not file_paths:
            window.evaluate_js('updateMessage("Operation cancelled: No files selected.")')
            return
        
        decrypted_count = 0
        for file_path in file_paths:
            try:
                # 1. Read the entire encrypted file
                with open(file_path, 'rb') as f:
                    encrypted_blob = f.read()

                # 2. Extract metadata from the blob
                salt = encrypted_blob[:SALT_SIZE]
                nonce = encrypted_blob[SALT_SIZE:SALT_SIZE + NONCE_SIZE]
                ext_len = int.from_bytes(encrypted_blob[SALT_SIZE + NONCE_SIZE:SALT_SIZE + NONCE_SIZE + 1], 'big')
                ext_start = SALT_SIZE + NONCE_SIZE + 1
                ext_end = ext_start + ext_len
                original_ext = encrypted_blob[ext_start:ext_end].decode('utf-8')
                encrypted_data = encrypted_blob[ext_end:]

                # 3. Derive the key
                key = self._derive_key(master_key, salt)

                # 4. Decrypt using AES-GCM
                aesgcm = AESGCM(key)
                decrypted_data = aesgcm.decrypt(nonce, encrypted_data, None)

                # 5. Define the new file path and write the decrypted data
                decrypted_file_path = file_path + original_ext
                with open(decrypted_file_path, 'wb') as f:
                    f.write(decrypted_data)
                
                decrypted_count += 1
                print(f"Successfully decrypted: {file_path}")

            except InvalidTag:
                error_message = f"Decryption failed for {os.path.basename(file_path)}: Incorrect master key or corrupted file."
                print(error_message)
                window.evaluate_js(f'updateMessage("{error_message}")')
                return # Stop on first error
            except Exception as e:
                error_message = f"An error occurred with {os.path.basename(file_path)}: {e}"
                print(error_message)
                window.evaluate_js(f'updateMessage("{error_message}")')
                return # Stop on first error

        message = f"Successfully decrypted {decrypted_count} of {len(file_paths)} file(s)."
        window.evaluate_js(f'updateMessage("{message}")')


if __name__ == '__main__':
    api = Api()

    # Get screen dimensions
    user32 = ctypes.windll.user32
    screen_width = user32.GetSystemMetrics(0)
    screen_height = user32.GetSystemMetrics(1)

    # Set window dimensions
    window_width = 700
    window_height = 500

    # Calculate centered position
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2

    # Create the window and expose the API object.
    window = webview.create_window(
        'Aegis',
        'index.html',
        js_api=api,
        width=window_width,
        height=window_height,
        x=x,
        y=y,
        resizable=False
    )
    webview.start()