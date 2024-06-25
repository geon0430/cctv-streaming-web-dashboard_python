document.getElementById('capture-icon').addEventListener('click', captureScreen);
function captureScreen() {
    html2canvas(videoPlayersContainer).then(canvas => {
        canvas.toBlob(blob => {
            const formData = new FormData();
            const filename = `screenshot_${Date.now()}.png`;
            formData.append('image', blob, filename);

            fetch('/save_screenshot/', {
                method: 'POST',
                body: formData
            }).then(response => {
                if (response.ok) {
                    showNotification(`Screenshot saved successfully at /desired/path/${filename}`);
                } else {
                    showNotification('Failed to save screenshot.');
                }
            }).catch(error => {
                console.error('Error:', error);
                showNotification('An error occurred while saving the screenshot.');
            });
        });
    }).catch(error => {
        console.error('Error capturing screen:', error);
        showNotification('An error occurred while capturing the screen.');
    });
}


function showNotification(message) {
    const notificationModal = document.getElementById('notification-modal');
    const notificationMessage = document.getElementById('notification-message');
    notificationMessage.textContent = message;
    notificationModal.style.display = 'block';

    document.getElementById('close-notification').addEventListener('click', () => {
        notificationModal.style.display = 'none';
    });
}
