import sqlite3
import os
from config import Config

def get_db_connection():
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Leads (Müşteri Adayları) Tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            phone TEXT NOT NULL,
            pet_name TEXT,
            pet_type TEXT,
            notes TEXT,
            status TEXT DEFAULT 'Yeni',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Sohbet Geçmişi Tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            sender TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()

# Lead CRUD Operasyonları
def add_lead(full_name, phone, pet_name="", pet_type="", notes=""):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO leads (full_name, phone, pet_name, pet_type, notes)
        VALUES (?, ?, ?, ?, ?)
    ''', (full_name, phone, pet_name, pet_type, notes))
    lead_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return lead_id

def get_all_leads(status_filter=None, search_query=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM leads WHERE 1=1"
    params = []

    if status_filter and status_filter != 'Tümü':
        query += " AND status = ?"
        params.append(status_filter)

    if search_query:
        query += " AND (full_name LIKE ? OR phone LIKE ? OR pet_name LIKE ? OR notes LIKE ?)"
        like_pattern = f"%{search_query}%"
        params.extend([like_pattern, like_pattern, like_pattern, like_pattern])

    query += " ORDER BY created_at DESC"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]

def get_lead_by_id(lead_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM leads WHERE id = ?", (lead_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def update_lead_status(lead_id, status):
    valid_statuses = ['Yeni', 'Arandı', 'Randevu Oluşturuldu', 'Tamamlandı', 'İptal']
    if status not in valid_statuses:
        return False

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE leads SET status = ? WHERE id = ?", (status, lead_id))
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return affected > 0

def delete_lead(lead_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM leads WHERE id = ?", (lead_id,))
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return affected > 0

def get_lead_stats():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) as total FROM leads")
    total = cursor.fetchone()['total']

    cursor.execute("SELECT COUNT(*) as new_leads FROM leads WHERE status = 'Yeni'")
    new_leads = cursor.fetchone()['new_leads']

    cursor.execute("SELECT COUNT(*) as contacted FROM leads WHERE status = 'Arandı'")
    contacted = cursor.fetchone()['contacted']

    cursor.execute("SELECT COUNT(*) as appointment FROM leads WHERE status = 'Randevu Oluşturuldu'")
    appointment = cursor.fetchone()['appointment']

    conn.close()
    return {
        'total': total,
        'new': new_leads,
        'contacted': contacted,
        'appointment': appointment
    }

# Chat Mesaj Kayıt Operasyonları
def save_chat_message(session_id, sender, content):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO messages (session_id, sender, content)
        VALUES (?, ?, ?)
    ''', (session_id, sender, content))
    msg_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return msg_id

def get_chat_history(session_id, limit=50):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT sender, content, created_at FROM messages
        WHERE session_id = ?
        ORDER BY created_at ASC
        LIMIT ?
    ''', (session_id, limit))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]
