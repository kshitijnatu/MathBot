// script.js

const chatBox = document.getElementById("chat-box");
const chatForm = document.getElementById("chat-form");
const userInput = document.getElementById("user-input");
const summarizeButton = document.getElementById("summarize-button");
const loadingSpinner = document.getElementById("loading-spinner");
const summaryText = document.getElementById("summary-text");

// Function to add a message to the chat box
function addMessageToChatBox(message, isUser = true) {
    const messageElement = document.createElement("div");
    messageElement.className = `message ${isUser ? 'user' : 'bot'}`;
    messageElement.innerHTML = isUser ? `<strong>You:</strong> ${message}` : `<strong>Bot:</strong> ${message}`;
    chatBox.appendChild(messageElement);
    chatBox.scrollTop = chatBox.scrollHeight;
    return messageElement;
}

// Handle form submission
chatForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const message = userInput.value.trim();
    if (!message) return;

    // Display the user's message
    addMessageToChatBox(message);
    userInput.value = "";

    // Show loading spinner
    loadingSpinner.style.display = "block";

    // Stream the bot's response
    await streamChatResponse(message);

});

// Function to stream the bot's response
async function streamChatResponse(message) {
    const response = await fetch("/chat", {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded",
        },
        body: new URLSearchParams({ "user-input": message }),
    });

    // Hide loading spinner
    loadingSpinner.style.display = "none";

    // Display bot response progressively
    let responseText = "";
    const botMessageElement = addMessageToChatBox("", false);

    if (response.body) {
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let done = false;

        while (!done) {
            const { value, done: readerDone } = await reader.read();
            done = readerDone;
            const chunk = decoder.decode(value);

            // Append the received chunk to the bot's message
            responseText += chunk;
            botMessageElement.innerHTML = `<strong>Bot:</strong> ${responseText}`;
            chatBox.scrollTop = chatBox.scrollHeight;
        }
    }
}

// Handle summarize button click
summarizeButton.addEventListener("click", async () => {
    // Show loading spinner
    loadingSpinner.style.display = "block";

    const response = await fetch("/summarize", {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded",
        },
        body: new URLSearchParams(),
    });

    const data = await response.json();
    
    // Hide loading spinner
    loadingSpinner.style.display = "none";
 
    
    // Add the summary to the new chat-box element
    addMessageToChatBox(data.summary, false);
    // summaryText.innerHTML = data.summary;
});
