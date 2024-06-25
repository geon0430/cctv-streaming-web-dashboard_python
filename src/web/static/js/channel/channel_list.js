document.addEventListener('DOMContentLoaded', () => {
    const addChannelButton = document.getElementById('add-channel');
    const cancelButton = document.getElementById('cancel-button');
    const modal = document.getElementById('modal');
    const addGroupButton = document.getElementById('add-group');

    function openModal() {
        resetFormFields();
        modal.style.display = 'block';
        fetchGroups();
    }

    function closeModal() {
        modal.style.display = 'none';
    }

    function openGroupModal() {
        const groupModal = document.getElementById('group-modal');
        groupModal.style.display = 'block';
    }

    function closeGroupModal() {
        const groupModal = document.getElementById('group-modal');
        groupModal.style.display = 'none';
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
    }

    addChannelButton.addEventListener('click', openModal);
    cancelButton.addEventListener('click', closeModal);
    addGroupButton.addEventListener('click', openGroupModal);

    document.getElementById('channel-form').addEventListener('submit', (event) => {
        event.preventDefault();
        queryChannel();
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
        } else {
            document.getElementById('onvif-tab').classList.remove('active');
            document.getElementById('rtsp-tab').classList.add('active');
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

    async function queryChannel() {
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

    function displayResults(data, queryData) {
        const modalContent = document.querySelector('.modal-content');
        modalContent.innerHTML = `
            <h1>ONVIF 조회 결과</h1>
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
                <button id="prev-button">이전</button>
                <button id="register-button">등록</button>
            </div>
        `;

        document.getElementById('prev-button').addEventListener('click', () => {
            displayForm();
        });

        document.getElementById('register-button').addEventListener('click', async () => {
            const selectedRow = document.querySelector('#result-table tr.selected');
            if (selectedRow) {
                const selectedData = {
                    id: queryData.id,
                    pw: queryData.pw,
                    name: selectedRow.cells[0].textContent,
                    onvif_result_address: selectedRow.cells[4].textContent,
                    height: parseInt(selectedRow.cells[1].textContent.split('x')[1]),
                    width: parseInt(selectedRow.cells[1].textContent.split('x')[0]),
                    codec: selectedRow.cells[2].textContent,
                    fps: parseFloat(selectedRow.cells[3].textContent),
                    group: queryData.group 
                };
                console.log('Selected Data:', selectedData);
                await registerChannel(selectedData);
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

    async function registerChannel(data) {
        console.log('Register Channel Data:', data);
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
            alert('채널 등록 성공: ' + JSON.stringify(result));
            resetToInitialState(); 
        } catch (error) {
            alert('채널 등록 중 오류 발생: ' + error);
        }
    }

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
                <div class="form-group">
                    <label for="group">Group:</label>
                    <select id="group" name="group" class="input-field">
                        <option value="">Select group</option>
                    </select>
                    <button type="button" id="add-group" class="group-button">그룹 추가</button>
                </div>
                <div class="button-container">
                    <button type="submit" class="action-button">조회</button>
                    <button type="button" id="cancel-button" class="cancel-button">취소</button>
                </div>
            </form>
        `;

        document.getElementById('channel-form').addEventListener('submit', (event) => {
            event.preventDefault();
            queryChannel();
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
        addChannelButton.removeEventListener('click', openModal);
        addChannelButton.addEventListener('click', openModal);
        displayForm();
    }
});
