document.getElementById('add-channel').addEventListener('click', () => {
    resetFormFields();
    document.getElementById('modal').style.display = 'block';
});

document.getElementById('cancel-button').addEventListener('click', () => {
    document.getElementById('modal').style.display = 'none';
});

document.getElementById('channel-form').addEventListener('submit', (event) => {
    event.preventDefault();
    queryChannel();
});

async function queryChannel() {
    const ip = document.getElementById('ip').value;
    const id = document.getElementById('id').value;
    const password = document.getElementById('pass').value;

    const data = {
        ip_address: ip,
        id: id,
        pw: password
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
        <h1>조회 결과</h1>
        <div id="result-table-container">
            <table id="result-table">
                <thead>
                    <tr>
                        <th>Profile</th>
                        <th>Resolution</th>
                        <th>Codec</th>
                        <th>FPS</th>
                        <th style="display:none;">RTSP</th> <!-- RTSP URL을 숨긴 칼럼 -->
                    </tr>
                </thead>
                <tbody>
                    ${data.map(item => `
                        <tr onclick="selectRow(this)">
                            <td>${item.name}</td>
                            <td>${item.width}x${item.height}</td>
                            <td>${item.codec}</td>
                            <td>${item.fps}</td>
                            <td style="display:none;">${item.rtsp}</td> <!-- RTSP URL을 숨긴 데이터 -->
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
                fps: parseFloat(selectedRow.cells[3].textContent)
            };
            console.log('Selected Data:', selectedData);
            await registerChannel(selectedData);
        } else {
            alert('항목을 선택하세요.');
        }
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
        document.getElementById('modal').style.display = 'none';
        resetFormFields(); 
    } catch (error) {
        alert('채널 등록 중 오류 발생: ' + error);
    }
}

function selectRow(row) {
    const selected = document.querySelector('#result-table tr.selected');
    if (selected) {
        selected.classList.remove('selected');
    }
    row.classList.add('selected');
}

function resetFormFields() {
    document.getElementById('channel-form').reset();
    document.getElementById('ip').value = '';
    document.getElementById('id').value = '';
    document.getElementById('pass').value = '';
}

function displayForm() {
    const modalContent = document.querySelector('.modal-content');
    modalContent.innerHTML = `
        <h1>채널 등록</h1>
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
        document.getElementById('modal').style.display = 'none';
    });
}
