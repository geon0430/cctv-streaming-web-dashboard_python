document.addEventListener('DOMContentLoaded', () => {
    const addChannelButton = document.getElementById('add-channel');
    const cancelButton = document.getElementById('cancel-button');
    const modal = document.getElementById('modal');
    const addGroupButton = document.getElementById('add-group');
    const groupCancelButton = document.getElementById('cancel-group');
    const saveGroupButton = document.getElementById('save-group');
    const groupModal = document.getElementById('group-modal');
    const removeChannelButton = document.getElementById('remove-channel');

    function openModal() {
        resetFormFields();
        modal.style.display = 'block';
        fetchGroups();
    }

    function closeModal() {
        modal.style.display = 'none';
    }

    function openGroupModal() {
        resetGroupModal(); // 그룹 모달 초기화
        groupModal.style.display = 'block';
    }

    function closeGroupModal() {
        groupModal.style.display = 'none';
    }

    function resetGroupModal() {
        document.getElementById('group-name').value = ''; // 그룹명 입력 필드 초기화
    }

    async function addGroup() {
        const groupName = document.getElementById('group-name').value;

        if (!groupName) {
            alert('그룹명을 입력하세요.');
            return;
        }

        const groupSelect = document.getElementById('group');

        const option = document.createElement('option');
        option.value = groupName;
        option.textContent = groupName;
        groupSelect.appendChild(option);

        closeGroupModal();
        resetGroupModal(); // 그룹 모달 초기화
    }

    addChannelButton.addEventListener('click', openModal);
    cancelButton.addEventListener('click', closeModal);
    addGroupButton.addEventListener('click', openGroupModal);
    saveGroupButton.addEventListener('click', addGroup);
    groupCancelButton.addEventListener('click', closeGroupModal);

    document.getElementById('channel-form').addEventListener('submit', (event) => {
        event.preventDefault();
        if (document.getElementById('onvif-tab').classList.contains('active')) {
            queryOnvifChannel();
        } else {
            queryRtspChannel();
        }
    });

    document.getElementById('onvif-tab').addEventListener('click', () => {
        setActiveTab('onvif');
    });

    document.getElementById('rtsp-tab').addEventListener('click', () => {
        setActiveTab('rtsp');
    });

    function setActiveTab(tab) {
        if (tab === 'onvif') {
            document.getElementById('onvif-tab').classList.add('active');
            document.getElementById('rtsp-tab').classList.remove('active');
            document.getElementById('onvif-form').style.display = 'block';
            document.getElementById('rtsp-form').style.display = 'none';
        } else {
            document.getElementById('onvif-tab').classList.remove('active');
            document.getElementById('rtsp-tab').classList.add('active');
            document.getElementById('onvif-form').style.display = 'none';
            document.getElementById('rtsp-form').style.display = 'block';
        }
    }

    async function fetchGroups() {
        try {
            const response = await fetch('/get_groups/');
            const groups = await response.json();
            const groupSelect = document.getElementById('group');
            groupSelect.innerHTML = '<option value="">Select group</option>';
            if (groups.length > 0) {
                groups.forEach(group => {
                    const option = document.createElement('option');
                    option.value = group;
                    option.textContent = group;
                    groupSelect.appendChild(option);
                });
            } else {
                const option = document.createElement('option');
                option.value = '';
                option.textContent = 'No groups available';
                groupSelect.appendChild(option);
            }
        } catch (error) {
            console.error('Error fetching groups:', error);
        }
    }

    async function queryOnvifChannel() {
        const ip = document.getElementById('ip').value;
        const id = document.getElementById('id').value;
        const password = document.getElementById('pass').value;
        const group = document.getElementById('group').value;

        const data = {
            ip_address: ip,
            id: id,
            pw: password,
            group: group
        };

        try {
            const response = await fetch('/onvif_list/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify([data])
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            if (result.detail === "success") {
                displayResults(result.data, data);
            } else {
                alert('Error: ' + result.detail);
            }
        } catch (error) {
            alert('조회 중 오류 발생: ' + error);
        }
    }

    async function queryRtspChannel() {
        const address = document.getElementById('address').value;
        const id = document.getElementById('rtsp-id').value;
        const password = document.getElementById('rtsp-pass').value;
        const group = document.getElementById('group').value;
    
        const data = {
            address: address,
            id: id,
            password: password,
            group: group
        };
    
        try {
            const response = await fetch('/rtsp_channel_add/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
    
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
    
            const result = await response.json();
            if (result.detail === "success") {
                displayRtspResults(result.data, data);
            } else {
                alert('Error: ' + result.detail);
            }
        } catch (error) {
            alert('조회 중 오류 발생: ' + error);
        }
    }

    function displayResults(data, queryData) {
        const modalContent = document.querySelector('.modal-content');
        modalContent.innerHTML = `
            <h1>${document.getElementById('onvif-tab').classList.contains('active') ? 'ONVIF' : 'RTSP'} 조회 결과</h1>
            <div id="result-table-container">
                <table id="result-table">
                    <thead>
                        <tr>
                            <th>Profile</th>
                            <th>Resolution</th>
                            <th>Codec</th>
                            <th>FPS</th>
                            <th style="display:none;">RTSP</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${data.map(item => `
                            <tr onclick="selectRow(this)">
                                <td>${item.name}</td>
                                <td>${item.width}x${item.height}</td>
                                <td>${item.codec}</td>
                                <td>${item.fps}</td>
                                <td style="display:none;">${item.rtsp}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
            <div class="button-container">
                <button id="prev-button" class="main-action-button">이전</button>
                <button id="register-button" class="main-action-button">등록</button>
            </div>
        `;

        document.getElementById('prev-button').addEventListener('click', () => {
            displayForm();
        });

        document.getElementById('register-button').addEventListener('click', async () => {
            const selectedRow = document.querySelector('#result-table tr.selected');
            if (selectedRow) {
                const selectedData = {
                    ip: queryData.ip_address,
                    onvif_result_address: selectedRow.cells[4].textContent,
                    height: parseInt(selectedRow.cells[1].textContent.split('x')[1]),
                    width: parseInt(selectedRow.cells[1].textContent.split('x')[0]),
                    codec: selectedRow.cells[2].textContent,
                    fps: parseFloat(selectedRow.cells[3].textContent),
                    group: queryData.group
                };
                await registerChannel(selectedData);
                await fetchChannelList(); // 채널 목록 업데이트
            } else {
                alert('항목을 선택하세요.');
            }
        });

        document.querySelectorAll('#result-table tbody tr').forEach(row => {
            row.addEventListener('click', function() {
                document.querySelectorAll('#result-table tbody tr').forEach(r => r.classList.remove('selected'));
                this.classList.add('selected');
            });
        });

        document.getElementById('modal').style.display = 'block';
    }

    function displayRtspResults(data, queryData) {
        const modalContent = document.querySelector('.modal-content');
        modalContent.innerHTML = `
            <h1>RTSP 조회 결과</h1>
            <div id="result-table-container">
                <table id="result-table">
                    <tbody>
                        <tr>
                            <th>RTSP URL</th>
                            <td class="long-text">${data.onvif_result_address}</td>
                        </tr>
                        <tr>
                            <th>FPS</th>
                            <td>${data.fps}</td>
                        </tr>
                        <tr>
                            <th>Codec</th>
                            <td>${data.codec}</td>
                        </tr>
                        <tr>
                            <th>Width</th>
                            <td>${data.width}</td>
                        </tr>
                        <tr>
                            <th>Height</th>
                            <td>${data.height}</td>
                        </tr>
                        <tr>
                            <th>Group</th>
                            <td>${data.group}</td>
                        </tr>
                        <tr>
                            <th>IP</th>
                            <td>${data.ip}</td>
                        </tr>
                    </tbody>
                </table>
            </div>
            <div class="button-container">
                <button id="prev-button" class="main-action-button">이전</button>
                <button id="register-button" class="main-action-button">등록</button>
            </div>
        `;

        document.getElementById('prev-button').addEventListener('click', () => {
            displayForm();
        });

        document.getElementById('register-button').addEventListener('click', async () => {
            const selectedData = {
                ip: data.ip,
                onvif_result_address: data.onvif_result_address,
                fps: data.fps,
                codec: data.codec,
                width: data.width,
                height: data.height,
                group: data.group
            };
            await registerRtspChannel(selectedData);
            await fetchChannelList(); // 채널 목록 업데이트
        });

        document.getElementById('modal').style.display = 'block';
    }

    async function registerRtspChannel(data) {
        try {
            const response = await fetch('/channel_add/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify([data])
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            showNotificationModal('채널 등록 성공');
            resetToInitialState();
        } catch (error) {
            showNotificationModal('채널 등록 중 오류 발생: ' + error);
        }
    }

    async function registerChannel(data) {
        try {
            const response = await fetch('/channel_add/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify([data])
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            showNotificationModal('채널 등록 성공');
            resetToInitialState();
        } catch (error) {
            showNotificationModal('채널 등록 중 오류 발생: ' + error);
        }
    }

    function showNotificationModal(message) {
        const notificationMessage = document.getElementById('notification-message');
        notificationMessage.textContent = message;
        const notificationModal = document.getElementById('notification-modal');
        notificationModal.style.display = 'block';
    }

    document.getElementById('close-notification').addEventListener('click', () => {
        const notificationModal = document.getElementById('notification-modal');
        notificationModal.style.display = 'none';
    });

    function resetFormFields() {
        const form = document.getElementById('channel-form');
        if (form) {
            form.reset();
        }
    }

    function displayForm() {
        const modalContent = document.querySelector('.modal-content');
        modalContent.innerHTML = `
            <div class="tab-container">
                <button class="tab-button active" id="onvif-tab">Onvif 등록</button>
                <button class="tab-button" id="rtsp-tab">RTSP 등록</button>
            </div>
            <form id="channel-form">
                <div id="onvif-form">
                    <div class="form-group">
                        <label for="ip">IP:</label>
                        <input type="text" id="ip" name="ip" class="input-field">
                    </div>
                    <div class="form-group">
                        <label for="id">ID:</label>
                        <input type="text" id="id" name="id" class="input-field">
                    </div>
                    <div class="form-group">
                        <label for="pass">Password:</label>
                        <input type="password" id="pass" name="pass" class="input-field">
                    </div>
                </div>
                <div id="rtsp-form" style="display:none;">
                    <div class="form-group">
                        <label for="address">Address:</label>
                        <input type="text" id="address" name="address" class="input-field">
                    </div>
                    <div class="form-group">
                        <label for="id">ID:</label>
                        <input type="text" id="rtsp-id" name="id" class="input-field">
                    </div>
                    <div class="form-group">
                        <label for="pass">Password:</label>
                        <input type="password" id="rtsp-pass" name="pass" class="input-field">
                    </div>
                </div>
                <div class="form-group">
                    <label for="group">Group:</label>
                    <select id="group" name="group" class="input-field">
                        <option value="">Select group</option>
                    </select>
                    <button type="button" id="add-group" class="group-button">그룹 추가</button>
                </div>
                <div class="button-container">
                    <button type="submit" class="main-action-button">조회</button>
                    <button type="button" id="cancel-button" class="main-action-button">취소</button>
                </div>
            </form>
        `;

        document.getElementById('channel-form').addEventListener('submit', (event) => {
            event.preventDefault();
            if (document.getElementById('onvif-tab').classList.contains('active')) {
                queryOnvifChannel();
            } else {
                queryRtspChannel();
            }
        });

        document.getElementById('cancel-button').addEventListener('click', () => {
            closeModal();
        });

        document.getElementById('onvif-tab').addEventListener('click', () => {
            setActiveTab('onvif');
        });

        document.getElementById('rtsp-tab').addEventListener('click', () => {
            setActiveTab('rtsp');
        });

        fetchGroups();
    }

    function resetToInitialState() {
        closeModal();
        resetFormFields();
        resetGroupModal(); // 그룹 모달 초기화 추가
        displayForm();
    }
});

function selectRow(row) {
    row.classList.add('selected');
}
