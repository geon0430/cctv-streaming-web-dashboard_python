async function connectWebSocket(playerIdx) {
    const videoElement = document.getElementById(`video${playerIdx}`);
    const ws = new WebSocket(`ws://${window.location.hostname}:13000/ws/${playerIdx}`);
    let pc = new RTCPeerConnection();

    pc.ontrack = function(event) {
        videoElement.srcObject = event.streams[0];
        console.log('Received remote track:', event.streams[0]);
    };

    ws.onopen = async () => {
        console.log('WebSocket connection opened');
        const offer = await pc.createOffer();
        await pc.setLocalDescription(offer);
        console.log('Created offer:', pc.localDescription);

        ws.send(JSON.stringify({
            'sdp': pc.localDescription.sdp,
            'type': pc.localDescription.type
        }));
        console.log('Sent offer:', pc.localDescription);
    };

    ws.onmessage = async (event) => {
        const message = JSON.parse(event.data);
        console.log('Received message:', message);
        if (message.type === 'answer') {
            const remoteDesc = new RTCSessionDescription(message);
            await pc.setRemoteDescription(remoteDesc);
            console.log('Set remote description:', remoteDesc);
        }
    };

    ws.onerror = (error) => {
        console.error('WebSocket error:', error);
    };

    ws.onclose = () => {
        console.log('WebSocket connection closed');
    };
}

function itemClicked(event, device) {
    const items = document.querySelectorAll('#file-list li');
    items.forEach(item => {
        item.classList.remove('selected');
        item.setAttribute('draggable', 'false');
    });
    event.currentTarget.classList.add('selected');
    event.currentTarget.setAttribute('draggable', 'true');
    event.currentTarget.addEventListener('dragstart', (e) => itemDragStart(e, device));
    console.log('Item clicked:', device);
}

function itemDragStart(event, device) {
    if (event.currentTarget.classList.contains('selected')) {
        event.dataTransfer.setData('application/json', JSON.stringify(device));
    } else {
        event.preventDefault();
    }
}

function allowDrop(event) {
    event.preventDefault();
}

async function drop(event) {
    event.preventDefault();
    const data = event.dataTransfer.getData('application/json');
    const device = JSON.parse(data);
    const playerIdx = event.currentTarget.dataset.idx;
    console.log('Dropped device:', device, 'on player:', playerIdx);
    await postDeviceToPlayer(device, playerIdx);
    connectWebSocket(playerIdx);
}

async function postDeviceToPlayer(device, playerIdx) {
    try {
        console.log('Sending POST request with device:', device);
        const response = await fetch(`/video_player/${playerIdx}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(device)
        });
        if (response.ok) {
            console.log(`Device ${device.idx} successfully assigned to player ${playerIdx}`);
        } else {
            const errorData = await response.json();
            console.error(`Failed to assign device: ${errorData.detail}`);
        }
    } catch (error) {
        console.error('Error during POST request:', error);
    }
}

function removeChannel() {
    console.log('Remove channel functionality not yet implemented.');
}

document.getElementById('remove-channel').addEventListener('click', removeChannel);
document.getElementById('search-bar').addEventListener('input', function () {
    const searchTerm = this.value.toLowerCase();
    const items = document.querySelectorAll('#file-list li, #file-list .group-title');
    items.forEach(item => {
        if (item.textContent.toLowerCase().includes(searchTerm)) {
            item.style.display = '';
            const group = item.closest('.group');
            if (group) {
                group.style.display = '';
                group.querySelector('ul').style.display = 'block';
            }
        } else {
            item.style.display = 'none';
        }
    });
});

window.fetchChannelList = fetchChannelList;
window.onload = fetchChannelList;
