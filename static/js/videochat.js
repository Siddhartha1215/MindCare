const socket = io.connect(window.location.origin);

let localStream;
let peerConnection;
let isCaller = false;
let callTimeout;
let isMuted = false;
let isVideoOn = true;
let callInProgress = false;
let peerAvailable = false; // Default to false, wait for server update

// ICE server configuration
const configuration = {
    iceServers: [
        { urls: 'stun:stun.l.google.com:19302' } // Google STUN server
    ]
};

// Update UI based on user status from the server
socket.on('user_status', (data) => {
    peerAvailable = data.peerAvailable;
    updateUI();
});

function updateUI() {
    if (peerAvailable && !callInProgress) {
        document.getElementById('startCall').style.display = 'block';
        document.getElementById('status').textContent = ''; // Clear status message
    } else if (!peerAvailable) {
        document.getElementById('startCall').style.display = 'none';
        showNotification('No admin available to call.');
        document.getElementById('status').textContent = 'Waiting for admin to join...'; // Update status message
    }
}


// Capture local media (video and audio)
navigator.mediaDevices.getUserMedia({ video: true, audio: true })
    .then(stream => {
        localStream = stream;
        document.getElementById('localVideo').srcObject = stream;
    })
    .catch(error => console.error('Error accessing media devices.', error));

// Handle the Start Call button
document.getElementById('startCall').addEventListener('click', () => {
    if (callInProgress) {
        showNotification('You are already in a call.');
        return;
    }

    if (!peerAvailable) {
        showNotification('No admin available to call.');
        return;
    }

    isCaller = true;
    startCall();
    updateStatus('Connecting...');
    callInProgress = true;
    updateUI();
});

// Handle the Pick Up button
document.getElementById('pickUpCall').addEventListener('click', () => {
    pickUpCall();
    callInProgress = true;
    peerAvailable = false;
    updateUI();
});

// Handle the Reject Call button
document.getElementById('rejectCall').addEventListener('click', () => {
    rejectCall();
    callInProgress = false;
    peerAvailable = true;
    updateUI();
});

// Handle the End Call button
document.getElementById('endCall').addEventListener('click', () => {
    endCall();
    callInProgress = false;
    peerAvailable = true;
    updateUI();
});

// Handle the Mute/Unmute button
document.getElementById('muteButton').addEventListener('click', toggleMute);

// Handle the Video On/Off button
document.getElementById('videoToggleButton').addEventListener('click', toggleVideo);

function startCall() {
    callInProgress = true;
    peerAvailable = false;
    peerConnection = createPeerConnection();

    if (localStream) {
        localStream.getTracks().forEach(track => {
            peerConnection.addTrack(track, localStream);
        });
    }

    peerConnection.createOffer()
        .then(offer => {
            return peerConnection.setLocalDescription(offer);
        })
        .then(() => {
            socket.emit('signal', { offer: peerConnection.localDescription });
        })
        .catch(error => console.error('Error creating an offer:', error));
}

function pickUpCall() {
    clearTimeout(callTimeout);
    updateStatus('In Call');
    hideAllButtonsExcept(['endCall', 'muteButton', 'videoToggleButton']);

    peerConnection = createPeerConnection();

    if (localStream) {
        localStream.getTracks().forEach(track => {
            peerConnection.addTrack(track, localStream);
        });
    }

    peerConnection.setRemoteDescription(new RTCSessionDescription(window.receivedOffer))
        .then(() => {
            return peerConnection.createAnswer();
        })
        .then(answer => {
            return peerConnection.setLocalDescription(answer);
        })
        .then(() => {
            socket.emit('signal', { answer: peerConnection.localDescription });
        })
        .catch(error => console.error('Error setting up the call:', error));
}

function rejectCall() {
    updateStatus('Call Rejected');
    socket.emit('signal', { reject: true });
    hideAllButtonsExcept(['startCall']);
    callInProgress = false;
}

function endCall() {
    if (peerConnection) {
        peerConnection.close();
        peerConnection = null;
    }

    socket.emit('signal', { end: true });

    updateStatus('Call Ended');
    hideAllButtonsExcept(['startCall']);

    // Refresh the page to reset video and UI state
    setTimeout(() => {
        location.reload();
    }, 1000);
}

function toggleMute() {
    isMuted = !isMuted;
    localStream.getAudioTracks().forEach(track => track.enabled = !isMuted);
    document.getElementById('muteButton').textContent = isMuted ? 'Unmute' : 'Mute';
}

function toggleVideo() {
    isVideoOn = !isVideoOn;
    if (localStream) {
        localStream.getVideoTracks().forEach(track => track.enabled = isVideoOn);
    }
    document.getElementById('videoToggleButton').textContent = isVideoOn ? 'Turn Video Off' : 'Turn Video On';
}

function createPeerConnection() {
    const pc = new RTCPeerConnection(configuration);

    pc.ontrack = (event) => {
        const remoteVideo = document.getElementById('remoteVideo');
        if (!remoteVideo.srcObject) {
            remoteVideo.srcObject = event.streams[0];
        }
    };

    pc.onicecandidate = (event) => {
        if (event.candidate) {
            socket.emit('signal', { candidate: event.candidate });
        }
    };

    return pc;
}

function updateStatus(status) {
    document.getElementById('status').textContent = status;
}

function showNotification(message) {
    const notificationElement = document.getElementById('notification');
    notificationElement.textContent = message;
    setTimeout(() => {
        notificationElement.textContent = '';
    }, 3000);
}

function hideAllButtonsExcept(buttonsToShow) {
    const buttonIds = ['startCall', 'pickUpCall', 'rejectCall', 'endCall', 'muteButton', 'videoToggleButton'];
    buttonIds.forEach(id => {
        document.getElementById(id).style.display = buttonsToShow.includes(id) ? 'block' : 'none';
    });
}

// Listen for signaling messages
socket.on('signal', async (message) => {
    if (message.offer) {
        if (callInProgress) {
            socket.emit('signal', { reject: true });
            return;
        }

        window.receivedOffer = message.offer;
        updateStatus('Incoming Call...');
        hideAllButtonsExcept(['pickUpCall', 'rejectCall']);
        callTimeout = setTimeout(() => {
            updateStatus('Missed Call');
            hideAllButtonsExcept(['startCall']);
            peerAvailable = true; // Reset peer availability after a missed call
        }, 30000);
    } else if (message.answer) {
        if (isCaller) {
            await peerConnection.setRemoteDescription(new RTCSessionDescription(message.answer));
            updateStatus('In Call');
            hideAllButtonsExcept(['endCall', 'muteButton', 'videoToggleButton']);
        }
    } else if (message.candidate) {
        if (peerConnection) {
            await peerConnection.addIceCandidate(new RTCIceCandidate(message.candidate));
        }
    } else if (message.reject) {
        updateStatus('Call Rejected by the other party');
        callInProgress = false;
        peerAvailable = true; // Set peer available since the call was rejected
        hideAllButtonsExcept(['startCall']);
    } else if (message.end) {
        updateStatus('Call Ended by the other party');
        if (peerConnection) {
            peerConnection.close();
            peerConnection = null;
        }
        callInProgress = false;
        peerAvailable = true; // Set peer available since the call ended
        hideAllButtonsExcept(['startCall']);
    }
});


socket.on('admin_joined', (data) => {
    if (data.message === "Admin has joined") {
        updateStatus('Admin has joined');
        hideAllButtonsExcept(['endCall', 'muteButton', 'videoToggleButton']);
    }
});

socket.on('user_in_call', (data) => {
    updateStatus('You are in a call with the admin');
    hideAllButtonsExcept(['endCall', 'muteButton', 'videoToggleButton']);
});
