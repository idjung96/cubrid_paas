from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
import os


# Create your views here.
def home(request):
    return HttpResponse("Hello, Django")


def check_required_keys(json_data, required_keys):
    check_key: object
    for check_key in required_keys:
        if check_key in json_data:
            continue
        else:
            return False

    return True


@csrf_exempt
def build(request):
    req_keys = ["ha_type", "svr_type"]
    num_svr_ha_type = {
        'single': '1',
        '1standby': '2',
        '2standby': '3',
        '1replica': '3',
        '2replica': '4',
    }
    conf_template_file = {
        'single': 'single.yml',
        '1standby': '1standby.yml',
        '2standby': '2standby.yml',
        '1replica': '1replica.yml',
        '2replica': '2replica.yml',
    }

    if request.method != 'POST':
        data = {"code": "405",
                "msg": "Method Not Allowed"}
        return JsonResponse(data, safe=False)

    req_json = json.loads(request.body)

    if not check_required_keys(req_json, req_keys):
        data = {"code": "404",
                "msg": "Required keys are missed"}
        return JsonResponse(data, safe=False)

    # todo: Add to codes for handling servers
    # svr info is for demonstration
    svr_list = get_servers_info(req_json['svr_type'], num_svr_ha_type[req_json['ha_type']])
    data = dict(svr_list=svr_list)

    # todo: Add to codes for handling template & conf file
    conf_template_file = open(os.path.join('conf_template', conf_template_file[req_json['ha_type']]), 'r')
    conf_output = open(os.path.join('tmp', req_json['ha_type']+'.yml'), 'w+')

    success = True
    url = {}
    if 'single' == req_json['ha_type']:
        make_conf_single(conf_template_file, conf_output, req_json, svr_list)
        url = make_url_single(req_json, svr_list)
    elif req_json['ha_type'] == '1standby':
        make_conf_1standby(conf_template_file, conf_output, req_json, svr_list)
        url = make_url_1standby(req_json, svr_list)
    elif req_json['ha_type'] == '2standby':
        success = True
    elif req_json['ha_type'] == '1replica':
        success = True
    elif req_json['ha_type'] == '2replica':
        success = True
    else:
        success = False

    conf_template_file.close()
    conf_output.close()

    # todo: Add codes for handling result & error
    os.system('rm -rf '+os.path.join('~', '.ansible', 'files', '*'))
    os.system('python '+os.path.join('CUBRID_conf_generator', 'get_cub_conf.py')+' cubrid1 '+os.path.join('tmp',req_json['ha_type'])+'.yml')
    os.system('mv '+os.path.join(req_json['cluster_name'], '*')+' '+os.path.join('~', '.ansible', 'files'))
    os.system('rmdir '+req_json['cluster_name'])

    # todo: Add codes for playbook
    host_file = open('hosts_'+req_json['ha_type'], 'w+')
    host_file.write('[cubrid]\n')
    for i in range(0,len(svr_list)):
        host_file.write(svr_list[i]['name']+'\n')
    host_file.close()
    os.system('ansible-playbook -i hosts_'+req_json['ha_type']+' play.yml')
    os.system('rm hosts_'+req_json['ha_type'])
    
    if success:
        data['result'] = 'ok'
        data['url'] = url
    else:
        data['result'] = 'fail'

    return JsonResponse(data, safe=False)


def make_url_single(json_data, svr_list):
    ret_val = {}
    ip = svr_list[0]['ip']

    ret_val['dba_so'] = 'jdbc:CUBRID:'+ip+':20140:'+json_data['cluster_name']+':dba::'
    ret_val['dba_rw'] = 'jdbc:CUBRID:'+ip+':20150:'+json_data['cluster_name']+':dba::'
    ret_val['svc_rw'] = 'jdbc:CUBRID:'+ip+':33000:'+json_data['cluster_name']+':dba::'
    ret_val['svc_ro'] = 'jdbc:CUBRID:'+ip+':34000:'+json_data['cluster_name']+':dba::'

    return ret_val


def make_url_1standby(json_data, svr_list):
    ret_val = {}
    ip0 = svr_list[0]['ip']
    ip1 = svr_list[1]['ip']

    ret_val['dba_so'] = 'jdbc:CUBRID:'+ip1+':20140:'+json_data['cluster_name']+':dba::'
    ret_val['dba_rw'] = 'jdbc:CUBRID:'+ip1+':20150:'+json_data['cluster_name']+':dba::'
    ret_val['svc_rw'] = 'jdbc:CUBRID:'+ip0+':33000:'+json_data['cluster_name']+':dba::?altHosts='+ip1+':33000'
    ret_val['svc_ro'] = 'jdbc:CUBRID:'+ip0+':34000:'+json_data['cluster_name']+':dba::?altHosts='+ip1+':34000'

    return ret_val


def make_conf_1standby(conf_template_file, conf_output, json_data, svr_list):
    for line in conf_template_file:
        line = line.replace("__SVC_NAME__", json_data['cluster_name'])
        line = line.replace("__PC_IP__", json_data['pc_ip'])
        line = line.replace("__WAS_IP__", json_data['was_ip'])
        line = line.replace("__SVR1_NAME__", svr_list[0]['name'])
        line = line.replace("__SVR1_IP__", svr_list[0]['ip'])
        line = line.replace("__SVR2_NAME__", svr_list[1]['name'])
        line = line.replace("__SVR2_IP__", svr_list[1]['ip'])
        conf_output.write(line)


def make_conf_single(conf_template_file, conf_output, json_data, svr_list):
    for line in conf_template_file:
        line = line.replace("__SVC_NAME__", json_data['cluster_name'])
        line = line.replace("__PC_IP__", json_data['pc_ip'])
        line = line.replace("__WAS_IP__", json_data['was_ip'])
        line = line.replace("__SVR_NAME__", svr_list[0]['name'])
        line = line.replace("__SVR_IP__", svr_list[0]['ip'])
        conf_output.write(line)


def get_servers_info(svr_type, svr_of_num):
    svr_pool = [{"name": "cubrid_svr0",
                 "ip": "10.0.2.10"},
                {"name": "cubrid_svr1",
                 "ip": "10.0.2.20"},
                {"name": "cubrid_svr2",
                 "ip": "10.0.2.30"},
                {"name": "cubrid_svr3",
                 "ip": "10.0.2.40"}]
    ret_svr = []

    for i in range(int(svr_of_num)):
        ret_svr.append(svr_pool[i])

    return ret_svr
