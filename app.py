from flask import Flask, render_template, request, redirect, url_for, send_file
import json
import os
import threading
import csv
import io
from datetime import datetime

DATA_FILE = 'initiative_data.json'
data_lock = threading.Lock() #prevent simulitaneous read/write

app = Flask(__name__)

#temp data store
initiative_list = []
notes = []
current_turn = 0
round_count = 1

def init_data_file():
	"""create a fully validated data file if it doesn't exist yet"""
	if not os.path.exists(DATA_FILE):
		print("initializing data file with defaults")
		default_data = {
			'initiative_list': [],
			'current_turn': 0,
			'round_count': 1,
			'notes': []
		}
		
		with open(DATA_FILE, 'w') as f:
			json.dump(default_data, f, indent=2)

@app.route('/')
def home():
    return redirect(url_for('player_view'))

###### json data helper functions
def save_data():
    temp_file = DATA_FILE + '.tmp'
    with data_lock:
        try:
            with open(temp_file, 'w') as f:
                print('trying to make a temp file for data init')
                json.dump({'initiative_list': initiative_list,
                                 'current_turn':current_turn,
                                 'round_count':round_count,
                                 'notes':notes
                },f)
            os.replace(temp_file, DATA_FILE)
        except Exception as e:
            print("Error saving data:", e)

def import_csv(filename):
    """load combatants from .csv if you please"""
    global initiative_list
    initiative_list = []

    try:
        with open(filename, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                initiative_list.append({
                    'name': row['name'],
                    'initiative': int(row['initiative']),
                    'status': row.get('status', 'alive') #defult to alive
                })
            initiative_list.sort(key=lambda x: x['initiative'], reverse=True)
            print("loaded .csv file")
    except FileNotFoundError:
        print(f"no csv file found: {filename}")
    except Exception as e:
        print(f"error importing csv: {e}")

@app.route('/export')
def export_initiative():
    load_data()

    # get date/time
    current_datetime = datetime.now()
    current_date = str(current_datetime.date())

    # create an in-memory CSV file
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Name','Initiative', 'Status'])
    for combatant in initiative_list:
        writer.writerow([combatant['name'], combatant['initiative'], combatant['status']])

    writer.writerow(notes)
    # move cursor back 2 the start
    output.seek(0)

    return send_file(
            io.BytesIO(output.getvalue().encode()),
            mimetype='tet/csv',
            as_attachment=True,
            download_name='initiative_'+current_date+'.csv'
    )

def load_data():
    global initiative_list, current_turn, notes, round_count
    with data_lock:
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r') as f:
                        data = json.load(f)
                        initiative_list = data.get('initiative_list', [])
                        current_turn = data.get('current_turn', 0)
                        round_count = data.get('round_count', 1)
                        notes = data.get('notes', [])
                return
            except json.JSONDecodeError as e:
                print("Warning: JSON decode error:", e)
            except Exception as e:
                print("Error loading data:", e)
        
        if os.path.exists('initiative.csv'):
            print('found initiative.csv, importing peeps')
            import_csv('initiative.csv')
            save_data()
        else:
            print('no data file found, initializing empty state')
            initiative_list.clear()
            current_turn = 0
            round_count = 1
            notes.clear()
            save_data()

init_data_file()

@app.route('/player')
def player_view():
    load_data()
    return render_template('player.html', initiative_list = initiative_list, current_turn = current_turn, round_count= round_count, notes=notes)

@app.route('/admin')
def admin_view():
    load_data()
    return render_template('admin.html', initiative_list=initiative_list, current_turn=current_turn, round_count=round_count, notes=notes)

@app.route('/add', methods=['POST'])
def add():
    load_data()
    name = request.form['name']
    initiative = int(request.form['initiative'])
    initiative_list.append({'name': name, 'initiative': initiative, 'status': 'alive'})
    initiative_list.sort(key=lambda x: x['initiative'], reverse=True)
    save_data()
    return redirect(url_for('admin_view'))

@app.route('/add_note', methods=['POST'])
def add_note():
    load_data()
    note = request.form['note']
    notes.append(note)
    save_data()
    return redirect(url_for('admin_view'))

@app.route('/next')
def next_turn():
    load_data()
    global current_turn, round_count
    if initiative_list:
        current_turn = (current_turn + 1) % len(initiative_list)
        if current_turn == 0:
            round_count += 1    
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
    load_data()
    global initiative_list, current_turn, round_count, notes
    initiative_list = []
    notes = []
    current_turn = 0
    round_count = 1
    save_data()
    return redirect(url_for('admin_view'))

@app.route('/clear_notes')
def clear_notes():
    global notes
    notes = []
    save_data()
    return redirect(url_for('admin_view'))

@app.route('/upload_csv', methods=['POST'])
def upload_csv():
    if 'file' not in request.files:
        print("no file part in request")
        return redirect(url_for('admin_view'))

    file = request.files['file']
    if file.filename == '':
        print('no selected file')
        return redirect(url_for('admin_view'))
    if file and file.filename.endswith('.csv'):
        filepath = os.path.join('uploads', file.filename)
        file.save(filepath)
        print(f"uploaded csv file: {filepath}")
        import_csv(filepath)
        save_data()
    return redirect(url_for('admin_view'))

if __name__ == '__main__':
    app.run(debug=True)
