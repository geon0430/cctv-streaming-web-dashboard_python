# CCTV Streaming Web Dashboard
[English](https://github.com/geon0430/cctv-streaming-web-dashboard_python/blob/main/README_en.md)
- 사용자가 ONVIF 및 RTSP 프로토콜을 통해 CCTV 스트림을 등록하고 웹 인터페이스에서 실시간 CCTV 화면을 확인하는 웹 페이지를 개발하였다.
- 회사 프로젝트를 시작하기 전에 개인 공부 목적으로 개발하여 이후 회사 프로젝트가 시작되면서 개발이 중단되었고, 원본 영상 스트리밍 기능까지 버전 1로 마무리하였다.
- 현재 다 채널 스트리밍은 불안정하며, AI 모델 기반 이벤트 처리, 디자인 개선 및 기타 기능 구현과 같은 추가 개발이 필요하다.

  ## 주요 기능
- 실시간 CCTV 스트리밍: ONVIF 또는 RTSP를 사용하여 CCTV 스트림을 추가하고 웹에서 실시간 영상 확인 가능.
- 캡처 기능: 대시보드에서 직접 영상의 스냅샷을 캡처.
- 전체 화면 보기: 개별 스트림을 전체 화면으로 확대하여 보다 선명하게 확인.
- 화면 분할: 화면을 분할하여 여러 스트림을 동시에 확인 가능. 최대 16분할 화면을 지원.
- 저지연 재생: 스트림은 최대 2초의 딜레이로 프레임드랍 없이 재생
- 스트리밍 프로토콜: ONVIF, FFMPEG, FFMPROBE 

## 실행

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
