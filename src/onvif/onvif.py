from onvif2 import ONVIFCamera
import sys
sys.path.append("../../")

def get_onvif_rtsp_address_list(ip, port=80, id=None, passwd=None):
    try:
        mycam = ONVIFCamera(ip, port, id, passwd, wsdl_dir='/webrtc_python/src/onvif/wsdl', adjust_time=True)
        media_service2 = mycam.create_media2_service()
        profiles = media_service2.GetProfiles()
        configurations = media_service2.GetVideoEncoderConfigurations()

        configuration_list = []
        for configuration in configurations:
            if configuration.UseCount != 0:
                configuration_list.append(configuration)

        results = []
        for p, c in zip(profiles, configuration_list):
            o = media_service2.create_type('GetStreamUri')
            o.ProfileToken = p.token
            o.Protocol = 'RTSP'
            uri_response = media_service2.GetStreamUri(o)

            uri = uri_response if isinstance(uri_response, str) else uri_response.Uri

            if passwd is None:
                rtsp_uri = uri
            else:
                rtsp_uri = f'rtsp://{id}:{passwd}@{uri[7:]}'

            result = {
                'name': p.Name,
                'width': c.Resolution.Width,
                'height': c.Resolution.Height,
                'codec': c.Encoding.lower(),
                'fps': int(c.RateControl.FrameRateLimit),
                'rtsp': rtsp_uri
            }

            results.append(result)

        return results
    except Exception as e:
        if "401" in str(e):
            raise ValueError("Authentication failed: Invalid ID or password")
        else:
            raise ValueError(f"An error occurred: {str(e)}")


# if __name__ == "__main__":
#     ip = "192.168.10.70"
#     id = "admin"
#     password = "qazwsx123!"
#     profile_info = get_onvif_rtsp_address(ip, 80, id, password)
#     print(profile_info)
