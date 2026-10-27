import time
import board
import busio
import digitalio

from gpiozero import Motor, DigitalOutputDevice
from gpiozero.pins.pigpio import PiGPIOFactory

from adafruit_mcp3xxx.mcp3008 import MCP3008
from adafruit_mcp3xxx.analog_in import AnalogIn
from adafruit_mcp3xxx import mcp3008



# ---------------- MOTORS ----------------

factory = PiGPIOFactory()

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

# DRV8833 sleep pin
slp = DigitalOutputDevice(
    21,
    pin_factory=factory
)

slp.on()


# ---------------- IR SENSOR ----------------

spi = busio.SPI(
    clock=board.SCK,
    MISO=board.MISO,
    MOSI=board.MOSI
)

cs = digitalio.DigitalInOut(board.CE0)

mcp = MCP3008(spi, cs)

ir = AnalogIn(
    mcp,
    mcp3008.P0
)


# ============================================================
# CONTROL SETTINGS
# ============================================================

# Target is approximately 30 cm
TARGET_V = 1.55

# Safety stop before getting inside ~20 cm
STOP_V = 2.25

# Motor settings
MIN_SPEED = 0.08
MAX_SPEED = 0.35

# Proportional gain
KP = 0.35

# Sensor filtering
ALPHA = 0.60

# Sharp sensor updates roughly every ~40 ms
LOOP_TIME = 0.04


# ============================================================
# FUNCTIONS
# ============================================================

def stop():
    left.stop()
    right.stop()


def forward(speed):

    speed = max(0.0, min(MAX_SPEED, speed))

    left.forward(speed)
    right.forward(speed)


# ============================================================
# START
# ============================================================

filtered_v = ir.voltage

print()
print("==============================")
print(" LAB 11 - STRAIGHT FOLLOWER")
print("==============================")
print()
print("Target distance: ~30 cm")
print("Allowed range:   20-40 cm")
print("Starting in 3 seconds...")
print()

time.sleep(3)


# ============================================================
# MAIN LOOP
# ============================================================

try:

    while True:

        # Read sensor
        raw_v = ir.voltage

        # Low-pass filter to reduce noise
        filtered_v = (
            ALPHA * raw_v
            + (1.0 - ALPHA) * filtered_v
        )


        # ----------------------------------------------------
        # TOO CLOSE -> STOP
        # ----------------------------------------------------

        if filtered_v >= STOP_V:

            speed = 0.0
            stop()

            state = "STOP"


        # ----------------------------------------------------
        # CLOSER THAN TARGET -> WAIT
        # ----------------------------------------------------

        elif filtered_v >= TARGET_V:

            speed = 0.0
            stop()

            state = "WAIT"


        # ----------------------------------------------------
        # LEADER MOVING AWAY -> FOLLOW
        # ----------------------------------------------------

        else:

            # Lower voltage means leader is farther away.
            error = TARGET_V - filtered_v

            # More distance -> more speed
            speed = MIN_SPEED + (KP * error)

            # Limit maximum motor command
            speed = min(speed, MAX_SPEED)

            forward(speed)

            state = "FOLLOW"


        print(
            f"IR={filtered_v:.3f} V   "
            f"speed={speed:.3f}   "
            f"{state}"
        )

        time.sleep(LOOP_TIME)


# ============================================================
# SAFE SHUTDOWN
# ============================================================

except KeyboardInterrupt:

    print("\nStopping...")


finally:

    stop()
    slp.off()

    print("Follower stopped safely.")
