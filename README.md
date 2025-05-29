# ESP32-Weather-Monitoring

&emsp;&emsp;The content below contains project documentation translated into English and Portuguese:

<details>
<summary>English</summary>

## Esp32 Weather Monitoring

&emsp;&emsp;A MicroPython aplication using the famous Esp32 as the microcontroller, the weather station consists into 2 sensors, BMP280 and DHT11, and a IPS 240x240 display. The project has visual display not only with the eletronic components, but also in your phone, with a webserver with auto-refresh for see real-time datas from the sensors.

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

&emsp;&emsp;To use your ESP32 with micropython you first need to upload the .bin file from firmware paste to your board using esptool.

&emsp;&emsp;First install esptool via terminal using the following command:
```bash
pip install esptool
```

&emsp;&emsp;Now you need to erase the flash memory from your ESP32 microcontroller, first you need to put your board on boot mode using the BOOT and EN/RST buttons:
* Hold the BOOT button.
* While holding the BOOT button, press and release the EN/RST button.
* Hold the BOOT for more 1 or 2 seconds and then release.

&emsp;&emsp;Now your board is in boot mode, you erase the flash memory using the command above:
```bash
python -m esptool --port (your COM port) erase_flash
```

&emsp;&emsp;When the flash memory got erased, use the following command to upload the micropython firmware from [Micropython Oficial Download Website](https://micropython.org/download/ESP32_GENERIC/) and download the latest version of firmware to your board:
```bash
python -m esptool --chip esp32 --port (your COM port) --baud 460800 write_flash -z 0x1000 C:\Users\your_user\the_path_you_download_the_firmware\the_file_name.bin
```

&emsp;&emsp;With your micropython firmware installed, it's time to start the project.


### Libraries

&emsp;&emsp;The Libraries folder contains all the libraries used in this project, to use then it's simple, open the folder on your IDE and open the terminal, use the upload command to send the files to your board and then you are ready to run the program code.
* Upload files to board:  
```bash
mpremote connect (your COM port) cp (library_file_name.py) :
```
* Upload files to board with `upload` command (Check package.json):  
```bash
mpremote connect (your COM port) upload (library_file_name.py) :
```

### Components Connection

&emsp;&emsp;The following tables contains all the Pin connections of the eletronic components:

#### DHT11

Sensor | Board
:--------- | :------
`+` | `VCC`
`OUT` | `D4`
`-` | `GND`

#### BMP280

Sensor | Board
:--------- | :------
`VCC` | `VCC`
`GND` | `GND`
`SCL` | `D22`
`SDA` | `D21`

#### DISPLAY IPS 240x240

Sensor | Board
:--------- | :------
`GND` | `GND`
`VCC` | `VCC`
`SCL` | `D18`
`SDA` | `D23`
`RES` | `D4`
`DC` | `D15`
`BLK` | `D5`
</details>


<details>
<summary>Portuguese</summary>

## Esp32 Estação Meteorológica

&emsp;&emsp;Uma aplicação MicroPython usando o famoso ESP32 como microcontrolador, a estação meteorológica consiste em 2 sensores, BMP280 e DHT11, e um display IPS 240x240. O projeto tem exibição visual não só nos componentes eletrônicos, mas também no seu celular, com um servidor web com auto-refresh para ver os dados dos sensores em tempo real.

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

&emsp;&emsp;Para usar seu ESP32 com MicroPython você precisa primeiro enviar o arquivo `.bin` do firmware para a placa usando o esptool.

&emsp;&emsp;Primeiro instale o esptool no terminal com o comando:  
```bash
pip install esptool
```

&emsp;&emsp;Agora é necessário apagar a memória flash do ESP32. Para isso, coloque a placa em modo boot usando os botões BOOT e EN/RST:  
* Segure o botão BOOT.  
* Enquanto segura o BOOT, pressione e solte o EN/RST.  
* Segure o BOOT por mais 1 ou 2 segundos e depois solte.

&emsp;&emsp;Com a placa em modo boot, apague a memória flash com:  
```bash
python -m esptool --port (seu COM) erase_flash
```

&emsp;&emsp;Depois que a memória foi apagada, envie o firmware MicroPython baixado no site oficial [Micropython Oficial Download Website](https://micropython.org/download/ESP32_GENERIC/):  
```bash
python -m esptool --chip esp32 --port (seu COM) --baud 460800 write_flash -z 0x1000 C:\Users\seu_usuario\caminho_do_firmware\nome_do_arquivo.bin
```

&emsp;&emsp;Com o firmware MicroPython instalado, você pode começar o projeto.

### Bibliotecas

&emsp;&emsp;A pasta Libraries contém todas as bibliotecas usadas neste projeto. Para usar, abra a pasta na sua IDE e no terminal envie os arquivos para a placa com o comando upload. Depois, é só rodar o código.

* Enviar arquivos para a placa:  
```bash
mpremote connect (seu COM) cp (nome_da_biblioteca.py) :
```
* Enviar arquivos para a placa com `upload` (veja package.json):  
```bash
mpremote connect (seu COM) upload (nome_da_biblioteca.py) :
```

### Conexão dos componentes

&emsp;&emsp;As tabelas abaixo mostram todas as conexões dos pinos dos componentes eletrônicos:

#### DHT11

| Sensor | Placa  |
|--------|--------|
| `+`    | `VCC`  |
| `OUT`  | `D4`   |
| `-`    | `GND`  |

#### BMP280

| Sensor | Placa  |
|--------|--------|
| `VCC`  | `VCC`  |
| `GND`  | `GND`  |
| `SCL`  | `D22`  |
| `SDA`  | `D21`  |

#### DISPLAY IPS 240x240

| Sensor | Placa  |
|--------|--------|
| `GND`  | `GND`  |
| `VCC`  | `VCC`  |
| `SCL`  | `D18`  |
| `SDA`  | `D23`  |
| `RES`  | `D4`   |
| `DC`   | `D15`  |
| `BLK`  | `D5`   |

</details>

    Thanks for reading! 😁
