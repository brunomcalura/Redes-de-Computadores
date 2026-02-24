import socket
from aplicacao import MensagemApp
from protocolo import Segmento, Pacote, Quadro, enviar_pela_rede_ruidosa

HOST, PORT = '127.0.0.1', 65432
MEU_VIP = "SERVIDOR_PRIME"
MEU_MAC = "99:88:77:66:55:44"

ROUTER_IP, ROUTER_PORT = '127.0.0.1', 60000
ROUTER_MAC = "AA:BB:CC:DD:EE:FF"

COR_APP = '\033[92m'
COR_AMARELA = '\033[93m'
COR_TRANSP = '\033[96m'
COR_ERRO = '\033[91m'
RESET = '\033[0m'

def iniciar_servidor():
    expected_seq_num = 0

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind((HOST, PORT))
        print(f"Servidor escutando em {HOST}:{PORT} (VIP: {MEU_VIP} | MAC: {MEU_MAC})")

        while True:
            data, addr = s.recvfrom(2048)
            
            # ENLACE: Verificação física
            quadro_dict, is_valid = Quadro.deserializar(data)
            
            if not is_valid:
                print(f"{COR_ERRO}   [ENLACE] Placa de rede detectou CRC inválido! Quadro descartado.{RESET}")
                continue # Como hardware real, apenas ignora o lixo elétrico

            pacote_recebido_dict = quadro_dict.get('data', {})
            vip_origem = pacote_recebido_dict.get('src_vip')
            segmento_recebido = pacote_recebido_dict.get('data', {})
            
            if segmento_recebido.get('is_ack'): continue

            seq_recebido = segmento_recebido.get('seq_num')
            payload_json = segmento_recebido.get('payload')

            if seq_recebido == expected_seq_num:
                print(f"{COR_TRANSP}   [TRANSPORTE] Segmento {seq_recebido} íntegro.{RESET}")
                
                msg_obj = MensagemApp.from_json(payload_json)
                print(f"{COR_APP}[APLICAÇÃO] {msg_obj.sender} disse: {msg_obj.message}{RESET}")
                
                # Prepara o ACK subindo pelas camadas
                ack_segmento = Segmento(seq_num=expected_seq_num, is_ack=True, payload="")
                pacote_ack = Pacote(src_vip=MEU_VIP, dst_vip=vip_origem, ttl=5, segmento_dict=ack_segmento.to_dict())
                quadro_ack = Quadro(src_mac=MEU_MAC, dst_mac=ROUTER_MAC, pacote_dict=pacote_ack.to_dict())
                
                print(f"{COR_TRANSP}   [TRANSPORTE] Enviando ACK {expected_seq_num}...{RESET}")
                enviar_pela_rede_ruidosa(s, quadro_ack.serializar(), (ROUTER_IP, ROUTER_PORT))

                expected_seq_num = 1 - expected_seq_num
            else:
                print(f"{COR_AMARELA}   [TRANSPORTE] Duplicata do segmento {seq_recebido}. Reenviando ACK...{RESET}")
                ack_segmento = Segmento(seq_num=seq_recebido, is_ack=True, payload="")
                pacote_ack = Pacote(src_vip=MEU_VIP, dst_vip=vip_origem, ttl=5, segmento_dict=ack_segmento.to_dict())
                quadro_ack = Quadro(src_mac=MEU_MAC, dst_mac=ROUTER_MAC, pacote_dict=pacote_ack.to_dict())
                
                enviar_pela_rede_ruidosa(s, quadro_ack.serializar(), (ROUTER_IP, ROUTER_PORT))

if __name__ == "__main__":
    iniciar_servidor()