// Embeddable chat widget JavaScript
(function () {
    // CSS styles for the chat widget
    const styles = `
    #chat-widget {
        display: none;
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 300px;
        height: 500px;
        border-radius: 10px;
        box-shadow: 0 0 15px rgba(0, 0, 0, 0.2);
        overflow: hidden;
        background-color: white;
        border: 1px solid #ccc;
        z-index: 1100;
    }
    #chat-header {
        background-color: #0078d4;
        color: white;
        padding: 10px;
        text-align: center;
        position: relative;
    }
    #close-btn {
        position: absolute;
        right: 10px;
        cursor: pointer;
    }
    #chat-history {
        padding: 10px;
        height: 400px;
        overflow-y: auto;
        border-top: 1px solid #ccc;
    }
    .message.bot {
        text-align: left;
        margin: 5px 0;
        padding: 5px 10px;
        background-color: #f1f1f1;
        border-radius: 15px;
        max-width: 80%;
    }
    .message.user {
        text-align: right;
        margin: 5px 0;
        padding: 5px 10px;
        background-color: #0078d4;
        color: white;
        border-radius: 15px;
        max-width: 80%;
        align-self: flex-end;
    }
    #chat-input-container {
        display: flex;
        padding: 5px;
        border-top: 1px solid #ccc;
    }
    #chat-input {
        flex: 1;
        padding: 5px;
        border: 1px solid #ccc;
        border-radius: 3px;
    }
    #send-btn {
        padding: 5px 10px;
        background-color: #0078d4;
        color: white;
        border: none;
        cursor: pointer;
        margin-left: 5px;
    }
    #chat-icon {
        position: fixed;
        bottom: 20px;
        right: 20px;
        font-size: 36px;
        cursor: pointer;
        z-index: 1050;
    }`;

    // HTML structure for the chat widget
    const widgetHTML = `
    <div id="chat-widget">
        <div id="chat-header">Chatbot
            <span id="close-btn">&times;</span>
        </div>
        <div id="chat-history"></div>
        <div id="chat-input-container">
            <input type="text" id="chat-input" placeholder="Type your message...">
            <button id="send-btn">Send</button>
        </div>
    </div>
    <div id="chat-icon">💬</div>`;

    // Append CSS styles to the head
    const styleSheet = document.createElement("style");
    styleSheet.type = "text/css";
    styleSheet.innerText = styles;
    document.head.appendChild(styleSheet);

    // Append the HTML structure to the body
    const widgetDiv = document.createElement("div");
    widgetDiv.innerHTML = widgetHTML;
    document.body.appendChild(widgetDiv);

    // JavaScript logic for the chat widget
    const chatWidget = document.getElementById('chat-widget');
    const chatIcon = document.getElementById('chat-icon');
    const closeBtn = document.getElementById('close-btn');
    const sendBtn = document.getElementById('send-btn');
    const chatInput = document.getElementById('chat-input');
    const chatHistory = document.getElementById('chat-history');
    let conversation = []; // To hold the chat history for API requests

    // Show chat widget when clicking chat icon
    chatIcon.addEventListener('click', function () {
        chatWidget.style.display = 'block';
        chatIcon.style.display = 'none';
    });

    // Hide chat widget when clicking close button
    closeBtn.addEventListener('click', function () {
        chatWidget.style.display = 'none';
        chatIcon.style.display = 'block';
    });

    // Handle send button or enter key press
    const handleUserMessage = () => {
        const userMessage = chatInput.value.trim();
        if (userMessage === '') return;

        addMessageToHistory('user', userMessage); // Add user's message to chat history
        chatInput.value = '';

        // Add user's message to conversation array for API request
        conversation.push({ role: 'user', content: userMessage });

        // Call OpenAI API to get response
        fetchOpenAIResponse();
    };

    sendBtn.addEventListener('click', handleUserMessage);
    chatInput.addEventListener('keypress', function (event) {
        if (event.key === 'Enter') {
            handleUserMessage();
        }
    });

    // Function to add a message to the chat history
    const addMessageToHistory = (sender, message) => {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', sender === 'user' ? 'user' : 'bot');
        messageDiv.textContent = message;
        chatHistory.appendChild(messageDiv);
        chatHistory.scrollTop = chatHistory.scrollHeight; // Auto-scroll to bottom
    };

    // Function to call OpenAI API with conversation history
    const fetchOpenAIResponse = async () => {
        try {
            const response = await fetch(`https://staging-ai-js.izen.ai/api/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    messages: conversation, // Send the entire conversation history
                }),
            });

            // const response = await fetch(`http://127.0.0.1:5000/api/chat`, {
            //     method: 'POST',
            //     headers: {
            //         'Content-Type': 'application/json'
            //     },
            //     body: JSON.stringify({
            //         messages: conversation, // Send the entire conversation history
            //     }),
            // });

            if (response.ok) {
                const data = await response.json();
                const botMessage = data.message;
                addMessageToHistory('bot', botMessage);

                // Add bot's message to conversation array for future API requests
                conversation.push({ role: 'assistant', content: botMessage });
            } else {
                addMessageToHistory('bot', 'Error: Failed to fetch response.');
            }
        } catch (error) {
            addMessageToHistory('bot', 'Error: Network issue, please try again.');
        }
    };
})();