import RPi.GPIO as GPIO
import time
import serial

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

# Pines
heater_pin = 5
fan_pin = 26

GPIO.setup(heater_pin, GPIO.OUT)
GPIO.setup(fan_pin, GPIO.OUT)

GPIO.output(heater_pin, GPIO.HIGH)
GPIO.output(fan_pin, GPIO.HIGH)

archivo = "temperature.txt"

def leer_temperatura():
    with open(archivo, "r") as file:
        line = file.readline().strip()
        if "," in line:
            valor, unidad = line.split(",")
            try:
                temp = float(valor)
                unidad = unidad.upper()
                if unidad == "F":
                    temp = (temp - 32) * 5 / 9  # convertir a °C
                return temp
            except ValueError:
                print("⚠️ Formato incorrecto en temperature.txt")
                return None
        else:
            print("⚠️ El archivo debe tener formato: 25,C o 77,F")
            return None

# UART
ser = serial.Serial('/dev/ttyACM0', 9600)
ser.reset_input_buffer()

print("Escuchando...")

try:
    while True:
        temperatura = leer_temperatura()
        if temperatura is None:
            time.sleep(1)
            continue

        if ser.in_waiting > 0:
            raw = ser.readline()
            try:
                data = raw.decode('utf-8').rstrip()
                print("Tiva dice:", data)
                if data == "medir":
                    print(f"Temperatura en °C: {temperatura:.2f}")

                    if temperatura > 20:
                        print("hot")
                        GPIO.output(heater_pin, GPIO.LOW)
                        GPIO.output(fan_pin, GPIO.LOW)
                    elif temperatura < 2:
                        print("cold")
                        GPIO.output(heater_pin, GPIO.HIGH)
                        GPIO.output(fan_pin, GPIO.HIGH)
                else:
                    print("no")
            except UnicodeDecodeError:
                print("⚠️ Datos corruptos ignorados:", raw)

        time.sleep(0.1)

except KeyboardInterrupt:
    print("\nSaliendo del programa.")
    GPIO.cleanup()
    ser.close()