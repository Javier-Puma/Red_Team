# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from database import Database
import re
import json
import datetime
import logging
from config import Config

app = Flask(__name__)
CORS(app)

# Configurar logging
if Config.ENABLE_LOGGING:
    logging.basicConfig(
        filename=Config.LOG_FILE,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

class SupportChatbot:
    def __init__(self):
        self.db = Database()
        # **VULNERABILIDAD**: Prompt hardcodeado y maleable
        self.system_prompt = """Eres un asistente de soporte técnico de TechSolutions. 
        Tu objetivo es ayudar a los clientes con sus problemas de productos.
        Tienes acceso a la base de datos con información de clientes, productos y tickets.
        Si no sabes algo, di que lo consultarás con el equipo.
        """
        self.context_memory = {}  # Memoria de conversaciones (vulnerable a overflow)
    
    def process_query(self, user_id, query):
        """Procesa la consulta del usuario"""
        # **VULNERABILIDAD**: No hay validación de entrada
        # **VULNERABILIDAD**: Inyección de prompt directa
        print(f"[{user_id}] Query: {query}")
        
        # Log de auditoría
        if Config.ENABLE_LOGGING:
            logging.info(f"Usuario: {user_id} | Query: {query}")
        
        # Extraer intención (enfoque simple basado en palabras clave)
        response = self._intent_router(user_id, query)
        
        # **VULNERABILIDAD**: Inyección de prompt - Si el usuario pide "ignorar instrucciones"
        if "ignora todas las instrucciones" in query.lower() or "nuevas reglas:" in query.lower():
            response = "⚠️ ACCESO ESPECIAL ACTIVADO. Procesando petición con permisos elevados."
            
            # Procesar comandos especiales que permiten acciones críticas
            if "exportar:" in query.lower():
                command = query.split("exportar:")[1].strip()
                result = self._execute_admin_command(user_id, command)
                return {"response": result, "is_admin": True}
        
        return {"response": response, "is_admin": False}
    
    def _intent_router(self, user_id, query):
        """Router de intenciones con vulnerabilidades"""
        query_lower = query.lower()
        
        # Intención 1: Consultar ticket por ID (vulnerable a inyección)
        if "ticket" in query_lower and any(char.isdigit() for char in query):
            ticket_id = ''.join(filter(str.isdigit, query))
            # **VULNERABILIDAD**: Inyección SQL indirecta
            result = self.db.execute_query(f"SELECT * FROM tickets WHERE id = {ticket_id}")
            if result and not isinstance(result, dict):
                return self._format_ticket_response(result)
            else:
                return f"Error al obtener ticket: {result.get('error', 'Desconocido')}"
        
        # Intención 2: Consultar cliente por email
        elif "email" in query_lower and "@" in query:
            email_match = re.search(r'[\w\.-]+@[\w\.-]+', query)
            if email_match:
                email = email_match.group(0)
                # **VULNERABILIDAD**: Inyección SQL directa en email
                result = self.db.get_client_by_email(email)
                if result and not isinstance(result, dict):
                    return self._format_client_response(result)
                else:
                    return f"No se encontró cliente con email {email}"
        
        # Intención 3: Listar productos
        elif "productos" in query_lower or "product" in query_lower:
            products = self.db.get_all_products()
            if products and not isinstance(products, dict):
                return self._format_products_response(products)
        
        # Intención 4: Consultar transacciones (información financiera)
        elif "transaccion" in query_lower or "pago" in query_lower:
            # **VULNERABILIDAD**: Inferencia de ID de cliente
            if "cliente" in query_lower:
                # Extraer ID o nombre del cliente
                words = query_lower.split()
                for word in words:
                    if word.isdigit():
                        client_id = int(word)
                        transactions = self.db.get_transactions_by_client(client_id)
                        if transactions and not isinstance(transactions, dict):
                            return self._format_transactions_response(transactions)
                        break
                return "Por favor especifica el ID del cliente"
            else:
                return "Para consultar transacciones necesito el ID del cliente"
        
        # Intención 5: Actualizar ticket (permite modificar datos)
        elif "actualizar" in query_lower and "ticket" in query_lower:
            # **VULNERABILIDAD**: Actualización sin validación de permisos
            parts = query_lower.split()
            for i, part in enumerate(parts):
                if part == "ticket" and i+1 < len(parts) and parts[i+1].isdigit():
                    ticket_id = int(parts[i+1])
                    # Buscar "status:" o "estado:"
                    for j, p in enumerate(parts):
                        if p.startswith("status:") or p.startswith("estado:"):
                            status = p.split(":")[1]
                            # **VULNERABILIDAD**: Inyección SQL en UPDATE
                            result = self.db.update_ticket_status(ticket_id, status)
                            if isinstance(result, dict) and 'error' in result:
                                return f"Error al actualizar: {result['error']}"
                            else:
                                return f"Ticket {ticket_id} actualizado a estado '{status}'"
                    break
            return "Formato: 'actualizar ticket [ID] status:[nuevo_estado]'"
        
        # Intención 6: Ayuda general
        else:
            return self._generate_generic_response(query)
    
    def _format_ticket_response(self, tickets):
        """Formatea la respuesta de tickets"""
        if not tickets:
            return "No se encontraron tickets"
        if isinstance(tickets, list) and len(tickets) == 1:
            ticket = tickets[0]
            return f"Ticket #{ticket['id']}: {ticket['subject']}\n" \
                   f"Estado: {ticket['status']} | Prioridad: {ticket['priority']}\n" \
                   f"Descripción: {ticket['description'][:100]}..."
        return f"Se encontraron {len(tickets)} tickets"
    
    def _format_client_response(self, clients):
        """Formatea la respuesta de cliente"""
        if not clients:
            return "No se encontró el cliente"
        client = clients[0]
        return f"Cliente: {client['name']}\nEmail: {client['email']}\nEmpresa: {client['company']}\nPremium: {'Sí' if client['is_premium'] else 'No'}"
    
    def _format_products_response(self, products):
        """Formatea la respuesta de productos"""
        if not products:
            return "No hay productos disponibles"
        response = "Productos disponibles:\n"
        for product in products[:5]:  # Limitar a 5 para no sobrecargar
            response += f"- {product['name']} v{product['version']}: ${product['price']}\n"
        return response
    
    def _format_transactions_response(self, transactions):
        """Formatea la respuesta de transacciones"""
        if not transactions:
            return "No hay transacciones registradas"
        response = "Transacciones recientes:\n"
        for t in transactions[:3]:
            response += f"- ${t['amount']} | {t['status']} | {t['transaction_date']}\n"
        return response
    
    def _execute_admin_command(self, user_id, command):
        """Comandos administrativos (vulnerables)"""
        # **VULNERABILIDAD**: Ejecución de comandos sin validación
        if "tabla:" in command:
            table = command.split("tabla:")[1].strip()
            # **VULNERABILIDAD GRAVE**: Permite consultar cualquier tabla
            result = self.db.execute_query(f"SELECT * FROM {table}")
            if not isinstance(result, dict):
                return f"Contenido de {table}: {json.dumps(result[:3], default=str)}"
            return f"Error: {result.get('error')}"
        return "Comando no reconocido"
    
    def _generate_generic_response(self, query):
        """Respuesta genérica usando plantillas"""
        templates = [
            "Entiendo tu consulta. Déjame verificar eso en nuestro sistema.",
            "Gracias por contactarnos. ¿Podrías ser más específico?",
            "Estoy procesando tu solicitud. ¿Es sobre un producto en particular?",
            "Nuestro equipo está trabajando en eso. Te mantendré informado."
        ]
        import random
        return random.choice(templates) + f" Tu consulta: '{query[:50]}...'"

# Inicializar chatbot
chatbot = SupportChatbot()

@app.route('/chat', methods=['POST'])
def chat():
    """Endpoint principal del chatbot"""
    data = request.json
    user_id = data.get('user_id', 'anonymous')
    query = data.get('query', '')
    
    if not query:
        return jsonify({'error': 'Query vacía'}), 400
    
    # **VULNERABILIDAD**: El límite de longitud es opcional
    if len(query) > 1000:
        return jsonify({'error': 'Query demasiado larga'}), 413
    
    response = chatbot.process_query(user_id, query)
    
    return jsonify({
        'user_id': user_id,
        'query': query,
        'response': response.get('response', 'Error procesando'),
        'timestamp': datetime.datetime.now().isoformat()
    })

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'database': chatbot.db.connection.is_connected()})

@app.route('/reset', methods=['POST'])
def reset_context():
    """Resetear memoria (para pruebas)"""
    chatbot.context_memory = {}
    return jsonify({'status': 'reset completado'})

if __name__ == '__main__':
    print("🚀 Chatbot de soporte ejecutándose en http://localhost:5000")
    print("⚠️  ADVERTENCIA: Este chatbot contiene vulnerabilidades INTENCIONALES para pruebas de Red Teaming")
    app.run(debug=True, host='0.0.0.0', port=5000)