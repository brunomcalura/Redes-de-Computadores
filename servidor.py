import socket
from aplicacao import MensagemApp
from protocolo import Segmento, Pacote, Quadro, enviar_pela_rede_ruidosa

# Definição de endereços e portas do servidor
HOST, PORT = '127.0.0.1', 65432
MEU_VIP = "SERVIDOR_PRIME" # VIP do Servidor, usado para endereçamento lógico na camada de rede
MEU_MAC = "99:88:77:66:55:44" # MAC do Servidor, usado para endereçamento físico na camada de enlace

# Definição de endereços do roteador para envio dos ACKs
ROUTER_IP, ROUTER_PORT = '127.0.0.1', 60000
ROUTER_MAC = "AA:BB:CC:DD:EE:FF" # MAC do Roteador, usado para endereçamento físico na camada de enlace ao enviar ACKs de volta para o cliente via roteador

# Definição de cores para logs
COR_APP = '\033[92m'
COR_AMARELA = '\033[93m'
COR_TRANSP = '\033[96m'
COR_ERRO = '\033[91m'
RESET = '\033[0m'

def iniciar_servidor():
    # Número de sequência esperado para o próximo segmento
    expected_seq_num = 0

    # Inicia o socket UDP para receber mensagens dos clientes
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind((HOST, PORT))
        print(f"Servidor escutando em {HOST}:{PORT} (VIP: {MEU_VIP} | MAC: {MEU_MAC})")

        # Loop principal para receber mensagens dos clientes
        while True:
            data, addr = s.recvfrom(2048) # Fica esperando até chegar um dado
            
            # Verifica o quadro recebido e extrai o pacote (desencapsulamento da camada de enlace)
            quadro_dict, is_valid = Quadro.deserializar(data)
            
            # Se o quadro for inválido (CRC incorreto), simula a detecção de erro pela placa de rede e descarta o quadro
            if not is_valid:
                print(f"{COR_ERRO}   [ENLACE] Placa de rede detectou CRC inválido! Quadro descartado.{RESET}")
                continue # Como hardware real, apenas ignora o lixo elétrico

            # Verifica o pacote recebido e extrai o segmento (desencapsulamento da camada de rede)
            pacote_recebido_dict = quadro_dict.get('data', {})
            # Verifica o VIP de origem
            vip_origem = pacote_recebido_dict.get('src_vip')
            # Verifica o segmento recebido e extrai a mensagem da aplicação (desencapsulamento da camada de transporte)
            segmento_recebido = pacote_recebido_dict.get('data', {})
            
            # Se for um ACK, apenas processa o ACK e continua esperando por dados
            if segmento_recebido.get('is_ack'): 
                continue
            
            # Acessa o número de sequência e o payload (JSON da aplicação) do segmento recebido
            seq_recebido = segmento_recebido.get('seq_num')
            payload_json = segmento_recebido.get('payload')

            # Verifica se o número de sequência é o esperado (Stop-and-Wait)
            if seq_recebido == expected_seq_num:
                print(f"{COR_TRANSP}   [TRANSPORTE] Segmento {seq_recebido} íntegro.{RESET}")
                
                # Processa a mensagem da aplicação (desencapsulamento da camada de aplicação)
                msg_obj = MensagemApp.from_json(payload_json)
                print(f"{COR_APP}[APLICAÇÃO] {msg_obj.sender} disse: {msg_obj.message}{RESET}")
                
                # Prepara o ACK subindo pelas camadas
                ack_segmento = Segmento(seq_num=expected_seq_num, is_ack=True, payload="")
                pacote_ack = Pacote(src_vip=MEU_VIP, dst_vip=vip_origem, ttl=5, segmento_dict=ack_segmento.to_dict())
                quadro_ack = Quadro(src_mac=MEU_MAC, dst_mac=ROUTER_MAC, pacote_dict=pacote_ack.to_dict())
                
                # Função para enviar o ACK pela rede ruidosa
                print(f"{COR_TRANSP}   [TRANSPORTE] Enviando ACK {expected_seq_num}...{RESET}")
                enviar_pela_rede_ruidosa(s, quadro_ack.serializar(), (ROUTER_IP, ROUTER_PORT))

                # Alterna o número de sequência esperado para o próximo segmento
                expected_seq_num = 1 - expected_seq_num
            
            # Se o número de sequência não for o esperado, é uma repetição do segmento anterior (mensagem do cliente, que já foi recebida, recebida novamente), então reenvia o ACK do último segmento recebido corretamente
            else:
                print(f"{COR_AMARELA}   [TRANSPORTE] Duplicata do segmento {seq_recebido}. Reenviando ACK...{RESET}")
                ack_segmento = Segmento(seq_num=seq_recebido, is_ack=True, payload="")
                pacote_ack = Pacote(src_vip=MEU_VIP, dst_vip=vip_origem, ttl=5, segmento_dict=ack_segmento.to_dict())
                quadro_ack = Quadro(src_mac=MEU_MAC, dst_mac=ROUTER_MAC, pacote_dict=pacote_ack.to_dict())
                
                # Função para reenviar o ACK pela rede ruidosa
                enviar_pela_rede_ruidosa(s, quadro_ack.serializar(), (ROUTER_IP, ROUTER_PORT))

if __name__ == "__main__":
    iniciar_servidor()