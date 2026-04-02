import unittest

from steam_achievement_utils import select_latest_recent_steam_achievement


class SelectLatestRecentSteamAchievementTests(unittest.TestCase):
    def test_picks_newest_unlock_across_multiple_recent_games(self):
        calls = []

        def fake_steam_api_get(interface, method, version, params):
            calls.append(params['appid'])
            payloads = {
                10: {
                    'playerstats': {
                        'achievements': [
                            {'name': 'Older Unlock', 'achieved': 1, 'unlocktime': 100},
                        ]
                    }
                },
                20: {
                    'playerstats': {
                        'achievements': [
                            {'name': 'Newest Unlock', 'achieved': 1, 'unlocktime': 300},
                        ]
                    }
                },
            }
            return payloads[params['appid']]

        result = select_latest_recent_steam_achievement(
            [{'appid': 10, 'name': 'Game One'}, {'appid': 20, 'name': 'Game Two'}],
            'steam-user',
            fake_steam_api_get,
        )

        self.assertEqual(calls, [10, 20])
        self.assertIsNotNone(result)
        self.assertEqual(result['game']['appid'], 20)
        self.assertEqual(result['achievement']['name'], 'Newest Unlock')

    def test_skips_recent_games_without_unlocks_and_keeps_searching(self):
        def fake_steam_api_get(interface, method, version, params):
            payloads = {
                10: {'playerstats': {'achievements': [{'name': 'Locked', 'achieved': 0, 'unlocktime': 0}]}},
                20: {'playerstats': {'achievements': [{'name': 'Found Later', 'achieved': 1, 'unlocktime': 250}]}}
            }
            return payloads[params['appid']]

        result = select_latest_recent_steam_achievement(
            [{'appid': 10, 'name': 'No Unlocks'}, {'appid': 20, 'name': 'Has Unlock'}],
            'steam-user',
            fake_steam_api_get,
        )

        self.assertIsNotNone(result)
        self.assertEqual(result['game']['appid'], 20)
        self.assertEqual(result['achievement']['name'], 'Found Later')

    def test_returns_none_when_no_recent_games_have_unlocks(self):
        def fake_steam_api_get(interface, method, version, params):
            return {'playerstats': {'achievements': [{'name': 'Locked', 'achieved': 0, 'unlocktime': 0}]}}

        result = select_latest_recent_steam_achievement(
            [{'appid': 10, 'name': 'Still Locked'}],
            'steam-user',
            fake_steam_api_get,
        )

        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()
