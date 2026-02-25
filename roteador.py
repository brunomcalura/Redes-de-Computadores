import socket
import json
from protocolo import Quadro, enviar_pela_rede_ruidosa

# Definição de endereços e portas do roteador
HOST = '127.0.0.1'
PORT = 60000
MEU_MAC = "AA:BB:CC:DD:EE:FF"  # MAC do Roteador

# Definição de cores para logs
COR_REDE = '\033[94m'
COR_ERRO = '\033[91m'
RESET = '\033[0m'

# Simulando uma tabela de roteamento (VIP para IP e Porta)
TABELA_ROTEAMENTO = {
    "CLIENTE_BRUNO": ("127.0.0.1", 50001),
    "SERVIDOR_PRIME": ("127.0.0.1", 65432)
}

# Simulando uma tabela ARP (Mapeamento de VIP para MAC)
TABELA_ARP = {
    "CLIENTE_BRUNO": "00:11:22:33:44:55",
    "SERVIDOR_PRIME": "99:88:77:66:55:44"
}

# Função para iniciar o roteador
def iniciar_roteador():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind((HOST, PORT))
        print(f"{COR_REDE}[ROTEADOR/SWITCH] Ligado (MAC: {MEU_MAC}){RESET}")

        while True:
            data, addr = s.recvfrom(2048)
            
            # Deserializa o quadro recebido e verifica a integridade usando o CRC32
            quadro_dict, is_valid = Quadro.deserializar(data)
            
            if not is_valid:
                print(f"{COR_ERRO}[ENLACE] Roteador detectou corrupção (Erro de CRC)! Descartando quadro fisicamente.{RESET}")
                continue # Descarta silenciosamente (simulando hardware)
            
            # Desencapsula o pacote da camada de rede
            pacote_dict = quadro_dict.get('data', {})
            
            # Verifica o TTL do pacote para evitar loops infinitos
            ttl_atual = pacote_dict.get('ttl', 0)
            if ttl_atual <= 0:
                print(f"{COR_ERRO}[REDE] Pacote descartado! TTL expirou.{RESET}")
                continue
                
            # Decrementa o TTL antes de encaminhar
            pacote_dict['ttl'] = ttl_atual - 1
            destino_vip = pacote_dict.get('dst_vip')
            
            # Verifica se o destino VIP está na tabela de roteamento
            if destino_vip in TABELA_ROTEAMENTO:
                ip_porta_destino = TABELA_ROTEAMENTO[destino_vip]
                mac_destino = TABELA_ARP[destino_vip]
                
                print(f"{COR_REDE}[ROTEADOR] Encaminhando pacote para {destino_vip} (TTL: {pacote_dict['ttl']}){RESET}")
                
                # Re-encapsula o pacote em um novo Quadro de Enlace para o próximo salto
                novo_quadro = Quadro(src_mac=MEU_MAC, dst_mac=mac_destino, pacote_dict=pacote_dict)
                quadro_bytes = novo_quadro.serializar() # Aqui o CRC32 é calculado automaticamente
                
                enviar_pela_rede_ruidosa(s, quadro_bytes, ip_porta_destino)
            else:
                print(f"{COR_ERRO}[REDE] Destino {destino_vip} desconhecido!{RESET}")

if __name__ == "__main__":
    iniciar_roteador()