import ctypes
import os
import webview
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidTag

# --- Constants for Encryption ---
# Parameter to generate a unique salt for each file.
SALT_SIZE = 16
TAG_SIZE = 16
NONCE_SIZE = 12
KEY_SIZE = 32  # For AES-256
ITERATIONS = 100_000  # Number of iterations for PBKDF2
CHUNK_SIZE = 64 * 1024  # 64KB chunks

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
        Opens a file dialog, reads selected files as bytes, and encrypts them in chunks.
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

                # 2. Generate a random salt for each file
                salt = os.urandom(SALT_SIZE)

                # 3. Derive the encryption key from the master key and salt
                key = self._derive_key(master_key, salt)

                # 4. Generate a random nonce
                nonce = os.urandom(NONCE_SIZE)

                # 5. Create AES-GCM cipher
                cipher = Cipher(algorithms.AES(key), modes.GCM(nonce))
                encryptor = cipher.encryptor()

                # 6. Define the new file path
                encrypted_file_path = os.path.splitext(file_path)[0]

                # 7. Write the encrypted file with metadata and encrypted chunks
                with open(encrypted_file_path, 'wb') as f_out, open(file_path, 'rb') as f_in:
                    # Write metadata
                    f_out.write(salt)
                    f_out.write(nonce)
                    f_out.write(len(original_ext_bytes).to_bytes(1, 'big'))
                    f_out.write(original_ext_bytes)

                    # Read and encrypt file in chunks
                    while chunk := f_in.read(CHUNK_SIZE):
                        encrypted_chunk = encryptor.update(chunk)
                        f_out.write(encrypted_chunk)

                    # Finalize encryption and write the last chunk
                    f_out.write(encryptor.finalize())
                    # Write the authentication tag
                    f_out.write(encryptor.tag)

                encrypted_count += 1
                print(f"Successfully encrypted: {file_path}")

            except Exception as e:
                error_message = f"Failed to encrypt {os.path.basename(file_path)}: {e}"
                print(error_message)
                window.evaluate_js(f'updateMessage("{error_message}")')
                return

        message = f"Successfully encrypted {encrypted_count} of {len(file_paths)} file(s)."
        window.evaluate_js(f'updateMessage("{message}")')

    def decrypt(self, master_key):
        """
        Opens a file dialog, reads selected files, and decrypts them in chunks.
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
                with open(file_path, 'rb') as f:
                    # 1. Read metadata
                    salt = f.read(SALT_SIZE)
                    nonce = f.read(NONCE_SIZE)
                    ext_len = int.from_bytes(f.read(1), 'big')
                    original_ext = f.read(ext_len).decode('utf-8')

                    # 2. Get the tag from the end of the file
                    f.seek(-TAG_SIZE, os.SEEK_END)
                    tag = f.read(TAG_SIZE)
                    
                    # 3. Derive the key
                    key = self._derive_key(master_key, salt)
                    
                    # 4. Create AES-GCM cipher
                    cipher = Cipher(algorithms.AES(key), modes.GCM(nonce, tag))
                    decryptor = cipher.decryptor()

                    # 5. Define the new file path and write decrypted data in chunks
                    decrypted_file_path = file_path + original_ext
                    
                    f.seek(SALT_SIZE + NONCE_SIZE + 1 + ext_len)
                    
                    with open(decrypted_file_path, 'wb') as f_out:
                        while True:
                            # We need to determine how much to read, avoiding the tag at the end
                            current_pos = f.tell()
                            remaining_bytes = f.seek(0, os.SEEK_END) - current_pos - TAG_SIZE
                            f.seek(current_pos)
                            
                            if remaining_bytes <= 0:
                                break

                            read_size = min(CHUNK_SIZE, remaining_bytes)
                            encrypted_chunk = f.read(read_size)
                            decrypted_chunk = decryptor.update(encrypted_chunk)
                            f_out.write(decrypted_chunk)
                            
                        # Finalize decryption (this will raise InvalidTag if authentication fails)
                        f_out.write(decryptor.finalize())

                decrypted_count += 1
                print(f"Successfully decrypted: {file_path}")

            except InvalidTag:
                error_message = f"Decryption failed for {os.path.basename(file_path)}: Incorrect master key or corrupted file."
                print(error_message)
                window.evaluate_js(f'updateMessage("{error_message}")')
                # Clean up partially decrypted file
                if os.path.exists(decrypted_file_path):
                    os.remove(decrypted_file_path)
                return
            except Exception as e:
                error_message = f"An error occurred with {os.path.basename(file_path)}: {e}"
                print(error_message)
                window.evaluate_js(f'updateMessage("{error_message}")')
                # Clean up partially decrypted file
                if 'decrypted_file_path' in locals() and os.path.exists(decrypted_file_path):
                    os.remove(decrypted_file_path)
                return

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