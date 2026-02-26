import socket
import time
import base64
import os
import math
from aplicacao import MensagemApp
from protocol import Segmento, Pacote, Quadro, enviar_pela_rede_ruidosa

# Definição de endereços e portas do cliente
MEU_IP, MINHA_PORTA = '127.0.0.1', 50001
MEU_VIP = "CLIENTE_BRUNO"
MEU_MAC = "00:11:22:33:44:55"

# Definição de endereços do roteador para envio dos pacotes
ROUTER_IP, ROUTER_PORT = '127.0.0.1', 60000
ROUTER_MAC = "AA:BB:CC:DD:EE:FF"
DEST_VIP = "SERVIDOR_PRIME"

# Configurações de timeout e cores para logs
TIMEOUT = 2.0
COR_AMARELA = '\033[93m'
COR_ERRO = '\033[91m'
COR_TRANSP = '\033[96m'
COR_ARQUIVO = '\033[96m' # Ciano para arquivos
RESET = '\033[0m'

TAMANHO_FRAGMENTO = 500 # Quantidade de caracteres Base64 por pacote

def enviar_pacote_confiavel(s, payload_json, seq_num):
    """Encapsula e garante a entrega usando Stop-and-Wait"""
    segmento = Segmento(seq_num=seq_num, is_ack=False, payload=payload_json)
    pacote = Pacote(src_vip=MEU_VIP, dst_vip=DEST_VIP, ttl=5, segmento_dict=segmento.to_dict())
    quadro = Quadro(src_mac=MEU_MAC, dst_mac=ROUTER_MAC, pacote_dict=pacote.to_dict())
    quadro_bytes = quadro.serializar()

    # Loop de retransmissão até receber o ACK correto ou ocorrer timeout
    while True:
        enviar_pela_rede_ruidosa(s, quadro_bytes, (ROUTER_IP, ROUTER_PORT))
        try:
            data, _ = s.recvfrom(2048)
            quadro_dict, is_valid = Quadro.deserializar(data)
            
            if not is_valid: continue
            
            seg_rec = quadro_dict.get('data', {}).get('data', {})
            if seg_rec.get('is_ack') and seg_rec.get('seq_num') == seq_num:
                print(f"{COR_TRANSP}   [TRANSPORTE] ACK {seq_num} recebido!{RESET}")
                return 1 - seq_num # Retorna o próximo número de sequência
            
        except socket.timeout:
            print(f"{COR_AMARELA}   [TRANSPORTE] TIMEOUT! Retransmitindo pacote {seq_num}...{RESET}")
        except ConnectionResetError:
            print(f"{COR_AMARELA}   [REDE] Roteador inalcançável. Retransmitindo...{RESET}")
            time.sleep(1)

def iniciar_cliente():
    seq_num = 0 # Número de sequência inicial para o protocolo Stop-and-Wait

    # Inicia o socket UDP para enviar mensagens ao servidor
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind((MEU_IP, MINHA_PORTA))
        s.settimeout(TIMEOUT)
        print(f"Cliente iniciado (VIP: {MEU_VIP})")
        print("Digite uma mensagem, ou use '/arquivo nome.txt' para enviar arquivos.")
        
        # Loop principal para enviar mensagens ao servidor
        while True:
            texto = input("> ")
            if texto.lower() == 'sair': break

            if texto.startswith("/arquivo "):
                caminho_arquivo = texto.split(" ", 1)[1]
                try:
                    # Lê o arquivo e converte para texto Base64
                    with open(caminho_arquivo, "rb") as f:
                        b64_dados = base64.b64encode(f.read()).decode('utf-8')
                    
                    # Fragmenta em pedaços de 500 caracteres
                    total_parts = math.ceil(len(b64_dados) / TAMANHO_FRAGMENTO)
                    nome_arq = os.path.basename(caminho_arquivo)
                    print(f"{COR_ARQUIVO}[APLICAÇÃO] Iniciando envio de {nome_arq} em {total_parts} fragmentos...{RESET}")

                    # Envia fragmento por fragmento confiavelmente
                    for i in range(total_parts):
                        pedaco = b64_dados[i * TAMANHO_FRAGMENTO : (i + 1) * TAMANHO_FRAGMENTO]
                        msg = MensagemApp(sender=MEU_VIP, msg_type="file", filename=nome_arq, file_data=pedaco, part=i+1, total_parts=total_parts)
                        
                        print(f"{COR_ARQUIVO}[APLICAÇÃO] Enviando parte {i+1}/{total_parts}...{RESET}")
                        seq_num = enviar_pacote_confiavel(s, msg.to_json(), seq_num)
                        
                    print(f"{COR_ARQUIVO}[APLICAÇÃO] Arquivo {nome_arq} transferido com sucesso!{RESET}")
                except FileNotFoundError:
                    print(f"{COR_ERRO}Arquivo '{caminho_arquivo}' não encontrado.{RESET}")
            else:
                # Envio normal de Chat
                msg = MensagemApp(sender=MEU_VIP, message=texto)
                seq_num = enviar_pacote_confiavel(s, msg.to_json(), seq_num)

if __name__ == "__main__":
    iniciar_cliente()