import json
import requests

def _list_rrs(url=None, request_headers=None):
    _payload = json.dumps({
        "action_type": 'list_rrs_free',
    })
    _response_list_rrs = requests.post(url, headers=request_headers, data=_payload).json()
    return _response_list_rrs


def _update_rr(request_headers=None, rr_record=None, rr_value=None):
        ddns_request_type = 'create_rr_free'
        payload_rr_id = None
        rrs = _list_rrs(url='https://devnull.cn/dns', request_headers=request_headers)
        rrs_reformed = dict()
        for _id in rrs:
            _record = rrs[_id]['rr_record']
            _value = rrs[_id]['rr_value']
            rrs_reformed[_record] = {
                '_id': _id,
                '_value': _value
            }
        for _rr in rrs_reformed:
            _value = rrs_reformed[_rr]['_value']
            _id = rrs_reformed[_rr]['_id']
            if _rr == rr_record:
                if _value != rr_value:
                    ddns_request_type = 'update_rr_free'
                    payload_rr_id = rrs_reformed[_rr]['_id']
                else:
                    ddns_request_type = 'take_no_action'
                break
        final_payload = _build_payload(ddns_request_type=ddns_request_type, rr_record=rr_record, rr_value=rr_value)
        final_payload['rr_id'] = payload_rr_id
        # print(f"Updating RR: {rr_record}.thedns.cn || {rr_value}")
        _request = requests.post('https://devnull.cn/dns',
                                 headers=request_headers,
                                 data=json.dumps(final_payload)).json()

def _build_payload(ddns_request_type=None, rr_record=None, rr_value=None):
        return {
            "action_type": ddns_request_type,
            "rr_type": 'A',
            "rr_record": rr_record,
            "rr_value": rr_value,
        }