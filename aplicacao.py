import json
import time

class MensagemApp:
    """
    Camada de Aplicação: Responsável por padronizar a mensagem do chat.
    """
    def __init__(self, sender, message="", msg_type="chat", filename=None, file_data=None, part=1, total_parts=1):
        self.type = msg_type          # "chat" ou "file"
        self.sender = sender
        self.message = message
        self.filename = filename      # Nome do arquivo (ex: foto.jpg)
        self.file_data = file_data    # Pedaço do arquivo em Base64
        self.part = part              # Qual fragmento é este? (ex: 1)
        self.total_parts = total_parts# Total de fragmentos (ex: 10)
        self.timestamp = int(time.time())

    def to_json(self):
        """Faz o encapsulamento da mensagem da camada de aplicação em um formato JSON para envio."""
        return json.dumps({
            "type": self.type,
            "sender": self.sender,
            "message": self.message,
            "filename": self.filename,
            "file_data": self.file_data,
            "part": self.part,
            "total_parts": self.total_parts,
            "timestamp": self.timestamp
        })

    @staticmethod
    def from_json(json_str):
        """Desfaz o encapsulamento da mensagem da camada de aplicação, convertendo o JSON de volta para uma instância de MensagemApp."""
        data = json.loads(json_str)
        # Reconstruindo a instância da mensagem
        msg = MensagemApp(
            data['sender'], 
            data.get('message', ''), 
            data['type'], 
            data.get('filename'), 
            data.get('file_data'), 
            data.get('part', 1), 
            data.get('total_parts', 1)
        )
        msg.timestamp = data['timestamp']
        return msg