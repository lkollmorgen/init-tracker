import pytest
from app import app
import io


@pytest.fixture
def client():
	app.config['TESTING'] = True
	with app.test_client() as client:
		yield client
	
def test_player_view(client):
	"""Test the player view page loads."""
	response = client.get('/player')
	assert response.status_code == 200
	assert b"INITIATIVE ORDER" in response.data

def test_admin_view(client):
	"""Test the admin view page loads."""
	response = client.get('/admin')
	assert response.status_code == 200
	assert b"Admin Panel" in response.data

def test_add_combatant(client):
	"""Test adding a combatant"""
	response = client.post('/add', data={'name': 'Boblin', 'initiative': 12}, follow_redirects=True)
	assert response.status_code == 200
	assert b'Boblin' in response.data

def test_csv_upload(client):
    """Test uploading csv combatans"""
    csv_content = (
            "name,initiative,status\n"
            "csv man!,15,alive\n"
    )
    data = {
            'file': (io.BytesIO(csv_content.encode()), 'test.csv')
    }
    response = client.post('/upload_csv', data=data, content_type='multipart/form-data', follow_redirects=True)
    assert response.status_code == 200
    assert b'csv man!' in response.data

