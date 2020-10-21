from django.shortcuts import render
import requests
import json
from django.http import HttpResponse
from django.views.generic import UpdateView
from .forms import CUBRIDBuildForm


# Create your views here.
def home(request):
    return HttpResponse("Hello, Django")


def build(request):
    if request.method == 'GET':
        form_class = CUBRIDBuildForm
        content = {'form': form_class}
        return render(request, 'builder.html', content)
    else:
        req_json = {'svr_type': request.POST['server_type'],
                    'ha_type': request.POST['ha_type'],
                    'pc_ip': request.POST['pc_ip'],
                    'was_ip': request.POST['was_ip'],
                    'cluster_name': request.POST['cluster_name']}
        ret_json = request_post('http://localhost:8000/ha_api/build/', req_json, False)
        if ret_json['result'] == 'ok':
            ret_json['msg'] = 'Cluster is build now'
            return render(request, 'build_result.html', ret_json)

        return HttpResponse(json.dumps(ret_json))


def request_post(url, dict_data, is_urlencoded=True):
    if is_urlencoded is True:
        response = requests.post(url=url, data=dict_data,
                                 headers={'Content-Type': 'application/x-www-form-urlencoded'})
    else:
        response = requests.post(url=url, data=json.dumps(dict_data), headers={'Content-Type': 'application/json'})

    dict_meta = {'status_code': response.status_code, 'ok': response.ok, 'encoding': response.encoding,
                 'Content-Type': response.headers['Content-Type']}
    if 'json' in str(response.headers['Content-Type']):  # JSON
        return {**dict_meta, **response.json()}
    else:  # String
        return {**dict_meta, **{'text': response.text}}
