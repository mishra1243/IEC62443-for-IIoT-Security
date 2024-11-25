from flask import Flask, request, jsonify, render_template_string, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import psutil
import threading
import time
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'superadmin'  # Change this to a random secret key

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id):
        self.id = id

# Replace this with a secure method to store passwords (e.g., database)
users = {
    'superadmin': generate_password_hash('superadmin_password')
}

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

pending_requests = []
request_history = []

def get_sudo_status():
    with open('/home/superadmin/sudo_control.txt', 'r') as f:
        return f.read().strip() == '1'

def update_sudo_status(status):
    with open('/home/superadmin/sudo_control.txt', 'w') as f:
        f.write(str(int(status)))

def remove_sudo_access():
    time.sleep(300)  # Wait for 5 minutes
    update_sudo_status(False)
    print("Admin's sudo access has been revoked after 5 minutes.")

def get_active_ssh_sessions(username='z004ymtp'):
    sessions = []
    for proc in psutil.process_iter(attrs=['pid', 'name', 'username', 'cmdline']):
        try:
            if proc.info['username'] == username and 'ssh' in proc.info['name'].lower():
                print(f"Found SSH Process: {proc.info}")  # Debug line
                sessions.append({
                    'pid': proc.info['pid'],
                    'name': proc.info['name'],
                    'cmdline': proc.info['cmdline'],
                    'ip': proc.info['cmdline'][-1] if proc.info['cmdline'] else 'N/A'
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return sessions

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username in users and check_password_hash(users[username], password):
            login_user(User(username))
            return redirect(url_for('admin_panel'))
        return 'Invalid username or password'
    return render_template_string('''
        <form method="post">
            Username: <input type="text" name="username"><br>
            Password: <input type="password" name="password"><br>
            <input type="submit" value="Login">
        </form>
    ''')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/request_access', methods=['POST'])
def request_access():
    user = request.json.get('user')
    if user:
        pending_requests.append(user)
        return jsonify({"message": "Request received"}), 200
    return jsonify({"message": "Invalid request"}), 400

@app.route('/admin_panel')
@login_required
def admin_panel():
    active_sessions = get_active_ssh_sessions()
    sudo_status = get_sudo_status()
    return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Superadmin Panel</title>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.0/jquery.min.js"></script>
            <style>
                body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f0f0f0; }
                .container { display: flex; flex-direction: column; }
                .section { background-color: white; padding: 20px; border-radius: 10px; margin: 10px; }
                table { width: 100%; border-collapse: collapse; }
                th, td { border: 1px solid #ccc; padding: 10px; text-align: left; }
                button { margin-left: 10px; }
                .logout { position: absolute; top: 10px; right: 10px; }
            </style>
            <script>
                function updateDashboard() {
                    $.get('/get_dashboard_data', function(data) {
                        $('#sudo-status').text(data.sudo_status ? 'Sudo: Active' : 'Sudo: Inactive');
                        $('#requests').html(data.pending_requests.map(user => 
                            `<li>${user} <button onclick="handleRequest('${user}', true)">Accept</button> <button onclick="handleRequest('${user}', false)">Reject</button></li>`
                        ).join(''));
                        $('#history').html(data.request_history.map(req => 
                            `<li>${req.time} - ${req.user}: ${req.status}</li>`
                        ).join(''));
                    });
                }
                
                function handleRequest(user, accept) {
                    $.post('/handle_request', {user: user, accept: accept}, function() {
                        updateDashboard();
                    });
                }
                
                function terminateSession(pid) {
                    fetch(`/terminate_session/${pid}`, { method: 'POST' })
                        .then(response => {
                            if (response.ok) {
                                location.reload();  // Reload the page to refresh the session list
                            } else {
                                alert('Failed to terminate session');
                            }
                        });
                }

                setInterval(updateDashboard, 5000);
                updateDashboard();
            </script>
        </head>
        <body>
            <h1>Superadmin Panel</h1>
            <a href="{{ url_for('logout') }}" class="logout">Logout</a>
            <div class="container">
                <div class="section">
                    <h2>Sudo Status</h2>
                    <p id="sudo-status">{{ 'Sudo: Active' if sudo_status else 'Sudo: Inactive' }}</p>
                </div>
                <div class="section">
                    <h2>Active SSH Sessions for z004ymtp</h2>
                    <table>
                        <thead>
                            <tr>
                                <th>PID</th>
                                <th>Name</th>
                                <th>Command Line</th>
                                <th>IP Address</th>
                                <th>Action</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for session in active_sessions %}
                                <tr>
                                    <td>{{ session.pid }}</td>
                                    <td>{{ session.name }}</td>
                                    <td>{{ session.cmdline | join(' ') }}</td>
                                    <td>{{ session.ip }}</td>
                                    <td><button onclick="terminateSession({{ session.pid }})">Terminate</button></td>
                                </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
                <div class="section">
                    <h2>Pending Requests:</h2>
                    <ul id="requests"></ul>
                </div>
                <div class="section">
                    <h2>Recent Request History:</h2>
                    <ul id="history"></ul>
                </div>
            </div>
        </body>
        </html>
    ''', active_sessions=active_sessions, sudo_status=sudo_status)

@app.route('/get_dashboard_data')
@login_required
def get_dashboard_data():
    return jsonify({
        "sudo_status": get_sudo_status(),
        "pending_requests": pending_requests,
        "request_history": request_history[-5:]  # Get the last 5 requests
    })

@app.route('/handle_request', methods=['POST'])
@login_required
def handle_request():
    user = request.form.get('user')
    accept = request.form.get('accept') == 'true'
    
    if user in pending_requests:
        pending_requests.remove(user)
        
        status = "Approved" if accept else "Rejected"
        request_history.append({
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "user": user,
            "status": status
        })
        
        if accept:
            update_sudo_status(True)
            threading.Thread(target=remove_sudo_access).start()
    
    return '', 204

@app.route('/terminate_session/<int:pid>', methods=['POST'])
@login_required
def terminate_session(pid):
    try:
        process = psutil.Process(pid)
        process.terminate()  # You can use process.kill() for a forceful termination
        return '', 204
    except psutil.NoSuchProcess:
        return 'Process not found', 404
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')  # Change to your specific IP if needed