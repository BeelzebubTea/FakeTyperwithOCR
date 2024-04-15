import cv2
import time
import random
import tkinter as tk
from tkinter import ttk
import keyboard
import threading
import pyautogui
from pynput import mouse
from PIL import Image
from pytesseract import pytesseract

path_to_tesseract = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
pytesseract.tesseract_cmd = path_to_tesseract
listener = None

def get_nearby_chars(char):
    nearby_chars = {
        'a': 'qwsz',
        'b': 'vghn',
        'c': 'xdfv',
        'd': 'erfcxs',
        'e': 'rdsw',
        'f': 'rtgvcd',
        'g': 'tyhbvf',
        'h': 'yujnbg',
        'i': 'ujklo',
        'j': 'uikmnh',
        'k': 'iolmj',
        'l': 'opk',
        'm': 'njk',
        'n': 'bhjm',
        'o': 'iklp',
        'p': 'ol',
        'q': 'wa',
        'r': 'tfde',
        's': 'wedxza',
        't': 'ygfr',
        'u': 'yhji',
        'v': 'cfgb',
        'w': 'qase',
        'x': 'zsdc',
        'y': 'hgtu',
        'z': 'asx'
    }
    return nearby_chars.get(char.lower(), char)

def fake_typing(text, char_speed, word_speed, typo_chars, typo_percentage, grace_period):
    global is_paused, current_index, progress_var

    index = current_index
    last_typo_index = -1  # Initialize the last typo index
    while index < len(text):
        if is_paused:
            break

        char = text[index]
        if char != " " and random.random() < typo_percentage and index - last_typo_index > grace_period:
            r = random.random()
            if r < 0.5:  # 50% chance of reversed letters
                if index + 1 < len(text):
                    next_char = text[index + 1]
                    keyboard.write(next_char + char)
                    time.sleep(random.uniform(char_speed - 0.01, char_speed + 0.01))
                    time.sleep(random.uniform(0.5, 1))  # Delay for recognizing the typo
                    keyboard.press_and_release('backspace')
                    time.sleep(random.uniform(0.1, 0.3))
                    keyboard.press_and_release('backspace')
                    time.sleep(random.uniform(0.1, 0.3))
                    keyboard.write(char)
                    time.sleep(random.uniform(0.1, 0.3))  # Delay between typing the correct characters
                    keyboard.write(next_char)
                    time.sleep(random.uniform(char_speed - 0.01, char_speed + 0.01))
                    index += 1
                    last_typo_index = index  # Update the last typo index
            elif r < 0.7:  # 20% chance of wrong nearby letter
                nearby_chars = get_nearby_chars(char)
                typo_char = random.choice(nearby_chars)
                keyboard.write(typo_char)
                time.sleep(random.uniform(0.5, 1))  # Delay for recognizing the typo
                keyboard.press_and_release('backspace')
                time.sleep(random.uniform(0.1, 0.3))
                keyboard.write(char)  # Type the correct character
                time.sleep(random.uniform(char_speed - 0.01, char_speed + 0.01))
                last_typo_index = index  # Update the last typo index
            elif r < 0.85:  # 15% chance of missing letter
                if index + 1 < len(text):
                    next_char = text[index + 1]
                    keyboard.write(next_char)
                    time.sleep(random.uniform(char_speed - 0.01, char_speed + 0.01))
                    time.sleep(random.uniform(0.5, 1))  # Delay for recognizing the typo
                    keyboard.press_and_release('backspace')
                    time.sleep(random.uniform(0.1, 0.3))
                    keyboard.write(char)
                    time.sleep(random.uniform(0.1, 0.3))  # Delay between typing the correct characters
                    keyboard.write(next_char)
                    time.sleep(random.uniform(char_speed - 0.01, char_speed + 0.01))
                    index += 1
                    last_typo_index = index  # Update the last typo index
            else:  # 15% chance of extra nearby letter
                nearby_chars = get_nearby_chars(char)
                typo_char = random.choice(nearby_chars)
                keyboard.write(char + typo_char)
                time.sleep(random.uniform(char_speed - 0.01, char_speed + 0.01))
                time.sleep(random.uniform(0.5, 1))  # Delay for recognizing the typo
                keyboard.press_and_release('backspace')
                time.sleep(random.uniform(0.1, 0.5))  # Delay before resuming typing
                last_typo_index = index  # Update the last typo index
        else:
            keyboard.write(char)
            if char == " ":
                time.sleep(random.uniform(word_speed - 0.01, word_speed + 0.01))
            else:
                time.sleep(random.uniform(char_speed - 0.01, char_speed + 0.01))
        index += 1

        current_index = index
        progress_var.set(f"{current_index}/{len(text)}")

    if not is_paused:
        current_index = 0
        progress_var.set(f"{current_index}/{len(text)}")
        window.after(0, unlock_input_controls)
        window.after(0, lambda: start_button.config(state="normal"))

def start_typing():
    text = text_entry.get("1.0", tk.END).strip()
    char_speed = char_speed_slider.get()
    word_speed = word_speed_slider.get()
    typo_chars = int(typo_chars_entry.get())
    typo_percentage = float(typo_percentage_entry.get())
    grace_period = 8  # Adjust this value according to your preference
    countdown(5)
    lock_input_controls()
    start_button.config(state="disabled")
    if block_input_var.get():
        block_keyboard_input()  # Block keyboard input if checkbox is checked
    typing_thread = threading.Thread(target=fake_typing, args=(text, char_speed, word_speed, typo_chars, typo_percentage, grace_period))
    typing_thread.start()

def reset_typing():
    global current_index, is_paused
    current_index = 0
    progress_var.set("0/0")
    start_button.config(state="normal")
    unlock_input_controls()
    if is_paused:
        is_paused = False
        pause_resume_button.config(text="Pause", state="disabled")
        window.after(1000, lambda: pause_resume_button.config(state="normal"))

def on_click(x, y, button, pressed):
    global listener
    if pressed:
        on_click.rx = x
        on_click.ry = y
    else:
        on_click.rx2 = x
        on_click.ry2 = y
        listener.stop()

def ocr_text():
    global listener
    countdown(3, ocr=True)
    listener = mouse.Listener(on_click=on_click)
    listener.start()
    listener.join()

    # Get the screen dimensions
    screen_width, screen_height = pyautogui.size()

    # Ensure the selected area stays within the screen boundaries
    left = max(0, min(on_click.rx, on_click.rx2))
    top = max(0, min(on_click.ry, on_click.ry2))
    right = min(screen_width, max(on_click.rx, on_click.rx2))
    bottom = min(screen_height, max(on_click.ry, on_click.ry2))

    # Calculate the width and height of the selected area
    width = right - left
    height = bottom - top

    # Capture the screenshot of the selected area
    ss = pyautogui.screenshot(region=(left, top, width, height))
    ss.save(r"text.png")

    img = cv2.imread('text.png', cv2.IMREAD_GRAYSCALE)
    text = pytesseract.image_to_string(img)

    # Remove extra new lines and join sentences
    text = text.replace('-\n', '').replace('\n', ' ')
    text = ' '.join(text.split())
    
    with open("words.txt", "w") as file:
        file.write(text)
    with open('words.txt', 'r') as file:
        filedata = file.read()
    filedata = filedata.replace('|', 'I')
    filedata = filedata.replace('\\', 'I')
    text_entry.delete("1.0", tk.END)
    text_entry.insert(tk.END, filedata)

    # Update the message in the countdown_label
    countdown_label.config(text="OCR completed. Text captured!")
        
def block_keyboard_input():
    keyboard.block_key('a')
    keyboard.block_key('b')
    keyboard.block_key('c')
    keyboard.block_key('d')
    keyboard.block_key('e')
    keyboard.block_key('f')
    keyboard.block_key('g')
    keyboard.block_key('h')
    keyboard.block_key('i')
    keyboard.block_key('j')
    keyboard.block_key('k')
    keyboard.block_key('l')
    keyboard.block_key('m')
    keyboard.block_key('n')
    keyboard.block_key('o')
    keyboard.block_key('p')
    keyboard.block_key('q')
    keyboard.block_key('r')
    keyboard.block_key('s')
    keyboard.block_key('t')
    keyboard.block_key('u')
    keyboard.block_key('v')
    keyboard.block_key('w')
    keyboard.block_key('x')
    keyboard.block_key('y')
    keyboard.block_key('z')

def unblock_keyboard_input():
    keyboard.unblock_key('a')
    keyboard.unblock_key('b')
    keyboard.unblock_key('c')
    keyboard.unblock_key('d')
    keyboard.unblock_key('e')
    keyboard.unblock_key('f')
    keyboard.unblock_key('g')
    keyboard.unblock_key('h')
    keyboard.unblock_key('i')
    keyboard.unblock_key('j')
    keyboard.unblock_key('k')
    keyboard.unblock_key('l')
    keyboard.unblock_key('m')
    keyboard.unblock_key('n')
    keyboard.unblock_key('o')
    keyboard.unblock_key('p')
    keyboard.unblock_key('q')
    keyboard.unblock_key('r')
    keyboard.unblock_key('s')
    keyboard.unblock_key('t')
    keyboard.unblock_key('u')
    keyboard.unblock_key('v')
    keyboard.unblock_key('w')
    keyboard.unblock_key('x')
    keyboard.unblock_key('y')
    keyboard.unblock_key('z')

def update_char_speed_label(value):
    char_speed_label.config(text=f"Character Delay Range (seconds): {value}")

def update_word_speed_label(value):
    word_speed_label.config(text=f"Word Delay Range (seconds): {value}")

def pause_resume_typing(event=None):
    global is_paused
    if not is_paused:
        is_paused = True
        pause_resume_button.config(text="Resume", state="disabled")
        window.after(1000, lambda: pause_resume_button.config(state="normal"))
        unlock_input_controls()
        if block_input_var.get():
            unblock_keyboard_input()  # Unblock keyboard input when paused if checkbox is checked
    else:
        is_paused = False
        pause_resume_button.config(text="Pause", state="disabled")
        window.after(1000, lambda: pause_resume_button.config(state="normal"))
        countdown(3)
        time.sleep(3)
        lock_input_controls()
        if block_input_var.get():
            block_keyboard_input()  # Block keyboard input when resumed if checkbox is checked
        typing_thread = threading.Thread(target=fake_typing, args=(text_entry.get("1.0", tk.END).strip(), char_speed_slider.get(), word_speed_slider.get(), int(typo_chars_entry.get()), float(typo_percentage_entry.get())))
        typing_thread.start()

def countdown(seconds, ocr=False):
    message = "Selecting area" if ocr else "Typing started!"
    for i in range(seconds, -1, -1):
        countdown_label.config(text=f"{message} in {i} seconds...")
        countdown_label.update()
        time.sleep(1)
    countdown_label.config(text=message)

def lock_input_controls():
    block_input_checkbox.config(state="disabled")
    text_entry.config(state="disabled")
    typo_chars_entry.config(state="disabled")
    char_speed_slider.config(state="disabled")
    word_speed_slider.config(state="disabled")

def unlock_input_controls():
    block_input_checkbox.config(state="normal")
    text_entry.config(state="normal")
    typo_chars_entry.config(state="normal")
    char_speed_slider.config(state="normal")
    word_speed_slider.config(state="normal")

# Create the main window
window = tk.Tk()
window.title("Fake Typing")
window.geometry("450x600")

# Create and pack the text label and entry
text_label = ttk.Label(window, text="Text to Type:")
text_label.pack()
text_entry = tk.Text(window, height=10, width=40)
text_entry.pack()

# Create and pack the typo chars label and entry
typo_chars_label = ttk.Label(window, text="Number of Typo Characters:")
typo_chars_label.pack()
typo_chars_entry = ttk.Entry(window, width=5)
typo_chars_entry.insert(0, "1")
typo_chars_entry.pack()

# Create and pack the character speed range slider
char_speed_label = ttk.Label(window, text="Character Delay Range (seconds): 0.1")
char_speed_label.pack()
char_speed_slider = ttk.Scale(window, from_=0.05, to=0.5, length=200, orient=tk.HORIZONTAL, command=lambda value: update_char_speed_label(round(float(value), 2)))
char_speed_slider.set(0.1)
char_speed_slider.pack()

# Create and pack the word speed range slider
word_speed_label = ttk.Label(window, text="Word Delay Range (seconds): 0.3")
word_speed_label.pack()
word_speed_slider = ttk.Scale(window, from_=0.05, to=0.5, length=200, orient=tk.HORIZONTAL, command=lambda value: update_word_speed_label(round(float(value), 2)))
word_speed_slider.set(0.2)
word_speed_slider.pack()

# Create and pack the block input checkbox
block_input_var = tk.BooleanVar()
block_input_checkbox = ttk.Checkbutton(window, text="Block Keyboard Input", variable=block_input_var)
block_input_checkbox.pack()

# Create and pack the pause/resume button
pause_resume_button = ttk.Button(window, text="Pause", command=pause_resume_typing)
pause_resume_button.pack()
hotkey_label = ttk.Label(window, text="Press F2 to Pause")
hotkey_label.pack()

# Create and pack the OCR button
ocr_button = ttk.Button(window, text="OCR", command=ocr_text)
ocr_button.pack()

# Create and pack the countdown label
countdown_label = ttk.Label(window, text="", font=("Helvetica", 16))
countdown_label.pack()

# Create and pack the typo percentage label and entry
typo_percentage_label = ttk.Label(window, text="Typo Percentage:")
typo_percentage_label.pack()
typo_percentage_entry = ttk.Entry(window, width=5)
typo_percentage_entry.insert(0, "0.02")
typo_percentage_entry.pack()

# Create and pack the progress label
progress_var = tk.StringVar()
progress_label = ttk.Label(window, textvariable=progress_var)
progress_label.pack()

# Create a frame to hold the start and reset buttons
button_frame = ttk.Frame(window)
button_frame.pack()

# Create and pack the start button
start_button = ttk.Button(button_frame, text="Start Typing", command=start_typing)
start_button.pack(side=tk.LEFT, padx=(0, 10))

# Create and pack the reset button
reset_button = ttk.Button(button_frame, text="Reset", command=reset_typing)
reset_button.pack(side=tk.LEFT)

# Bind the F2 key to pause/resume the program
keyboard.on_press_key("f2", pause_resume_typing)

is_paused = False
current_index = 0

# Start the main event loop
window.mainloop()
