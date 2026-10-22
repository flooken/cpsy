import time
import board
import adafruit_tcs34725

from gpiozero import Motor, DigitalOutputDevice
from gpiozero.pins.pigpio import PiGPIOFactory


# ============================================================
# SETTINGS
# ============================================================

# Your measured values:
# black centre ≈ 5-10
# line edge    ≈ 15-30
# white        ≈ 60-76

# We deliberately follow the RIGHT edge of the black line.
TARGET_C = 24

BASE_SPEED = 0.105

# Steering strength
KP = 0.0040

# Limits
MIN_SPEED = 0.045
MAX_SPEED = 0.14

# Definitely lost line
LOST_C = 42

LOOP_DELAY = 0.01


# ============================================================
# HARDWARE
# ============================================================

factory = PiGPIOFactory()

# CONFIRMED:
# MOTA = RIGHT wheel
right = Motor(
    forward=12,
    backward=18,
    pin_factory=factory
)

# MOTB = LEFT wheel
left = Motor(
    forward=13,
    backward=19,
    pin_factory=factory
)

# DRV8833 sleep
slp = DigitalOutputDevice(
    21,
    pin_factory=factory
)

slp.on()


# ============================================================
# TCS34725
# ============================================================

i2c = board.I2C()
sensor = adafruit_tcs34725.TCS34725(i2c)


def get_clear():
    return sensor.color_raw[3]


# ============================================================
# MOTOR CONTROL
# ============================================================

def clamp(value, minimum, maximum):
    return max(minimum, min(maximum, value))


def drive(left_speed, right_speed):

    left_speed = clamp(
        left_speed,
        0,
        MAX_SPEED
    )

    right_speed = clamp(
        right_speed,
        0,
        MAX_SPEED
    )

    if left_speed > 0:
        left.forward(left_speed)
    else:
        left.stop()

    if right_speed > 0:
        right.forward(right_speed)
    else:
        right.stop()


def stop():
    left.stop()
    right.stop()


# ============================================================
# MAIN
# ============================================================

try:

    print("Proportional line follower")
    print("Target C =", TARGET_C)
    print("Ctrl+C to stop")

    while True:

        c = get_clear()


        # ====================================================
        # LINE COMPLETELY LOST
        # ====================================================

        if c >= LOST_C:

            # We are following the RIGHT edge.
            #
            # If the sensor reaches full white, the black
            # line should be to the LEFT of the sensor.
            #
            # Therefore make a strong but slow LEFT curve.

            left_speed = MIN_SPEED
            right_speed = MAX_SPEED

            drive(
                left_speed,
                right_speed
            )

            print(
                f"C={c:3d} LOST  "
                f"L={left_speed:.3f} "
                f"R={right_speed:.3f}"
            )


        # ====================================================
        # PROPORTIONAL EDGE FOLLOWING
        # ====================================================

        else:

            # Positive error:
            # C too high -> too much white
            # -> move LEFT toward black
            #
            # Negative error:
            # C too low -> too much black
            # -> move RIGHT toward edge

            error = c - TARGET_C

            correction = KP * error


            # ------------------------------------------------
            # RIGHT EDGE FOLLOWING
            #
            # Need LEFT:
            # right wheel faster
            #
            # Need RIGHT:
            # left wheel faster
            # ------------------------------------------------

            left_speed = BASE_SPEED - correction
            right_speed = BASE_SPEED + correction


            # Don't let either wheel become too weak
            left_speed = clamp(
                left_speed,
                MIN_SPEED,
                MAX_SPEED
            )

            right_speed = clamp(
                right_speed,
                MIN_SPEED,
                MAX_SPEED
            )


            drive(
                left_speed,
                right_speed
            )


            print(
                f"C={c:3d} "
                f"err={error:+3d} "
                f"L={left_speed:.3f} "
                f"R={right_speed:.3f}"
            )


        time.sleep(LOOP_DELAY)


except KeyboardInterrupt:

    print("\nStopped")


finally:

    stop()
    slp.off()

    print("Motors stopped")
