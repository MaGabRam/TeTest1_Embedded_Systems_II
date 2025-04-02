import RPi.GPIO as GPIO
import time
import serial
button1_pin = 19  
aux=3
heater_pin = 5
fan_pin = 26
TRIG = 23
ECHO = 24
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(button1_pin, GPIO.IN, pull_up_down = GPIO.PUD_UP)

GPIO.setup(heater_pin, GPIO.OUT)
GPIO.setup(fan_pin, GPIO.OUT)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)
    
GPIO.output(heater_pin, GPIO.HIGH)
GPIO.output(fan_pin, GPIO.LOW)
archivo = "magnitude.txt"
prevx=0
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
def medir_distancia():
    GPIO.output(TRIG, False)
    time.sleep(0.05)

    # Pulso de activación de 10us
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    # Medir el tiempo de respuesta
    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()

    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start
    distancia = pulse_duration * 17150  # en cm
    return round(distancia, 2)

#UART
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
        if GPIO.input(button1_pin) == GPIO.LOW:
            print("Button 1 on")
            x=int(input("Ingrese un valor de 0-100: "))
            ser.write((str(int(x)) + "\n").encode('utf-8'))
            aux=1
            prevx=x
            time.sleep(0.2)
        elif aux==1:
            print("Button 1 off")
            ser.write((str(int(prevx)) + "\n").encode('utf-8'))
            aux=0
            time.sleep(0.2)
        distancia = medir_distancia()
        print(f"Distancia: {distancia} cm")

        if distancia<10:
            ser.write((str("alarm") + "\n").encode('utf-8'))
            time.sleep(0.1)
        time.sleep(0.1)
except KeyboardInterrupt:
    print("\nSaliendo del programa.")
    GPIO.cleanup()
    #ser.close()
