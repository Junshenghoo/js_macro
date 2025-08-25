from adafruit_hid.keycode import Keycode
import time

# A basic mapping for characters — expand as needed
CHAR_TO_KEYCODE = {
    # Letters
    'a': Keycode.A, 'b': Keycode.B, 'c': Keycode.C, 'd': Keycode.D, 'e': Keycode.E,
    'f': Keycode.F, 'g': Keycode.G, 'h': Keycode.H, 'i': Keycode.I, 'j': Keycode.J,
    'k': Keycode.K, 'l': Keycode.L, 'm': Keycode.M, 'n': Keycode.N, 'o': Keycode.O,
    'p': Keycode.P, 'q': Keycode.Q, 'r': Keycode.R, 's': Keycode.S, 't': Keycode.T,
    'u': Keycode.U, 'v': Keycode.V, 'w': Keycode.W, 'x': Keycode.X, 'y': Keycode.Y,
    'z': Keycode.Z,

    # Uppercase letters
    'A': [Keycode.LEFT_SHIFT, Keycode.A], 'B': [Keycode.LEFT_SHIFT, Keycode.B],
    'C': [Keycode.LEFT_SHIFT, Keycode.C], 'D': [Keycode.LEFT_SHIFT, Keycode.D],
    'E': [Keycode.LEFT_SHIFT, Keycode.E], 'F': [Keycode.LEFT_SHIFT, Keycode.F],
    'G': [Keycode.LEFT_SHIFT, Keycode.G], 'H': [Keycode.LEFT_SHIFT, Keycode.H],
    'I': [Keycode.LEFT_SHIFT, Keycode.I], 'J': [Keycode.LEFT_SHIFT, Keycode.J],
    'K': [Keycode.LEFT_SHIFT, Keycode.K], 'L': [Keycode.LEFT_SHIFT, Keycode.L],
    'M': [Keycode.LEFT_SHIFT, Keycode.M], 'N': [Keycode.LEFT_SHIFT, Keycode.N],
    'O': [Keycode.LEFT_SHIFT, Keycode.O], 'P': [Keycode.LEFT_SHIFT, Keycode.P],
    'Q': [Keycode.LEFT_SHIFT, Keycode.Q], 'R': [Keycode.LEFT_SHIFT, Keycode.R],
    'S': [Keycode.LEFT_SHIFT, Keycode.S], 'T': [Keycode.LEFT_SHIFT, Keycode.T],
    'U': [Keycode.LEFT_SHIFT, Keycode.U], 'V': [Keycode.LEFT_SHIFT, Keycode.V],
    'W': [Keycode.LEFT_SHIFT, Keycode.W], 'X': [Keycode.LEFT_SHIFT, Keycode.X],
    'Y': [Keycode.LEFT_SHIFT, Keycode.Y], 'Z': [Keycode.LEFT_SHIFT, Keycode.Z],

    # Numbers and shifted numbers
    '1': Keycode.ONE, '2': Keycode.TWO, '3': Keycode.THREE, '4': Keycode.FOUR,
    '5': Keycode.FIVE, '6': Keycode.SIX, '7': Keycode.SEVEN, '8': Keycode.EIGHT,
    '9': Keycode.NINE, '0': Keycode.ZERO,
    '!': [Keycode.LEFT_SHIFT, Keycode.ONE],
    '@': [Keycode.LEFT_SHIFT, Keycode.TWO],
    '#': [Keycode.LEFT_SHIFT, Keycode.THREE],
    '$': [Keycode.LEFT_SHIFT, Keycode.FOUR],
    '%': [Keycode.LEFT_SHIFT, Keycode.FIVE],
    '^': [Keycode.LEFT_SHIFT, Keycode.SIX],
    '&': [Keycode.LEFT_SHIFT, Keycode.SEVEN],
    '*': [Keycode.LEFT_SHIFT, Keycode.EIGHT],
    '(': [Keycode.LEFT_SHIFT, Keycode.NINE],
    ')': [Keycode.LEFT_SHIFT, Keycode.ZERO],

    # Whitespace
    ' ': Keycode.SPACE,
    '\n': Keycode.ENTER,

    # Symbols
    '-': Keycode.MINUS,
    '_': [Keycode.LEFT_SHIFT, Keycode.MINUS],
    '=': Keycode.EQUALS,
    '+': [Keycode.LEFT_SHIFT, Keycode.EQUALS],
    '[': Keycode.LEFT_BRACKET,
    '{': [Keycode.LEFT_SHIFT, Keycode.LEFT_BRACKET],
    ']': Keycode.RIGHT_BRACKET,
    '}': [Keycode.LEFT_SHIFT, Keycode.RIGHT_BRACKET],
    '\\': Keycode.BACKSLASH,
    '|': [Keycode.LEFT_SHIFT, Keycode.BACKSLASH],
    ';': Keycode.SEMICOLON,
    ':': [Keycode.LEFT_SHIFT, Keycode.SEMICOLON],
    '\'': Keycode.QUOTE,
    '"': [Keycode.LEFT_SHIFT, Keycode.QUOTE],
    '`': Keycode.GRAVE_ACCENT,
    '~': [Keycode.LEFT_SHIFT, Keycode.GRAVE_ACCENT],
    ',': Keycode.COMMA,
    '<': [Keycode.LEFT_SHIFT, Keycode.COMMA],
    '.': Keycode.PERIOD,
    '>': [Keycode.LEFT_SHIFT, Keycode.PERIOD],
    '/': Keycode.FORWARD_SLASH,
    '?': [Keycode.LEFT_SHIFT, Keycode.FORWARD_SLASH],
}

def type_string(kbd, text):
    for char in text:
        keycode = CHAR_TO_KEYCODE.get(char)
        if keycode is None:
            print(f"Unsupported character: {char}")
            continue
        if isinstance(keycode, list):
            modifier, main_key = keycode
            kbd.press(modifier)
            time.sleep(0.03)   # Let Shift settle
            kbd.press(main_key)
            time.sleep(0.02)    # Delay while holding
            kbd.release_all()
        else:
            kbd.press(keycode)
        time.sleep(0.01)
        kbd.release_all()
    time.sleep(0.01)