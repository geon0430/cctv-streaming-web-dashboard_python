const infoIcon = document.getElementById('info-icon');
let infoVisible = false;
let updateInterval = null;
let isUpdating = false;

infoIcon.addEventListener('click', () => {
    toggleVideoInfo();
});

function toggleVideoInfo() {
    infoVisible = !infoVisible;
    const videoInfos = document.querySelectorAll('.video-info');
    videoInfos.forEach(info => {
        info.style.display = infoVisible ? 'block' : 'none';
    });

    if (infoVisible) {
        startStatusUpdates();
    } else {
        stopStatusUpdates();
    }
}

async function updateConnectionStatus() {
    if (isUpdating) return;  // Prevent duplicate updates
    isUpdating = true;
    const videoPlayers = document.querySelectorAll('.player');
    const fetchPromises = [];
    const results = [];

    videoPlayers.forEach((player, index) => {
        const playerIdx = player.dataset.channelId;  // 각 플레이어에 data-channel-id 속성이 있음
        if (!playerIdx) {
            console.error(`Player channel id is undefined for player at index ${index}`);
            results[index] = { error: true, message: "Player channel id is undefined" };
            return;
        }

        const fetchPromise = fetch(`/video_info/${playerIdx}`)
            .then(response => response.json())
            .then(result => {
                results[index] = result;
            })
            .catch(error => {
                results[index] = { error: true, message: error.message };
            });

        fetchPromises.push(fetchPromise);
    });

    await Promise.all(fetchPromises);

    videoPlayers.forEach((player, index) => {
        const videoInfo = player.querySelector('.video-info');
        const noVideoMessage = player.querySelector('.no-video-message');

        if (!videoInfo || !noVideoMessage) {
            console.error(`Missing video info or no video message element for player at index ${index}`);
            return;
        }

        const result = results[index];

        if (result.error || (result.fps === 0 && result.width === 0 && result.height === 0 && result.codec === "")) {
            noVideoMessage.style.display = 'block';
            videoInfo.style.display = 'none';
            noVideoMessage.innerText = "No video data available";
        } else {
            noVideoMessage.style.display = 'none';
            videoInfo.style.display = 'block';

            let statusClass = '';
            let statusText = '';

            if (result.status === "good") {
                statusClass = 'good';
                statusText = 'Status: Good';
            } else if (result.status === "normal") {
                statusClass = 'normal';
                statusText = 'Status: Normal';
            } else {
                statusClass = 'bad';
                statusText = 'Status: Bad';
            }

            videoInfo.className = `video-info ${statusClass}`;
            videoInfo.innerHTML = `
                FPS: ${result.fps}<br>
                Codec: ${result.codec}<br>
                Bitrate: ${result.bit_rate} kbps<br>
                Resolution: ${result.width}x${result.height}<br>
                ${statusText}<br>
                Latency: ${result.latency || 'N/A'} ms
            `;
        }
    });

    isUpdating = false;
}

function startStatusUpdates() {
    if (!updateInterval) {
        updateInterval = setInterval(updateConnectionStatus, 1000);
    } 
}

function stopStatusUpdates() {
    if (updateInterval) {
        clearInterval(updateInterval);
        updateInterval = null;

        // Hide all video info when stopping updates
        const videoInfos = document.querySelectorAll('.video-info');
        videoInfos.forEach(info => {
            info.style.display = 'none';
        });
        const noVideoMessages = document.querySelectorAll('.no-video-message');
        noVideoMessages.forEach(msg => {
            msg.style.display = 'none';
        });
    } 
}

document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        stopStatusUpdates();
    } else if (infoVisible) {
        startStatusUpdates();
    }
});

window.addEventListener('beforeunload', () => {
    stopStatusUpdates();
});

function initializeVideoInfoState() {
    infoVisible = false;
    const videoInfos = document.querySelectorAll('.video-info');
    videoInfos.forEach(info => {
        info.style.display = 'none';
    });
    const noVideoMessages = document.querySelectorAll('.no-video-message');
    noVideoMessages.forEach(msg => {
        msg.style.display = 'none';
    });
    stopStatusUpdates();
}

// initializeVideoInfoState 함수가 전역에서 접근 가능하도록 설정
window.initializeVideoInfoState = initializeVideoInfoState;

// 로드 시 initializeVideoInfoState 함수 호출하여 상태 초기화
window.addEventListener('load', initializeVideoInfoState);
