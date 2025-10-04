// This function will be called from Python
function updateMessage(message) {
    document.getElementById('response-text').innerText = message;
}

// This function calls a Python function
function callPython() {
    // pywebview.api.<function_name>(...args) calls the exposed Python function
    window.pywebview.api.greet("User").then(response => {
        console.log("Python responded:", response);
    });
}