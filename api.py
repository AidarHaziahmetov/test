import requests
import os
import json
import time


API_KEY = os.environ["API_KEY"]
headers = {
    'accept': 'application/json',
    'Authorization': 'Bearer '+ API_KEY,
}


def check_nickname(nickname: str, headers=headers):
    params = {
        'nickname': nickname,
        'game': 'cs2',
    }
    response = requests.get('https://open.faceit.com/data/v4/players', params=params, headers=headers)
    if response.status_code == 200:
        all_info = json.loads(response.text)
        if "cs2" in all_info["games"]:
            return True
    return False



def info_about_player(nickname: str, headers=headers):
    params = {
        'nickname': nickname,
        'game': 'cs2',
    }
    response = requests.get('https://open.faceit.com/data/v4/players', params=params, headers=headers)
    if response.status_code == 200:
        a = json.loads(response.text)
        del a["friends_ids"]
        b = json.dumps(a, indent=3)
        return b
    else:
        return "Либо вы указали не правильно никнейм, либо в данный момент сервис не доступен"
    
def get_profile(nickname: str, headers=headers)->dict:

    params = {
        'nickname': nickname,
        'game': 'cs2',
    }
    response = requests.get('https://open.faceit.com/data/v4/players', params=params, headers=headers)
    if response.status_code == 200:
        all_info = json.loads(response.text)
        profile = {
            "nickname": nickname,
            "avatar": all_info["avatar"],
            "level": all_info["games"]["cs2"]["skill_level"],
            "elo": all_info["games"]["cs2"]["faceit_elo"],
            "player_id": all_info["player_id"]
        }
        return profile
    else:
        return "Либо вы указали не правильно никнейм, либо в данный момент сервис не доступен"



def get_last_match(player_id:str, headers=headers)->dict:
    params = {
    'offset': '0',
    'limit': '1'
    }
    response = requests.get(f'https://open.faceit.com/data/v4/players/{player_id}/games/cs2/stats',params=params,headers=headers)
    if response.status_code == 200:
        all_info = json.loads(response.text)["items"]
        if len(all_info)>0:
            all_info = all_info[0]["stats"]
            last_match = {
                "Map": all_info["Map"],
                "Result": all_info["Result"],
                "Score": all_info["Score"],
                "Kills": all_info["Kills"],
                "Deaths": all_info["Deaths"],
                "K/D Ratio": all_info["K/D Ratio"],
                "Headshots %": all_info["Headshots %"],
                "K/R Ratio": all_info["K/R Ratio"],
                "Match Id": all_info["Match Id"]
            }
            return last_match
        else:
            print("len(all_info)<0")
            time.sleep(10)
            return get_last_match(player_id, headers)
    else:
        print("status_code != 200")
        time.sleep(10)
        return get_last_match(player_id, headers)