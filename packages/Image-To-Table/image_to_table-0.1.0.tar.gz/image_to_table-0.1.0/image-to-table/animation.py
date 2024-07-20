import os
import random
import time

# Define the symbols for animation
icons = ["  ", "🟤", "👻"]

def generate_wave_frames(term_size):
    frames = []
    waves = []
    bg = [0] * term_size
    i = 10
    iend = term_size - 1
    
    while iend > 0:
        line = list(bg)
        
        if i % 10 == 0:
            waves.append(0)
        
        for iw in range(len(waves)):
            line[waves[iw]] = 1
            if waves[iw] >= iend:
                continue
            waves[iw] += 1
            if waves[iw] == iend:
                iend -= 1
        
        frames.append(line)
        i += 1
    
    return frames

def generate_surf_frames(term_size):
    frames = []
    bg = [1] * term_size
    rider = random.randint(2, len(icons) - 1)
    
    for i in reversed(range(term_size)):
        line = list(bg)
        line[i] = rider
        frames.append(line)
    
    frames.append(bg)
    return frames

def display_frames(frames, icons):
    for line in frames:
        print("".join(map(lambda x: icons[x], line)), end="\r", flush=True)
        time.sleep(0.1)

def clear_animation(term_size):
    # Clear the terminal by printing empty lines
    for _ in range(term_size):
        print()
        
def animate():
    term_size = os.get_terminal_size().columns //2
    
    while True:
        frames = generate_surf_frames(term_size)
        display_frames(frames, icons)
        time.sleep(1)
