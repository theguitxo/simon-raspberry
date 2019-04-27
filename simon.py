#!/usr/bin/env python3

from PIL import Image, ImageTk
from tkinter import Tk, ttk, Label
import sys
from time import sleep
import RPi.GPIO as GPIO
from random import randint, seed

"""
  clase Simon
  juego Simon usando pulsadores conectados a la GPIO
  recibe cinco parámetros al instanciarse
    pinInicio -> pin donde se conecta el botón para iniciar partida
    pinVerde -> pin donde se conecta el botón verde
    pinAmarillo -> pin donde se conecta el botón amarillo
    pinRojo -> pin donde se conecta el botón rojo
    pinAzul -> pin donde se conecta el botón azul
"""
class Simon():

  # contenedor para la ventana de tkinter
  raiz = None

  # botones
  # botón de inicio (negro)
  botonInicio = None
  # botones de colores:
  botonesColores = []

  # colores del juego
  colores = ('verde', 'amarillo', 'rojo', 'azul')

  # listas para los objetos de imagen de los colores
  coloresOn = [None, None, None, None]
  coloresOff = [None, None, None, None]

  # etiquetas de tkinter para mostrar las imagenes de les colores
  cajasColores = [None, None, None, None]

  # mensajes que muestra la aplicación al jugador
  mensajes = {
    "bienvenida.1": "Bienvenido a Simon",
    "bienvenida.2": "Pulsa el botón negro para empezar",
    "instrucciones.1": "Repite la secuencia de colores",
    "instrucciones.2": "¡Empezamos!",
    "secuencia.1": "Secuencia {0}",
    "secuencia.2": "Repite la secuencia",
    "puntos": "Puntos",
    "record": "Record",
    "juego.terminado": "Juego terminado",
    "intento.ok": "¡Bien! Siguiente secuencia",
    "intento.ko": "¡Oh! ¡Has fallado! "
  }

  # labels de tkinter donde se muetran los mensajes la jugador
  cajasMensajes = [None, None]  

  # para controlar si la partida esta iniciada
  partidaIniciada = False

  # para controlar si esta disponible la funcionalidad de los botones de colores
  botonesBloqueados = True

  # contadores para puntos y records
  puntos = 0
  record = 0

  # etiquetas de tkinter para las puntuaciones (títulos y valores)
  cajaTituloPuntos = None
  cajaTituloRecord = None
  cajaPuntos = None
  cajaRecord = None

  # secuencia de colores de la partida
  secuencia = []

  # punto de la secuencia a comprobar con la pulsación del jugador
  pasoComprobar = 0

  ##  
  # __init__
  ##
  def __init__(self, pinInicio, pinVerde, pinAmarillo, pinRojo, pinAzul):   

    # se asignan los valores para los pins recibidos al instanciar la clase
    self.botonInicio = pinInicio
    self.botonesColores = [pinVerde, pinAmarillo, pinRojo, pinAzul]

    # inicialización del GPIO
    GPIO.setmode(GPIO.BOARD)

    # configuración de los pines como entrada de datos
    GPIO.setup(self.botonInicio, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
    GPIO.setup(self.botonesColores, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)

    # se inicia un objeto de tkinter y se define su geometría y titulo
    self.raiz = Tk()
    self.raiz.geometry('300x200')
    self.raiz.title('Simón')

    # evento al cerrar la ventana
    self.raiz.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    # se inician las imagenes (cargarlas desde disco)
    self.iniciarImagenes("on")
    self.iniciarImagenes("off")

    # se montan las etiquetas para las imagenes, mensajes y puntuaciones
    self.montarImagenes()
    self.montarMensajes()
    self.montarPuntuaciones()

    # se muetran los mensajes de bienvenida al juego
    self.mostrarMensaje(0, "bienvenida.1")
    self.mostrarMensaje(1, "bienvenida.2")

    # se añaden los eventos para las pulsaciones de los botones
    self.anyadirEventoIniciar()
    self.anyadirEventosBotonesColores()

    # inicio de la aplicación
    self.raiz.mainloop()
  
  ##
  # iniciarJuego
  # evento que se lanza al pulsar el botón negro
  # inicia una nueva partida
  # @pin: el número de pin al que esta conectado el botón negro
  ##
  def iniciarJuego(self, pin):
    # se comprueba que la partida no este iniciada 
    if(self.partidaIniciada == False):
      # se marca la partida como iniciada
      # y se muetran las instrucciones
      self.partidaIniciada = True;     
      self.mostrarMensaje(0, "instrucciones.1")
      self.mostrarMensaje(1, None)
      sleep(0.5)
      self.mostrarMensaje(1, "instrucciones.2")
      sleep(0.5)

      # se reinician la secuencia y la puntuación
      # se lanza la primera secuencia
      self.secuencia.clear();
      self.puntos = 0
      self.actualizarPuntuaciones()
      self.lanzarSecuencia()

  ##
  # lanzarSecuencia
  # muestra la secuencia de colores actual
  ##
  def lanzarSecuencia(self):
    # se obtiene el número de secuencia y se muestra como mensaje
    numeroSecuencia = len(self.secuencia) + 1
    self.mostrarMensaje(0, "secuencia.1", [numeroSecuencia])
    self.mostrarMensaje(1, None)
    sleep(0.5)

    #se elige el color a mostrar y se coloca en la última posición de la secuencia
    seed()
    color = randint(0, 3)
    self.secuencia.append(color)

    # se recorre la secuencia mostrando el color almacenado en cada posición
    for item in self.secuencia:
      self.mostrarColor(item, True)

    # se muestra el mensaje indicando repetir la secuencia
    # se reinicia el control de paso de secuencia a comprobar
    # y se desbloquean los botones de colores
    self.mostrarMensaje(1, "secuencia.2")
    self.pasoComprobar = 0
    self.botonesBloqueados = False   
    
  ##
  # mostrarColor
  # muestra la versión 'iluminada' de un color y, tras una pausa,
  # lo devuelve a su versión 'apagada'
  # @color: el índice en la lista de colores que se va a mostrar
  # @segundaPausa: si se ha de hacer una pausa o no después de volver a poner el color a 'apagado'
  ##
  def mostrarColor(self, color, segundaPausa):
    self.cajasColores[color].configure(image = self.coloresOn[color])
    sleep(0.75)
    self.cajasColores[color].configure(image = self.coloresOff[color])
    if(segundaPausa):
      sleep(0.75)

  ##
  # comprobarBotonColor
  # al pulsar alguno de los botones de colores,
  # comprueba si la pulsación ha sido correcta,
  # según la posición de la secuencia a comprobar
  # @pin: el pin del botón que se ha pulsado
  ##
  def comprobarBotonColor(self, pin):
    # se comprueba que los botones no esten bloqueados
    # y que se haya recibido un valor de pin a True
    # (se comprueba el pin para evitar rebotes )    
    if(self.botonesBloqueados == False and GPIO.input(pin) == True):

      # bloquea los botones y, a partir del indice del botón pulsado, 'enciende' el color 
      self.botonesBloqueados = True
      indiceBoton = self.botonesColores.index(pin)
      self.mostrarColor(indiceBoton, False)

      # se comprueba si el pin del botón pulsado es igual 
      # al guardado en la posición a comprobar de la secuencia
      if(self.secuencia[self.pasoComprobar] == indiceBoton):
        # el jugador ha acertado, se incrementa el paso a comprobar
        # si se ha llegado al final de la secuencia, se pasa a mostrar la siguiente,
        # si no, se desbloquean los botones y se espera a la siguiente pulsación
        self.pasoComprobar += 1
        if(self.pasoComprobar == len(self.secuencia)):
          self.puntos += 1
          self.actualizarPuntuaciones()
          self.mostrarMensaje(1, "intento.ok")
          sleep(1)
          self.mostrarMensaje(1, None)
          self.lanzarSecuencia()
        else:
          self.botonesBloqueados = False
      else:
        # el jugador ha fallado, se muestra el mensaje
        # de find de juego y el mensaje de bienvenida
        self.mostrarMensaje(1, "intento.ko")
        sleep(1)
        self.mostrarMensaje(0, "juego.terminado")
        self.mostrarMensaje(1, None)
        sleep(1)
        self.mostrarMensaje(0, "bienvenida.1")
        self.mostrarMensaje(1, "bienvenida.2")
        self.partidaIniciada = False

  ##
  # actualizarPuntuaciones
  # comprueba si se ha superado el record, actualizando si es necesario,
  # y actualiza los textos en sus etiquetas
  ##
  def actualizarPuntuaciones(self):
    if(self.puntos > self.record):
      self.record = self.puntos    
    self.cajaPuntos.configure(text = self.puntos)
    self.cajaRecord.configure(text = self.record)

  ##
  # anyadirEventosBotonesColores
  # añade el evento a ejecutar cuando se pulsa uno de los botones de colores
  # se dispara al cambiar su estado de 0 a 1
  ##
  def anyadirEventosBotonesColores(self):
    for boton in self.botonesColores:
      GPIO.add_event_detect(boton, GPIO.RISING, callback = self.comprobarBotonColor, bouncetime = 250)

  ##
  # anyadirEventoIniciar
  # añade el evento a ejecutar cuando se pulsa el botón de inicio
  # se dispara al cambiar su estado de 0 a 1  
  ##
  def anyadirEventoIniciar(self):
    GPIO.add_event_detect(self.botonInicio, GPIO.RISING, callback = self.iniciarJuego, bouncetime = 1000)

  ##
  # mostrarMensaje
  # muestra un mensaje en alguna de las dos etiquetas disponibles
  # @index: indice de la etiqueta donde mostrar el mensaje
  # @mensaje: indice de la lista de mensajes que se ha de mostrar (indicar None para borrar el mensaje actual)
  # @parametros (opcional): lista de parametros que se han de incluir en el mensaje, mediante la función 'format'
  ##
  def mostrarMensaje(self, index, mensaje, parametros = None):
    texto = ""
    if(mensaje != None):          
      texto = self.mensajes[mensaje]
      if(parametros != None):
        texto = texto.format(*parametros)
    self.cajasMensajes[index].configure(text = texto)

  ##
  # montarPuntuaciones
  # monta las etiquetas en la rejilla de la ventana para mostrar las puntuaciones del juego
  ##
  def montarPuntuaciones(self):
    self.cajaTituloPuntos = Label(self.raiz, text = self.mensajes["puntos"])
    self.cajaTituloPuntos.grid(row = 3, column = 0, columnspan = 2, pady = 5)
    self.cajaTituloRecord = Label(self.raiz, text = self.mensajes["record"])
    self.cajaTituloRecord.grid(row=3, column=2, columnspan=2, pady = 5)
    self.cajaPuntos = Label(self.raiz, text = self.puntos)
    self.cajaPuntos.grid(row = 4, column = 0, columnspan = 2, pady = 5)
    self.cajaRecord = Label(self.raiz, text = self.record)
    self.cajaRecord.grid(row=4, column=2, columnspan=2, pady  = 5)

  ##
  # montarMensajes
  # monta las etiquetas en la rejilla de la ventana para mostrar los mensaje de información al jugador
  ##
  def montarMensajes(self):
    for indice, valor in enumerate(self.cajasMensajes):
      self.cajasMensajes[indice] = Label(self.raiz, text = "");
      self.cajasMensajes[indice].grid(row = (indice + 1), column = 0, columnspan = 4, pady = 10)

  ##
  # montarImagenes
  # monta las etiquetas para mostrar las imagenes con los colores del juego
  ##
  def montarImagenes(self):
    for indice, valor in enumerate(self.coloresOff):
      self.cajasColores[indice] = Label(self.raiz, image = self.coloresOff[indice])
      self.cajasColores[indice].grid(row = 0, column = indice, padx = 5, pady = 5)
      self.raiz.columnconfigure(indice, weight = 1)

  ##
  # iniciarImagenes
  # carga los ficheros con las imagenes que hacen de colores y los almacena en listas
  # @tipo el tipo de imagen que se va a cargar: 'on' para los colores 'encendidos', 'off' para los colores 'apagados'
  ##
  def iniciarImagenes(self, tipo):
    for indice, valor in enumerate(self.colores):           
      imagen = Image.open(valor + "_" + tipo + ".png")
      if(tipo == "on"):
        self.coloresOn[indice] = ImageTk.PhotoImage(imagen)
      else:
        self.coloresOff[indice] = ImageTk.PhotoImage(imagen)

  ##
  # on_closing
  # acciones a realizar al cerrar la aplicación:
  #   -destruye la ventana gráfica
  #   -limpia la configuración de GPIO
  #   -sale de la aplicación
  ## 
  def on_closing(self):        
    self.raiz.destroy()
    GPIO.cleanup()
    sys.exit()

##
# main
# función a ejecutar cuando se inicia el script
##
def main():

  # botón inicio juego -> 16
  # botones de colores:
  #   12 -> verde
  #   15 -> amarillo
  #   13 -> rojo
  #   11 -> azul

  # se arranca una instancia de la clase 'Simon'
  Simon(16, 12, 15, 13, 11)  
  return 0

if __name__ == '__main__':
  main()
