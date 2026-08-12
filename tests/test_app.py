import unittest
import os
import tempfile
import json
from app import create_app
from app.database import init_db, add_lead, get_all_leads, update_lead_status, delete_lead, get_lead_stats
from config import Config

class SmartLeadTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp()
        Config.DATABASE_PATH = self.db_path
        
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

        with self.app.app_context():
            init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def test_index_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'SallyPet Veteriner', response.data)

    def test_dashboard_page(self):
        response = self.client.get('/dashboard')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Y\xc3\xb6netim Paneli', response.data)

    def test_api_chat(self):
        payload = {
            'session_id': 'test-session-123',
            'message': 'Merhaba, acil servisiniz nerede?'
        }
        response = self.client.post('/api/chat', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('reply', data)

    def test_api_lead_submission_and_crud(self):
        # 1. Lead ekleme API testi
        payload = {
            'full_name': 'Ahmet Yılmaz',
            'phone': '0532 999 8877',
            'pet_name': 'Tekir',
            'pet_type': 'Kedi',
            'notes': 'Yıllık aşı kontrolü'
        }
        response = self.client.post('/api/lead', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        lead_id = data['lead_id']

        # 2. Veritabanından okuma kontrolü
        with self.app.app_context():
            leads = get_all_leads()
            self.assertEqual(len(leads), 1)
            self.assertEqual(leads[0]['full_name'], 'Ahmet Yılmaz')

            # 3. Status güncelleme testi
            updated = update_lead_status(lead_id, 'Randevu Oluşturuldu')
            self.assertTrue(updated)
            
            stats = get_lead_stats()
            self.assertEqual(stats['appointment'], 1)

            # 4. Silme testi
            deleted = delete_lead(lead_id)
            self.assertTrue(deleted)
            self.assertEqual(len(get_all_leads()), 0)

if __name__ == '__main__':
    unittest.main()
