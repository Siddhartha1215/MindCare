// Function to convert text to speech
function textToSpeech(text) {
    const synth = window.speechSynthesis;
    const utterance = new SpeechSynthesisUtterance(text);
    synth.speak(utterance);
}

// Function to convert speech to text
function startVoiceRecognition() {
    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = 'en-US';
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    recognition.start();

    recognition.onresult = function(event) {
        const speechToText = event.results[0][0].transcript;
        document.getElementById('user-input').value = speechToText;

        // Send the recognized text to the Flask backend
        fetch('/voicebot/generate-response', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ text: speechToText })
        })
        .then(response => response.json())
        .then(data => {
            const responseText = data.response;
            document.getElementById('response-text').textContent = responseText;
            textToSpeech(responseText);
        })
        .catch(error => {
            document.getElementById('response-text').textContent = 'An error occurred. Please try again.';
            console.error('Error:', error);
        });
    };

    recognition.onerror = function(event) {
        console.error('Speech recognition error detected: ' + event.error);
    };
}

// Function to stop speech synthesis
function stopSpeech() {
    window.speechSynthesis.cancel();
}

document.getElementById('voice-btn').addEventListener('click', startVoiceRecognition);
document.getElementById('stop-btn').addEventListener('click', stopSpeech);
