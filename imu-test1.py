import time
import board
import adafruit_icm20x

i2c = board.I2C()
imu = adafruit_icm20x.ICM20948(i2c, address=0x68)

while True:
    ax, ay, az = imu.acceleration
    gx, gy, gz = imu.gyro
    mx, my, mz = imu.magnetic

    print(
        f"ACC  x={ax:.2f} y={ay:.2f} z={az:.2f} | "
        f"MAG  x={mx:.2f} y={my:.2f} z={mz:.2f}"
    )

    time.sleep(0.5)
