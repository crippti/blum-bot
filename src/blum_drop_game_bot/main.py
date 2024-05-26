import argparse
import threading
import time
from pathlib import Path
from typing import Tuple, Optional

import cv2
import dxcam
import numpy as np
import pyautogui

GAME_DURATION = 30
SNOWFLAKE_COLORS = [
    (86, 211, 142),
    (13, 219, 71),
    (10, 214, 77)
]


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--play-times', type=int, required=True)
    args = parser.parse_args()
    return args


class DropGameBot:
    def __init__(self, resources_path: Path, game_duration, snowflakes_colors):
        self.cam = dxcam.create(output_color='BGR')
        new_game_image_p = resources_path / 'new_game.png'
        new_game_image_p2 = resources_path /'new_game2.png'

        self.new_game_variants = [
            cv2.imread(str(new_game_image_p), cv2.IMREAD_GRAYSCALE),
            cv2.imread(str(new_game_image_p2), cv2.IMREAD_GRAYSCALE),
        ]
        for template in self.new_game_variants:
            if template is None:
                raise ValueError('Failed to load new_game images.')
        self.snowflakes_colors = snowflakes_colors
        self.game_duration = game_duration

    def _detect_play_button(self, im) -> Optional[Tuple[int, int]]:
        for template in self.new_game_variants:
            res = cv2.matchTemplate(im, template, cv2.TM_CCOEFF_NORMED)
            w, h = template.shape[1], template.shape[0]
            _, _, _, max_loc = cv2.minMaxLoc(res)
            return max_loc[0] + w // 2, max_loc[1] + h // 2

        return None

    def start_new_game(self):
        im = self.cam.grab()
        im = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        coords = self._detect_play_button(im)
        if not coords:
            raise RuntimeError('Cannot find play button')

        x, y = coords
        pyautogui.click(x, y)

    def _find_snowflakes(self, im):
        mask = None
        for color in self.snowflakes_colors:
            lower_bound = np.array(color) - 10
            upper_bound = np.array(color) + 10
            color_mask = cv2.inRange(im, lower_bound, upper_bound)
            if mask is None:
                mask = color_mask
            else:
                mask = cv2.bitwise_or(mask, color_mask)
        return mask

    @staticmethod
    def calc_contour_center(contour) -> Optional[Tuple[int, int]]:
        M = cv2.moments(contour)
        if M["m00"] != 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            return cX, cY
        else:
            return None

    def play_game(self):
        start_ts = time.time()
        while time.time() - start_ts < self.game_duration:
            try:
                im = self.cam.grab()

                mask = self._find_snowflakes(im)
                contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                for contour in contours:
                    center = self.calc_contour_center(contour)
                    if center:
                        pyautogui.moveTo(center[0], center[1])
                        break

            except Exception:
                continue

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        # self.stop()
        pass


def main():
    print('Blum Drop Game bot made by @crippti.')
    args = parse_args()
    resources_path = Path(__file__).parent / 'resources'

    with DropGameBot(
        resources_path=resources_path,
        game_duration=GAME_DURATION,
        snowflakes_colors=SNOWFLAKE_COLORS
    ) as bot:
        time.sleep(2)
        # for i in range(args.play_times):
        while True:
            # try:
            #     bot.start_new_game()
            # except Exception as e:
            #     print(f'exc during start {e}')
            try:
                bot.play_game()
            except Exception as e:
                print(f'unhandled exception during game start. {e}')


if __name__ == '__main__':
    main()
