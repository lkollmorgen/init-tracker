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
	initiative_list.append({'name': name, 'initiative': initiative})
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

if __name__ == '__main__':
	app.run(debug=True)
