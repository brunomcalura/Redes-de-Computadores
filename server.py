import socket
import base64
from aplicacao import MensagemApp
from protocol import Segmento, Pacote, Quadro, enviar_pela_rede_ruidosa

HOST, PORT = '127.0.0.1', 65432
MEU_VIP = "SERVIDOR_PRIME"
MEU_MAC = "99:88:77:66:55:44"
ROUTER_IP, ROUTER_PORT = '127.0.0.1', 60000
ROUTER_MAC = "AA:BB:CC:DD:EE:FF"

COR_APP = '\033[92m'
COR_TRANSP = '\033[96m'
COR_ERRO = '\033[91m'
COR_ARQUIVO = '\033[95m' # Magenta para os arquivos chegando
RESET = '\033[0m'

def iniciar_servidor():
    expected_seq_num = 0
    buffer_arquivos = {} # Dicionário para armazenar fragmentos de arquivos em trânsito

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind((HOST, PORT))
        print(f"Servidor escutando em {HOST}:{PORT} (VIP: {MEU_VIP})")

        while True:
            data, addr = s.recvfrom(2048)
            quadro_dict, is_valid = Quadro.deserializar(data)
            if not is_valid: continue

            pacote_recebido = quadro_dict.get('data', {})
            vip_origem = pacote_recebido.get('src_vip')
            segmento_recebido = pacote_recebido.get('data', {})
            
            if segmento_recebido.get('is_ack'): continue

            seq_recebido = segmento_recebido.get('seq_num')
            payload_json = segmento_recebido.get('payload')

            if seq_recebido == expected_seq_num:
                msg_obj = MensagemApp.from_json(payload_json)
                
                # Tratamento de Chat Normal
                if msg_obj.type == "chat":
                    print(f"{COR_APP}[APLICAÇÃO] {msg_obj.sender} disse: {msg_obj.message}{RESET}")
                
                # Tratamento de Transferência de Arquivo
                elif msg_obj.type == "file":
                    print(f"{COR_ARQUIVO}[APLICAÇÃO] Recebido fragmento {msg_obj.part}/{msg_obj.total_parts} de '{msg_obj.filename}'{RESET}")
                    
                    if msg_obj.filename not in buffer_arquivos:
                        buffer_arquivos[msg_obj.filename] = {}
                        
                    buffer_arquivos[msg_obj.filename][msg_obj.part] = msg_obj.file_data
                    
                    # Verifica se todas as partes chegaram
                    if len(buffer_arquivos[msg_obj.filename]) == msg_obj.total_parts:
                        print(f"{COR_ARQUIVO}[APLICAÇÃO] Remontando arquivo '{msg_obj.filename}'...{RESET}")
                        # Junta as strings Base64 na ordem correta
                        b64_completo = "".join([buffer_arquivos[msg_obj.filename][i] for i in range(1, msg_obj.total_parts + 1)])
                        
                        # Salva o arquivo em disco
                        nome_salvo = "recebido_" + msg_obj.filename
                        with open(nome_salvo, "wb") as f:
                            f.write(base64.b64decode(b64_completo))
                        
                        print(f"{COR_APP}[APLICAÇÃO] Sucesso! Arquivo salvo como '{nome_salvo}'{RESET}")
                        del buffer_arquivos[msg_obj.filename] # Limpa o buffer
                
                # Confirmação (ACK)
                ack_segmento = Segmento(seq_num=expected_seq_num, is_ack=True, payload="")
                pacote_ack = Pacote(src_vip=MEU_VIP, dst_vip=vip_origem, ttl=5, segmento_dict=ack_segmento.to_dict())
                quadro_ack = Quadro(src_mac=MEU_MAC, dst_mac=ROUTER_MAC, pacote_dict=pacote_ack.to_dict())
                enviar_pela_rede_ruidosa(s, quadro_ack.serializar(), (ROUTER_IP, ROUTER_PORT))

                expected_seq_num = 1 - expected_seq_num
            else:
                # Duplicata (Reenvia o ACK para calar o emissor)
                ack_segmento = Segmento(seq_num=seq_recebido, is_ack=True, payload="")
                pacote_ack = Pacote(src_vip=MEU_VIP, dst_vip=vip_origem, ttl=5, segmento_dict=ack_segmento.to_dict())
                quadro_ack = Quadro(src_mac=MEU_MAC, dst_mac=ROUTER_MAC, pacote_dict=pacote_ack.to_dict())
                enviar_pela_rede_ruidosa(s, quadro_ack.serializar(), (ROUTER_IP, ROUTER_PORT))

if __name__ == "__main__":
    iniciar_servidor()