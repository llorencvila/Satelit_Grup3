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

## 4ª Entrega
### Funcionalitats extres:
- Implementació de la gràfica 3D i el botó que canvia entre gràfiques.
- Implementació i funcionament de les comandes manuals.
- Explicació de l'ús de les comandes manuals a través del messagebox de l'alarma.
- Comunicacions per làser.
  
### Video 4ª Entrega
[Vídeo entrega 4](https://youtu.be/2eA11_jPE5w)
## Videos d'entregues anteriors:

### 3ª Entrega: [Video 3a Entrega](https://youtu.be/0R641AyqAaY)

### 2ª Entrega: https://youtu.be/f7alUr-Og3A

### 1ª Entrega: https://www.youtube.com/watch?v=wUZRuor8o5I

> [!NOTE]
> És possible que les dates de les milestone no coincideixn amb les dates reals



