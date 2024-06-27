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
    const groupMap = new Map();

    // Separate groups and ungrouped items
    const groupedItems = [];
    const ungroupedItems = [];

    data.sort((a, b) => {
        if (a.group === b.group) {
            return (a.onvif_result_address || '').localeCompare(b.onvif_result_address || '');
        }
        return (a.group || '').localeCompare(b.group || '');
    });

    data.forEach(device => {
        const listItem = createListItem(device);
        if (device.group) {
            groupedItems.push({ group: device.group, listItem });
        } else {
            ungroupedItems.push(listItem);
        }
    });

    const groupSet = new Set();
    groupedItems.forEach(item => {
        const groupName = item.group;
        if (!groupSet.has(groupName)) {
            const groupElement = createGroupElement(groupName);
            fileList.appendChild(groupElement);
            groupMap.set(groupName, groupElement.querySelector('ul'));
            groupSet.add(groupName);
        }
        groupMap.get(groupName).appendChild(item.listItem);
    });

    ungroupedItems.forEach(item => fileList.appendChild(item));
}

function createListItem(device) {
    const listItem = document.createElement('li');
    listItem.textContent = `${device.ip} | ${device.codec} | ${device.fps}fps | ${device.width}x${device.height}`;
    listItem.setAttribute('draggable', 'false');
    listItem.dataset.id = device.idx; // Store device ID in the dataset
    listItem.addEventListener('click', (event) => itemClicked(event, device));
    listItem.addEventListener('dragstart', (e) => itemDragStart(e, device));
    listItem.style.userSelect = 'none'; // Prevent text selection
    return listItem;
}

function createGroupElement(groupName) {
    const groupElement = document.createElement('div');
    groupElement.className = 'group';
    groupElement.innerHTML = `<h3 class="group-title" onclick="toggleGroup('${groupName}')">${groupName}<span class="expand-icon"></span></h3><ul id="${groupName}-list" class="group-list"></ul>`;
    return groupElement;
}

function toggleGroup(groupName) {
    const groupList = document.getElementById(`${groupName}-list`);
    const groupTitle = groupList.parentElement.querySelector('.group-title');
    groupList.style.display = groupList.style.display === 'none' ? 'block' : 'none';
    groupTitle.classList.toggle('open');
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
        event.dataTransfer.setData('text/plain', JSON.stringify(device));
    } else {
        event.preventDefault(); 
    }
}

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

async function removeChannel() {
    const selected = document.querySelector('#file-list li.selected');
    if (selected) {
        const id = selected.dataset.id;
        try {
            const response = await fetch(`/delete_channel/${id}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            if (response.ok) {
                await fetchChannelList();
                showCustomNotification('채널이 성공적으로 삭제되었습니다.');
            } else {
                const errorData = await response.json();
                showCustomNotification(`채널 삭제 실패: ${errorData.detail}`);
            }
        } catch (error) {
            console.error('채널 삭제 중 오류 발생:', error);
            showCustomNotification('채널 삭제 중 오류 발생');
        }
    } else {
        showCustomNotification('삭제할 채널을 선택하세요.');
    }
}

function showCustomNotification(message) {
    const modal = document.getElementById('notification-modal');
    const messageElement = document.getElementById('notification-message');
    messageElement.textContent = message;
    modal.style.display = 'block';

    const closeBtn = document.getElementById('close-notification');
    closeBtn.onclick = function () {
        modal.style.display = 'none';
    }
}

document.getElementById('remove-channel').addEventListener('click', removeChannel);


document.getElementById('remove-channel').addEventListener('click', removeChannel);

window.fetchChannelList = fetchChannelList; 
window.onload = fetchChannelList;
