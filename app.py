from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

#temp data store
initiative_list = []
current_turn = 0

@app.route('/')
def index():
	return render_template('index.html', initiative_list = initiative_list, current_turn = current_turn)

@app.route('/add', methods=['POST'])
def add():
	name = request.form['name']
	initiative = int(request.form['initiative'])
	status = 'alive'
	initiative_list.append({'name': name, 'initiative': initiative, 'status': status})
	initiative_list.sort(key=lambda x: x['initiative'], reverse=True)
	return redirect(url_for('index'))

@app.route('/next')
def next_turn():
	global current_turn
	if initiative_list:
		current_turn = (current_turn + 1) % len(initiative_list)
	return redirect (url_for('index'))

@app.route('/reset')
def reset():
	global initiative_list, current_turn
	initiative_list = []
	current_turn = 0
	return redirect(url_for('index'))
'''
@app.route('/delete/<name>')
def delete(name):
#	completely removes a player from the list cause they died
#		input: name of the player to die
# 	return: index
#
	global initiative_list
	new_list = [d for d in initiative_list if d.get('name') != name]
	initiative_list = new_list
	return redirect(url_for('index'))
'''

@app.route('/dead/<name>')
def dead(name):
	global initiative_list
	for combatant in initiative_list:
		if combatant['name'] == name:
			combatant['status'] = 'dead'
	return redirect(url_for('index'))

if __name__ == '__main__':
	app.run(debug=True)
