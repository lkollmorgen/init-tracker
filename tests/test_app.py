import pytest
from app import app, sessions
import io


@pytest.fixture
def client():
	app.config['TESTING'] = True
	with app.test_client() as client:
		yield client

@pytest.fixture
def session_code(client):
    """creates a session and returns its join code"""
    response = client.post('/create_session', follow_redirects=True)
    code = response.request.path.split('/')[-1]
    return code

def test_player_view(client, session_code):
	"""Test the player view page loads."""
	response = client.get(f'/player/{session_code}')
	assert response.status_code == 200
	assert b"INITIATIVE ORDER" in response.data

def test_admin_view(client, session_code):
	"""Test the admin view page loads."""
	response = client.get(f'/admin/{session_code}')
	assert response.status_code == 200
	assert b"Admin Panel" in response.data

def test_add_combatant(client, session_code):
	"""Test adding a combatant"""
	response = client.post(f'/{session_code}/add', data={'name': 'Boblin', 'initiative': 12}, follow_redirects=True)
	assert response.status_code == 200
	assert b'Boblin' in response.data

def test_csv_upload(client, session_code):
    """Test uploading csv combatans"""
    csv_content = (
            "name,initiative,status\n"
            "csv man!,15,alive\n"
    )
    data = {
            'file': (io.BytesIO(csv_content.encode()), 'test.csv')
    }
    response = client.post(f'/{session_code}/upload_csv', data=data, content_type='multipart/form-data', follow_redirects=True)
    assert response.status_code == 200
    assert b'csv man!' in response.data

