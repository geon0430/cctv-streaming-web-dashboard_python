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
    if (isUpdating) return;  
    isUpdating = true;
    const videoPlayers = document.querySelectorAll('.player');
    const fetchPromise = fetch(`/video_info/`)
        .then(response => response.json())
        .then(results => {
            videoPlayers.forEach((player, index) => {
                const videoInfo = player.querySelector('.video-info');
                const noVideoMessage = player.querySelector('.no-video-message');
    
                if (!videoInfo || !noVideoMessage) {
                    console.error(`플레이어 인덱스 ${index}에 대해 영상 정보 또는 "영상 없음" 메시지 요소가 없습니다`);
                    return;
                }

                const result = results[index];

                if (result.error || (result.fps === 0 && result.width === 0 && result.height === 0 && result.codec === "")) {
                    noVideoMessage.style.display = 'block';
                    videoInfo.style.display = 'none';
                    noVideoMessage.innerText = "영상 데이터가 없습니다";
                } else {
                    noVideoMessage.style.display = 'none';
                    videoInfo.style.display = 'block';

                    let statusClass = '';
                    let statusText = '';

                    if (result.status === "good") {
                        statusClass = 'good';
                        statusText = '상태: 양호';
                    } else if (result.status === "normal") {
                        statusClass = 'normal';
                        statusText = '상태: 보통';
                    } else {
                        statusClass = 'bad';
                        statusText = '상태: 불량';
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
        })
        .catch(error => {
            videoPlayers.forEach((player, index) => {
                const noVideoMessage = player.querySelector('.no-video-message');
                if (noVideoMessage) {
                    noVideoMessage.style.display = 'block';
                    noVideoMessage.innerText = "영상 데이터를 가져오는 중 오류 발생";
                }
            });
            console.error("영상 데이터를 가져오는 중 오류 발생:", error.message);
        });

    await fetchPromise;
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

window.initializeVideoInfoState = initializeVideoInfoState;
window.addEventListener('load', initializeVideoInfoState);
