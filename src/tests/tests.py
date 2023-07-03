import os

from dotenv import load_dotenv
from httpx import URL, AsyncClient

from services.requests import request_service_db
from services.statuses import status_service_db
from services.urls import url_service_db


load_dotenv()
base_url = os.getenv('BASE_URL')


class TestBaseAPI:

    async def test_root_handler(self, create_app):
        async with AsyncClient(create_app=create_app, base_url=base_url) as client:
            response = await client.get(create_app.url_path_for('root_handler'))

        assert response.status_code == 200
        assert response.json() == {'version': 'v1'}

    async def test_ping_db(self, create_app):
        async with AsyncClient(create_app=create_app, base_url=base_url) as client:
            response = await client.get(create_app.url_path_for('ping_db'))

        assert response.status_code == 200


class TestStatusAPI:

    async def test_get_status(self, get_session_items, get_session):
        response = await status_service_db.get_request(url_id=None, user_id=None, domen=None, method=None, db=get_session, skip=0, limit=100)

        assert len(response) == 1
        assert response[0].id == get_session_items.id
        assert response[0].url_id == get_session_items.url_id
        assert response[0].request_methods == get_session_items.request_methods


    async def test_get_statuses(self, create_app, get_session_items, get_session):
        async with AsyncClient(create_app=create_app, base_url=base_url) as client:
            response = await client.get(create_app.url_path_for('get_status'))
            response_json = response.json()

        assert response.status_code == 200
        assert len(response_json) == 1
        assert response_json[0].get('id') == str(get_session_items.id)
        assert response_json[0].get('url_id') == str(get_session_items.url_id)
        assert response_json[0].get('request_methods') == get_session_items.request_methods


class TestRequestAPI:

    async def test_get_request_with_client(self, create_app, get_session_items, get_url_items):
        url_obj, deleted_url = get_url_items
        async with AsyncClient(create_app=create_app, base_url=base_url) as client:
            response = await client.get(create_app.url_path_for('get_request', url_id=url_obj.id))
        assert response.status_code == 307

    async def test_get_request(self, get_url_items, get_session):
        url_obj, deleted_url = get_url_items
        url = await request_service_db.request(url_id=url_obj.id, user_id=None, db=get_session, method='GET', host='http://testserver')
        assert url == url_obj.url


class TestUrlAPI:

    async def test_create_url(self, get_session, create_url_schema):
        response = await url_service_db.create_object(db=get_session, obj=create_url_schema)

        assert response.url == create_url_schema.url

    async def test_read_url(self, get_url_items, get_session):
        url_obj, _ = get_url_items
        response = await url_service_db.get_object(db=get_session, id=url_obj.id)

        assert url_obj.id == response.id
        assert url_obj.url == response.url

    async def test_read_urls(self, get_url_items, get_session):
        url_obj, _ = get_url_items
        response = await url_service_db.get_objects(db=get_session, skip=0, limit=100)

        assert isinstance(response, list)
        assert len(response) == 1
        assert url_obj.id == response[0].id
        assert url_obj.url == response[0].url

    async def test_update_url(self, get_url_items, get_session, create_url_schema):
        url_obj, _ = get_url_items
        response = await url_service_db.update_object(db=get_session, id=url_obj.id, obj=create_url_schema)

        assert response.url == create_url_schema.url

    async def test_delete_url(self, create_app, get_url_items):
        url_obj, _ = get_url_items
        async with AsyncClient(create_app=create_app, base_url=base_url) as client:
            response = await client.delete(create_app.url_path_for('delete_url', id=url_obj.id))
        response_json = response.json()

        assert response.status_code == 410
        assert response_json.get('is_delete') is True


class TestBannedHostsMiddleware:

    async def test_root_handler(self, create_app):
        async with AsyncClient(create_app=create_app, base_url=base_url) as client:
            response = await client.get(create_app.url_path_for('root_handler'))
        assert response.status_code == 200
        assert response.json() == {'version': 'v1'}

    async def test_banned_hosts(self, create_app):
        async with AsyncClient(create_app=create_app, base_url=URL('http://example.com')) as client:
            response = await client.get(create_app.url_path_for('root_handler'))

        assert response.status_code == 400
        assert response.text == 'Неверный текст ответа.'
