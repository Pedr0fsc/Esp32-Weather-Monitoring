"""
Biblioteca Adafruit IO para MicroPython
Compatível com ESP32/ESP8266
Autor: Baseado em exemplos da comunidade MicroPython
"""

import network
import time
import gc
from umqtt.robust import MQTTClient

class AdafruitIO_MQTT:
    """Cliente MQTT para Adafruit IO"""
    
    def __init__(self, username, key, mqtt_server="io.adafruit.com", port=1883):
        """
        Inicializa cliente Adafruit IO
        
        Args:
            username (str): Nome de usuário do Adafruit IO
            key (str): Chave AIO do Adafruit IO
            mqtt_server (str): Servidor MQTT (padrão: io.adafruit.com)
            port (int): Porta MQTT (padrão: 1883)
        """
        self.username = username
        self.key = key
        self.mqtt_server = mqtt_server
        self.port = port
        
        # ID único do cliente baseado no MAC
        sta_if = network.WLAN(network.STA_IF)
        mac = sta_if.config('mac')
        self.client_id = "micropython_" + ''.join(['{:02x}'.format(b) for b in mac])
        
        # Cliente MQTT
        self.client = None
        self.connected = False
        
        # Callbacks
        self.on_connect_callback = None
        self.on_disconnect_callback = None
        self.on_message_callback = None
        
        print(f"Adafruit IO Client ID: {self.client_id}")
    
    async def connect(self, wifi_ssid=None, wifi_password=None):
        """
        Conecta ao WiFi (se necessário) e ao Adafruit IO
        
        Args:
            wifi_ssid (str): SSID do WiFi (opcional se já conectado)
            wifi_password (str): Senha do WiFi (opcional se já conectado)
        
        Returns:
            bool: True se conectou com sucesso
        """
        try:
            # Verifica conexão WiFi
            if wifi_ssid and wifi_password:
                if not self._connect_wifi(wifi_ssid, wifi_password):
                    return False
            elif not self._check_wifi():
                print("WiFi não conectado e credenciais não fornecidas")
                return False
            
            # Configura cliente MQTT
            self.client = MQTTClient(
                client_id=self.client_id,
                server=self.mqtt_server,
                port=self.port,
                user=self.username,
                password=self.key,
                keepalive=60
            )
            
            # Define callback para mensagens
            self.client.set_callback(self._on_message)
            
            # Conecta ao MQTT
            print(f"Conectando ao Adafruit IO ({self.mqtt_server})...")
            self.client.connect()
            
            self.connected = True
            print("✓ Conectado ao Adafruit IO!")
            
            if self.on_connect_callback:
                self.on_connect_callback()
            
            return True
            
        except Exception as e:
            print(f"Erro ao conectar ao Adafruit IO: {e}")
            self.connected = False
            return False
    
    def _connect_wifi(self, ssid, password):
        """Conecta ao WiFi"""
        try:
            sta_if = network.WLAN(network.STA_IF)
            if not sta_if.isconnected():
                print(f"Conectando ao WiFi '{ssid}'...")
                sta_if.active(True)
                sta_if.connect(ssid, password)
                
                # Aguarda conexão (timeout 15s)
                timeout = 15
                while not sta_if.isconnected() and timeout > 0:
                    time.sleep(1)
                    timeout -= 1
                    print(".", end="")
                
                if sta_if.isconnected():
                    print(f"\n✓ WiFi conectado: {sta_if.ifconfig()}")
                    return True
                else:
                    print("\n✗ Falha na conexão WiFi")
                    return False
            else:
                print(f"✓ WiFi já conectado: {sta_if.ifconfig()}")
                return True
                
        except Exception as e:
            print(f"Erro no WiFi: {e}")
            return False
    
    def _check_wifi(self):
        """Verifica se WiFi está conectado"""
        try:
            sta_if = network.WLAN(network.STA_IF)
            return sta_if.isconnected()
        except:
            return False
    
    def _on_message(self, topic, msg):
        """Callback interno para mensagens recebidas"""
        try:
            topic_str = topic.decode('utf-8')
            msg_str = msg.decode('utf-8')
            
            print(f"Mensagem recebida: {topic_str} = {msg_str}")
            
            if self.on_message_callback:
                self.on_message_callback(topic_str, msg_str)
                
        except Exception as e:
            print(f"Erro ao processar mensagem: {e}")
    
    async def publish(self, feed, value):
        """
        Publica valor em um feed
        
        Args:
            feed (str): Nome do feed
            value: Valor para publicar
        
        Returns:
            bool: True se publicou com sucesso
        """
        if not self.connected or not self.client:
            print("Cliente não conectado")
            return False
        
        try:
            topic = f"{self.username}/feeds/{feed}"
            value_str = str(value)
            
            print(f"Publicando: {topic} = {value_str}")
            self.client.publish(topic, value_str)
            
            return True
            
        except Exception as e:
            print(f"Erro ao publicar {feed}: {e}")
            
            # Tenta reconectar se perdeu conexão
            try:
                await self.reconnect()
            except:
                pass
            
            return False
    
    def subscribe(self, feed):
        """
        Inscreve-se em um feed
        
        Args:
            feed (str): Nome do feed
        
        Returns:
            bool: True se inscreveu com sucesso
        """
        if not self.connected or not self.client:
            print("Cliente não conectado")
            return False
        
        try:
            topic = f"{self.username}/feeds/{feed}"
            print(f"Inscrevendo em: {topic}")
            self.client.subscribe(topic)
            return True
            
        except Exception as e:
            print(f"Erro ao inscrever em {feed}: {e}")
            return False
    
    def check_messages(self):
        """
        Verifica mensagens recebidas (não-bloqueante)
        Deve ser chamado regularmente no loop principal
        """
        if not self.connected or not self.client:
            return
        
        try:
            self.client.check_msg()
        except Exception as e:
            print(f"Erro ao verificar mensagens: {e}")
    
    def wait_for_message(self, timeout=1):
        """
        Aguarda por mensagem (bloqueante)
        
        Args:
            timeout (int): Timeout em segundos
        """
        if not self.connected or not self.client:
            return
        
        try:
            self.client.wait_msg()
        except Exception as e:
            print(f"Erro ao aguardar mensagem: {e}")
    
    async def reconnect(self):
        """Tenta reconectar ao MQTT"""
        try:
            print("Reconectando ao Adafruit IO...")
            
            if self.client:
                try:
                    self.client.disconnect()
                except:
                    pass
            
            # Recria cliente
            self.client = MQTTClient(
                client_id=self.client_id,
                server=self.mqtt_server,
                port=self.port,
                user=self.username,
                password=self.key,
                keepalive=60
            )
            
            self.client.set_callback(self._on_message)
            self.client.connect()
            
            self.connected = True
            print("✓ Reconectado ao Adafruit IO!")
            
            return True
            
        except Exception as e:
            print(f"Erro na reconexão: {e}")
            self.connected = False
            return False
    
    def disconnect(self):
        """Desconecta do MQTT"""
        try:
            if self.client and self.connected:
                self.client.disconnect()
                print("Desconectado do Adafruit IO")
            
            self.connected = False
            
            if self.on_disconnect_callback:
                self.on_disconnect_callback()
                
        except Exception as e:
            print(f"Erro ao desconectar: {e}")
    
    def is_connected(self):
        """Verifica se está conectado"""
        return self.connected and self.client is not None
    
    def set_on_connect_callback(self, callback):
        """Define callback para conexão estabelecida"""
        self.on_connect_callback = callback
    
    def set_on_disconnect_callback(self, callback):
        """Define callback para desconexão"""
        self.on_disconnect_callback = callback
    
    def set_on_message_callback(self, callback):
        """Define callback para mensagens recebidas"""
        self.on_message_callback = callback
    
    def get_client_id(self):
        """Retorna ID único do cliente"""
        return self.client_id
    
    def get_status(self):
        """Retorna status detalhado da conexão"""
        sta_if = network.WLAN(network.STA_IF)
        
        return {
            'wifi_connected': sta_if.isconnected(),
            'wifi_config': sta_if.ifconfig() if sta_if.isconnected() else None,
            'mqtt_connected': self.connected,
            'client_id': self.client_id,
            'server': self.mqtt_server,
            'username': self.username,
            'free_memory': gc.mem_free()
        }

# Função auxiliar para uso simplificado
def create_client(username, key, mqtt_server="io.adafruit.com"):
    """
    Cria cliente Adafruit IO de forma simplificada
    
    Args:
        username (str): Nome de usuário do Adafruit IO
        key (str): Chave AIO
        mqtt_server (str): Servidor MQTT
    
    Returns:
        AdafruitIO_MQTT: Cliente configurado
    """
    return AdafruitIO_MQTT(username, key, mqtt_server)

# Exemplo de uso
if __name__ == "__main__":
    import uasyncio as asyncio
    
    # Configurações - SUBSTITUA COM SUAS INFORMAÇÕES
    AIO_USERNAME = "seu_usuario"
    AIO_KEY = "sua_chave_aio"
    WIFI_SSID = "sua_rede_wifi"
    WIFI_PASSWORD = "sua_senha_wifi"
    
    async def exemplo_uso():
        # Cria cliente
        aio = create_client(AIO_USERNAME, AIO_KEY)
        
        # Conecta
        if await aio.connect(WIFI_SSID, WIFI_PASSWORD):
            
            # Publica alguns dados de teste
            for i in range(5):
                await aio.publish("temperatura", f"{20 + i}")
                await aio.publish("umidade", f"{50 + i * 5}")
                
                print(f"Dados enviados: ciclo {i + 1}")
                await asyncio.sleep(5)
            
            # Desconecta
            aio.disconnect()
        
        else:
            print("Falha na conexão")
    
    # Descomente para testar
    # asyncio.run(exemplo_uso())