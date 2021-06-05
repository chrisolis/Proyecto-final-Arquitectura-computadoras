import serial #Libreria para la comunicacion serial.
import subprocess #Libreria para la apertura del archivo de texto generado en la aplicacion default del sistema.
#Librerias 1 a 4 para poder manejar la pantalla OLED, obtenidas de consultar la pagina de Github 
#de Adafruit SSD1306 para comunicacion con pantallas OLED por I2C.
import board #1
import digitalio #2
from PIL import Image, ImageDraw, ImageFont #3
import adafruit_ssd1306 #4
from wia import Wia #Libreria 1 para realizar llamadas a Wia.
import random #Libreria 2 para realizar llamadas a Wia.
import requests #Libreria 3 para realizar llamadas a Wia.
import sys #Libreria 1 para la ejecucion de las ventanas de la interfaz.
import math #Libreria 1 para el uso de la camara.
import cv2 #Libreria 2 para el uso de la camara.
import datetime #Libreria para el uso de la fecha al igual que liberia 4 para realizar llamadas a Wia.
import time #Libreria para el uso de timers y tiempo del sistema.
#Librerias 2 a 7 para el uso de la interfaz por medio de PyQt y llamadas a objetos generados 
#por medio de QTDesigner que pertenecen al codigo de Python correspondiente a la interfaz. 
from PyQt5.QtWidgets import * #2
from PyQt5.QtCore import * #3
from PyQt5.QtCore import Qt, QTimer, pyqtSlot #4
from PyQt5 import QtCore, QtGui, QtWidgets #5
from PyQt5.QtGui import * #6
from GUI import* #7

#Configuracion del video de la camara

Capture = cv2.VideoCapture(0) #Asigna el video de la camara que aparece en el indice como 0 a la variable Capture (para uso futuro en los metodos de Camera) por medio de la libreria cv2.

#Configuracion inicial de la pantalla OLED.

oled_reset = digitalio.DigitalInOut(board.D4) #Asigna un pin para que funcione como reset de la pantalla.
WIDTH = 128 #Pixeles de altura de la pantalla
HEIGHT = 32 #Pixeles de ancho de la pantalla
BORDER = 5  #Pixeles a usar como borde en la pantalla en llamadas futuras.
i2c = board.I2C() #Crea la interfaz I2C
#Crea el objeto OLED de la clase adafruit ssd1306 al pasar los parametros como altura, ancho, 
#interfaz, direccion I2C a como aparece en el listado de la Raspberry y un pin de reseteo. 
#Todos pertenecientes a la pantalla.
oled = adafruit_ssd1306.SSD1306_I2C(WIDTH, HEIGHT, i2c, addr=0x3C, reset=oled_reset)

#Configuracion inicial para la comunicacion serial.

ser = serial.Serial('/dev/ttyACM0',baudrate=115200, timeout = 0.05) #Declaracion de la comunicacion
#serial al pasar parametros direccion en los dispositivos listados bajo comunicacion USB 
#(la del Arduino), tasa de baudios (velocidad de comunicacion) y timeout (permite el paso de bytes 
#despues de que se recibe cierto numero o regresa los recibidos en un determinado intervalo 
#de tiempo)
ser.flushInput() #Prepara el buffer del Serial al descartar todo su contenido previo.

#Variables a emplear para la preparacion de los datos recibidos por la comunicacion serial a
#imprimir en la pantalla, mandar a Wia y almacenar en un archivo de texto.

tempi = "C" #Variable que contiene el caracter que relaciona el dato recibido con el valor de la temperatura.
dis = "D" #Variable que contiene el caracter que relaciona el dato recibido con el valor de la distancia.
lux = "L" #Variable que contiene el caracter que relaciona el dato recibido con el valor de la luz.
tim = "T" #Variable que contiene el caracter que indica el paso de 10 segundos.
wia = Wia() #Se declara una instancia de Wia
wia.access_token = "d_sk_q6BqHXZezCccCZOOblxNCo8j" #Token con el cual Wia reconoce a que 
#dispositivo se relaciona los eventos y/o informacion publicada a la pagina.

class Ui_MainWindow(QtWidgets.QMainWindow,Ui_MainWindow): #Configuracion de la pantalla principal.
        def __init__(self):
                super().__init__()
                self.setupUi(self)
                self.setWindowTitle("Smart Hub") #Se altera el nombre principal de la ventana donde se monitorean los datos.
                self.camWindow = CamWindow() #Se asigna un formato para la ventana que contiene el video de la camara.
                self.Camera = Camera()
                self.Camera2 = Camera2()
                temp = 32 #Se declara un valor inicial para la etiqueta que refleja la temperatura (Pronto se remplaza por el valor leido por la comunicacion serial)
                oImage = QImage("b1.jpg") #Se asigna a una variable la imagen que se va a utilizar como fondo.								# Se asigna a una variable la imgaen que se va a utilizar como fondo 
                sImage = oImage.scaled(QSize(800,480)) #Se dimensiona la imagen al tamaño fijo de la ventana principal
                palette = QPalette() # QPalette -> clase que "pinta" los elementos en la ventana
                palette.setBrush(10, QBrush(sImage)) # Establece el pincel en el grupo de colores especificado, en este caso, los colores de la imagen utilizada
                self.setPalette(palette) #"Pinta" la imagen de la ventana principal

                timer = QTimer(self) #Se declara un timer por medio de Qtimer.
                timer.timeout.connect(self.showTime) #Se conecta la funcion de lectura de datos al timeout del timer. Se ejecutra cada vez que pase el tiempo declarado en timer.start.
                timer.start(100) # Actualiza cada 100 milisegundos

#-------------- Style ---------------- Establece el formato de los componentes de la interfaz como las etiquetas, botones, etc. Da color, tamano, etc.
                self.tmp_lb.setStyleSheet("""QLabel {border-radius: 25px; color: white; background-color: rgba(255, 255, 255, 50)}""")
                self.tmp_lb.setText(str(temp)+"°")
                self.tmp_lb.setStyleSheet("""QLabel {border: solid white;}""")
                self.dial_lb.setStyleSheet("""QLabel {border: 2px solid white; border-radius: 10px;color: white; background-color: rgba(0, 0, 0, 50)}""")
                self.dial_lb_2.setStyleSheet("""QLabel {border: 2px solid white; border-radius: 10px;color: white; background-color: rgba(0, 0, 0, 50)}""")
                self.label.setStyleSheet("""QLabel {border-radius: 10px;color: white; background-color: rgba(0, 0, 0, 50)}""")
                self.label_2.setStyleSheet("""QLabel {border-radius: 10px;color: white; background-color: rgba(0, 0, 0, 50)}""")
                self.date.setStyleSheet("""QLabel {color: #555b6e}""")
                self.Clock.setStyleSheet("""QLabel {color: white}""")
                self.alert.setStyleSheet("""QLabel {border-radius: 10px; color: white; background-color: rgba(255, 255, 255, 50)}""")
#--------------- Events ------------------- Establece las acciones a realizar de parte de los botones al ser presionados. Los vincula con los metodos existentes en la parte inferior del programa.		
                self.cam_btn.clicked.connect(self.on_click_cam) #Conecta al boton cam con el metodo self.on_click_cam
                self.home_btn.clicked.connect(self.on_click_home) #Conecta al boton home con el metodo self.on_click_home

#----------------------------------------
                self.showDate() #Se ejecuta la funcion showDate con la que se actualiza los elementos que despliegan la fecha en la interfaz.
                self.showTime() #Se ejecuta la funcion showTime con la que se actualiza la hora, se van leyendo los valores recibidos, se publica a Wia y se actualiza el archivo de texto.
                self.Camera.start() #Se ejecuta la apertura del video de la camara.
                self.Camera.ImageUpdate.connect(self.ImgUpdSlot) #Se vincula el metodo que actualiza la imagen de la camara con un atributo de la ejecucion de la misma.
                
#----------------------------------------
        def ImgUpdSlot(self, Image):
                self.cam.setPixmap(QPixmap.fromImage(Image)) #Convierte la imagen en un PixMap para que la muestre PyQt. Camara 1 o ventana 1 en otras palabras.

        def ImgUpdSlot2(self, Image):
                self.camWindow.cam_display.setPixmap(QPixmap.fromImage(Image)) #Convierte la imagen en un PixMap para que la muestre PyQt. Camara 2 o ventana 2 en otras palabras.

        def showTime(self): #Metodo que actualiza la hora del reloj, realiza la lectura de los sensores, los despliega en la pantalla OLED, los manda a Wia y los guarda en un archivo de texto.
                currentTime = QTime.currentTime() #Se llamada al metodo currentTime del objeto QT time con el fin de asignar a una variable el tiempo actual de la computadora que nos devuelve el metodo.
                displayTxt = currentTime.toString('hh:mm') #Se le aplica un formato a la hora del sistema y se convierte a string.
                self.Clock.setText(displayTxt) #Actualiza el reloj con la hora previamente formateada.
                try: #Intenta lo siguiente a menos que detecte una interrupcion por parte del teclado.
                        s= ser.readline() #Lee el dato que llego por la comunicacion serial.
                        s= s.strip() #Elimina los espacios extra al inicio y al final del dato.
                        mensaje = s.decode() #Decodifica el dato y lo asigna como mensaje.
                        if (mensaje != ''):
                                #Conversion del mensaje a un string a desplegar en la terminal y a ser revisado por el codigo subsecuente.
                                text = str(mensaje)
                                print(text) #Imprime en la terminal.
                                #Se declaran como globales procetemp, procedist, procelux con el fin de poder ser accesados por todas las condiciones posteriores a en las que se les asgina un valor.
                                global procetemp
                                global procedist
                                global procelux
                                if(text.find(tempi) != -1): #Si se encuentra el caracter 'C'.
                                        procetemp = text.replace('C', '') #Se elimina el caracter del mensaje.
                                        self.tmp_lb.setText(str(procetemp)+"°") #Se modifica el texto de la etiqueta para que muestre la nueva temperatura.
                                elif(text.find(lux) != -1): #Si se encuentra el caracter 'L'.
                                        procelux = text.replace('L', '') #Se elimina el caracter del mensaje.
                                        self.dial_lb_2.setText(str(procelux)+" %") #Se modifica el texto de la etiqueta para que muestre el nuevo brillo.
                                elif(text.find(dis) != -1): #Si se encuentra el caracter 'D'.
                                        procedist = text.replace('D', '') #Se elimina el caracter del mensaje.
                                        self.dial_lb.setText(str(procedist)+" cm") #Se modifica el texto de la etiqueta para que muestre la nueva distancia.
                                        currentDT = datetime.datetime.now() #Se extrae la informacion de la fecha actual por medio de datetime.date.now y se asigna al objeto currentDT
                                        f = open('/home/pi/Documents/Proyecto/SmartHub/monitoreo.txt','a') #Se abre el archivo de texto monitoreo con una a (append) para agregarle informacion. Si no existiera el archivo entonces lo crea.
                                        fecha = str("\n" + "Dia: " + str(currentDT.day) + "/" + str(currentDT.month) + "/" + str(currentDT.year) + ", Hora: " + str(currentDT.hour) + ":" + str(currentDT.minute) + ":" + str(currentDT.second)) #Se arma un string con los valores del dia, mes, anio, hora, minuto y segundo.
                                        f.write(fecha) #Se escribe dicho string en el archivo de texto de monitoreo.
                                        sensores = str(". Valores registrados -> Temperatura: " + str(procetemp) + " Celsius , Distancia: " + str(procedist) + " cm y Brillo: " + str(procelux) + "\n") #Se arma un string con los valores de los sensores junto con texto especificando que son cada uno.
                                        f.write(sensores) #Se escribe dicho string posterior al string de la fecha.
                                        f.close() #Se cierra el archivo para poder consultar los cambios en medio de la ejecucion si asi se deseara.
                                elif(text.find(tim) != -1): #Si se encuentra el caracter 'T'. Se publican los valores de los sensores con su formato correspondiente a Wia, se limpia la pantalla y se despliegan los nuevos ultimos valores recibidos en esos 10 segundos.
                                        wia.Event.publish(name="temp", data=procetemp) #Se publica la informacion del sensor de temperatura bajo el evento temp.
                                        time.sleep(0.01)
                                        wia.Event.publish(name="dista", data=procedist) #Se publica la informacion del sensor de temperatura bajo el evento dista.
                                        time.sleep(0.01)
                                        wia.Event.publish(name="luxa", data=procelux) #Se publica la informacion del sensor de temperatura bajo el evento luxa.
                                        time.sleep(0.01)
                                        #Limpieza de pantalla, construccion de cuadros en el marco de la misma.
                                        oled.fill(0)
                                        oled.show()
                                        image = Image.new("1", (oled.width, oled.height))
                                        draw = ImageDraw.Draw(image)
                                        draw.rectangle((0, 0, oled.width, oled.height), outline=255, fill=255)
                                        draw.rectangle(
                                        (BORDER, BORDER, oled.width - BORDER - 1, oled.height - BORDER - 1),
                                        outline=0,
                                        fill=0,
                                        )
                                        font = ImageFont.load_default()
                                        #Cambio de text a desplegar en la pantalla OLED por uno conformado con los 3 valores de los sensores y despliegue del mensaje.
                                        text = str(str(procetemp) + ", " + str(procedist) + ", " + str(procelux))
                                        (font_width, font_height) = font.getsize(text)
                                        draw.text(
                                        (oled.width // 2 - font_width // 2, oled.height // 2 - font_height // 2),
                                        text,
                                        font=font,
                                        fill=255,
                                        )
                                        oled.image(image)
                                        oled.show()
                except KeyboardInterrupt: #En caso de detectarse una interrupcion causada por el teclado se termina el programa.
                        sys.exit() #Terminacion del programa al manejar la excepcion.

        def showDate(self): #Metodo el cual muestra la fecha en el cuadro de texto destinado para esta en la intefaz.
                today = datetime.date.today() #Se extrae la informacion de la fecha actual por medio de datetime.date.today y se asigna a today.
                read = today.strftime("%a, %b %d") #Se convierte en string la fecha asignada con un formato especifico por medio de strftime y se almacena en la variable read.
                self.date.setText(read) #Se muestra la informacion en el cuadro de texto asignado para la fecha al mandar el texto de read.
                        
        def on_click_home(self): #Metodo que se ejecuta al presionar el boton de casa. Abre el archivo de texto de monitoreo en la aplicacion default cada vez que se presiona.
                if (self.rb_home.isChecked()): #Si el circulo que aparece debajo estuviera encendido
                        self.rb_home.setChecked(False) #Se apaga el circulo
                        subprocess.call(["xdg-open", r'/home/pi/Documents/Proyecto/SmartHub/monitoreo.txt']) #Se abre el archivo de monitoreo en la aplicacion default.
                else:
                        self.rb_home.setChecked(True) #Si estuviera apagado entonces se enciende.
                        subprocess.call(["xdg-open", r'/home/pi/Documents/Proyecto/SmartHub/monitoreo.txt']) #Se abre el archivo de monitoreo en la aplicacion default.

        def on_click_cam(self): #Metodo que se ejecuta al presionar el boton de la camara. Abre una ventana secundaria con una vista ampliada de la camara. En el caso de que esta estuviera abierta entonces se cierra.
                if (self.rb_cam.isChecked()): #En caso de estar cerrada la segunda ventana.
                        self.Camera.stop() #Se detiene la camara 1, la camara de la ventana chica.
                        self.rb_cam.setChecked(False) #Altera el circulo asociado a la ventana de la camara y lo pone en falso.
                        self.cam.setHidden(True) #Oculta el contenido del video de la camara 1.
                        self.camWindow.show() #Muestra la nueva ventana de la camara 2.
                        self.Camera2.start() #Inicia el video de la camara 2 a desplegar.
                        self.Camera2.ImageUpdate.connect(self.ImgUpdSlot2) #Vincula el metodo que va actualizando la imagen de la camara con lo que la prepara para trabajar con PyQt.
                        
                else: #En caso de estar abierta la segunda ventana.
                        self.Camera2.stop() #Se detiene la camara 2, la camara de la ventana grande.
                        self.rb_cam.setChecked(True) #Altera el circulo asociado a la ventana de la camara y lo pone encendido.
                        self.cam.setHidden(False) #Reaparece el contenido del video de la camara 1.
                        self.camWindow.hide() #Oculta la ventana grande de la camara 2.
                        self.Camera.start() #Inicia el video de la camara 1 a desplegar.
                        self.Camera.ImageUpdate.connect(self.ImgUpdSlot) #Vincula el metodo que va actualizando la imagen de la camara con lo que la prepara para trabajar con PyQt.		

#----------------------------------------
class Camera(QThread): #Clase que formatea el video de la camara 1, la acciona y la detiene.
        ImageUpdate = pyqtSignal(QImage)
        def run(self):
                self.ThreadActive = True
                while self.ThreadActive:
                        ret, frame = Capture.read()
                        if ret:
                                Image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                                FlippedImage = cv2.flip(Image, 1)
                                convert2QtFom = QImage(FlippedImage.data, FlippedImage.shape[1], FlippedImage.shape[0], QImage.Format_RGB888)
                                Pic = convert2QtFom.scaled(161,101, Qt.KeepAspectRatio)
                                self.ImageUpdate.emit(Pic)
        def stop(self): #En el caso de detener la imagen simplemente pone en falso el thread que mantienen la imagen corriendo.
                self.ThreadActive = False
                self.quit()

class Camera2(QThread): #Clase que formatea el video de la camara 2, la acciona y la detiene.
        ImageUpdate = pyqtSignal(QImage)
        def run(self):
                self.ThreadActive = True
                while self.ThreadActive:
                        ret, frame = Capture.read()
                        if ret:
                                Image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                                FlippedImage = cv2.flip(Image, 1)
                                convert2QtFom = QImage(FlippedImage.data, FlippedImage.shape[1], FlippedImage.shape[0], QImage.Format_RGB888)
                                Pic = convert2QtFom.scaled(500,300, Qt.KeepAspectRatio)
                                self.ImageUpdate.emit(Pic)
        def stop(self): #En el caso de detener la imagen simplemente pone en falso el thread que mantienen la imagen corriendo.
                self.ThreadActive = False
                self.quit()


class CamWindow(QWidget): #Clase con la que se forma la ventana de la version mas grande de la camara.
        def __init__(self, parent = None):
                super().__init__()
                self.setWindowTitle("Cam")

                self.setFixedSize(420, 380) #Se dimensiona el cuadro de la imagen para que la misma no aparezca pixeleada mas adelante.

                oImage = QImage("b4.jpg") #Se asigna a una variable la imgaen que se va a utilizar como fondo 
                sImage = oImage.scaled(QSize(600,450)) #Se dimensiona la imagen al tamaño fijo de la ventana principal
                palette = QPalette() #QPalette -> clase que "pinta" los elementos en la ventana
                palette.setBrush(10, QBrush(sImage)) #Establece el pincel en el grupo de colores especificado, en este caso, los colores de la imagen utilizada
                self.setPalette(palette)

                self.cam_display = QtWidgets.QLabel(self)
                self.cam_display.setGeometry(QtCore.QRect(10, 10, 400, 300))
                self.cam_display.setAutoFillBackground(True)
                self.cam_display.setFrameShape(QtWidgets.QFrame.Panel)
                self.cam_display.setFrameShadow(QtWidgets.QFrame.Sunken)
                self.cam_display.setText("")
                self.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, False)
                self.setWindowFlag(QtCore.Qt.WindowMinimizeButtonHint, False)


if __name__ == "__main__":
        app = QtWidgets.QApplication([]) #Declaracion de app la cual se usa para la aparicion de la ventana principal.
        window = Ui_MainWindow() #Asignacion de la invocacion de la ventana principal a la variable window.
        window.show() #Metodo show que causa la aparicion de la ventana principal.
        app.exec_() #Ejecucion de la ventana principal
