// Add event listeners when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', function () {
    const encryptBtn = document.getElementById('encryptBtn');
    const decryptBtn = document.getElementById('decryptBtn');
    const masterKeyInput = document.getElementById('masterkey');

    // Attach click event to the Encrypt button
    encryptBtn.addEventListener('click', () => {
        const masterKey = masterKeyInput.value;
        if (!masterKey) {
            updateMessage('Please enter a master key.');
            return;
        }
        // Call the Python 'encrypt' function and pass the master key
        window.pywebview.api.encrypt(masterKey);
    });

    // Attach click event to the Decrypt button
    decryptBtn.addEventListener('click', () => {
        const masterKey = masterKeyInput.value;
        if (!masterKey) {
            updateMessage('Please enter a master key.');
            return;
        }
        // Call the Python 'decrypt' function and pass the master key
        window.pywebview.api.decrypt(masterKey);
    });
});

// This function will be called from Python to update the UI
function updateMessage(message) {
    document.getElementById('response-text').innerText = message;
}