document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('.btn-delete').forEach(btn => {
    btn.addEventListener('click', async function () {
      const id = this.dataset.id;
      const action = this.dataset.action || this.closest('form')?.action;
      if (!action) return;

      if (!confirm('هل أنت متأكد من حذف هذه الشركة؟ لا يمكن التراجع عن هذا الإجراء.')) return;

      const form = this.closest('form');
      const formData = form ? new FormData(form) : new FormData();

      try {
        const resp = await fetch(action, {
          method: 'POST',
          headers: {'X-Requested-With': 'XMLHttpRequest'},
          body: formData,
          credentials: 'same-origin'
        });
        if (resp.ok) {
          const row = document.getElementById(`company-row-${id}`);
          if (row) row.remove();
        } else {
          const data = await resp.json().catch(()=>null);
          alert('فشل الحذف: ' + (data?.message || resp.statusText));
        }
      } catch (err) {
        console.error(err);
        alert('حدث خطأ أثناء الحذف.');
      }
    });
  });
});
