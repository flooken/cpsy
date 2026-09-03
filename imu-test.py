import time
import math
import board
import adafruit_icm20x
from gpiozero import LED

i2c = board.I2C()
imu = adafruit_icm20x.ICM20948(i2c, address=0x68)

red = LED(17)
blue = LED(27)

# Calibrated level acceleration vector
LEVEL_X = -3.15
LEVEL_Y = 2.08
LEVEL_Z = 9.83

LEVEL_TOLERANCE = 10.0  #degrees

while True:
    ax, ay, az = imu.acceleration
    mx, my, mz = imu.magnetic

    # North heading
    heading = math.degrees(math.atan2(my, mx))
    if heading < 0:
        heading += 360

    facing_north = heading <= 15 or heading >= 345

    #This to compare current gravity vector with calibrated level vector
    dot = (
        ax * LEVEL_X +
        ay * LEVEL_Y +
        az * LEVEL_Z
    )

    current_mag = math.sqrt(ax**2 + ay**2 + az**2)
    level_mag = math.sqrt(
        LEVEL_X**2 + LEVEL_Y**2 + LEVEL_Z**2
    )

    cos_angle = dot / (current_mag * level_mag)

    # Prevent rounding errors
    cos_angle = max(-1.0, min(1.0, cos_angle))
    level_error = math.degrees(math.acos(cos_angle))
    level = level_error <= LEVEL_TOLERANCE
    red.value = facing_north
    blue.value = level

    print(
        f"Heading={heading:.1f}° | "
        f"Level error={level_error:.1f}° | "
        f"North={facing_north} Level={level}"
    )

    time.sleep(0.2)
