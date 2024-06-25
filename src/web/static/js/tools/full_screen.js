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
    if (document.exitFullscreen) {
        document.exitFullscreen();
    } else if (document.mozCancelFullScreen) {
        document.mozCancelFullScreen();
    } else if (document.webkitExitFullscreen) { 
        document.webkitExitFullscreen();
    } else if (document.msExitFullscreen) { 
        document.msExitFullscreen();
    }
    isFullscreen = false;
}
