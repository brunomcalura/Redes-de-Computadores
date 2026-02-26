# Projeto Confiable UDP

Este projeto consiste na implementação de uma pilha de protocolos de rede customizada, desenvolvida sobre o protocolo UDP, para desmistificar o funcionamento das camadas TCP-IP. O objetivo é garantir a entrega de mensagens em um canal de comunicação **propositalmente** instável, simulando perdas e corrupção de dados.

## 🚀 Novidades da Versão

As seguintes funcionalidades foram integradas recentemente ao projeto:

* **Aprendizado Dinâmico de Endereços (ARP/Switch)**: O roteador agora atua como um Switch inteligente, mapeando dinamicamente a relação entre **VIP (Virtual IP)** e **MAC** conforme os pacotes trafegam.
* **Mecanismo de Broadcast**: Caso o destino seja desconhecido, o roteador utiliza o endereço `FF:FF:FF:FF:FF:FF` para localizar o destinatário na rede.
* **Fragmentação e Reconstituição de Arquivos**: Suporte para envio de arquivos de qualquer tamanho através de fragmentação em Base64, com buffer de remontagem no servidor para garantir a integridade do arquivo final.

## Arquitetura do Sistema

O sistema segue uma abordagem **Top-Down** com encapsulamento rígido:

**Quadro (Enlace)** → **Pacote (Rede)** → **Segmento (Transporte)** → **JSON (Aplicação)**

### Detalhamento das Camadas:

* **Aplicação (`aplicacao.py`)**: Padroniza mensagens e gerencia metadados de fragmentação (partes, total de fragmentos e timestamps).
* **Transporte (`protocol.py` / `client.py`)**: Implementa o protocolo **Stop-and-Wait**. Garante a entrega através de números de sequência (0/1), ACKs e retransmissões automáticas em caso de timeout.
* **Rede (`router.py`)**: Gerencia o endereçamento lógico via VIP, decremento de **TTL (Time To Live)** e agora conta com uma **Tabela ARP** para aprendizado dinâmico.
* **Enlace (`protocol.py`)**: Responsável pelo endereçamento físico (MAC) e verificação de integridade via **CRC32 (FCS)**.
* **Física (`protocol.py`)**: Simulador de canal ruidoso que aplica 20% de probabilidade de perda e 20% de corrupção de bits.

## Como Executar

1. **Inicie o Roteador/Switch:** `python router.py`
2. **Inicie o Servidor:** `python server.py`
3. **Inicie o Cliente:** `python client.py`

### Comandos do Cliente:

* Para mensagens de texto: Basta digitar o texto e pressionar Enter.
* Para enviar arquivos: Use o comando `/arquivo nome_do_arquivo.ext`.

## 📊 Monitoramento de Logs

* 🟡 **Amarelo**: Timeouts e retransmissões (Transporte).
* 🔴 **Vermelho**: Erros de CRC ou destino desconhecido.
* 🟣 **Magenta**: Inteligência ARP (Aprendizado de MAC) e progresso de transferência de arquivos.
* 🟢 **Verde**: Entrega final na camada de aplicação.

## 👤 Autores

* **João Pedro de Castro**
* **Bruno Moreira Calura**