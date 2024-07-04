const activeStreams = {};  // 현재 활성 스트림을 저장할 객체

async function connectWebSocket(playerIdx, device) {
    const videoElement = document.getElementById(`video${playerIdx}`);
    const canvasElement = document.createElement('canvas');
    const ctx = canvasElement.getContext('2d');
    videoElement.style.display = 'none'; // Hide the video element

    if (!videoElement) {
        console.error(`Video element with ID video${playerIdx} not found.`);
        return;
    }

    const container = videoElement.parentNode;
    container.appendChild(canvasElement);

    let ws;
    if (activeStreams[playerIdx] && activeStreams[playerIdx].ws) {
        ws = activeStreams[playerIdx].ws;  // 기존 WebSocket 연결 재사용
    } else {
        ws = new WebSocket(`ws://${window.location.hostname}:13000/ws/${playerIdx}`);
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
        };
    }

    activeStreams[playerIdx] = { ws, device };  // 활성 스트림 저장 또는 업데이트
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
    connectWebSocket(playerIdx, device);
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
