import uasyncio as asyncio

# =========================
# --- Basic LED Helpers ---
# =========================

def adjust_brightness(colour, brightness):
    """
    Scales an RGB tuple by brightness (0.0 - 1.0), 
    clamps each value to 0-255.
    """
    return tuple(min(255, max(0, int(c * brightness))) for c in colour)

def update_brightness(np, brightness):
    """
    Rescales all LEDs in np according to the new brightness.
    Preserves relative colour intensities by scaling each
    pixel to a max of 255.
    """
    for i in range(len(np)):
        r, g, b = np[i]
        max_val = max(r, g, b)
        if max_val > 0:
            scale = 255.0 / max_val
            r = int(r * scale * brightness)
            g = int(g * scale * brightness)
            b = int(b * scale * brightness)
        np[i] = (r, g, b)
    np.write()

def reset_brightness(np, brightness):
    """
    Reverses brightness scaling, useful if the previous 
    adjustment needs to be undone.
    """
    for i in range(len(np)):
        r, g, b = np[i]
        np[i] = (int(r / brightness), int(g / brightness), int(b / brightness))
    np.write()


# =========================
# --- Matrix Mapping ---
# =========================

def serpentine_index(row, col, width=5, height=5):
    """
    Maps a (row, col) coordinate to the physical NeoPixel index 
    on a serpentine-wired matrix.

    Assumes:
    - Bottom row (physical row 0) = row index height-1
    - Wiring snakes left-right, right-left for odd rows
    """
    physical_row = height - 1 - row  # bottom row = 0
    return physical_row * width + col


def write_letter(np, base_index, matrix, colour, brightness, letter_width=5, letter_height=5):
    """
    Writes a 5x5 letter matrix to the NeoPixel strip.

    Arguments:
    - np: NeoPixel object
    - base_index: starting index for this letter in the strip
    - matrix: 5x5 2D array of 0/1 representing the letter
    - colour: RGB tuple
    - brightness: float 0-1
    """
    for row in range(letter_height):
        for col in range(letter_width):
            idx = serpentine_index(row, col, letter_width, letter_height) + base_index
            if idx >= len(np):
                continue
            np[idx] = adjust_brightness(colour, brightness) if matrix[row][col] else (0, 0, 0)


# =========================
# --- Flashing Routine ---
# =========================

async def flashing_routine(np, num_pixels, skate_pixels, lettersx4, letters_5x5, word, colour_array, colour_idx, brightness):
    """
    Flashes the skate LEDs and the word letters once.

    Arguments:
    - np: NeoPixel object
    - num_pixels: total LEDs
    - skate_pixels: number of "skate" LEDs before letters
    - lettersx4: offset index for letters
    - letters_5x5: dictionary mapping letters to 5x5 matrices
    - word: string to display
    - colour_array: array of RGB tuples
    - colour_idx: current index in colour_array for word
    - brightness: scaling factor
    """

    pixels_per_letter = 25  # 5x5 letters

    # Flip serpentine rows 1,2,3
    def fix_serpentine_row_mirroring(matrix):
        rows_to_flip = {1, 2, 3}
        return [list(reversed(row)) if i in rows_to_flip else row for i, row in enumerate(matrix)]

    # --- Select colours ---
    colour_idx += 1
    if colour_idx < len(colour_array) and colour_array[colour_idx] == (-1, -1, -1):
        colour_idx = 2

    word_colour = colour_array[colour_idx]
    skate_colour = colour_array[1]  # always same for skate

    # --- Flash skate LEDs ---
    for i in range(min(skate_pixels, num_pixels)):
        np[i + lettersx4] = adjust_brightness(skate_colour, brightness)

    # --- Flash letters ---
    word = (word or "").upper()[:5]
    for letter_index, char in enumerate(word):
        if char not in letters_5x5:
            continue
        matrix = letters_5x5[char]
        matrix = fix_serpentine_row_mirroring(matrix)
        base = skate_pixels + letter_index * pixels_per_letter
        write_letter(np, base, matrix, word_colour, brightness)

    np.write()
    await asyncio.sleep(0.75)

    # --- Turn all LEDs off ---
    for i in range(num_pixels):
        np[i] = colour_array[0]
    np.write()
    await asyncio.sleep(0.75)

    return colour_idx


# =========================
# --- Fill Routine ---
# =========================

async def fill_routine(np, num_pixels, skate_pixels, lettersx4, letters_5x5, word,
                       colour_array, colour_idx,
                       colour_idx_letters, colour_b_letters,
                       brightness):
    """
    Animates letters row-by-row with skate row fix.
    Handles forward/backwards cycling of rows.
    """

    pixels_per_letter = 25

    def fix_serpentine_row_mirroring(matrix):
        rows_to_flip = {1, 2, 3}
        return [list(reversed(row)) if i in rows_to_flip else row for i, row in enumerate(matrix)]

    if colour_idx < 2:
        colour_idx = 2
    word_colour = colour_array[colour_idx]

    word = (word or "").upper()[:5]
    row_pixels = [[] for _ in range(7)]

    # Collect indices for each row
    for letter_index, char in enumerate(word):
        if char not in letters_5x5:
            continue
        matrix = fix_serpentine_row_mirroring(letters_5x5[char])
        base = skate_pixels + letter_index * pixels_per_letter
        for row in range(5):
            for col in range(5):
                if matrix[row][col]:
                    idx = base + serpentine_index(row, col, 5, 5)
                    row_pixels[row].append(idx)

    # Skate rows (fixed)
    row_pixels[5] = [0, 11]
    row_pixels[6] = list(range(1, 11))

    # Animate forward/backward
    if not colour_b_letters:
        colour_idx_letters += 1
        if colour_idx_letters < len(row_pixels):
            colour = word_colour if colour_idx_letters < 5 else colour_array[1]
            for idx in row_pixels[colour_idx_letters]:
                np[idx] = adjust_brightness(colour, brightness)
        else:
            colour_b_letters = True
            colour_idx_letters -= 1
    else:
        if colour_idx_letters >= 0:
            for idx in row_pixels[colour_idx_letters]:
                np[idx] = colour_array[0]
            colour_idx_letters -= 1
        else:
            colour_b_letters = False
            colour_idx_letters = -1
            # Advance word colour
            colour_idx += 1
            while colour_idx < len(colour_array) and (colour_array[colour_idx] == (-1, -1, -1) or colour_idx < 2):
                colour_idx += 1
            if colour_idx >= len(colour_array):
                colour_idx = 2

    np.write()
    await asyncio.sleep(0.1)
    return colour_idx, colour_idx_letters, colour_b_letters


# =========================
# --- Fade Routine ---
# =========================

async def fade_routine(np, num_pixels, skate_pixels, lettersx4, letters_5x5, word, colour_array, colour_idx, colour_b, brightness, fade):
    """
    Gradually fades word and skate LEDs in/out.
    Handles row mirroring and brightness adjustments.
    """

    pixels_per_letter = 25

    def fix_serpentine_row_mirroring(matrix):
        rows_to_flip = {1, 2, 3}
        return [list(reversed(row)) if i in rows_to_flip else row for i, row in enumerate(matrix)]

    if colour_idx < 2:
        colour_idx = 2
    while colour_idx >= len(colour_array) or colour_array[colour_idx] == (-1, -1, -1):
        colour_idx = 2

    # Fade logic
    if fade >= 0.007 and not colour_b:
        fade /= 1.2
        if fade <= 0.007:
            colour_idx += 1
            if colour_idx >= len(colour_array) or colour_array[colour_idx] == (-1, -1, -1):
                colour_idx = 2
    else:
        colour_b = True
        fade *= 1.2
        if fade >= brightness:
            fade = brightness
            colour_b = False

    # Skate LEDs
    skate_colour = colour_array[1]
    row_top = [0, 11]
    row_bottom = list(range(1, 11))
    for i in row_top + row_bottom:
        if i < num_pixels:
            np[i + lettersx4] = adjust_brightness(skate_colour, fade)

    # Word letters
    word = (word or "").upper()[:5]
    for letter_index, char in enumerate(word):
        if char not in letters_5x5:
            continue
        matrix = fix_serpentine_row_mirroring(letters_5x5[char])
        base = skate_pixels + letter_index * pixels_per_letter
        write_letter(np, base, matrix, colour_array[colour_idx], fade)

    np.write()
    await asyncio.sleep(0.1)
    return colour_idx, colour_b, fade

# =========================
# --- Skate Routine ---
# =========================

async def skate_routine(np, num_pixels, skate_pixels, lettersx4, letters_5x5, word,
                        colour_array, colour_idx,
                        colour_idx_skate, colour_b_skate,
                        colour_idx_letters, colour_b_letters,
                        brightness):
    """
    Animates a "skate block" (top LEDs) and the letters below it.

    Skate block moves forward/back, while letters are animated bottom-to-top.
    Handles row 2 mirroring and cycling of word colours.
    """

    pixels_per_letter = 25  # Each letter is a 5x5 matrix

    # Ensure the first word colour is valid
    if colour_idx < 2:
        colour_idx = 2

    skate_colour = colour_array[1]  # colour for skate block
    word_colour = colour_array[colour_idx]  # colour for letters

    # --- Animate skate block ---
    if not colour_b_skate:
        colour_idx_skate += 1
        if colour_idx_skate < skate_pixels:
            np[colour_idx_skate] = adjust_brightness(skate_colour, brightness)
        elif colour_idx_skate == skate_pixels:
            colour_b_skate = True
    else:
        colour_idx_skate -= 1
        if colour_idx_skate >= 0:
            np[colour_idx_skate] = colour_array[0]  # turn off LED when moving back
        else:
            colour_b_skate = False

    # --- Build word pixel indices ---
    word = (word or "").upper()[:5]  # limit to 5 letters
    word_pixels = []

    for letter_index, char in enumerate(word):
        if char not in letters_5x5:
            continue
        matrix = letters_5x5[char]
        base = skate_pixels + letter_index * pixels_per_letter

        # Bottom-to-top iteration for correct animation
        for row in reversed(range(5)):
            physical_row = 5 - 1 - row
            right_to_left = physical_row % 2 == 1  # odd rows go right-to-left
            if row == 2:  # middle row always right-to-left
                right_to_left = True
            for col in range(5):
                mapped_col = 4 - col if right_to_left else col
                if matrix[row][col]:
                    global_idx = base + physical_row * 5 + mapped_col
                    word_pixels.append(global_idx)

    # --- Animate letters forward/back ---
    if not colour_b_letters:
        if colour_idx_letters + 1 < len(word_pixels):
            colour_idx_letters += 1
            np[word_pixels[colour_idx_letters]] = adjust_brightness(word_colour, brightness)
        else:
            colour_b_letters = True
    else:
        if colour_idx_letters >= 0:
            np[word_pixels[colour_idx_letters]] = colour_array[0]
            colour_idx_letters -= 1
        else:
            colour_b_letters = False
            colour_idx_letters = -1
            # Cycle word colour
            colour_idx += 1
            if colour_idx < len(colour_array) and colour_array[colour_idx] == (-1, -1, -1):
                colour_idx = 2

    # --- Push updates to the strip ---
    np.write()
    await asyncio.sleep(0.1)

    return colour_idx, colour_idx_skate, colour_b_skate, colour_idx_letters, colour_b_letters


# =========================
# --- Skate Random/LED Cycling Routine ---
# =========================

async def skate_rng_routine(np, num_pixels, skate_pixels, lettersx4, letters_5x5, word,
                            colour_array, colour_idx,
                            colour_idx_skate, colour_b_skate,
                            colour_idx_letters, colour_b_letters,
                            brightness):
    """
    Similar to skate_routine, but cycles the word LEDs with proper per-LED colour cycling.
    Ensures boundaries are respected and skips "off" colours.
    """

    pixels_per_letter = 25
    if colour_idx < 2:
        colour_idx = 2

    skate_colour = colour_array[1]  # skate block colour
    base_colour_idx = colour_idx     # starting colour for word LEDs

    # --- Animate skate block ---
    if not colour_b_skate:
        colour_idx_skate += 1
        if colour_idx_skate < skate_pixels:
            np[colour_idx_skate] = adjust_brightness(skate_colour, brightness)
        else:
            colour_b_skate = True
    else:
        colour_idx_skate -= 1
        if colour_idx_skate >= 0:
            np[colour_idx_skate] = colour_array[0]
        else:
            colour_b_skate = False

    # --- Build word pixel list in physical order ---
    word = (word or "").upper()[:5]
    word_pixels = []
    for letter_index, char in enumerate(word):
        if char not in letters_5x5:
            continue
        matrix = letters_5x5[char]
        base = skate_pixels + letter_index * pixels_per_letter
        for row in reversed(range(5)):
            physical_row = 5 - 1 - row
            right_to_left = physical_row % 2 == 1
            if row == 2:  # middle row animates right-to-left
                right_to_left = True
            for col in range(5):
                mapped_col = 4 - col if right_to_left else col
                if matrix[row][col]:
                    global_idx = base + physical_row * 5 + mapped_col
                    word_pixels.append(global_idx)

    # --- Usable colours for letters ---
    usable_colours = [c for c in colour_array[2:] if c != (-1, -1, -1)]
    if not usable_colours:
        usable_colours = [(255, 255, 255)]  # default to white

    num_colours = len(usable_colours)

    # --- Animate word LEDs one at a time ---
    if not colour_b_letters:  # turning LEDs on
        colour_idx_letters += 1
        if colour_idx_letters < len(word_pixels):
            led_colour_idx = (base_colour_idx - 2 + colour_idx_letters) % num_colours
            np[word_pixels[colour_idx_letters]] = adjust_brightness(usable_colours[led_colour_idx], brightness)
        else:
            colour_b_letters = True
            colour_idx_letters -= 1
    else:  # turning LEDs off
        if colour_idx_letters >= 0:
            np[word_pixels[colour_idx_letters]] = colour_array[0]
            colour_idx_letters -= 1
        else:
            colour_b_letters = False
            colour_idx_letters = -1
            # Cycle base colour for next sequence
            colour_idx += 1
            while colour_idx < len(colour_array) and (colour_array[colour_idx] == (-1, -1, -1) or colour_idx < 2):
                colour_idx += 1
            if colour_idx >= len(colour_array):
                colour_idx = 2

    np.write()
    await asyncio.sleep(0.1)
    return colour_idx, colour_idx_skate, colour_b_skate, colour_idx_letters, colour_b_letters


# =========================
# --- Goal Routine ---
# =========================

def goal_function(np, num_pixels, colours, brightness, led_b_state):
    """
    Turns all LEDs on or off during goal celebration.
    """
    if led_b_state:
        for i in range(num_pixels):
            np[i] = adjust_brightness(colours[2], brightness)
    else:
        for i in range(num_pixels):
            np[i] = colours[0]
    np.write()


async def goal_routine(np, num_pixels, colours, brightness):
    """
    Repeated goal celebration sequence with timed on/off phases.
    """
    for i in range(2):
        goal_function(np, num_pixels, colours, brightness, True)
        await asyncio.sleep(2.5)
        goal_function(np, num_pixels, colours, brightness, False)
        await asyncio.sleep(0.5)
        # repeat multiple bursts
        goal_function(np, num_pixels, colours, brightness, True)
        await asyncio.sleep(2.5)
        goal_function(np, num_pixels, colours, brightness, False)
        await asyncio.sleep(0.5)
        goal_function(np, num_pixels, colours, brightness, True)
        await asyncio.sleep(0.5)
        goal_function(np, num_pixels, colours, brightness, False)
        await asyncio.sleep(0.5)
        goal_function(np, num_pixels, colours, brightness, True)
        await asyncio.sleep(0.5)
        goal_function(np, num_pixels, colours, brightness, False)
        await asyncio.sleep(0.5)
        goal_function(np, num_pixels, colours, brightness, True)
        await asyncio.sleep(2.5)
        goal_function(np, num_pixels, colours, brightness, False)
        await asyncio.sleep(0.5)


# =========================
# --- WiFi LED Routines ---
# =========================

async def wifi_connected_routine(np, num_pixels, skate_pixel, colours, brightness):
    """
    Blink skate LEDs 3 times to indicate WiFi connected.
    """
    for _ in range(3):
        for i in range(skate_pixel):
            np[i] = adjust_brightness(colours[1], brightness)
        np.write()
        await asyncio.sleep_ms(200)
        for i in range(skate_pixel):
            np[i] = colours[0]  # turn off
        np.write()
        await asyncio.sleep_ms(200)


async def wifi_connecting_routine(np, num_pixels, skate_pixel, colours, brightness):
    """
    Display a progress indicator for connecting WiFi.
    """
    for i in range((skate_pixel - skate_pixel + 1), (skate_pixel - 1)):
        np[i] = adjust_brightness(colours[1], brightness)
    np.write()
    await asyncio.sleep(0)