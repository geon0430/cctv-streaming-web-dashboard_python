const videoPlayersContainer = document.getElementById('video-players-container');
const fullscreenIcon = document.querySelector('.icon-wrapper[title="전체화면"]');
let isFullscreen = false;

fullscreenIcon.addEventListener('click', () => {
    if (!isFullscreen) {
        openFullscreen(videoPlayersContainer);
    }
});

document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && isFullscreen) {
        closeFullscreen();
    }
});

document.addEventListener('click', (event) => {
    if (isFullscreen && !videoPlayersContainer.contains(event.target)) {
        closeFullscreen();
    }
});

function openFullscreen(element) {
    if (element.requestFullscreen) {
        element.requestFullscreen();
    } else if (element.mozRequestFullScreen) { 
        element.mozRequestFullScreen();
    } else if (element.webkitRequestFullscreen) { 
        element.webkitRequestFullscreen();
    } else if (element.msRequestFullscreen) {
        element.msRequestFullscreen();
    }
    isFullscreen = true;
}

function closeFullscreen() {
    if (document.fullscreenElement) {
        if (document.exitFullscreen) {
            document.exitFullscreen().then(() => {
                isFullscreen = false;
            }).catch((err) => {
                console.error(`Failed to exit fullscreen mode: ${err.message}`);
            });
        } else if (document.mozCancelFullScreen) {
            document.mozCancelFullScreen().then(() => {
                isFullscreen = false;
            }).catch((err) => {
                console.error(`Failed to exit fullscreen mode: ${err.message}`);
            });
        } else if (document.webkitExitFullscreen) { 
            document.webkitExitFullscreen().then(() => {
                isFullscreen = false;
            }).catch((err) => {
                console.error(`Failed to exit fullscreen mode: ${err.message}`);
            });
        } else if (document.msExitFullscreen) { 
            document.msExitFullscreen().then(() => {
                isFullscreen = false;
            }).catch((err) => {
                console.error(`Failed to exit fullscreen mode: ${err.message}`);
            });
        }
    } else {
        console.warn('Not in fullscreen mode.');
    }
}
