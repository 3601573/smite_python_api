from datetime import datetime
import hashlib
import requests
import logging
from response_parser_json import ResponseParserJson
from session import Session


def refresh_session(func):
    def wrapper(api_accessor, *args, **kwargs):
        if not api_accessor.session.is_active():
            api_accessor.session = api_accessor.get_session()
        return func(api_accessor, *args, **kwargs)
    return wrapper


class SmiteApiClient:
    API_ENDPOINT_PC = 'http://api.smitegame.com/smiteapi.svc/'
    CREATE_SESSION_METHOD = 'createsession'

    def __init__(self, dev_id, auth_key):
        self.session = Session()
        self.dev_id = dev_id
        self.auth_key = auth_key
        self.response_format = 'Json'
        self.response_parser = ResponseParserJson()

    def __str__(self):
        return str(self.session)

    def _get_request_signature(self, method_name, timestamp):
        return hashlib.md5(self.dev_id.encode('utf-8') + method_name.encode('utf-8') + self.auth_key.encode('utf-8')
                           + timestamp.encode('utf-8')).hexdigest()

    def _get_timestamp(self):
        return datetime.utcnow().strftime(self.session.TIMESTAMP_FORMAT)

    def _create_request_url(self, method_name, *args):
        ts = self._get_timestamp()
        sig = self._get_request_signature(method_name, ts)
        method_url = self.API_ENDPOINT_PC + method_name + self.response_format + '/'
        if method_name == self.CREATE_SESSION_METHOD:
            return method_url + '/'.join((self.dev_id, sig, ts, *args))
        else:
            return method_url + '/'.join((self.dev_id, sig, self.session.id, ts, *args))

    def get_session(self):
        url = self._create_request_url(self.CREATE_SESSION_METHOD)
        r = requests.get(url)
        return self.response_parser.parse_create_session_response(r)

    @refresh_session
    def get_queue_matches(self, queue, date, hour):
        if hour < -1 or hour > 23:
            logging.error('Invalid value for hour: ' + str(hour))
            return
        url = self._create_request_url('getmatchidsbyqueue', str(queue), date.strftime('%Y%m%d'), str(hour))
        r = requests.get(url)
        return self.response_parser.parse_get_queue_matches_response(r)

    @refresh_session
    def get_match(self, match_id):
        url = self._create_request_url('getmatchdetails', str(match_id))
        r = requests.get(url)
        return self.response_parser.parse_get_match_response(r)

    @refresh_session
    def get_gods(self, lang_code=1):
        url = self._create_request_url('getgods', str(lang_code))
        r = requests.get(url)
        return self.response_parser.parse_get_gods_response(r)

    @refresh_session
    def get_data_used(self):
        url = self._create_request_url('getdataused')
        r = requests.get(url)
        return r.text

    # def get_player(self, player):
    #     if not self.is_active():
    #         logging.error('Session is not active')
    #         return
    #     method_name = 'getplayer'
    #     ts = Session.get_timestamp()
    #     sig = Session.get_signature(method_name, ts)
    #     request = SMITE_API_ENDPOINT_PC + method_name + SMITE_API_FORMAT_JSON + '/' + DEV_ID + '/' + sig + '/' \
    #               + self.id + '/' + ts + '/' + player
    #     r = requests.get(request)
    #     if r.status_code != 200:
    #         logging.error('API responded with: ' + r.status_code + '(' + r.text + ')')
    #         return
    #     json_response = json.loads(r.text)
    #     return r.text