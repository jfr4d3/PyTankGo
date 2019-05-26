import time
import RPi.GPIO as GPIO             #libreria para los delay ycontrol del tiempo
import _thread                      #libreria para hebra
import pygame                       #libreria para control del teclado matricial
from pad4pi import rpi_gpio
import random

GPIO.setmode(GPIO.BCM)              #Se declaran en inician los gpio de motores
GPIO.setup(2, GPIO.OUT)
GPIO.setup(3, GPIO.OUT)
x = GPIO.PWM(2, 50)
y = GPIO.PWM(3, 50)

FLAG_START_DISPARO = None           #declaramos los Flags
FLAG_START_IMPACTO = None
FLAG_START_MELODIA = None
FLAG_JUEGO_TERMINADO = None
FLAG_MENU = None
FLAG_DIFI = None
difi = None

KEYPAD = [
    ["1", "2", "3", "A"],           #declaracion de la matriz del teclado
    ["4", "5", "6", "B"],
    ["7", "8", "9", "C"],
    ["*", "0", "#", "D"]
]


ROW_PINS = [4, 14, 15, 17]  # BCM numbering
COL_PINS = [18, 27, 22, 23]  # BCM numbering

factory = rpi_gpio.KeypadFactory()              #iniciliacizacion del metodo de teclado

keypad = factory.create_keypad(keypad=KEYPAD, row_pins=ROW_PINS, col_pins=COL_PINS)

pygame.mixer.pre_init()
pygame.mixer.init()
pygame.init()


def inicializa_sistema():               #inicicializacion de variables a False o neutro
    global FLAG_START_DISPARO
    global FLAG_START_IMPACTO
    global FLAG_START_MELODIA
    global FLAG_JUEGO_TERMINADO
    global FLAG_MENU
    global FLAG_DIFI
    global difi

    FLAG_START_DISPARO = False
    FLAG_START_IMPACTO = False
    FLAG_START_MELODIA = False
    FLAG_JUEGO_TERMINADO = False
    FLAG_MENU = False
    FLAG_DIFI = False
    difi = 0


posicion_x = 7.5
posicion_y = 7.5


def inicializa_servos():
    global posicion_x
    global x
    x.start(posicion_x)

    global posicion_y
    global y
    y.start(posicion_y)


def servo_x(direccion):                 #Servo_X
    global x
    global posicion_x
    if (direccion == 0 and posicion_x <= 10):
        posicion_x = posicion_x + 0.25
        x.ChangeDutyCycle(posicion_x)
        print("Moviendo Servo_X a %f" % posicion_x)
    if (direccion == 1 and posicion_x >= 5):
        posicion_x = posicion_x - 0.25
        x.ChangeDutyCycle(posicion_x)
        print("Moviendo Servo_X a %f" % posicion_x)


def servo_y(direccion):                     #Servo_Y
    global y
    global posicion_y
    if (direccion == 0 and posicion_y <= 10):
        posicion_y = posicion_y + 0.25
        y.ChangeDutyCycle(posicion_y)
        print("Moviendo Servo_Y a %f" % posicion_y)
    if (direccion == 1 and posicion_y >= 5):
        posicion_y = posicion_y - 0.25
        y.ChangeDutyCycle(posicion_y)
        print("Moviendo Servo_Y a %f" % posicion_y)




class Player():             #clase para objeto player
    nombre = ""
    archivo = ""
    disparo = ""
    impacto = ""


def inicializa_player(nom, arc, disp, imp):     #crea un nuevo objeto player
    Player.nombre = nom
    Player.archivo = arc
    Player.disparo = disp
    Player.impacto = imp


countdisp = 1


def inicia_disparo(efecto):             #metodo para iniciar el disparo segun flags
    global FLAG_START_DISPARO
    global countdisp
    FLAG_START_DISPARO = True
    pygame.init()
    pygame.mixer.Channel(0).play(pygame.mixer.Sound(efecto))#inicia el efecto de sonido
    time.sleep(0.3)
    print("[DISPARO %d]" % (countdisp))
    countdisp = countdisp + 1
    impacto_detectado(Player.impacto)#contador de disparos


def impacto_detectado(efecto):                      #inicia el efecto de sonido
    probabilidad_impacto = random.randrange(10)
    global difi
    global FLAG_START_IMPACTO
    global FLAG_START_MELODIA
    if (FLAG_START_DISPARO == True and probabilidad_impacto > difi):
        FLAG_START_IMPACTO = True
        FLAG_START_MELODIA = True
        pygame.init()
        pygame.mixer.music.load(efecto)#inicia el efecto de sonido
        pygame.mixer.music.play()
        print("[IMPACTO DETECTADO]")
        time.sleep(2)
        fin()
    if (FLAG_START_DISPARO == True and probabilidad_impacto <= difi):#comprueba si se ha detectado en funcion de la dificultad elegida
        print("[IMPACTO FALLIDO]")


def play_music(cancion, musica):
    ##    if(FLAG_JUEGO_TERMINADO==False and FLAG_MENU==True):
    print("[Se reproducira " + cancion + "]")
    pygame.init()
    pygame.mixer.music.load(musica)                 #control de la melodia de fondo mediante una hebra
    pygame.mixer.music.play()
    pygame.mixer.music.set_volume(0.7)


try:
    while (FLAG_JUEGO_TERMINADO == False and FLAG_MENU == True):
        _thread.start_new_thread(play_music, (Player.nombre, Player.archivo))
except:
    print("Error en la thread musical")


def fin():              #metodo final de programa
    global FLAG_START_IMPACTO
    global FLAG_START_MELODIA
    global FLAG_JUEGO_TERMINADO
    if (FLAG_START_MELODIA == True and FLAG_START_IMPACTO == True):
        print("[FINAL DEL JUEGO]")
        print("Precision:  %f" % (100 / (countdisp - 1)))
        FLAG_JUEGO_TERMINADO = True
        print("Gracias por jugar")


print("%%%%%%%% WELCOME TO PYTANK %%%%%%%%")
print("Seleccione una melodia")
print("A) GoT ")
print("B) Tetris ")
print("C) StarWars ")
print("D) SuperMario ")

inicializa_sistema()            ##menu para elegir melodia e inicializar el sistema
inicializa_servos()##


def printKey(key1):
    global FLAG_JUEGO_TERMINADO
    global FLAG_MENU
    if (FLAG_MENU == False):
        print(key1)
        if (key1 == 'A' and FLAG_MENU == False):
            FLAG_MENU = True
            inicializa_player("GoT", "GoT.mp3", "GoT_disparo.wav", "GoT_impacto.mp3")
            play_music(Player.nombre, Player.archivo)
            time.sleep(0.4)

        if (key1 == 'B' and FLAG_MENU == False):
            FLAG_MENU = True
            inicializa_player("Tetris", "Tetris.mp3", "Tetris_disparo.wav", "Tetris_impacto.mp3")
            play_music(Player.nombre, Player.archivo)
            time.sleep(0.4)

        if (key1 == 'C' and FLAG_MENU == False):
            FLAG_MENU = True
            inicializa_player("StarWars", "StarWars.mp3", "SW_disparo.wav", "SW_impacto.mp3")
            play_music(Player.nombre, Player.archivo)
            time.sleep(0.4)

        if (key1 == 'D' and FLAG_MENU == False):
            FLAG_MENU = True
            inicializa_player("SuperMario", "SuperMario.mp3", "MB_disparo.wav", "MB_impacto.mp3")
            play_music(Player.nombre, Player.archivo)
            time.sleep(0.4)


keypad.registerKeyPressHandler(printKey)

try:
    while (FLAG_MENU == False):
        time.sleep(0.2)
except:
    pass


def dificultad(key):
    global FLAG_DIFI
                                    ##menu para elegir la dificultad de juego y activar flags para avanzar
    global difi
    global FLAG_MENU
    if (FLAG_MENU == True and FLAG_DIFI == False):
        print("A continuacion seleccione la dificultad:")
        print("1) Facil")
        print("2) Media")
        print("3) Dificil")
        if (key == '1' and FLAG_MENU == True):
            FLAG_DIFI = True
            difi = 3
            print("Dificultad: Facil")
            print("")
            print("Ya esta listo para jugar")
            print("Pulse 8 para disparar")

        if (key == '2' and FLAG_MENU == True):
            FLAG_DIFI = True
            difi = 5
            print("Dificultad: Media")
            print("")
            print("Ya esta listo para jugar")
            print("Pulse 8 para disparar")

        if (key == '3' and FLAG_MENU == True):
            FLAG_DIFI = True
            difi = 7
            print("Dificultad: Dificil")
            print("")
            print("Ya esta listo para jugar")
            print("Pulse 8 para disparar")


keypad.registerKeyPressHandler(dificultad)
try:
    while (FLAG_DIFI == False):
        time.sleep(0.2)
except:
    pass


def juego(key):                 ##menu de juego funcional
    global FLAG_JUEGO_TERMINADO
    global FLAG_MENU
    global FLAG_DIFI

    if (FLAG_JUEGO_TERMINADO == False and FLAG_MENU == True and FLAG_DIFI == True):

        if (key == '8'):
            inicia_disparo(Player.disparo)
        if (key == '7'):
            servo_x(1)
            time.sleep(0.5)
        if (key == '9'):
            servo_x(0)
            time.sleep(0.5)
        if (key == '0'):
            servo_y(1)
            time.sleep(0.5)
        if (key == '5'):
            servo_y(0)
            time.sleep(0.5)


keypad.registerKeyPressHandler(juego)

try:
    while (FLAG_JUEGO_TERMINADO == False):
        time.sleep(0.2)
except:
    keypad.cleanup()
