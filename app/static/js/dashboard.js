document.addEventListener('DOMContentLoaded', () => {
    // Status Güncelleme İletişimi
    const statusSelects = document.querySelectorAll('.status-select');
    statusSelects.forEach(select => {
        select.addEventListener('change', async (e) => {
            const leadId = select.getAttribute('data-lead-id');
            const newStatus = select.value;

            try {
                const response = await fetch(`/api/leads/${leadId}/status`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ status: newStatus })
                });

                const data = await response.json();
                if (data.success) {
                    // Sayfayı yenile veya badge stilini güncelle
                    window.location.reload();
                } else {
                    alert('Hata: ' + (data.error || 'Durum güncellenemedi.'));
                }
            } catch (err) {
                alert('Sunucu hatası oluştu.');
            }
        });
    });

    // Lead Silme İletişimi
    const deleteBtns = document.querySelectorAll('.delete-lead-btn');
    deleteBtns.forEach(btn => {
        btn.addEventListener('click', async () => {
            const leadId = btn.getAttribute('data-lead-id');
            if (confirm(`ID #${leadId} olan lead kaydını silmek istediğinize emin misiniz?`)) {
                try {
                    const response = await fetch(`/api/leads/${leadId}`, {
                        method: 'DELETE'
                    });
                    const data = await response.json();
                    if (data.success) {
                        const tr = btn.closest('tr');
                        if (tr) tr.remove();
                        window.location.reload();
                    } else {
                        alert('Silinemedi: ' + data.error);
                    }
                } catch (err) {
                    alert('Silme sırasında sunucu hatası oluştu.');
                }
            }
        });
    });
});
