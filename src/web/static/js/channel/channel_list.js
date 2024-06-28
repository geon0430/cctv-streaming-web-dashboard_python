async function fetchChannelList() {
    try {
        const response = await fetch('/get_channel_db/', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        if (response.ok) {
            const data = await response.json();
            renderChannelList(data);
        } else {
            console.error('채널 목록을 가져오는데 실패했습니다:', response.statusText);
        }
    } catch (error) {
        console.error('채널 목록을 가져오는 중 오류 발생:', error);
    }
}

function renderChannelList(data) {
    const fileList = document.getElementById('file-list');
    fileList.innerHTML = ''; 
    data.forEach(device => {
        const listItem = createListItem(device);
        fileList.appendChild(listItem);
    });
}

function createListItem(device) {
    const listItem = document.createElement('li');
    listItem.textContent = `${device.ip} | ${device.codec} | ${device.fps}fps | ${device.width}x${device.height}`;
    listItem.setAttribute('draggable', 'true');
    listItem.dataset.id = device.idx;
    listItem.addEventListener('click', (event) => itemClicked(event, device));
    listItem.addEventListener('dragstart', (e) => itemDragStart(e, device));
    listItem.style.userSelect = 'none';
    return listItem;
}

function itemClicked(event, device) {
    const items = document.querySelectorAll('#file-list li');
    items.forEach(item => {
        item.classList.remove('selected');
        item.setAttribute('draggable', 'false');
    });
    event.currentTarget.classList.add('selected');
    event.currentTarget.setAttribute('draggable', 'true'); 
    console.log('Item clicked:', device);
}

function itemDragStart(event, device) {
    if (event.currentTarget.classList.contains('selected')) {
        event.dataTransfer.setData('application/json', JSON.stringify(device));
    } else {
        event.preventDefault(); 
    }
}

document.getElementById('search-bar').addEventListener('input', function () {
    const searchTerm = this.value.toLowerCase();
    const items = document.querySelectorAll('#file-list li'); 
    items.forEach(item => {
        if (item.textContent.toLowerCase().includes(searchTerm)) {
            item.style.display = '';
        } else {
            item.style.display = 'none';
        }
    });
});

window.onload = fetchChannelList;
