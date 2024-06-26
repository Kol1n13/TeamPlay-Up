from flask import Flask, request, render_template, redirect, url_for
from flask_socketio import join_room, leave_room
from flask_socketio import SocketIO, emit
import database
import dota_db
import message_db


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

@app.route('/', methods=['GET', 'POST'])
def main():
    return render_template('main_page.html', error=False) 

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users = database.get_dictionary_of_users()
        if username in users and users[username][0] == password:
            response = redirect('/choose')
            response.set_cookie('nickname', str(username))
            response.set_cookie('is_authorized', "true")
            return response  # Redirect to the choose page after successful login
        else:
            error_message = 'Incorrect username or password. Please try again.'
            return render_template('login.html', error=True, error_message=error_message)
    else:
        return render_template('login.html', error=False)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        dict = database.get_dictionary_of_users()
        if username in dict.keys():
            error_message = 'Nickname already exists. Please choose a different one.'
            return render_template('registration.html', error=True, error_message=error_message)
        else:
            database.add_user(username, password)
            return redirect(url_for('main'))  # Redirect to the main page after successful registration
    return render_template('registration.html', error=False)

@app.route('/choose', methods=['GET', 'POST'])
def choose():
    return render_template('choose_desteny.html')  # Redirect to the login page if not authorized

@app.route('/dota2', methods=['GET', 'POST'])
def dota2():
    print(database.get_dictionary_of_users())
    print(request.cookies["nickname"])
    username = request.cookies["nickname"]
    user_id = database.get_user_id_by_login(username)
    print(request.cookies)
    dota_applications = dota_db.get_dictionary_of_quest()
    print(user_id)
    print(dota_applications.values())
    if any(user_id == application[0] for application in dota_applications.values()):
        default_application = {}
        kkk = 0
        for key in dota_applications:
            if user_id == dota_applications[key][0]:
                default_application = dota_applications[key]
                kkk = key
                break
        print(default_application)
        return render_template('dota2_alt.html', user_id=user_id, default_application=default_application, dota_applications=dota_applications, username=kkk)
    else:
        return render_template('dota.html', dota_applications=dota_applications, user_id=user_id)

@app.route('/wot', methods=['GET'])
def wot():
        print(database.get_dictionary_of_users())
        print(request.cookies["nickname"])
        username = request.cookies["nickname"]
        user_id = database.get_user_id_by_login(username)
        print(request.cookies)
        dota_applications = dota_db.get_dictionary_of_quest()
        print(user_id)
        print(dota_applications.values())
        return render_template('wot.html', applications=dota_applications, user_id=user_id)

@app.route('/pubg', methods=['GET'])
def pubg():
    username = request.cookies["nickname"]
    user_id = database.get_user_id_by_login(username)
    return render_template('pubg.html', applications={}, user_id=user_id)

@app.route('/cs2', methods=['GET'])
def cs2():
    username = request.cookies["nickname"]
    user_id = database.get_user_id_by_login(username)
    return render_template('cs2.html', applications={}, user_id=user_id)

@app.route('/apex', methods=['GET'])
def apex():
    username = request.cookies["nickname"]
    user_id = database.get_user_id_by_login(username)
    return render_template('apex.html', applications={}, user_id=user_id)

@app.route('/heartstone', methods=['GET'])
def heartstone():
    username = request.cookies["nickname"]
    user_id = database.get_user_id_by_login(username)
    return render_template('heartstone.html', applications={}, user_id=user_id)

@app.route('/valorant', methods=['GET'])
def valorant():
    username = request.cookies["nickname"]
    user_id = database.get_user_id_by_login(username)
    return render_template('valorant.html', applications={}, user_id=user_id)

@app.route('/overwatch', methods=['GET'])
def overwatch():
    username = request.cookies["nickname"]
    user_id = database.get_user_id_by_login(username)
    return render_template('overwatch.html', applications={}, user_id=user_id)

@app.route('/add_application', methods=['POST'])
def add_application():
    if request.method == 'POST':
        user_nickname = request.form['name']
        username = request.cookies["nickname"]
        user_id = database.get_user_id_by_login(username)
        user_MMR = int(request.form['rating'])
        user_comment = request.form['comment']
        user_pos = request.form['position']
        dota_db.add_application(user_id, user_MMR, user_nickname, user_comment, user_pos)
        return redirect(url_for('dota2'))
    
@app.route('/delete_application', methods=['POST'])
def delete_application():
    user_id = request.form['user_id']
    dota_db.delete_application(user_id)
    return redirect(url_for('dota2'))

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    return render_template('chat_base.html')

@app.route('/all_chats', methods=['GET', 'POST'])
def all_chats():
    return render_template('login.html')

@app.route('/chat/<int:sender_id>/with/<int:receiver_id>', methods=['GET', 'POST'])
def chat_with_user(sender_id, receiver_id):
    chat_id = f"{min(sender_id, receiver_id)}_{max(sender_id, receiver_id)}"
    chat_history = message_db.get_chat_history(chat_id)
    return render_template('chat_with_user.html', chat_id=chat_id, sender_id=sender_id, receiver_id=receiver_id, chat_history=chat_history, get_username_by_id=database.get_user_login_by_id)

@app.route('/user_chats')
def user_chats():
    if 'nickname' not in request.cookies:
        return redirect(url_for('login'))
    username = request.cookies['nickname']
    user_id = database.get_user_id_by_login(username)
    user_chats = message_db.get_chat_partner_by_id(user_id)  # Получаем список чатов пользователя
    data = message_db.get_chat_partner_by_id1(user_id)

    chat_links = []
    user_chats = [x[0].split('_') for x in data]
    user_chats = [qqq[0] if str(user_id) != qqq[0] else qqq[1] for qqq in user_chats]
    messages = [x[1] for x in data]
    messages.reverse()

    for partner_id in user_chats:
        chat_link = url_for('chat_with_user', sender_id=user_id, receiver_id=partner_id)
        partner_username = database.get_user_login_by_id(partner_id)
        chat_links.append((chat_link, partner_username, messages[-1]))
        messages.pop()
    return render_template('user_chats.html', chat_links=chat_links)


@socketio.on('message')
def handle_message(data):
    print(data)
    chat_id = data['chat_id']
    sender_id = data['sender_id']
    message = data['message']
    message_db.add_message(chat_id, sender_id, message)
    sender_username = database.get_user_login_by_id(sender_id)
    data['sender_username'] = sender_username
    emit('message', data, room=chat_id)

@socketio.on('connect')
def on_join(data):
    chat_id = data['chat_id']
    join_room(chat_id)

@socketio.on('disconnect')
def on_leave(data):
    chat_id = data['chat_id']
    leave_room(chat_id)


if __name__ == '__main__':
    socketio.run(app, host="127.0.0.1", port=5000, allow_unsafe_werkzeug=True)
