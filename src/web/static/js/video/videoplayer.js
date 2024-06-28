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

// Add event listeners
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
