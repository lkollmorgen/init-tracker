from flask import Flask, render_template, request, redirect, url_for, send_file, session, jsonify
import json
import os
import threading
import time
import csv
import io
from datetime import datetime, timedelta
import random, string

DATA_FILE = 'initiative_data.json'
data_lock = threading.Lock() #prevent simulitaneous read/write

app = Flask(__name__)

# session tracking
app.secret_key = 'supersecretkey'

sessions = {}
sessions_lock = threading.Lock()

def generate_code(length=4):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/create_session', methods=['POST'])
def create_session():
    with sessions_lock:
        code = generate_code()
        #while code in sessions:
        #code = generate_code()
        sessions[code] = {
                'initiative_list': [],
                'notes': [],
                'current_turn': 0,
                'round_count': 1,
                'last_active': datetime.utcnow().isoformat()
                }
    print(f'session created! Code: {code}')
    save_data()
    touch_session(code)
    return redirect(url_for('admin_view', code=code))

@app.route('/join_session', methods=['POST'])
def join_session():
    code = request.form['code'].strip().upper()
    if code in sessions:
        return redirect(url_for('player_view', code=code))
    else:
        return render_template('landing.html', error='Invalid code')

def init_data_file(code):
    """create a fully validated data file if it doesn't exist yet"""
    if not os.path.exists(DATA_FILE):
        print("initializing data file with defaults")
        default_data = {code: {
		    'initiative_list': [],
		    'current_turn': 0,
		    'round_count': 1,
		    'notes': []
        }}
        with open(DATA_FILE, 'w') as f:
            json.dump(default_data, f, indent=2)
    else:
        return

@app.route('/')
def home():
    return redirect(url_for('landing'))

###### json data helper functions
def save_data():
    temp_file = DATA_FILE + '.tmp'
    with data_lock:
        try:
            with open(temp_file, 'w') as f:
                json.dump(sessions, f, indent=2)
            
            os.replace(temp_file, DATA_FILE)
        except Exception as e:
            print("Error saving data:", e)

def import_csv(code, filename):
    """load combatants from .csv if you please"""
    touch_session(code)
    game = sessions.get(code)
    if not game:
        return render_template("session_not_found.html"), 404
    try:
        with open(filename, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                row = {k.lower(): v for k, v in row.items()}
                game['initiative_list'].append({
                    'name': row['name'],
                    'initiative': int(row['initiative']),
                    'status': row.get('status', 'alive') #defult to alive
                })
            game['initiative_list'].sort(key=lambda x: x['initiative'], reverse=True)
    except FileNotFoundError:
        print(f"no csv file found: {filename}")
    except Exception as e:
        print(f"error importing csv: {e}")

@app.route('/<code>/export_initiative', methods=['POST'])
def export_initiative(code):
    touch_session(code)
    game = sessions.get(code)
    if not game:
        return render_template("session_not_found.html"), 404
    # get date/time
    current_datetime = datetime.now()
    current_date = str(current_datetime.date())

    # create an in-memory CSV file
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['name','initiative', 'status'])
    for combatant in game['initiative_list']:
        writer.writerow([combatant['name'], combatant['initiative'], combatant['status']])

    writer.writerow(game['notes'])
    # move cursor back 2 the start
    output.seek(0)

    return send_file(
            io.BytesIO(output.getvalue().encode()),
            mimetype='tet/csv',
            as_attachment=True,
            download_name='initiative_'+current_date+'.csv'
    )

def load_data():
    global sessions
    with data_lock:
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r') as f:
                    sessions = json.load(f)
                return
            except json.JSONDecodeError as e:
                print("Warning: JSON decode error:", e)
            except Exception as e:
                print("Error loading data:", e)
        
        if os.path.exists('initiative.csv'):
            print('found initiative.csv, importing peeps')
            import_csv(code, 'initiative.csv')
            save_data()
        else:
            print('no data file found, initializing empty state')
            sessions = {}
            save_data()

def touch_session(code):
    if code in sessions:
        sessions[code]['last_active'] = datetime.utcnow().isoformat()

def cleanup_sessions(timeout_minutes=30, sleep_seconds=300):
    print("[CLEANUP] Cleanup thread started")
    while True:
        try:
            time.sleep(sleep_seconds) # every 5 mins
            now = datetime.utcnow()
            expired = []

            with sessions_lock:
                for code, session_data in list(sessions.items()):
                    last_iso = session_data.get('last_active')
                    try:
                        last_active = datetime.fromisoformat(session_data.get('last_active',now.isoformat()))
                    except Exception:
                        last_active = now - timedelta(minutes=timeout_minutes + 1)

                    if now - last_active > timedelta(minutes=timeout_minutes):
                        expired.append(code)

                for code in expired:
                    print(f"Cleaning up exired session: {code}")
                    del sessions[code]

            if expired:
                try:
                    save_data()
                except Exception as e:
                    print("[CLEANUP] Error saving after data cleanup:", e)

        
        except Exception as e:
            print("[CLEANUP] unexpected error in cleaup thread:", e)
            time.sleep(5)

@app.route('/player_data/<code>')
def player_data(code):
    game = sessions.get(code)
    if not game:
        return jsonify({'error': 'Invalid code'}), 404
    return jsonify({
            'initiative_list': game['initiative_list'],
            'current_turn': game['current_turn'],
            'round_count': game['round_count'],
            'notes': game['notes'],
            #code:code
    })

@app.route('/player/<code>')
def player_view(code):
    #touch_session(code)
    game = sessions.get(code)
    if not game:
        return render_template("session_not_found.html"), 404
    return render_template('player.html',
                            initiative_list = game['initiative_list'],
                            current_turn = game['current_turn'],
                            round_count= game['round_count'],
                            notes=game['notes'],
                            code=code)

@app.route('/admin/<code>')
def admin_view(code):
    #touch_session(code)
    if not os.path.exists(DATA_FILE):
        init_data_file()
    game = sessions.get(code)
    if not game:
        return render_template("session_not_found.html"), 404
    load_data()
    #return render_template('admin.html', code=code, **game)
    return render_template('admin.html', 
                            initiative_list=game['initiative_list'],
                            current_turn=game['current_turn'],
                            round_count=game['round_count'], 
                            notes=game['notes'],
                            code=code)

@app.route('/<code>/add', methods=['POST'])
def add(code):
    touch_session(code)
    load_data()
    game = sessions.get(code)
    name = request.form['name']
    initiative = int(request.form['initiative'])
    sessions.get(code)['initiative_list'].append({'name': name, 'initiative': initiative, 'status': 'alive'})
    sessions.get(code)['initiative_list'].sort(key=lambda x: x['initiative'], reverse=True)
    save_data()
    return redirect(url_for('admin_view',code=code))

@app.route('/<code>/add_note', methods=['POST'])
def add_note(code):
    touch_session(code)
    game = sessions.get(code) 
    if not game:
        return render_template("session_not_found.html"), 404
    note = request.form['note']
    game['notes'].append(note)
    save_data()
    return redirect(url_for('admin_view',code=code))

@app.route('/<code>/next', methods=['POST'])
def next_turn(code):
    touch_session(code)
    game = sessions.get(code)
    if not game:
        return render_template("session_not_found.html"), 404
    if len(game['initiative_list']) == 0:
        return redirect(url_for('admin_view', code=code))
    game['current_turn'] = (game['current_turn'] + 1) % len(game['initiative_list'])
    if game['current_turn'] == 0:
        game['round_count'] += 1
    save_data()
    return redirect(url_for('admin_view', code=code))

@app.route('/<code>/previous', methods=['POST'])
def previous_turn(code):
    touch_session(code)
    game = sessions.get(code)
    if not game:
        return render_template("session_not_found.html"), 404
    if len(game['initiative_list']) == 0:
        return redirect(url_for('admin_view', code=code))
    game['current_turn'] = (game['current_turn'] - 1) % len(game['initiative_list'])
    if game['current_turn'] == 0:
        game['round_count'] -= 1
    save_data()
    return redirect(url_for('admin_view', code=code))


@app.route('/<code>/toggle_dead/<name>', methods=['POST'])
def toggle_dead(code, name):
    touch_session(code)
    game = sessions.get(code)
    if not game:
        return render_template("session_not_found.html"), 404
    for combatant in game['initiative_list']:
        if combatant['name'] == name and combatant['status'] == 'alive':
            combatant['status'] = 'dead'
        elif combatant['name'] == name and combatant['status'] == 'dead':
            combatant['status'] = 'alive'
    save_data()
    return redirect(url_for('admin_view',code=code))


@app.route('/<code>/delete/<name>', methods=['POST'])
def delete(code, name):
    touch_session(code)
    game = sessions.get(code)
    if not game:
        return render_template("session_not_found.html"), 404
    new_list = [d for d in game['initiative_list'] if d.get('name') != name]
    game['initiative_list'] = new_list
    save_data()
    return redirect(url_for('admin_view',code=code))


@app.route('/<code>/reset', methods=['POST'])
def reset(code):
    touch_session(code)
    load_data()
    game = sessions.get(code)
    if not game:
        return render_template("session_not_found.html"), 404
    game['initiative_list'] = []
    game['notes'] = []
    game['current_turn'] = 0
    game['round_count'] = 1
    save_data()
    return redirect(url_for('admin_view',code=code))

@app.route('/<code>/clear_notes', methods=['POST'])
def clear_notes(code):
    print('trying to reset')
    game = sessions.get(code)
    if not game:
        return render_template("session_not_found.html"), 404
    game['notes'] = []
    save_data()
    return redirect(url_for('admin_view',code=code))

@app.route('/<code>/upload_csv', methods=['POST'])
def upload_csv(code):
    print('trying to reset')
    game = sessions.get(code)
    if not game:
        return render_template("session_not_found.html"), 404
    if 'file' not in request.files:
        print("no file part in request")
        return redirect(url_for('admin_view',code=code))

    file = request.files['file']
    if file.filename == '':
        print('no selected file')
        return redirect(url_for('admin_view',code=code))
    if file and file.filename.endswith('.csv'):
        filepath = os.path.join('uploads', file.filename)
        file.save(filepath)
        print(f"uploaded csv file: {filepath}")
        import_csv(code, filepath)
        save_data()
    return redirect(url_for('admin_view',code=code))

if __name__ == '__main__':
    threading.Thread(target=cleanup_sessions, daemon=True).start()
    app.run(debug=True)
