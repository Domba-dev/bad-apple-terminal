import cv2
import numpy as np
import pygame
import os
import time
import shutil
import sys
from pathlib import Path

if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path(__file__).parent

VIDEO = str(BASE_DIR / "bad_apple.mp4")
AUDIO = str(BASE_DIR / "bad_apple.mp3")
THRESHOLD = 128


def render_frame(frame, width, height):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    gray = cv2.resize(
        gray,
        (width, height * 2),
        interpolation=cv2.INTER_AREA
    )

    pixels = gray >= THRESHOLD

    output = []

    for y in range(0, height * 2, 2):
        row = []

        for x in range(width):
            top = pixels[y, x]
            bottom = pixels[y + 1, x]

            if top and bottom:
                row.append("\033[97;107m ")
            elif top:
                row.append("\033[97;40m▀")
            elif bottom:
                row.append("\033[30;107m▀")
            else:
                row.append("\033[30;40m ")

        output.append("".join(row))

    return "\n".join(output)


def main():
    if not os.path.exists(VIDEO):
        print("Missing bad_apple.mp4!")
        return

    if not os.path.exists(AUDIO):
        print("Missing bad_apple.mp3!")
        return

    cap = cv2.VideoCapture(VIDEO)

    if not cap.isOpened():
        print("Couldn't open video!")
        return

    fps = cap.get(cv2.CAP_PROP_FPS)

    if fps <= 0:
        fps = 30

    pygame.mixer.init()

    pygame.mixer.music.load(AUDIO)

    terminal = shutil.get_terminal_size()
    width = terminal.columns - 1
    height = terminal.lines - 2

    frame_number = 0

    print("\033[2J\033[?25l", end="", flush=True)

    try:
        pygame.mixer.music.play()

        while True:
            if not pygame.mixer.music.get_busy():
                break
            
            audio_position = pygame.mixer.music.get_pos() / 1000

            if audio_position < 0:
                audio_position = 0

            target_frame = int(audio_position * fps)

            if frame_number > target_frame:
                time.sleep(0.001)
                continue

            while frame_number < target_frame:
                ret, _ = cap.read()

                if not ret:
                    break

                frame_number += 1

            ret, frame = cap.read()

            if not ret:
                break

            image = render_frame(frame, width, height)

            print("\033[H" + image + "\033[0m",
                  end="", flush=True)

            frame_number += 1

    except KeyboardInterrupt:
        pass

    finally:
        pygame.mixer.music.stop()
        pygame.quit()
        cap.release()

        print("\033[0m\033[?25h\nPlayback finished!")


if __name__ == "__main__":
    main()
