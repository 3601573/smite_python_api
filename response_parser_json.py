import logging
import json
from smite_api_exception import APIOveruseError
from datetime import datetime
from session import Session


class ResponseParserJson:
    API_OVERUSE_ERROR = 'Daily request limit reached.'

    @staticmethod
    def _get_json_from_response(response):
        if response.status_code != 200:
            logging.error('API responded with: ' + response.status_code + '(' + response.text + ')')
            raise Exception('API response code is not OK')
        return json.loads(response.text)

    def check_json_entry_for_api_reported_errors(self, entry):
        if entry['ret_msg'] == self.API_OVERUSE_ERROR:
            raise APIOveruseError(self.API_OVERUSE_ERROR)

    def parse_create_session_response(self, response):
        json_response = self._get_json_from_response(response)
        self.check_json_entry_for_api_reported_errors(json_response)
        try:
            s = Session()
            s.status = json_response['ret_msg']
            s.id = json_response['session_id']
            s.start_ts = datetime.strptime(json_response['timestamp'], '%m/%d/%Y %I:%M:%S %p')
            return s
        except ValueError:
            logging.exception('Unknown createsession response: ' + json.dumps(json_response))
            return Session()

    def parse_get_queue_matches_response(self, response):
        json_response = self._get_json_from_response(response)

        matches = []
        for match in json_response:
            try:
                self.check_json_entry_for_api_reported_errors(match)
                if match['Active_Flag'] != 'n':
                    if match['Active_Flag'] != 'y':
                        logging.info('Match flag value: ' + str(match))
                    continue
                if match['ret_msg'] is not None:
                    logging.info('RET_MSG: ' + match['ret_msg'])
                    continue
                matches.append(int(match['Match']))
            except ValueError:
                logging.exception('Could not parse match')
                pass
        return matches

    def parse_get_match_response(self, response):
        json_response = self._get_json_from_response(response)

        match_id_field = 'Match'
        match_related_fields = ['Entry_Datetime', 'First_Ban_Side', 'Minutes', 'hasReplay', 'name']
        match_related_fields += ['Ban' + str(i) for i in range(1, 10)]
        match_related_fields += ['Ban' + str(i) + 'Id' for i in range(1, 10)]
        match = {'_id': None, 'Details': {}, 'Players': []}
        for player in json_response:
            self.check_json_entry_for_api_reported_errors(player)
            # match_details = {k: v for k, v in player.items() if k in match_related_fields and k != match_id_field}
            # player_details   = {k: v for k, v in player.items() if k not in match_related_fields and k != match_id_field}
            match_details = {}
            player_details = {}
            for k, v in player.items():
                if k == match_id_field:
                    continue
                if k in match_related_fields:
                    match_details[k] = v
                else:
                    player_details[k] = v
            match['_id'] = player[match_id_field]
            match['Details'] = match_details
            match['Players'].append(player_details)
        return match

    def parse_get_gods_response(self, response):
        return self._get_json_from_response(response)