import json
import time

class MensagemApp:
    """
    Camada de Aplicação: Responsável por padronizar a mensagem do chat.
    """
    def __init__(self, sender, message, msg_type="chat"):
        self.type = msg_type
        self.sender = sender
        self.message = message
        self.timestamp = int(time.time())

    def to_json(self):
        """Converte o objeto para uma string JSON."""
        return json.dumps({
            "type": self.type,
            "sender": self.sender,
            "message": self.message,
            "timestamp": self.timestamp
        })

    @staticmethod
    def from_json(json_str):
        """Reconstrói o objeto a partir de uma string JSON."""
        data = json.loads(json_str)
        # Reconstruindo a instância da mensagem
        msg = MensagemApp(data['sender'], data['message'], data['type'])
        msg.timestamp = data['timestamp']
        return msg