def test_delete_company_ajax(client, app, db_session):
    from app.modules.companies.models import Company
    # Create company for test
    c = Company(name='T-Test', slug='t-test', country='Test')
    db_session.add(c)
    db_session.commit()
    cid = c.id

    resp = client.post(f'/companies/{c.slug}/delete', headers={'X-Requested-With': 'XMLHttpRequest'})
    assert resp.status_code == 200
    assert resp.json().get('status') == 'ok'

    # After soft-delete, deleted_at should be set
    db_session.refresh(c)
    assert c.deleted_at is not None
