from flask import Flask, render_template, request, redirect, url_for
import json
DATA_FILE = 'initiative_data.json'

app = Flask(__name__)

#temp data store
initiative_list = []
current_turn = 0

@app.route('/')
def home():
    return redirect(url_for('player_view'))

###### json data helper functions
def save_data():
	with open(DATA_FILE, 'w') as f:
			json.dump({'initiative_list': initiative_list, 'current_turn':current_turn},f)
	
def load_data():
	global initiative_list, current_turn
	try:
		with open(DATA_FILE, 'r') as f:
				data = json.load(f)
				initiative_list = data['initiative_list']
				current_turn = data['current_turn']
	except FileNotFoundError:
		initiative_list = []
		current_turn = 0

@app.route('/player')
def player_view():
	load_data()
	return render_template('player.html', initiative_list = initiative_list, current_turn = current_turn)

@app.route('/admin')
def admin_view():
	load_data()
	return render_template('admin.html', initiative_list=initiative_list, current_turn=current_turn)

@app.route('/add', methods=['POST'])
def add():
	load_data()
	name = request.form['name']
	initiative = int(request.form['initiative'])
	initiative_list.append({'name': name, 'initiative': initiative, 'status': 'alive'})
	initiative_list.sort(key=lambda x: x['initiative'], reverse=True)
	save_data()
	return redirect(url_for('admin_view'))

@app.route('/next')
def next_turn():
	load_data()
	global current_turn
	if initiative_list:
		current_turn = (current_turn + 1) % len(initiative_list)
		save_data()
	return redirect (url_for('admin_view'))

@app.route('/dead/<name>')
def dead(name):
	load_data()
	global initiative_list
	for combatant in initiative_list:
		if combatant['name'] == name:
			combatant['status'] = 'dead'
	save_data()
	return redirect(url_for('admin_view'))


@app.route('/delete/<name>')
def delete(name):
	load_data()
	global initiative_list
	new_list = [d for d in initiative_list if d.get('name') != name]
	initiative_list = new_list
	save_data()
	return redirect(url_for('admin_view'))


@app.route('/reset')
def reset():
	global initiative_list, current_turn
	initiative_list = []
	current_turn = 0
	return redirect(url_for('admin_view'))

if __name__ == '__main__':
	app.run(debug=True)
