import socket
import json
from protocol import Quadro, enviar_pela_rede_ruidosa

# Definição de endereços e portas do roteador
HOST = '127.0.0.1'
PORT = 60000
MEU_MAC = "AA:BB:CC:DD:EE:FF"  

# Cores para logs
COR_REDE = '\033[94m'
COR_ERRO = '\033[91m'
COR_ARP = '\033[95m'  # Nova cor (Magenta) para os logs de inteligência do Switch
RESET = '\033[0m'

# Tabela de roteamento estática (VIP -> (IP, Porta))
TABELA_ROTEAMENTO = {
    "CLIENTE_BRUNO": ("127.0.0.1", 50001),
    "SERVIDOR_PRIME": ("127.0.0.1", 65432)
}

# Tabela ARP para aprendizado dinâmico de VIPs e seus respectivos MACs (VIP -> MAC)
TABELA_ARP = {}

# Definição da função principal do roteador, que recebe quadros, aprende VIPs/MACs e encaminha os pacotes
def iniciar_roteador():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind((HOST, PORT))
        print(f"{COR_REDE}[ROTEADOR/SWITCH] Ligado (MAC: {MEU_MAC}){RESET}")
        print(f"{COR_ARP}[ARP] Tabela MAC limpa. Aguardando tráfego para aprender...{RESET}")

        while True:
            data, addr = s.recvfrom(2048)
            
            quadro_dict, is_valid = Quadro.deserializar(data)
            
            if not is_valid:
                print(f"{COR_ERRO}   [ENLACE] Corrupção física! Descartando.{RESET}")
                continue 
            
            pacote_dict = quadro_dict.get('data', {})
            
            # Lógica para atualizar a tabela ARP com o VIP e MAC de origem do pacote recebido
            src_mac = quadro_dict.get('src_mac')
            src_vip = pacote_dict.get('src_vip')

            if src_vip and src_mac:
                # Se o IP não estiver na tabela, ou se o MAC mudou, ele aprende/atualiza
                if TABELA_ARP.get(src_vip) != src_mac:
                    TABELA_ARP[src_vip] = src_mac
                    print(f"{COR_ARP}[ARP] Aprendizado Dinâmico! VIP '{src_vip}' pertence ao MAC '{src_mac}'{RESET}")
            
            ttl_atual = pacote_dict.get('ttl', 0)
            if ttl_atual <= 0:
                continue
                
            # Lógica de decremento do TTL
            pacote_dict['ttl'] = ttl_atual - 1
            destino_vip = pacote_dict.get('dst_vip')
            
            if destino_vip in TABELA_ROTEAMENTO:
                ip_porta_destino = TABELA_ROTEAMENTO[destino_vip]
                
                # Se ele ainda não souber o MAC de destino, faz o Broadcast
                mac_destino = TABELA_ARP.get(destino_vip, "FF:FF:FF:FF:FF:FF")
                
                if mac_destino == "FF:FF:FF:FF:FF:FF":
                    print(f"{COR_ARP}[ARP] Destino '{destino_vip}' ainda desconhecido. Fazendo Broadcast!{RESET}")
                
                print(f"{COR_REDE}[ROTEADOR] Encaminhando pacote para {destino_vip} (TTL: {pacote_dict['ttl']}){RESET}")
                
                # Encapsula o pacote em um novo quadro e envia
                novo_quadro = Quadro(src_mac=MEU_MAC, dst_mac=mac_destino, pacote_dict=pacote_dict)
                enviar_pela_rede_ruidosa(s, novo_quadro.serializar(), ip_porta_destino)
            else:
                print(f"{COR_ERRO}[REDE] Destino {destino_vip} desconhecido!{RESET}")

if __name__ == "__main__":
    iniciar_roteador()