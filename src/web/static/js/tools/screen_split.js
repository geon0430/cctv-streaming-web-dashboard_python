document.addEventListener('DOMContentLoaded', async () => {
    try {
        const response = await fetch('/get_layout/');
        if (!response.ok) {
            throw new Error('Failed to fetch layout.');
        }
        const result = await response.json();
        const layout = result.layout;

        // Call the function to update the video player layout based on the fetched layout
        updateVideoPlayers(layout);
        console.log(`Page has loaded with layout: ${layout}`);
        
        // Reconnect to active streams after layout is updated
        const activeStreams = JSON.parse(localStorage.getItem('activeStreams')) || {};
        Object.keys(activeStreams).forEach(playerIdx => {
            const { device } = activeStreams[playerIdx];
            setTimeout(() => connectWebSocket(playerIdx, device), 0); // delay to ensure elements are ready
        });

    } catch (error) {
        console.error('Error fetching layout:', error);
    }

    document.addEventListener('contextmenu', (event) => {
        console.log('Right-click event was blocked.');
        event.preventDefault();
    });

    const contextMenu = document.getElementById('custom-context-menu');

    const players = document.querySelectorAll('.player');
    players.forEach(player => {
        attachContextMenuEvent(player);
    });

    document.addEventListener('click', () => {
        contextMenu.style.display = 'none';
        console.log('Custom context menu was closed by page click.');
    });

    console.log('Page has loaded.');

    // Monitor split icon click event
    const monitorSplitIcon = document.getElementById('monitor-split-icon');
    const monitorSplitDropdown = document.getElementById('monitor-split-dropdown');

    monitorSplitIcon.addEventListener('click', (event) => {
        toggleDropdown(monitorSplitDropdown);
        event.stopPropagation();
    });

    document.addEventListener('click', (event) => {
        if (!monitorSplitDropdown.contains(event.target) && !monitorSplitIcon.contains(event.target)) {
            monitorSplitDropdown.style.display = 'none';
        }
    });
});

function attachContextMenuEvent(player) {
    const contextMenu = document.getElementById('custom-context-menu');

    player.addEventListener('contextmenu', (event) => {
        event.preventDefault();
        console.log(`Right-click detected on player ${player.id}.`);

        const { clientX: mouseX, clientY: mouseY } = event;
        console.log(`Mouse position - X: ${mouseX}, Y: ${mouseY}`);

        contextMenu.style.top = `${mouseY}px`;
        contextMenu.style.left = `${mouseX}px`;
        contextMenu.style.display = 'block';
        console.log('Custom context menu is displayed.');

        const playerId = player.id.replace("player", ""); 

        document.getElementById('player-info').onclick = () => {
            alert(`Player Info for player${playerId}`);
            contextMenu.style.display = 'none';
            console.log('Player info was clicked.');
        };

        document.getElementById('delete-video').onclick = async () => {
            console.log(`Delete video was clicked for player${playerId}.`);

            await removeChannel(playerId);

            contextMenu.style.display = 'none';
        };
    });
}


function selectPlayer(playerId) {
    const players = document.querySelectorAll('.player');
    players.forEach(player => player.classList.remove('selected'));
    const selectedPlayer = document.getElementById(playerId);
    if (selectedPlayer) {
        selectedPlayer.classList.add('selected');
    }
    console.log(`Player ${playerId} was selected.`);
}

function updateVideoPlayers(layout) {
    const videoPlayersContainer = document.getElementById('video-players-container');
    const playersGrid = videoPlayersContainer.querySelector('.players-grid') || document.createElement('div');
    playersGrid.className = 'players-grid';

    const currentPlayers = Array.from(playersGrid.children);
    const currentStreams = {};

    currentPlayers.forEach(player => {
        const playerIdx = player.dataset.idx;
        if (activeStreams[playerIdx]) {
            currentStreams[playerIdx] = activeStreams[playerIdx];
        }
    });

    let rows, columns;
    switch (layout) {
        case 'img1':
            rows = 1;
            columns = 1;
            break;
        case 'img2':
            rows = 2;
            columns = 2;
            break;
        case 'img3':
            rows = 3;
            columns = 3;
            break;
        case 'img4':
            rows = 4;
            columns = 4;
            break;
        default:
            rows = 1;
            columns = 1;
    }

    playersGrid.style.gridTemplateRows = `repeat(${rows}, 1fr)`;
    playersGrid.style.gridTemplateColumns = `repeat(${columns}, 1fr)`;

    for (let i = 1; i <= rows * columns; i++) {
        let player = playersGrid.querySelector(`#player${i}`);
        if (!player) {
            player = document.createElement('div');
            player.className = `player player${i}`;
            player.dataset.idx = i;
            player.id = `player${i}`;
            player.ondrop = (event) => drop(event);
            player.ondragover = (event) => allowDrop(event);
            player.onclick = () => selectPlayer(player.id);
            player.innerHTML = `
                <video id="video${i}" width="100%" height="100%" autoplay muted></video>
                <div class="video-info" id="info${i}"></div>
                <div class="no-video-message" id="no-video${i}" style="display:none;">No video data available</div>
            `;
            playersGrid.appendChild(player);

            if (currentStreams[i]) {
                activeStreams[i] = currentStreams[i];
                connectWebSocket(i, currentStreams[i].device);
            }

            attachContextMenuEvent(player);
        }
    }

    Array.from(playersGrid.children).forEach(player => {
        if (parseInt(player.dataset.idx, 10) > rows * columns) {
            player.remove();
        }
    });

    videoPlayersContainer.innerHTML = '';
    videoPlayersContainer.appendChild(playersGrid);
    console.log('Video player layout has been updated.');
}

function toggleDropdown(dropdown) {
    dropdown.style.display = dropdown.style.display === 'block' ? 'none' : 'block';
    console.log(`Dropdown menu is now ${dropdown.style.display === 'block' ? 'open' : 'closed'}.`);
}

function selectImage(imageId) {
    callSortVideoPlayerAPI(imageId);
    const monitorSplitDropdown = document.getElementById('monitor-split-dropdown');
    monitorSplitDropdown.style.display = 'none';
    if (window.initializeVideoInfoState) {
        window.initializeVideoInfoState();  
    } else {
        console.error('initializeVideoInfoState function is not defined.');
    }
    console.log(`Image ${imageId} was selected.`);
}

async function callSortVideoPlayerAPI(layout) {
    try {
        const response = await fetch('/sort_player_layout/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ layout }),
        });

        if (!response.ok) {
            throw new Error('Failed to update player layout.');
        }

        const result = await response.json();
        const { active_players, inactive_players } = result;

        for (const playerId of inactive_players) {
            await deletePlayer(playerId);
        }

        updateVideoPlayers(layout);
        console.log('Player layout was successfully updated.');
    } catch (error) {
        console.error('Error:', error);
    }
}

async function deletePlayer(playerId) {
    try {
        const response = await fetch(`/delete_player/${playerId}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
            }
        });

        if (!response.ok) {
            throw new Error('Failed to delete player.');
        }

        const result = await response.json();
        console.log(result.detail);
    } catch (error) {
        console.error('Error:', error);
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
    console.log('Device dropped:', device, 'on player:', playerIdx);
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

async function fetchChannelList() {
    try {
        const response = await fetch('/channel_list/');
        if (!response.ok) {
            throw new Error('Failed to fetch channel list.');
        }
        const channels = await response.json();
        console.log('Channel list was successfully loaded.');
    } catch (error) {
        console.error('Error fetching channel list:', error);
    }
}

window.fetchChannelList = fetchChannelList;
window.onload = fetchChannelList;
