from machine import Pin, ADC, PWM
import time

pot_base = ADC(Pin(35))
pot_brazo = ADC(Pin(34))

pot_base.atten(ADC.ATTN_11DB)
pot_brazo.atten(ADC.ATTN_11DB)

servo_base = PWM(Pin(18), freq=50)
servo_brazo = PWM(Pin(19), freq=50)

led_verde = Pin(26, Pin.OUT)
led_rojo = Pin(25, Pin.OUT)
buzzer = Pin(2, Pin.OUT)
btn_home = Pin(16, Pin.IN, Pin.PULL_UP)
btn_secuencia = Pin(17, Pin.IN, Pin.PULL_UP)

modo_manual = True
angulo_actual_base = 90
angulo_actual_brazo = 0

def mapear(valor, in_min, in_max, out_min, out_max):
    return int((valor - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)

def mover_servo_angulo(servo, angulo):
    duty = mapear(angulo, 0, 180, 26, 128)
    servo.duty(duty)
    return duty

def mover_servo_gradual(servo, angulo_actual, angulo_objetivo):
    if angulo_actual < angulo_objetivo:
        for angulo in range(angulo_actual, angulo_objetivo + 1, 2):
            mover_servo_angulo(servo, angulo)
            time.sleep_ms(50)
    else:
        for angulo in range(angulo_actual, angulo_objetivo - 1, -2):
            mover_servo_angulo(servo, angulo)
            time.sleep_ms(50)
    return angulo_objetivo

def volver_a_inicio():
    global modo_manual, angulo_actual_base, angulo_actual_brazo
    print("Volviendo a posición inicial...")
    modo_manual = False
    led_verde.off()
    led_rojo.on()
    buzzer.on()
    time.sleep(0.2)
    buzzer.off()
    
    angulo_actual_base = mover_servo_gradual(servo_base, angulo_actual_base, 90)
    angulo_actual_brazo = mover_servo_gradual(servo_brazo, angulo_actual_brazo, 0)
    
    buzzer.on()
    time.sleep(0.1)
    buzzer.off()
    
    led_rojo.off()
    led_verde.on()
    modo_manual = True
    print("Modo manual activado")

def ejecutar_secuencia():
    global modo_manual, angulo_actual_base, angulo_actual_brazo
    print("Ejecutando secuencia...")
    modo_manual = False
    led_verde.off()
    led_rojo.on()
    buzzer.on()
    time.sleep(0.3)
    buzzer.off()
    
    movimientos = [
        (45, 90),
        (135, 45),
        (90, 135),
        (0, 90),
        (90, 0)
    ]
    
    for ang_base, ang_brazo in movimientos:
        angulo_actual_base = mover_servo_gradual(servo_base, angulo_actual_base, ang_base)
        angulo_actual_brazo = mover_servo_gradual(servo_brazo, angulo_actual_brazo, ang_brazo)
        time.sleep(0.5)
    
    buzzer.on()
    time.sleep(0.2)
    buzzer.off()
    
    led_rojo.off()
    led_verde.on()
    modo_manual = True
    print("Secuencia completada")

print("Iniciando Grúa Robótica...")
print("Potenciómetro 1: Rotación de base")
print("Potenciómetro 2: Elevación de brazo")
print("Botón VERDE: Volver a inicio")
print("Botón 2: Secuencia")

angulo_actual_base = mover_servo_angulo(servo_base, 90)
angulo_actual_brazo = mover_servo_angulo(servo_brazo, 0)
led_verde.on()

try:
    while True:
        if btn_home.value() == 0:
            time.sleep_ms(20)
            if btn_home.value() == 0:
                volver_a_inicio()
                angulo_actual_base = 90
                angulo_actual_brazo = 0
                time.sleep(1)
        
        if btn_secuencia.value() == 0 and modo_manual:
            time.sleep_ms(20)
            if btn_secuencia.value() == 0:
                ejecutar_secuencia()
                time.sleep(1)
        
        if modo_manual:
            valor_pot_base = pot_base.read()
            valor_pot_brazo = pot_brazo.read()
            
            angulo_base = mapear(valor_pot_base, 0, 4095, 0, 180)
            angulo_brazo = mapear(valor_pot_brazo, 0, 4095, 0, 180)
            
            if abs(angulo_base - angulo_actual_base) > 3:
                angulo_actual_base = mover_servo_angulo(servo_base, angulo_base)
            
            if abs(angulo_brazo - angulo_actual_brazo) > 3:
                angulo_actual_brazo = mover_servo_angulo(servo_brazo, angulo_brazo)
        
        time.sleep_ms(50)
        
except:
    servo_base.deinit()
    servo_brazo.deinit()
    led_verde.off()
    led_rojo.off()
    buzzer.off()
    print("Programa detenido")