from .post import post_files
import json
from urllib.parse import urlparse
import paho.mqtt.client as mqtt
import sys
import ssl
import requests
import threading

def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code.is_failure:
        print(f"Bad connection (reason: {reason_code.getName()})", file=sys.stderr)
        sys.exit(3)
    else:
        name = userdata['name']
        print(f"Post process '{name}' Connect OK! Subscribe Start")

def on_disconnect(client, userdata, flags, reason_code, properties):
    print(f"Post process '{userdata['name']}' on_disconnect: {reason_code}")
    if reason_code.is_failure:
        print(f"Post process '{userdata['name']}' disconnected unexpectedly (reason:{reason_code.getName()})", file=sys.stderr)
        sys.exit(3)
        
def on_message(client, userdata, msg):
    try:
        message = json.loads((msg.payload).decode('utf-8'))

        topic_levels = msg.topic.split('/')
        if len(topic_levels) > 4:
            param = topic_levels[4]
        else:
            param = None

        data = message.copy()
        data.pop('pp_list', None)
        data.pop('pp_error', None)
        data['pp_warning'] = ''

        try:
            result = userdata['func'](data, param)
        except Exception as e:
            trace = ""
            tb = e.__traceback__
            while tb is not None:
                if len(trace) > 0:
                    trace += ","
                trace += f"{tb.tb_frame.f_code.co_name}({tb.tb_frame.f_code.co_filename}:{tb.tb_lineno})"
                tb = tb.tb_next
            trace = f"<{type(e).__name__}> {str(e)} [ {trace} ]"
            print(f"Error on calling the user-defined function for PP '{userdata['name']}' of '{userdata['group']}': {trace}", file=sys.stderr)

            message['pp_error'][message['pp_list'][0]['name']] = f"Error on post process ({trace})"

            if userdata['dry'] == False:
                client.publish('iotown/proc-done', json.dumps(message), 1)
                return

        if userdata['dry'] == True:
            print(f"Discard the message for dry-run")
            return

        if result is None:
            print(f"Discard the message")
            del message['pp_list']
            client.publish('iotown/proc-done', json.dumps(message), 1)
            return
    
        if type(result) is dict and 'data' in result.keys():
            pp_warning = result.get('pp_warning')
            if pp_warning is not None and type(pp_warning) is str and len(pp_warning) > 0:
                message['pp_error'][message['pp_list'][0]['name']] = f"Warning on post process ({pp_warning})"

            group_id = message['grpid'] if userdata['group'] == 'common' else None
            result = post_files(result, userdata['url'], userdata['token'], group_id, userdata['verify'])
            message['data'] = result['data']
            try:
                client.publish('iotown/proc-done', json.dumps(message), 1)
            except Exception as e:
                print(e)
                print(message)
        else:
            print(f"CALLBACK FUNCTION TYPE ERROR {type(result)} must [ dict ]", file=sys.stderr)
            client.publish('iotown/proc-done', msg.payload, 1)
    except Exception as e:
        print(f"[pyiotown] {e}", file=sys.stderr)

def updateExpire(url, token, name, verify=True, timeout=60):
    apiaddr = url + "/api/v1.0/pp/proc"
    header = {'Accept':'application/json', 'token':token}
    payload = { 'name' : name}
    try:
        r = requests.post(apiaddr, json=payload, headers=header, verify=verify, timeout=timeout)
        if r.status_code != 200 and r.status_code != 403:
            print(f"update Expire Fail! {r}")
    except Exception as e:
        print(f"update Expire Fail! reason: {e}")
    timer = threading.Timer(60, updateExpire, [url, token, name, verify, timeout])
    timer.start()

def getTopic(url, token, name, verify=True, timeout=60):
    apiaddr = url + "/api/v1.0/pp/proc"
    header = {'Accept':'application/json', 'token':token}
    payload = {'name':name}    

    r = requests.post(apiaddr, json=payload, headers=header, verify=verify, timeout=timeout)
    if r.status_code == 200 or r.status_code == 403: # Same with 200 (deprecated)
        topic = json.loads((r.content).decode('utf-8'))['topic']
        return topic
    else:
        raise Exception(r.content.decode('utf-8'))

def connect(url, name, func, mqtt_url=None, verify=True, dry_run=False):
    url_parsed = urlparse(url)
    if url_parsed.username is None:
        raise Exception("The username is not specified.")
    username = url_parsed.username

    if url_parsed.password is None:
        raise Exception("The password (token) is not specified.")
    token = url_parsed.password

    url = f"{url_parsed.scheme}://{url_parsed.hostname}"
    if url_parsed.port is not None:
        url += f":{url_parsed.port}"
    
    # get Topic From IoTown
    topic = getTopic(url, token, name, verify)

    if topic == None:
        raise Exception("The server does not assign a topic for you.")

    try:
        group = topic.split('/')[2]
    except Exception as e:
        raise Exception(f"Invalid topic {topic}")
    
    updateExpire(url, token, name, verify)
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message
    client.user_data_set({
        "url": url,
        "token": token,
        "func": func,
        "group": group,
        "name": name,
        "verify": verify,
        "dry": dry_run,
    })

    if mqtt_url is None:
        mqtt_host = urlparse(url).hostname
        mqtt_port = 8883

    else:
        url_parsed = urlparse(mqtt_url)
        mqtt_host = url_parsed.hostname
        mqtt_port = url_parsed.port
        if mqtt_port is None:
            mqtt_port = 8883

        if url_parsed.username is not None:
            username = url_parsed.username

        if url_parsed.password is not None:
            token = url_parsed.password

    client.username_pw_set(username, token)
    
    print(f"Post process '{name}' is trying to connect to {mqtt_host}:{mqtt_port}")
    client.tls_set(cert_reqs=ssl.CERT_NONE)
    client.tls_insecure_set(True)
    client.connect(mqtt_host, port=mqtt_port)
    client.subscribe([(topic, 1), (topic + '/+', 1)])
    return client

def connect_common(url, topic, func, mqtt_url=None, dry_run=False):
    url_parsed = urlparse(url)
    if url_parsed.username is None:
        raise Exception("The username is not specified.")
    username = url_parsed.username

    if url_parsed.password is None:
        raise Exception("The password (token) is not specified.")
    token = url_parsed.password

    url = f"{url_parsed.scheme}://{url_parsed.hostname}"
    if url_parsed.port is not None:
        url += f":{url_parsed.port}"

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message
    client.user_data_set({
        "url": url,
        "token": token,
        "func": func,
        "group": "common",
        "name": topic,
        "verify": False,
        "dry": dry_run,
    })

    if mqtt_url is None:
        mqtt_host = urlparse(url).hostname
        mqtt_port = 8883
    else:
        url_parsed = urlparse(mqtt_url)
        mqtt_host = url_parsed.hostname
        mqtt_port = url_parsed.port
        if mqtt_port is None:
            mqtt_port = 8883

        if url_parsed.username is not None:
            username = url_parsed.username

        if url_parsed.password is not None:
            token = url_parsed.password

    client.username_pw_set(username, token)
    print(f"Post process '{topic}' is trying to Connect to {mqtt_host}:{mqtt_port}")
    client.tls_set(cert_reqs=ssl.CERT_NONE)
    client.tls_insecure_set(True)
    client.connect(mqtt_host, port=mqtt_port)
    client.subscribe([(f'iotown/proc/common/{topic}', 1), (f'iotown/proc/common/{topic}/+', 1)])
    return client

def loop_forever(clients):
    if isinstance(clients, list) == False:
        clients = [ clients ]

    while True:
        for c in clients:
            c.loop(timeout=0.01)
