# CCTV-streaming-web-dashboard_python
- This project is a CCTV Streaming Web Dashboard that enables users to register CCTV streams via ONVIF and RTSP protocols and view live CCTV feeds in real-time directly from the web interface. It was developed as part of a study initiative prior to starting a company project. Development was discontinued as the company project began, and the project was finalized as version 1 with the functionality of streaming raw video feeds. The code has not been fully stabilized, and further development is required, including the implementation of features such as AI model-based event handling, design improvements, and other enhancements.

## Documents
<a href="https://drive.google.com/drive/folders/1X15xp01TwhPIo8RGjtv203kUQFsOC7Ov?usp=sharing">
    <img alt="googledrive" src="https://img.shields.io/badge/drive-4285F4.svg?&style=for-the-badge&logo=googledrive&logoColor=white"/>
</a>
<a href="https://docs.google.com/presentation/d/1Wv2KExN0OKaopT74u-r_N9sOZxSiCbApAYBa8oFJjmM/edit?usp=sharing">
    <img alt="Web Interface" src="https://img.shields.io/badge/Web_Interface-FFA500.svg?&style=for-the-badge&logo=googleslides&logoColor=white"/>
</a>
<a href="https://docs.google.com/spreadsheets/d/1aZmW5uiR416mbD7YT220Uet3KyaL_Lss/edit?usp=sharing&ouid=102344057613445860363&rtpof=true&sd=true">
    <img alt="WBS" src="https://img.shields.io/badge/WBS-34A853.svg?&style=for-the-badge&logo=googlesheets&logoColor=white"/>
</a>

## Features
- Live CCTV Streaming: Add CCTV streams using ONVIF or RTSP and monitor live video feeds from the web.
- Capture Functionality: Take snapshots of the video feed directly from the dashboard.
- Full-Screen View: View individual streams in full-screen mode for better clarity.
- Screen Splitting: Divide the screen to view multiple feeds simultaneously. The dashboard supports up to 16 split screens.
- Low-Latency Playback: Streams play smoothly with a delay of only 2 seconds

## Technical Overview
- Streaming Protocols: ONVIF, FFMPEG, FFMPROBE

## Execution

### 1. DOCKER IMAGE BUILD
```
bash build_docker.sh
```
### 2. DOCKER CONTAINER START
```
bash build_docker.sh
```
### 3. FASTAPI START
```
bash src/run_server.sh
```

|Main Page |Streaming |
|:--------------:|:--------------:|
| ![CleanShot 2024-11-19 at 15 56 42@2x](https://github.com/user-attachments/assets/b3777f92-dd17-4e46-87dc-f38da9f014f2) | ![CleanShot 2024-11-19 at 15 57 52@2x](https://github.com/user-attachments/assets/38a159d3-bc45-4b76-9c26-baa078df84a5)
 |
