import time

import requests
from mercury_traceloop import MercuryTraceLoop
from mercury_traceloop.instruments import Instruments

MercuryTraceLoop.init(app_name="test.rick.vip2.com", server_endpoint="10.189.109.45:4317",
                      is_debug=True, instruments={Instruments.REQUESTS})


def make_http_request():
    url = f"http://localhost:8082/test_py/001"
    headers = {
        "X-Custom-Header": "value",
        "baggage-test-rick": "liudeng",
        "X-B3-X-dbg": "1"
    }
    # 发起 HTTP GET请求
    response = requests.request("GET", url, headers=headers, timeout=20000)
    print("Status code:", response.status_code)
    print("Response content:", response.content.decode())

    time.sleep(10)

if __name__ == "__main__":
    make_http_request()