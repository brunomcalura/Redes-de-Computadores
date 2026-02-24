import socket
import time
from aplicacao import MensagemApp
from protocolo import Segmento, Pacote, Quadro, enviar_pela_rede_ruidosa

MEU_IP, MINHA_PORTA = '127.0.0.1', 50001
MEU_VIP = "CLIENTE_BRUNO"
MEU_MAC = "00:11:22:33:44:55"

ROUTER_IP, ROUTER_PORT = '127.0.0.1', 60000
ROUTER_MAC = "AA:BB:CC:DD:EE:FF"
DEST_VIP = "SERVIDOR_PRIME"

TIMEOUT = 2.0
COR_AMARELA = '\033[93m'
COR_ERRO = '\033[91m'
RESET = '\033[0m'

def iniciar_cliente():
    seq_num = 0

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind((MEU_IP, MINHA_PORTA))
        s.settimeout(TIMEOUT)
        print(f"Cliente iniciado (VIP: {MEU_VIP} | MAC: {MEU_MAC})")
        
        while True:
            texto = input("> ")
            if texto.lower() == 'sair': break

            msg = MensagemApp(sender=MEU_VIP, message=texto)
            segmento = Segmento(seq_num=seq_num, is_ack=False, payload=msg.to_json())
            pacote = Pacote(src_vip=MEU_VIP, dst_vip=DEST_VIP, ttl=5, segmento_dict=segmento.to_dict())
            
            # ENLACE: Encapsula no Quadro e serializa (calcula CRC)
            quadro = Quadro(src_mac=MEU_MAC, dst_mac=ROUTER_MAC, pacote_dict=pacote.to_dict())
            quadro_bytes = quadro.serializar()

            ack_recebido = False
            while not ack_recebido:
                enviar_pela_rede_ruidosa(s, quadro_bytes, (ROUTER_IP, ROUTER_PORT))

                try:
                    data, addr = s.recvfrom(2048)
                    
                    # ENLACE: Verificação de hardware simulada
                    quadro_dict, is_valid = Quadro.deserializar(data)
                    
                    if not is_valid:
                        print(f"{COR_ERRO}   [ENLACE] Placa de rede detectou CRC inválido no ACK! Descartando.{RESET}")
                        continue # Deixa dar o timeout natural
                        
                    pacote_recebido_dict = quadro_dict.get('data', {})
                    segmento_recebido = pacote_recebido_dict.get('data', {})

                    if segmento_recebido.get('is_ack') and segmento_recebido.get('seq_num') == seq_num:
                        print(f"   [TRANSPORTE] ACK {seq_num} recebido com sucesso!")
                        ack_recebido = True
                        seq_num = 1 - seq_num
                    else:
                        print(f"{COR_AMARELA}   [TRANSPORTE] ACK incorreto recebido.{RESET}")

                except socket.timeout:
                    print(f"{COR_AMARELA}   [TRANSPORTE] TIMEOUT! Retransmitindo pacote {seq_num}...{RESET}")
                except ConnectionResetError:
                    print(f"{COR_AMARELA}   [REDE] Roteador inalcançável. Retransmitindo...{RESET}")
                    time.sleep(1)

if __name__ == "__main__":
    iniciar_cliente()