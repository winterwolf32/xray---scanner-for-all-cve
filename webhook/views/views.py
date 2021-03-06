import datetime
from datetime import datetime

from executor.executor import dispatch_web_vuln, dispatch_service_vuln, dispatch_statistics
from model.vuln import Statistics, WebVuln, WebParam, WebParamPosition, WebRequest, WebResponse, ServiceVuln


def process_web_vuln(instance, data):
    """将 web 漏洞 json 转换为相关 model"""
    detail = data["detail"]
    p = detail['extra']["param"]
    if p:
        param = WebParam(key=p["key"], value=p["value"], position=WebParamPosition(p["position"]))
    else:
        param = None

    request = []
    response = []
    extra = {}

    for i, pair in enumerate(detail['snapshot']):
        req = pair[0]
        resp = pair[1]

        if req == "" or resp == "":
            continue
        if req is None or resp is None:
            break
        request.append(WebRequest(raw=req))
        response.append(WebResponse(raw=resp))

    # 其他的数据可能是自定义的，就单独拿出来
    not_extra_key = ["param"]
    for k, v in detail["extra"].items():
        for item in not_extra_key:
            if item in k:
                break
        else:
            extra[k] = v

    vuln = WebVuln(create_time=datetime.fromtimestamp(data["create_time"] / 1000), plugin=data["plugin"],
                   url=data["target"]["url"], param=param, request=request, response=response, extra=extra,
                   raw_json=data)
    dispatch_web_vuln(instance, vuln)


def process_statistics(instance, data):
    """将统计数据 json 转换为相关 json"""
    s = Statistics(num_found_urls=data["num_found_urls"],
                   num_scanned_urls=data["num_scanned_urls"],
                   num_sent_http_requests=data["num_sent_http_requests"],
                   average_response_time=data["average_response_time"],
                   ratio_failed_http_requests=data["ratio_failed_http_requests"],
                   ratio_progress=data["ratio_progress"],
                   raw_json=data)
    dispatch_statistics(instance, s)


def process_host_vuln(instance, data):
    """将服务漏洞 json 转换为相关 json"""
    detail = data["detail"]
    extra = {}

    not_extra_key = []
    for k, v in detail['extra'].items():
        for item in not_extra_key:
            if item in k:
                break
        else:
            extra[k] = v

    vuln = ServiceVuln(create_time=datetime.fromtimestamp(data["create_time"] / 1000), plugin=data["plugin"],
                       host=detail["host"], port=detail["port"],
                       extra=extra, raw_json=data)
    dispatch_service_vuln(instance, vuln)
