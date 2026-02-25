# Projeto Mini-NET 

Este projeto consiste na implementação de uma pilha de protocolos de rede customizada, desenvolvida sobre o protocolo UDP, para desmistificar o funcionamento das camadas OSI/TCP-IP. O objetivo é garantir a entrega de mensagens em um canal de comunicação **propositalmente** instável (com perda e corrupção de dados).

## Arquitetura do Sistema

O sistema segue uma abordagem **Top-Down** e respeita o encapsulamento rígido entre as camadas (uma camada N só se comunica com a camada N-1):

**Quadro (Enlace)** → **Pacote (Rede)** → **Segmento (Transporte)** → **JSON (Aplicação)**

### Camadas Implementadas:
* **Aplicação (`aplicacao.py`)**: Padronização de mensagens em formato JSON (campos: `type`, `sender`, `message`, `timestamp`).
* **Transporte (`protocol.py`)**: Implementação do protocolo **Stop-and-Wait** com números de sequência (0/1), ACKs e mecanismos de Timeout para garantir a confiabilidade.
* **Rede (`router.py`)**: Endereçamento lógico via **VIP (Virtual IP)**, controle de **TTL (Time To Live)** e roteamento estático.
* **Enlace (`protocol.py`)**: Endereçamento físico (MAC) e verificação de integridade via **CRC32**.
* **Física (`protocol.py`)**: Simulador de canal ruidoso com probabilidade de perda de pacotes e corrupção de bits.

## Requisitos Técnicos
* **Linguagem:** Python 3.8+
* **Bibliotecas:** Apenas bibliotecas padrão (`socket`, `json`, `zlib`, `random`, `threading`, etc.).
* **Socket:** Uso obrigatório de `SOCK_DGRAM` (UDP) para as fases de transporte, rede e enlace.

## Como Executar

Para rodar o projeto, você precisará de três terminais abertos simultaneamente. Siga a ordem de execução abaixo:

1.  **Inicie o Roteador:**
    ```bash
    python router.py
    ```

2.  **Inicie o Servidor:**
    ```bash
    python server.py
    ```

3.  **Inicie o Cliente:**
    ```bash
    python client.py
    ```

## Testando a Resiliência

O sistema foi projetado para lidar com falhas simuladas no arquivo `protocol.py`:
* **Probabilidade de Perda:** 20%
* **Probabilidade de Corrupção:** 20%

Você poderá observar no terminal os logs coloridos indicando:
* 🟡 **Amarelo**: Timeouts e retransmissões na camada de transporte.
* 🔴 **Vermelho**: Erros de CRC (corrupção) detectados na camada de enlace e pacotes descartados.
* 🔵 **Azul**: Encaminhamento de pacotes pelo roteador.
* 🟢 **Verde**: Mensagens entregues com sucesso na camada de aplicação.

## 👤 Autor
* **João Pedro de Castro**
* **Bruno Moreira Calura**
---
*Trabalho prático para a disciplina de Redes de Computadores.*