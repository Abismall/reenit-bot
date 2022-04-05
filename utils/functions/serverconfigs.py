import json
import ftplib
from io import BytesIO


def create_config_file(map_list, match_id, team1_steamIDs, team2_steamIDs):
    match_config = {
        'matchid': match_id,
        'num_maps': 1,
        'maplist': map_list,
        'skip_veto': True,
        'veto_first': 'team1',
        'side_type': 'always_knife',
        'players_per_team': 5,
        'min_players_to_ready': 1,
        'team1': {
            'name': "Abis & kopla",
            'flag': "Fi",
            'players': team1_steamIDs
        },
        'team2': {
            'name': "Abis & kopla",
            'flag': "Fi",
            'players': team2_steamIDs
        },
        'cvars': {
            'get5_print_damage': 0,
            'mp_halftime_duration': 15,
        },
    }
    config_encode_data = json.dumps(match_config, indent=2).encode('utf-8')
    configs_bytes = BytesIO(config_encode_data)
    return configs_bytes


async def send_config_file(configs, host, ftp_user, ftp_password):
    try:
        with ftplib.FTP(host, ftp_user, ftp_password, timeout=30) as ftp:
            ftp.login
            ftp.storbinary('STOR reenit_match_configs.json', configs)
            return True
    except ftplib.all_errors as err:
        print(f"ftp error: {err}")
        return False


async def delete_config_file(ftp_user, ftp_password):
    try:
        with ftplib.FTP('styr.dathost.net', ftp_user, ftp_password) as ftp:
            ftp.delete("reenit_match_configs.json")
            return True
    except ftplib.all_errors as err:
        print(f"ftp error: {err}")
        return False
