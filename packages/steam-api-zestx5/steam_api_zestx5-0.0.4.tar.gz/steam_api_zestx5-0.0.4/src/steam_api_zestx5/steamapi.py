import json
from dotenv import load_dotenv
import os

import requests

load_dotenv()
# https://steamcommunity.com/dev/apikey
STEAM_KEY = os.getenv("STEAM_KEY")


def get_news_for_app(app_id: str, count: int, max_length: int, format: str = "json"):
    """Returns the lastest of a game specified by its appid

    Args:
        appid (str): AppID of the game you want the news of.
        count (int): How many news enties you want to get returned.
        maxlength (int): Maximum length of each news entry.
        format (str): Output format. json (default), xml or vdf.
    """
    URL = f"http://api.steampowered.com/ISteamNews/GetNewsForApp/v0002/?appid={app_id}&count={count}&maxlength={max_length}&format={format}"
    response = requests.get(URL)
    return response.text


def get_global_achievement_percentages_for_app(game_id: str, format: str = "json"):
    """Returns on global achievements overview of a specific game in percentages.

    Args:
        game_id (str): AppID of the game you want the news of.
        format (str, optional): Output format. json (default), xml or vdf.
    """
    URL = f"http://api.steampowered.com/ISteamUserStats/GetGlobalAchievementPercentagesForApp/v0002/?gameid={game_id}&format={format}"
    response = requests.get(URL)
    return response.text


def get_player_summaries(steam_ids: list[str], format: str = "json"):
    """Returns basic profile information for a list of 64-bit Steam IDs.

    Args:
        steamd_ids (list[str]): List of 64 bit Steam IDs to return profile information for. Up to 100 Steam IDs can be requested.
        format (str, optional): Output format. json (default), xml or vdf.
    """
    URL = f"http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={STEAM_KEY}&steamids={",".join(steam_ids)}"
    response = requests.get(URL)
    return response.text


def get_friend_list(steam_id: str, relationship: str, format: str = "json"):
    """Returns the friend list of any Steam user, provided their Steam Community profile visibility is set to "Public".

    Args:
        steam_id (str): 64 bit Steam ID to return friend list for.
        relationship (str): Relationship filter. Possibles values: all, friend.
        format (str, optional): Output format. json (default), xml or vdf.
    """
    URL = f"http://api.steampowered.com/ISteamUser/GetFriendList/v0001/?key={STEAM_KEY}&steamid={steam_id}&relationship={relationship}"
    response = requests.get(URL)
    return response.text


def get_player_achievements(steam_id: str, app_id: str, lang: str = ""):
    """Returns a list of achievements for this user by app id

    Args:
        steam_id (str): 64 bit Steam ID to return friend list for.
        app_id (str): The ID for the game you're requesting
        lang (str, optional): Language. If specified, it will return language data for the requested language.
    """
    if lang == "":
        URL = f"http://api.steampowered.com/ISteamUserStats/GetPlayerAchievements/v0001/?appid={app_id}&key={STEAM_KEY}&steamid={steam_id}"
    else:
        URL = f"http://api.steampowered.com/ISteamUserStats/GetPlayerAchievements/v0001/?appid={app_id}&key={STEAM_KEY}&steamid={steam_id}&l={lang}"

    response = requests.get(URL)
    return response.text


def get_owned_games(
    steam_id: str,
    include_appinfo: bool = False,
    include_free_games: bool = False,
    format: str = "json",
    appids_filter: list[int] = [],
):
    """Returns a list of games a player owns along with some playtime information, if the profile is publicly visible. Private, friends-only, and other privacy settings are not supported unless you are asking for your own personal details (ie the WebAPI key you are using is linked to the steamid you are requesting).

    Args:
        steam_id (str): The SteamID of the account.
        include_appinfo (bool, optional): Include game name and logo information in the output. The default is to return appids only. Defaults to False.
        include_free_games (bool, optional): By default, free games like Team Fortress 2 are excluded (as technically everyone owns them). If include_played_free_games is set, they will be returned if the player has played them at some point. This is the same behavior as the games list on the Steam Community. Defaults to False.
        format (str, optional): Output format. json (default), xml or vdf.
        appids_filter (list[int], optional): You can optionally filter the list to a set of appids. Note that these cannot be passed as a URL parameter, instead you must use the JSON format described in Steam_Web_API#Calling_Service_interfaces. The expected input is an array of integers (in JSON: "appids_filter: [ 440, 500, 550 ]" ). Defaults to [].
    """
    URL = f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={STEAM_KEY}&steamid={steam_id}&format={format}"
    if include_appinfo == True:
        URL = URL + f"&include_appinfo=true"
    if include_free_games == True:
        URL = URL + f"&include_played_free_games=true"
    if appids_filter != {}:
        to_json = {
            "steamid": steam_id,
            "include_appinfo": include_appinfo,
            "include_played_free_games": include_free_games,
            "appids_filter": appids_filter,
        }
        json_test = json.dumps(to_json)
        URL = f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={STEAM_KEY}&format={format}&input_json={json_test}"
    response = requests.get(URL)
    return response.text


def get_recently_played_games(steam_id: str, count: int = None, format: str = "json"):
    """Returns a list of games a player has played in the last two weeks, if the profile is publicly visible. Private, friends-only, and other privacy settings are not supported unless you are asking for your own personal details (ie the WebAPI key you are using is linked to the steamid you are requesting).

    Args:
        steam_id (str): The SteamID of the account.
        count (int): Optionally limit to a certain number of games (the number of games a person has played in the last 2 weeks is typically very small).
        format (str, optional): Output format. json (default), xml or vdf.
    """
    URL = f"http://api.steampowered.com/IPlayerService/GetRecentlyPlayedGames/v0001/?key={STEAM_KEY}&steamid={steam_id}&format={format}"
    if count != None:
        URL = URL + f"&count={count}"
    response = requests.get(URL)
    return response.text
