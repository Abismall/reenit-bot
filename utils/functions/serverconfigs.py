import json
import ftplib
from io import BytesIO


def create_config_file(map_list, match_id, team1_steamIDs, team2_steamIDs, captain1, captain2):
    match_config = {
        'matchid': str(match_id),
        'num_maps': 1,
        'maplist': map_list,
        'skip_veto': True,
        'veto_first': 'team1',
        'side_type': 'always_knife',
        'players_per_team': 5,
        'min_players_to_ready': 1,
        'team1': {
            'name': f"{captain1} & kopla",
            'flag': "Fi",
            'players': team1_steamIDs
        },
        'team2': {
            'name': f"{captain2} & kopla",
            'flag': "Fi",
            'players': team2_steamIDs
        },
        'cvars': {
            'get5_event_api_url': f"http://13.53.34.176:8000/servers/status/",


        },
    }
    config_encode_data = json.dumps(match_config, indent=2).encode('utf-8')
    configs_bytes = BytesIO(config_encode_data)
    return configs_bytes


def send_config_file(configs, host, ftp_user, ftp_password):
    try:
        with ftplib.FTP(host, ftp_user, ftp_password, timeout=30) as ftp:
            ftp.login
            ftp.storbinary('STOR reenit_match_configs.json', configs)
            return True
    except ftplib.all_errors as err:
        print(f"ftp error: {err}")
        return False


def delete_config_file(ftp_user, ftp_password):
    try:
        with ftplib.FTP('styr.dathost.net', ftp_user, ftp_password) as ftp:
            ftp.delete("reenit_match_configs.json")
            return True
    except ftplib.all_errors as err:
        print(f"ftp error: {err}")
        return False
