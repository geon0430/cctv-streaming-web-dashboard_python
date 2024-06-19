function setupPeer(videoElementId) {
    const videoElement = document.getElementById(videoElementId);
    const peer = new SimplePeer({ initiator: location.hash === '#1', trickle: false });

    peer.on('signal', data => {
        document.getElementById(videoElementId + 'Id').value = JSON.stringify(data);
    });

    const connectBtn = document.getElementById('connect' + videoElementId);
    if (connectBtn) {
        connectBtn.addEventListener('click', () => {
            const otherId = JSON.parse(document.getElementById('other' + videoElementId + 'Id').value);
            peer.signal(otherId);
        });
    }

    peer.on('stream', stream => {
        videoElement.srcObject = stream;
        videoElement.play();
    });
}

setupPeer('video1');
setupPeer('video2');
setupPeer('video3');
setupPeer('video4');

document.getElementById('add-channel').addEventListener('click', () => {
    document.getElementById('modal').style.display = 'block';
});

document.getElementById('close-modal').addEventListener('click', () => {
    document.getElementById('modal').style.display = 'none';
});

document.getElementById('cancel-button').addEventListener('click', () => {
    document.getElementById('modal').style.display = 'none';
});

function queryChannel() {
    alert('조회 버튼이 클릭되었습니다.');
}
