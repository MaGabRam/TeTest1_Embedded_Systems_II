import RPi.GPIO as GPIO
import time
import serial

# Configuración de pines
button1_pin = 19  
aux = 0
prevx = 0

# Configuración de GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(button1_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# UART
ser = serial.Serial('/dev/ttyACM0', 9600)
ser.reset_input_buffer()

print("Escuchando botón...")

try:
    while True:
        if GPIO.input(button1_pin) == GPIO.LOW:
            print("Button 1 on")
            x = int(input("Ingrese un valor de 0-100: "))
            ser.write((str(x) + "\n").encode('utf-8'))
            aux = 1
            prevx = x
            time.sleep(0.2)
        elif aux == 1:
            print("Button 1 off")
            ser.write((str(prevx) + "\n").encode('utf-8'))
            aux = 0
            time.sleep(0.2)

except KeyboardInterrupt:
    print("\nSaliendo del programa.")
    GPIO.cleanup()
    ser.close()
