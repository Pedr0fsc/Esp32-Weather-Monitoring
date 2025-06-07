# ESP32-Weather-Monitoring

  The content below contains project documentation translated into English and Portuguese:

<details>
<summary>English</summary>

## Esp32 Weather Monitoring

  A MicroPython application using the famous ESP32 as the microcontroller. The weather station consists of a DHT11 sensor, an LDR light sensor, a HW-028 rain sensor, and an IPS 240x240 display. The project has a visual display not only with the electronic components, but also on your phone, with a web server with auto-refresh to see real-time data from the sensors.

### Configuring `package.json`

```
{
  "name": "esp32-project",
  "version": "1.0.0",
  "scripts": {
    "run": "mpremote connect (your COM port) run file_name.py",
    "upload": "mpremote connect (your COM port) fs cp file_name.py :"
  }
}
```

### Essential Terminal Commands

* Connect to board / Enter REPL:  
```bash
mpremote connect (your COM port)
```
* Upload files to board:  
```bash
mpremote connect (your COM port) cp (file_name.py) :
```
* Upload files to board with `upload` command (Check package.json):  
```bash
mpremote connect (your COM port) upload (file_name.py) :
```
* Run files from IDE or from board (Check package.json):  
```bash
mpremote connect (your COM port) run (file_name.py)
```
* List files from the board:  
```bash
mpremote connect (your COM port) fs ls
```
* Delete files from the board:  
```bash
mpremote connect (your COM port) fs rm :(file_name.py)
```

### Firmware

  To use your ESP32 with MicroPython you first need to upload the `.bin` file from the firmware folder to your board using esptool.

  First, install esptool via terminal using the following command:
```bash
pip install esptool
```

  Now you need to erase the flash memory from your ESP32 microcontroller. First, put your board in boot mode using the BOOT and EN/RST buttons:
* Hold the BOOT button.
* While holding the BOOT button, press and release the EN/RST button.
* Hold the BOOT for 1 or 2 more seconds and then release.

  Now your board is in boot mode. Erase the flash memory using:
```bash
python -m esptool --port (your COM port) erase_flash
```

  When the flash memory is erased, use the following command to upload the MicroPython firmware from the [Micropython Official Download Website](https://micropython.org/download/ESP32_GENERIC/):
```bash
python -m esptool --chip esp32 --port (your COM port) --baud 460800 write_flash -z 0x1000 C:\Users\your_user\path_to_firmware\file_name.bin
```

  With your MicroPython firmware installed, it's time to start the project.

### Libraries

  The Libraries folder contains all the libraries used in this project. To use them, open the folder in your IDE and upload the files to the board using the upload command.

* Upload files to board:  
```bash
mpremote connect (your COM port) cp (library_file_name.py) :
```
* Upload files to board with `upload` command (Check package.json):  
```bash
mpremote connect (your COM port) upload (library_file_name.py) :
```

### Components Connection

  The following tables contain all the pin connections of the electronic components:

#### DHT11

| Sensor | Board |
|--------|-------|
| `+`    | `VCC` |
| `OUT`  | `D4`  |
| `-`    | `GND` |

#### LDR

| Sensor | Board |
|--------|-------|
|  `Analogic data`      |  `D32`     |

#### HW-028 Rain Sensor

| Sensor | Board |
|--------|-------|
|   `Analogic data`     |  `D34`     |

#### DISPLAY IPS 240x240

| Sensor | Board |
|--------|-------|
| `GND`  | `GND` |
| `VCC`  | `VCC` |
| `SCL`  | `D18` |
| `SDA`  | `D23` |
| `RES`  | `D4`  |
| `DC`   | `D15` |
| `BLK`  | `D5`  |

</details>


<details>
<summary>Portuguese</summary>

## Esp32 Estação Meteorológica

  Uma aplicação MicroPython usando o famoso ESP32 como microcontrolador. A estação meteorológica consiste em um sensor DHT11, um sensor de luminosidade LDR, um sensor de chuva HW-028 e um display IPS 240x240. O projeto tem exibição visual não só nos componentes eletrônicos, mas também no seu celular, com um servidor web com auto-refresh para ver os dados dos sensores em tempo real.

### Configurando o `package.json`
```
{
  "name": "esp32-project",
  "version": "1.0.0",
  "scripts": {
    "run": "mpremote connect (seu COM) run nome_do_arquivo.py",
    "upload": "mpremote connect (seu COM) fs cp nome_do_arquivo.py :"
  }
}
```

### Comandos essenciais no terminal

* Conectar à placa / Entrar no REPL:  
```bash
mpremote connect (seu COM)
```
* Enviar arquivos para a placa:  
```bash
mpremote connect (seu COM) cp (nome_do_arquivo.py) :
```
* Enviar arquivos para a placa com o comando `upload` (veja package.json):  
```bash
mpremote connect (seu COM) upload (nome_do_arquivo.py) :
```
* Executar arquivos pelo IDE ou pela placa (veja package.json):  
```bash
mpremote connect (seu COM) run (nome_do_arquivo.py)
```
* Listar arquivos da placa:  
```bash
mpremote connect (seu COM) fs ls
```
* Apagar arquivos da placa:  
```bash
mpremote connect (seu COM) fs rm :(nome_do_arquivo.py)
```

### Firmware

  Para usar seu ESP32 com MicroPython, você precisa primeiro enviar o arquivo `.bin` do firmware para a placa usando o esptool.

  Primeiro instale o esptool com o comando:  
```bash
pip install esptool
```

  Agora é necessário apagar a memória flash do ESP32. Coloque a placa em modo boot usando os botões BOOT e EN/RST:  
* Segure o botão BOOT.  
* Enquanto segura o BOOT, pressione e solte o EN/RST.  
* Segure o BOOT por mais 1 ou 2 segundos e depois solte.

  Com a placa em modo boot, apague a memória flash:  
```bash
python -m esptool --port (seu COM) erase_flash
```

  Depois que a memória for apagada, envie o firmware MicroPython baixado no site oficial [Micropython Oficial Download Website](https://micropython.org/download/ESP32_GENERIC/):  
```bash
python -m esptool --chip esp32 --port (seu COM) --baud 460800 write_flash -z 0x1000 C:\Users\seu_usuario\caminho_do_firmware\nome_do_arquivo.bin
```

  Com o firmware MicroPython instalado, você pode começar o projeto.

### Bibliotecas

  A pasta Libraries contém todas as bibliotecas usadas neste projeto. Para usá-las, abra a pasta na sua IDE e envie os arquivos para a placa com o comando upload.

* Enviar arquivos para a placa:  
```bash
mpremote connect (seu COM) cp (nome_da_biblioteca.py) :
```
* Enviar arquivos para a placa com `upload` (veja package.json):  
```bash
mpremote connect (seu COM) upload (nome_da_biblioteca.py) :
```

### Conexão dos componentes

  As tabelas abaixo mostram todas as conexões dos pinos dos componentes eletrônicos:

#### DHT11

| Sensor | Placa |
|--------|-------|
| `+`    | `VCC` |
| `OUT`  | `D4`  |
| `-`    | `GND` |

#### LDR

| Sensor | Placa |
|--------|-------|
|  `Dados analógicos`      |  `D32`     |

#### Sensor de Chuva HW-028

| Sensor | Placa |
|--------|-------|
|  `Dados analógicos`      |  `D34`     |

#### DISPLAY IPS 240x240

| Sensor | Placa |
|--------|-------|
| `GND`  | `GND` |
| `VCC`  | `VCC` |
| `SCL`  | `D18` |
| `SDA`  | `D23` |
| `RES`  | `D4`  |
| `DC`   | `D15` |
| `BLK`  | `D5`  |

</details>

Thanks for reading! 😁
