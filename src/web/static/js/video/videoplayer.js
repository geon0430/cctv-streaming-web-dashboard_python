const activeStreams = JSON.parse(localStorage.getItem('activeStreams')) || {};

async function fetchPlayerState() {
    try {
        const response = await fetch('/get_player/');
        if (!response.ok) {
            throw new Error('Failed to fetch player state.');
        }
        const players = await response.json();
        return players.filter(player => player.onvif_result_address !== null &&
                                        player.height !== 0 &&
                                        player.width !== 0 &&
                                        player.fps !== 0.0 &&
                                        player.codec !== "");
    } catch (error) {
        console.error('Error fetching player state:', error);
        return [];
    }
}

async function connectWebSocket(playerIdx, device) {
    console.log(`Connecting WebSocket for playerIdx: ${playerIdx}, device:`, device);

    const videoElement = document.getElementById(`video${playerIdx}`);
    if (!videoElement) {
        console.error(`Video element with ID video${playerIdx} not found.`);
        return;
    }

    const canvasElement = document.createElement('canvas');
    const ctx = canvasElement.getContext('2d');
    videoElement.style.display = 'none';

    const container = videoElement.parentNode;
    container.appendChild(canvasElement);

    if (activeStreams[playerIdx] && activeStreams[playerIdx].ws) {
        try {
            const existingWs = activeStreams[playerIdx].ws;
            existingWs.onclose = function() {
                console.log('Existing WebSocket closed');
                activeStreams[playerIdx] = null; // Clear the existing WebSocket reference
            };
            existingWs.close();
        } catch (error) {
            console.error('Error closing existing WebSocket:', error);
        }
    }

    const ws = new WebSocket(`ws://${window.location.hostname}:14000/ws/${playerIdx}`);
    ws.binaryType = 'arraybuffer';

    ws.onmessage = (event) => {
        const buffer = event.data;
        console.log('Received video frame:', buffer.byteLength);

        const blob = new Blob([buffer], { type: 'image/jpeg' });
        const url = URL.createObjectURL(blob);

        const img = new Image();
        img.onload = () => {
            canvasElement.width = img.width;
            canvasElement.height = img.height;
            ctx.drawImage(img, 0, 0, img.width, img.height);
            URL.revokeObjectURL(url);
        };
        img.src = url;
    };

    ws.onopen = () => {
        console.log('WebSocket connection opened');
        ws.send(JSON.stringify({
            'type': 'assign_device',
            'device': device
        }));
        console.log('Sent assign device message');
    };

    ws.onerror = (error) => {
        console.error('WebSocket error:', error);
    };

    ws.onclose = (event) => {
        console.log('WebSocket connection closed', event);
        if (event.code !== 1000) {
            console.error('Unexpected WebSocket closure. Reconnecting...');
            setTimeout(() => connectWebSocket(playerIdx, device), 1000);
        }
    };

    activeStreams[playerIdx] = { ws, device };
    localStorage.setItem('activeStreams', JSON.stringify(activeStreams));
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
    connectWebSocket(playerIdx, device);
}

async function postDeviceToPlayer(device, playerIdx) {
    try {
        const response = await fetch(`/video_player/${playerIdx}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(device)
        });
        if (!response.ok) {
            const errorData = await response.json();
            console.error(`Failed to assign device: ${errorData.detail}`);
            return;
        }
        console.log(`Device ${device.idx} was successfully assigned to player ${playerIdx}.`);
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
window.onload = async () => {
    await fetchChannelList();

    const players = await fetchPlayerState();
    for (const player of players) {
        if (player.onvif_result_address && player.height && player.width && player.fps && player.codec) {
            const playerIdx = player.channel_id;
            const device = {
                idx: playerIdx,
                onvif_result_address: player.onvif_result_address,
                height: player.height,
                width: player.width,
                codec: player.codec,
                fps: player.fps
            };
            setTimeout(() => connectWebSocket(playerIdx, device), 0); // delay to ensure elements are ready
        }
    }
};
