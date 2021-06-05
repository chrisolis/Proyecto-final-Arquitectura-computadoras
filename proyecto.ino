//HC-SR04
#define echoPin 4 // Pin D4 del Arduino conectado al pin Echo del HC-SR04
#define trigPin 3 // Pin D3 del Arduino conectado al pin Trig del HC-SR04
//DHT11 o en especifico el modulo KY-015 que es equivalente en su manejo
#include <dht11.h> //Se importa la libreria con la que se controla el sensor DHT11 de temperatura y humedad.
dht11 DHT11; //Se declara un objeto del tipo dht11 de la libreria DHT11LIB con el nombre DHT11 para poder utilizarlo mas adelante y llamar a los metodos de la libreria misma.
//Comunicacion serial
const byte numChars = 32; //Variable para definir el largo del string basado en un numero de caracteres.
char receivedChars[numChars];   //Arreglo para guardar informacion recibida.
//LDR o fotoresistencia
const long A = 1000;     //Resistencia en oscuridad en KΩ
const int B = 15;        //Resistencia a la luz (10 Lux) en KΩ
const int Rc = 10;       //Resistencia calibracion en KΩ
const int LDRPin = A0;   //Pin del LDR o fotoresistencia.
int V; //Variable a emplear en el calculo del valor del brillo.
float ilum; //Variable a emplear en el calcuulo del valor del brillo.
float porcent; //Variable para guardar el resultado de brillo regresado por la fotoresistencia.
int maxi = 100; //Variable con el valor de brillo maximo reportable.
String tempa = "C"; //Caracter a acompaniar al valor de la temperatura.
String dista = "D"; //Caracter a acompaniar al valor de la distancia.
String luxa = "L"; //Caracter a acompaniar al valor del brillo.
String esHora = "T"; //Caracter a indicar que han pasado 10 segundos.

boolean newData = false;
int contador = 0; //Variable para contar los 10 segundos que accionan T.
long duration; //Variable para guardar cuando se tardo en regresar el sonido.
int distance; //Variable para guardar la distancia calculada

void setup() {
  DHT11.attach(2); //Se realiza la conexion al pin analogo 2 al que se encuentra conectada la linea de datos del sensor.  
  Serial.begin(115200); //Comunicacion a 115200.
  pinMode(trigPin, OUTPUT); //Configura el pin del trigger como Output
  pinMode(echoPin, INPUT); //Configura el pin del echo como Input
}

void loop() {
  //Manda cada segundo los valores de temperatura, humedad, brillo y distancia.
  int chk = DHT11.read(); //Se lee la temperatura y la humedad. El metodo de la libreria actualiza dichos atributos del objeto DHT11.
  String tempo = String(DHT11.temperature, DEC); //Se convierte en String el atributo de temperatura con el fin de concatenarlo despues.
  String completo = tempa + tempo; //Se concatena un String conteniendo una 'C' al string conteniendo la temperatura.
  Serial.println(completo); //Se imprime el string completo concatenado que contiene el atributo temperature del objeto DHT11 en decimal.
  delay(10); //Se realiza un delay con el motivo de evitar lecturas erroneas dado a una ejecucion inmediata de la siguiente linea al apenas haber terminado de mandarse el mensaje por medio de la comunicacion serial.
  V = analogRead(LDRPin); //Lee el valor analogo de la fotoresistencia.
  ilum = ((long)V*A*10)/((long)B*Rc*(1024-V));//Calculo del brillo
  porcent = ((ilum/3036)*100); //Valor del brillo registrado por la fotoresistencia convertido a un porcentaje de 0 a 100.
  if(porcent >= 100){ //Si la lectura sobrepasara el limite de 100, solo se regresa 100.
    tempo = String(maxi); //Se convierte en String el entero maxi con el valor de intensidad maxima de brillo.
    completo = luxa + tempo; //Se concatena un String conteniendo una 'L' al string conteniendo el entero que representa la intensidad del brillo.
    Serial.println(completo); //Se imprime el string completo concatenado que contiene el porcentaje de luz.
  }
  else{
    tempo = String(porcent); //Se convierte en String el float porcent con el valor de intensidad de la luz.
    completo = luxa + tempo; //Se concatena un String conteniendo una 'L' al string conteniendo el entero que representa la intensidad de la luz.
    Serial.println(completo); //Se imprime el string completo concatenado que contiene el porcentaje de luz.
  }
  delay(10); //Nuevamente se utiliza un retraso con el fin de garantizar errores al realizar la lectura del siguiente sensor.
  //Deja el trigger apagado previo a la lectura de la distancia por 2 microsegundos para asegurar que el mismo este libre.
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  //Enciende el trigger por 10 microsegundos con el fin de generar una rafaga ultrasonica de 8 ciclos.
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  duration = pulseIn(echoPin, HIGH); //Lee el valor en microsegundos que tardo en volver el sonido.
  distance = duration * 0.034 / 2; //Calcula la distancia en base a la velocidad del sonido.
  tempo = String(distance); //Se convierte en String el valor entero de la distancia.
  completo = dista + tempo; //Se concatena un String conteniendo una 'D' al string conteniendo el entero que representa la intensidad del brillo.
  Serial.println(completo); //Envia el valor de la distancia junto con el caracter previamente descrito por la comunicacion serial.
  delay(10); //Se realiza un retraso despues de el envio del mensaje por comunicacion serial.
  contador = contador + 1; //Va aumentando el valor del contador en uno por cada segundo que pase.   
  delay(970); //Delay compensando los tiempos de lectura con el fin de completar el segundo.
  if(contador == 10){ //Si llega a diez el contador indica que ya pasaron 10 segundos
    contador = 0; //Se devuelve el contador a su valor inicial.
    Serial.println(esHora); //Se envia una 'T' para indicarle a la Raspberry que ya pasaron 10 segundos.
  }
}
