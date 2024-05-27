import argparse
import time
from multiprocessing import Pool
from pathlib import Path
from random import randint

import tls_client
import yaml

from settings import Settings, TgConnection, ThreadSettings



def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('--config', type=Path, required=True)
    args = parser.parse_args()
    return args



def play_game(settings: ThreadSettings):
    session = tls_client.Session(
        random_tls_extension_order=True
    )
    url = 'https://game-domain.blum.codes/api/v1/game/play'
    headers = {
        'Authorization': settings.tg.jwt_token
    }
    res = session.post(url, headers=headers, proxy=settings.tg.proxy)
    if res.status_code > 400:
        raise RuntimeError(f'Failed start game for {settings}')
    res_json = res.json()
    gameId = res_json['gameId']
    time.sleep(31)

    url = 'https://game-domain.blum.codes/api/v1/game/claim'
    payload = {
        'gameId': gameId,
        'points': settings.points
    }
    res = session.post(url, headers=headers, json=payload, proxy=settings.tg.proxy)
    if res.status_code > 400:
        raise RuntimeError(f'Failed claim point for game {gameId} for {settings}')


def main():
    print('Blum Drop Game bot made by @crippti.')
    args = parse_args()
    with args.config.open() as f:
        config = yaml.safe_load(f)

    settings = Settings(**config)

    with Pool(processes=settings.cpu_count) as pool:
        for tg in settings.telegrams:
            thread_settings = ThreadSettings(
                points=randint(settings.min_points, settings.max_points),
                tg=tg
            )
            pool.apply_async(play_game, [thread_settings])


if __name__ == '__main__':
    main()
