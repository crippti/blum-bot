import argparse
import time
from pathlib import Path
from typing import Tuple, Optional
import threading
from pynput.mouse import Button, Controller
from pynput.keyboard import Listener, Key

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
delay = 0.00001
button = Button.left
start_stop_key = Key.space
mouse = Controller()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--play-times', type=int, required=True)
    args = parser.parse_args()
    return args


class ClickMouse(threading.Thread):

    # delay and button is passed in class
    # to check execution of auto-clicker
    def __init__(self, delay, button):
        super(ClickMouse, self).__init__()
        self.delay = delay
        self.button = button
        self.running = False
        self.program_running = True


    def start_clicking(self):
        self.running = True

    def stop_clicking(self):
        self.running = False

    def exit(self):
        self.stop_clicking()
        self.program_running = False

    # method to check and run loop until
    # it is true another loop will check
    # if it is set to true or not,
    # for mouse click it set to button
    # and delay.
    def run(self):
        while self.program_running:
            while self.running:
                mouse.click(self.button)
                time.sleep(self.delay)
            time.sleep(0.1)

        # instance of mouse controller is created


# on_press method takes
# key as argument


            # here exit method is called and when
    # key is pressed it terminates auto clicker

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
        self.click_thread = ClickMouse(delay, button)
        self.listener = Listener(on_press=self.on_press)
        self.listener.start()

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
        self.click_thread.start()
        self.click_thread.start_clicking()
        while time.time() - start_ts < self.game_duration:
            try:
                im = self.cam.grab()
                # im = cv2.cvtColor(im, cv2.COLOR_RGB2BGR)

                mask = self._find_snowflakes(im)
                contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                for contour in contours:
                    center = self.calc_contour_center(contour)
                    if center:
                        pyautogui.moveTo(center[0], center[1])
                        break

                # time.sleep(0.01)
            except Exception:
                continue
        self.click_thread.stop_clicking()

    def on_press(self, key):
        # start_stop_key will stop clicking
        # if running flag is set to true
        if key == start_stop_key:
            if self.click_thread.running:
                self.click_thread.stop_clicking()
            else:
                self.click_thread.start_clicking()

    def stop(self):
        self.cam.release()
        self.click_thread.exit()
        self.listener.stop()
        self.listener.join()
        self.click_thread.join()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.stop()



def main():
    args = parse_args()
    resources_path = Path(__file__).parent / 'resources'

    with DropGameBot(
        resources_path=resources_path,
        game_duration=GAME_DURATION,
        snowflakes_colors=SNOWFLAKE_COLORS
    ) as bot:
        time.sleep(3)
        for i in range(args.play_times):
            try:
                bot.start_new_game()
            except Exception as e:
                print(f'exc during start {e}')
            try:
                bot.play_game()
            except Exception as e:
                print(f'unhandled exception during game start. {e}')



if __name__ == '__main__':
    main()
