import time
import board
import adafruit_tcs34725
import adafruit_ssd1306

from PIL import Image, ImageDraw, ImageFont

#--------------
#I2C + devices
#--------------

i2c = board.I2C()

sensor = adafruit_tcs34725.TCS34725(i2c)
display = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)

display.fill(0)
display.show()

#Default font for the display
font = ImageFont.load_default()

#These are the sensor settings
sensor.integration_time = 100
sensor.gain = 16

#Average sensor readings

def read_average(samples=5, delay=0.05):
    r_total = 0
    g_total = 0
    b_total = 0
    c_total = 0

    for _ in range(samples):
        r, g, b, c = sensor.color_raw
        r_total += r
        g_total += g
        b_total += b
        c_total += c

        time.sleep(delay)
    return (
        r_total / samples,
        g_total / samples,
        b_total / samples,
        c_total / samples
    )

#Color classifier

def classify_color(r, g, b, c):

    if c < 3:
        return "BLACK"
    total = r + g + b
    if total == 0:
        return "UNKNOWN"
    rn = r / total
    gn = g / total
    bn = b / total

    #Black
    if c < 8:
        return "BLACK"

    #White
    if (
        abs(rn - gn) < 0.08
        and abs(gn - bn) < 0.08
        and abs(rn - bn) < 0.08
    ):
        return "WHITE"
    #Pink
    if (
        rn > 0.43
        and rn < 0.65
        and gn > 0.18
        and bn > 0.10
        and r > g
        and r > b
    ):
        return "PINK"
    #Red
    if (
        rn > 0.52
        and r > g * 1.5
        and r > b * 1.5
    ):
        return "RED"
    #Green
    if (
        gn > 0.42
        and g > r * 1.15
        and g > b * 1.25
    ):
        return "GREEN"
    #Blue
    if (
        bn > 0.38
        and b > r * 1.15
        and b > g * 1.15
    ):
        return "BLUE"
    #Yellow
    if (
        rn > 0.35
        and gn > 0.28
        and bn < 0.22
        and r > b * 1.5
        and g > b * 1.3
    ):
        return "YELLOW"
    #Orange
    if (
        rn > 0.48
        and gn > 0.22
        and bn < 0.18
        and r > g
    ):
        return "ORANGE"
    return "UNKNOWN"

#OLED display

def show_color(color):

    image = Image.new(
        "1",
        (display.width, display.height)
    )

    draw = ImageDraw.Draw(image)

    #Roughly center the text on the display
    bbox = draw.textbbox((0, 0), color, font=font)

    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    x = (display.width - text_width) // 2
    y = (display.height - text_height) // 2

    draw.text(
        (x, y),
        color,
        font=font,
        fill=255
    )

    display.image(image)
    display.show()

#Main loop

print("color classifier running...")
print("Press CTRL+C to stop.")

try:
    while True:
        r, g, b, c = read_average(samples=5)
        color = classify_color(
            r,
            g,
            b,
            c
        )

        #To keep detailed readings in terminal for testing or debugging
        total = r + g + b
        if total > 0:
            rn = r / total
            gn = g / total
            bn = b / total
        else:
            rn = gn = bn = 0

        print(
            f"R={r:.1f} "
            f"G={g:.1f} "
            f"B={b:.1f} "
            f"C={c:.1f} | "
            f"Rn={rn:.2f} "
            f"Gn={gn:.2f} "
            f"Bn={bn:.2f} "
            f"-> {color}"
        )
        #OLED only shows the color name
        show_color(color)

        time.sleep(0.3)
#To stop the program press CTRL+C
except KeyboardInterrupt:
    print("\nStopped.")
    display.fill(0)
    display.show()
