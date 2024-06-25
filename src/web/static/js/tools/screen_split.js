const monitorSplitIcon = document.getElementById('monitor-split-icon');
const monitorSplitDropdown = document.getElementById('monitor-split-dropdown');

monitorSplitIcon.addEventListener('click', (event) => {
    toggleDropdown();
    event.stopPropagation();
});

function toggleDropdown() {
    monitorSplitDropdown.style.display = monitorSplitDropdown.style.display === 'block' ? 'none' : 'block';
}

function selectImage(imageId) {
    updateVideoPlayers(imageId);
    monitorSplitDropdown.style.display = 'none';
    if (window.initializeVideoInfoState) {
        window.initializeVideoInfoState();  // 비디오 정보 초기화 후 다시 불러오기
    } else {
        console.error('initializeVideoInfoState function is not defined.');
    }
}

function updateVideoPlayers(layout) {
    const videoPlayersContainer = document.getElementById('video-players-container');
    videoPlayersContainer.innerHTML = '';

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

    videoPlayersContainer.style.gridTemplateRows = `repeat(${rows}, 1fr)`;
    videoPlayersContainer.style.gridTemplateColumns = `repeat(${columns}, 1fr)`;

    for (let i = 1; i <= rows * columns; i++) {
        const player = document.createElement('div');
        player.className = `player player${i}`;
        player.innerHTML = `
            <video id="video${i}" width="100%" height="100%" autoplay muted></video>
            <div class="video-info" id="info${i}"></div>
        `;
        videoPlayersContainer.appendChild(player);
    }
}

updateVideoPlayers('img1');

document.addEventListener('click', (event) => {
    if (!monitorSplitDropdown.contains(event.target) && !monitorSplitIcon.contains(event.target)) {
        monitorSplitDropdown.style.display = 'none';
    }
});
