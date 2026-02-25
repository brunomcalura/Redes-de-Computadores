import json
import time

class MensagemApp:
    """
    Camada de Aplicação: Responsável por padronizar a mensagem do chat.
    """
    def __init__(self, sender, message, msg_type="chat"):
        self.sender = sender
        self.message = message
        self.type = msg_type
        self.timestamp = int(time.time())

    def to_json(self):
        """Faz o encapsulamento da mensagem da camada de aplicação em um formato JSON para envio."""
        return json.dumps({
            "type": self.type,
            "sender": self.sender,
            "message": self.message,
            "timestamp": self.timestamp
        })

    @staticmethod
    def from_json(json_str):
        """Desfaz o encapsulamento da mensagem da camada de aplicação, convertendo o JSON de volta para uma instância de MensagemApp."""
        data = json.loads(json_str)
        # Reconstruindo a instância da mensagem
        msg = MensagemApp(data['sender'], data['message'], data['type'])
        msg.timestamp = data['timestamp']
        return msg