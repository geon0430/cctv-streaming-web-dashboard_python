const infoIcon = document.getElementById('info-icon');
let infoVisible = false;
let updateInterval = null;

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
    const videoPlayers = document.querySelectorAll('.player');
    const fetchPromises = [];
    const results = [];

    videoPlayers.forEach((player, index) => {
        const fetchPromise = fetch('/ping/').then(response => response.json()).then(result => {
            results[index] = result;
        }).catch(error => {
            results[index] = { status: "bad", latency: "N/A", error: error.message };
        });

        fetchPromises.push(fetchPromise);
    });

    await Promise.all(fetchPromises);

    videoPlayers.forEach((player, index) => {
        const videoInfo = player.querySelector('.video-info');
        const result = results[index];

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
            FPS: 30<br>
            Codec: H.264<br>
            Bitrate: 5000 kbps<br>
            Resolution: 1920x1080<br>
            ${statusText}<br>
            Latency: ${result.latency} ms
        `;
    });
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
    stopStatusUpdates();
}

// Ensure initializeVideoInfoState is globally accessible
window.initializeVideoInfoState = initializeVideoInfoState;

// Call the initializeVideoInfoState function on load to reset state
window.addEventListener('load', initializeVideoInfoState);
