import requests
import datetime
import ssl
import asyncio
import aiohttp

def node(url, token, nid=None, group_id=None, verify=True, timeout=60):
    header = {'Accept':'application/json','token':token}

    # only for administrators
    if group_id is not None:
        header['grpid'] = group_id

    uri = url + "/api/v1.0/" + ("nodes" if nid is None else f"node/{nid}")
    
    try:
        r = requests.get(uri, headers=header, verify=verify, timeout=timeout)
    except Exception as e:
        print(e)
        return None
    
    if r.status_code == 200:
        return r.json()['node']
    else:
        print(r)
        raise Exception(r.content)
    
def storage(url, token, nid=None, date_from=None, date_to=None, count=None, sort=None, lastKey=None, consolidate=True, group_id=None, verify=True, timeout=60):
    '''
    url : IoT.own Server Address
    token : IoT.own API Token
    nid : Node ID
    '''
                    
    header = {'Accept':'application/json','token':token}

    # only for administrators
    if group_id is not None:
        header['grpid'] = group_id

    uri_prefix = url + "/api/v1.0/storage"

    params = []
    
    if nid is not None:
        params.append(f"nid={nid}")
        
    if date_from is not None:
        params.append(f"from={date_from}")

    if date_to is not None:
        params.append(f"to={date_to}")

    if count is not None:
        params.append(f"count={count}")

    if sort is not None:
        params.append(f"sort={sort}")

    if len(params) > 0:
        uri_prefix += '?' + '&'.join(params)
        
    result = None
    
    while True:
        try:
            uri = uri_prefix if lastKey is None else uri_prefix + "&lastKey=" + lastKey
            print(uri)
            r = requests.get(uri, headers=header, verify=verify, timeout=timeout)
        except Exception as e:
            print(e)
            return None
    
        if r.status_code == 200:
            data_obj = r.json()
            if result is None:
                # at first
                result = data_obj
                
                # if 'lastKey' in result.keys():
                #     del result['lastKey']
            else:
                result['data'] += data_obj['data']
                if 'lastKey' in data_obj.keys():
                    result['lastKey'] = data_obj['lastKey']
                elif 'lastKey' in result.keys():
                    del result['lastKey']

            if consolidate == True and 'lastKey' in result.keys():
                lastKey = result['lastKey']
            else:
                return result
        else:
            print(r)
            return None

def command_common(url, token, nid, group_id):
    uri = f"{url}/api/v1.0/command/{nid}"
    header = {
        'Accept': 'application/json',
        'token': token
    }

    if group_id is not None:
        header['grpid'] = group_id

    return uri, header

def command(url, token, nid, group_id=None, verify=True, timeout=60):
    uri, header = command_common(uri, token, nid, group_id)

    try:
        r = requests.get(uri, headers=header, verify=verify, timeout=timeout)
        if r.status_code == 200:
            return True, r.json()
        else:
            return False, r.json()
    except Exception as e:
        print(e)
        return False, None

async def async_command(url, token, nid, group_id=None, verify=True, timeout=60):
    uri, header = command_common(url, token, nid, group_id)

    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=True, verify_ssl=verify)) as session:
        async with session.get(uri, headers=header) as response:
            if response.status == 200:
                return True, await response.json()
            else:
                return False, await response.json()

def downloadImage(url, token, imageID, verify=True, timeout=60):
    ''' 
    url : IoT.own Server Address
    token : IoT.own API Token
    imageID : IoT.own imageID ( using annotation's 'id' not '_id' ) 
    '''
    uri = url + "/nn/dataset/img/" + imageID
    header = {'Accept':'application/json', 'token':token}
    try:
        r = requests.get(uri, headers=header, verify=verify, timeout=timeout)
        if r.status_code == 200:
            return r.content
        else:
            print(r)
            return None
    except Exception as e:
        print(e)
        return None

def downloadAnnotations(url, token, classname, verify=True, timeout=60):
    ''' 
    url : IoT.own Server Address
    token : IoT.own API Token
    classname : Image Class ex) car, person, airplain
    '''
    uri = url + "/api/v1.0/nn/images?labels=" + classname
    header = {'Accept':'application/json', 'token':token}
    try:
        r = requests.get(uri, headers=header, verify=verify, timeout=timeout)
        if r.status_code == 200:
            return r.json()
        else:
            print(r)
            return None
    except Exception as e:
        print(e)
        return None
