from __future__ import annotations

from typing import Callable, Iterable


def select_latest_recent_steam_achievement(
    recent_games: Iterable[dict],
    steam_id: str,
    steam_api_get_func: Callable[[str, str, str, dict], dict],
):
    latest_match = None

    for game in recent_games or []:
        app_id = game.get('appid')
        if not app_id:
            continue

        try:
            achievement_response = steam_api_get_func(
                'ISteamUserStats',
                'GetPlayerAchievements',
                'v0001',
                {'steamid': steam_id, 'appid': app_id, 'l': 'english'}
            )
        except Exception:
            continue

        achievements = (achievement_response or {}).get('playerstats', {}).get('achievements', []) or []
        unlocked = [
            achievement for achievement in achievements
            if achievement.get('achieved') == 1 and achievement.get('unlocktime')
        ]
        if not unlocked:
            continue

        game_latest = max(unlocked, key=lambda item: item.get('unlocktime', 0))
        if latest_match is None or game_latest.get('unlocktime', 0) > latest_match['achievement'].get('unlocktime', 0):
            latest_match = {
                'game': game,
                'achievement': game_latest,
            }

    return latest_match
