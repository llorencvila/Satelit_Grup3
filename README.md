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
| Temperatura | 0 |
| Humitat     | 1 |
| Radar       | 2 |
| Alarmes     | 3 |
| Escombreig  | 4 |
| All         | 5 |
| Laser       | 6 |


> [!TIP]
> La informació de la llista seguent està organitzada de la seguent forma:
>   - Acció
>       - Argument
>           - Valors 1 i 2 si escau

- **Observacions (0)**
  
  Recull totes les observacions fetes per el satèl·lit i les envia en un una sola línea separada per " : " on la posició indica de quin sistema prové la informació.

  Exemple:
  | 0 |:| Humitat |:|  Temperatura  |:|   Distància   |:|   Angle Radar   |:|   Angle Radar   |:|   Angle Radar   |:|   Angle Radar   |:|   Angle Radar   |:|   Angle Radar   |
  | ------ |-| ------ |-| ------ |-| ------ |
  

  
- **Alarmes (1)**
    - Temp (0)
    - Hum (1)
    - Dist (2)
    - PerdudaConexió (3)
      
- **Ordres (2)**
  - Stop (0)
      - Id_Sys
  - Start (1)
      - Id_Sys
  - Freq (2)
      - Id_sys
          - Freqüència
  
- **Radar (3)**
    - Vel (0)
    - Lock (1)
        - Valor1 = Posició
        - Valor2 = Angle de Búsqueda
    - Mov (2)
    
- **Mitjanes (4)**
  - Lloc on es calculen (Satèl·lit = 0 / PC =1)
    - Id_Sys
      - Valor1 = Nº de Valors a pendre per la mitjana
  


# Entregues

## 4ª Entrega
### Funcionalitats extres:
- Implementació de la gràfica 3D i el botó que canvia entre gràfiques.
- Implementació i funcionament de les comandes manuals.
- Explicació de l'ús de les comandes manuals a través del messagebox de l'alarma.
- Comunicacions per làser.
  
### Video 4ª Entrega
[Vídeo entrega 4](https://youtu.be/eSXh5SxtM-U)
## Videos d'entregues anteriors:

### 3ª Entrega: [Video 3a Entrega](https://youtu.be/0R641AyqAaY)

### 2ª Entrega: https://youtu.be/f7alUr-Og3A

### 1ª Entrega: https://www.youtube.com/watch?v=wUZRuor8o5I

> [!NOTE]
> És possible que les dates de les milestone no coincideixn amb les dates reals



