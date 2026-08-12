import uuid
from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from config import Config
from app.database import (
    add_lead, get_all_leads, get_lead_by_id, update_lead_status, delete_lead, get_lead_stats, get_chat_history
)
from app.services.ai_service import generate_ai_response

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    session_id = request.cookies.get('session_id')
    if not session_id:
        session_id = str(uuid.uuid4())
    
    response = render_template(
        'index.html',
        business_name=Config.BUSINESS_NAME,
        business_slogan=Config.BUSINESS_SLOGAN,
        business_phone=Config.BUSINESS_PHONE,
        business_address=Config.BUSINESS_ADDRESS,
        session_id=session_id,
        wix_booking_url=Config.WIX_BOOKING_URL
    )
    return response

@main_bp.route('/dashboard')
def dashboard():
    status_filter = request.args.get('status', 'Tümü')
    search_query = request.args.get('search', '')
    
    leads = get_all_leads(status_filter=status_filter, search_query=search_query)
    stats = get_lead_stats()

    return render_template(
        'dashboard.html',
        leads=leads,
        stats=stats,
        current_status=status_filter,
        search_query=search_query,
        business_name=Config.BUSINESS_NAME
    )

@main_bp.route('/api/chat', methods=['POST'])
def api_chat():
    data = request.get_json() or {}
    session_id = data.get('session_id')
    user_message = data.get('message', '').strip()

    if not session_id or not user_message:
        return jsonify({'error': 'Geçersiz mesaj veya oturum kimliği.'}), 400

    result = generate_ai_response(session_id, user_message)
    return jsonify({
        'success': True,
        'reply': result['reply'],
        'suggest_lead_form': result['suggest_lead_form']
    })

@main_bp.route('/api/lead', methods=['POST'])
def api_lead():
    data = request.get_json() or {}
    full_name = data.get('full_name', '').strip()
    phone = data.get('phone', '').strip()
    pet_name = data.get('pet_name', '').strip()
    pet_type = data.get('pet_type', '').strip()
    notes = data.get('notes', '').strip()

    if not full_name or not phone:
        return jsonify({'error': 'Lütfen Ad Soyad ve Telefon numarası alanlarını doldurun.'}), 400

    lead_id = add_lead(full_name, phone, pet_name, pet_type, notes)
    
    return jsonify({
        'success': True,
        'message': 'İletişim bilgileriniz başarıyla alındı! Veteriner hekimlerimiz en kısa sürede sizinle iletişime geçecektir.',
        'lead_id': lead_id
    }), 201

@main_bp.route('/api/leads/<int:lead_id>/status', methods=['POST', 'PUT'])
def api_update_status(lead_id):
    data = request.get_json() or {}
    new_status = data.get('status')

    if not new_status:
        return jsonify({'error': 'Yeni durum belirtilmedi.'}), 400

    updated = update_lead_status(lead_id, new_status)
    if updated:
        return jsonify({'success': True, 'message': 'Lead durumu güncellendi.'})
    else:
        return jsonify({'error': 'Güncelleme başarısız veya geçersiz durum.'}), 400

@main_bp.route('/api/leads/<int:lead_id>', methods=['DELETE'])
def api_delete_lead(lead_id):
    deleted = delete_lead(lead_id)
    if deleted:
        return jsonify({'success': True, 'message': 'Lead kaydı silindi.'})
    else:
        return jsonify({'error': 'Kayıt bulunamadı veya silinemedi.'}), 404

@main_bp.route('/api/chat/history/<session_id>', methods=['GET'])
def api_chat_history(session_id):
    history = get_chat_history(session_id)
    return jsonify({'success': True, 'history': history})
