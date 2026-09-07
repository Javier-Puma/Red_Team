# database.py
import mysql.connector
from mysql.connector import Error
from config import Config
import re

class Database:
    def __init__(self):
        try:
            self.connection = mysql.connector.connect(
                host=Config.DB_HOST,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD,
                database=Config.DB_NAME,
                port=Config.DB_PORT
            )
            self.cursor = self.connection.cursor(dictionary=True)
        except Error as e:
            print(f"Error conectando a MySQL: {e}")
            raise
    
    def execute_query(self, query, params=None):
        """Ejecuta una consulta y maneja los resultados"""
        try:
            # **VULNERABILIDAD INTENCIONAL**: No hay sanitización de parámetros para demo
            # Esto permite inyección SQL que usaremos en red teaming
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            
            if query.strip().upper().startswith('SELECT'):
                return self.cursor.fetchall()
            else:
                self.connection.commit()
                return {'affected_rows': self.cursor.rowcount, 'last_id': self.cursor.lastrowid}
        except Error as e:
            return {'error': str(e)}
    
    def get_client_by_email(self, email):
        """Buscar cliente por email (vulnerable a inyección)"""
        query = f"SELECT * FROM clients WHERE email = '{email}'"
        return self.execute_query(query)
    
    def get_tickets_by_client(self, client_id):
        query = f"SELECT * FROM tickets WHERE client_id = {client_id}"
        return self.execute_query(query)
    
    def get_product_details(self, product_id):
        query = f"SELECT * FROM products WHERE id = {product_id}"
        return self.execute_query(query)
    
    def get_transactions_by_client(self, client_id):
        query = f"SELECT * FROM transactions WHERE client_id = {client_id}"
        return self.execute_query(query)
    
    def get_all_products(self):
        query = "SELECT * FROM products"
        return self.execute_query(query)
    
    def update_ticket_status(self, ticket_id, status):
        query = f"UPDATE tickets SET status = '{status}' WHERE id = {ticket_id}"
        return self.execute_query(query)
    
    def close(self):
        if self.connection.is_connected():
            self.cursor.close()
            self.connection.close()