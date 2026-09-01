@main_bp.route('/api/leads', methods=['POST'])
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

# --- BURAYA EKLE ---
@main_bp.route('/api/leads/list', methods=['GET'])
def api_leads_list():
    try:
        status_filter = request.args.get('status', 'Tümü')
        search_query = request.args.get('search', '')
        leads = get_all_leads(status_filter=status_filter, search_query=search_query)

        leadler = [{
            'id': lead['id'],
            'isim': lead['full_name'],
            'telefon': lead['phone'],
            'mesaj': lead.get('notes', ''),
            'tarih': lead['created_at']
        } for lead in leads]

        return jsonify({'basari': True, 'leadler': leadler})
    except Exception as e:
        return jsonify({'basari': False, 'hata': str(e)}), 500
# --- BURAYA KADAR ---

@main_bp.route('/api/leads/<int:lead_id>/status', methods=['POST', 'PUT'])
def api_update_status(lead_id):
    ...
