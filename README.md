> [!WARNING]
> ENTREGA EL DIJOUS A LES 8H

# **Satelit_Grup3**
Grup format per Èlia i Llorenç

# Informació general
Carpeta drive general -> [Link Carpeta Drive](https://drive.google.com/drive/folders/1hFdYLKDdTL-kQPWVFNueYWwphaPcYzBX?usp=sharing)

Organigrama -> [Link Organigrama](https://docs.google.com/spreadsheets/d/1V03nwSN4Qgww2q2C-urp8QdjpU71eczaaE-8ALJhC-Y/edit?usp=sharing)

## Protocol d'aplicació
El protocol unitari està estructurat per elements separats per "**;**", és a dir, funciona d'una forma similar a els "comandos" d'una terminal. Tanmateix, les tots els avalors estan pensats pequè puguin cabre en 3bits (numero màxim de opcions diferents) 

L'estructura del missatge enviat té aquesta forma:
| ACCIÓ |;|  ARGUMENT  |;|   VALOR1   |;|   VALOR2   |
| ------ |-| ------ |-| ------ |-| ------ |

Adicionalment, per adreçar-se als diferents sistemes es fa servir el conjunt d'**identificadors absoluts de sistemes** (**Id_Sys**). I aquest conjunt té la seguent forma:
| Sistema | Valor |
| ------- | ----- |
| Temperatura | 000 |
| Humitat     | 001 |
| Radar       | 010 |
| Alarmes     | 011 |
| Escombreig  | 100 |
| All         | 101 |


> [!TIP]
> La informació de la llista seguent està organitzada de la seguent forma:
>   - Acció
>       - Argument
>           - Valors 1 i 2 si escau

- **Observacions (000)**
  
  Recull totes les observacions fetes per el satèl·lit i les envia en un una sola línea separada per " : " on la posició indica de quin sistema prové la informació.

  Exemple:
  | temperatura |:|  humitat  |:|   Distància   |:|   Angle Radar   |
  | ------ |-| ------ |-| ------ |-| ------ |
  

  
- **Alarmes (001)**
    - Temp (000)
    - Hum (001)
    - Dist (010)
    - PerdudaConexió (011)
      
- **Ordres (010)**
  - Stop (000)
      - Id_Sys
  - Start (001)
      - Id_Sys
  - Freq (010)
      - Id_sys
          - Freqüència
  
- **Radar (011)**
    - Vel (000)
    - Lock (001)
        - Valor1 = Posició
        - Valor2 = Angle de Búsqueda
    - Mov (010)
    
- **Mitjanes (100)**
  - Lloc on es calculen (Satèl·lit = 000 / PC =001)
    - Id_Sys
      - Valor1 = Nº de Valors a pendre per la mitjana
  


# Entregues

## 3ª Entrega
![Imatge del muntatge de la versió 3](https://github.com/llorencvila/Satelit_Grup3/blob/main/ImatgeMuntatgeVersi%C3%B33.jpg)

### Requisits 3ª Entrega:
- [X] El controlador capta correctamente los datos de humedad, temperatura, distancia y posición del satélite.
- [X] La estación de tierra recibe correctamente los datos que le envía el controlador y los muestra en gráficas dinámicas apropiadas (incluida la gráfica 2D con la posición del satélite).
- [X] Las gráficas dinámicas están incrustadas en la interfaz gráfica.
- [X] Las gráficas también muestran la evolución del valor medio de las últimas 10 temperaturas.
- [X] El usuario puede elegir dónde deben calcularse las medias de las 10 últimas temperaturas (si en el satélite o en tierra).
- [X] El usuario puede parar/reanudar el envío de los datos de humedad/temperatura, el envio de datos de distancia y el envío de la posición del satélite.
- [ ] El usuario puede cambiar el periodo de envío de datos de temperatura/humedad, de distancia y de posición.
- [X] El controlador avisa correctamente a la estación de tierra en el caso de que no pueda captar bien los datos de temperatura/humedad o los datos de distancia (por ejemplo, porque se han desconectado los sensores).
- [X] La estación de tierra detecta un fallo en la comunicación con el controlador y avisa al usuario de esta circunstancia.
- [X] El usuario puede poner al sensor de distancia en modo rastreo (hace un barrido continuo de toda la zona alrededor del satelite) y también puede establecer una orientación determinada para el sensor.
- [X] El usuario puede establecer el valor máximo de temperatura que hará que salte una alarma si se reciben tres valores medios seguidos por encima de ese valor máximo.
- [ ] El usuario puede introducir en el sistema texto con sus observaciones en cualquier momento.
- [ ] El sistema registra en ficheros los 3 tipos de eventos (alarmas, comandos y observaciones).
- [ ] El usuario puede consultar en cualquier momento los eventos registrados, filtrando por dia y por tipo de evento.
- [X] El sistema funciona correctamente al sustituir la comunicación por cable por la comunicación inalámbrica.
- [X] El sistema de comunicaciones usa el mecanismo de checksum para detectar alteraciones en el mensaje.
- [X] El usuario de la estación de tierra no tiene ninguna duda de como interactuar con la interfaz gráfica ni para interpretar correctamente la información que se muestra en consola (tanto los datos como las alarmas)
- [X] El código está bien estructurado e indentado. Es fácil localizar en que parte del código que hace cada una de las operaciones de la versión 1.
- [X] Se han añadido comentarios clarificadores. En particular, hay comentarios que describen claramente el protocolo de aplicación. Cada función tiene un comentario que describe lo que hace, qué parámetros tiene y qué resultado produce.
- [X] Se ha implementado correctamente una cola circular para facilitar el cálculo de la media de los últimos 10 valores de temperatura.

### Video 3a Entrega
 [Video 3a Entrega](https://youtu.be/0R641AyqAaY)

## 2ª Entrega

### Requisits 2ª Entrega:
- [X] El controlador capta correctamente los datos de humedad, temperatura y distancia.
- [X]  La estación de tierra recibe correctamente los datos que le envía el controlador y los muestra en gráficas dinámicas apropiadas.
- [x]  Las gráficas dinámicas están incrustadas en la interfaz gráfica.
- [ ]  Las gráficas también muestran la evolución del valor medio de las últimas 10 temperaturas.
- [ ]  El usuario puede elegir dónde deben calcularse las medias de las 10 últimas temperaturas (si en el satélite o en tierra).
- [x]  El usuario puede parar/reanudar el envío de los datos de humedad/temperatura y el envio de datos de distancia.
- [ ]  El usuario puede cambiar el periodo de envío de datos de temperatura/humedad y de distancia.
- [x]  El controlador avisa correctamente a la estación de tierra en el caso de que no pueda captar bien los datos de temperatura/humedad o los datos de distancia (por ejemplo, porque se han desconectado los sensores).
- [ ]  La estación de tierra detecta un fallo en la comunicación con el controlador y avisa al usuario de esta circunstancia.
- [ ]  El usuario puede poner al sensor de distancia en modo rastreo (hace un barrido continuo de toda la zona alrededor del satelite) y también puede establecer una orientación determinada para el sensor.
- [ ]  El usuario puede establecer el valor máximo de temperatura que hará que salte una alarma si se reciben tres valores medios seguidos por encima de ese valor máximo.
- [ ]  El usuario de la estación de tierra no tiene ninguna duda de como interactuar con la interfaz gráfica ni para interpretar correctamente la información que se muestra en consola (tanto los datos como las alarmas)
- [x]  El código está bien estructurado e indentado. Es fácil localizar en que parte del código que hace cada una de las operaciones de la versión 1.
- [X]  Se han añadido comentarios clarificadores. En particular, hay comentarios que describen claramente el protocolo de aplicación. Cada función tiene un comentario que describe lo que hace, qué parámetros tiene y qué resultado produce.
- [ ]  Se ha implementado correctamente una cola circular para facilitar el cálculo de la media de los últimos 10 valores de temperatura.

### Video
https://youtu.be/f7alUr-Og3A

## 1ª Entrega
### Requiists 1ª Entrega:
- [X] https://github.com/llorencvila/Satelit_Grup3/issues/3
- [X] https://github.com/llorencvila/Satelit_Grup3/issues/2 
- [x] El controlador capta correctamente los datos de humedad y temperatura.
- [X] La estación de tierra recibe correctamente los datos que le envía el controlador y los muestra en una gráfica dinámica.
- [X] La gráfica dinámica está incrustada en la interfaz gráfica.
- [X] El usuario puede parar/reanudar el envío de los datos de humedad y temperatura
- [X] El controlador avisa correctamente a la estación de tierra en el caso de que no pueda captar bien los datos de temperatura y humedad (por ejemplo, porque se han desconectado los sensores).
- [X] La estación de tierra detecta un fallo en la comunicación con el controlador y avisa al usuario de esta circunstancia.
- [X] El usuario de la estación de tierra no tiene ninguna duda de como interactuar con la interfaz gráfica ni para interpretar correctamente la información que se muestra en consola (tanto los datos como las alarmas)
- [X] El código está bien estructurado e indentado. Es fácil localizar en que parte del código que hace cada una de las operaciones de la versión 1
- [X] Se han añadido comentarios clarificadores.
- [X] Video

### Video
https://www.youtube.com/watch?v=wUZRuor8o5I

> [!NOTE]
> És possible que les dates de les milestone no coincideixn amb les dates reals



