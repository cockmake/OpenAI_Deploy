import ctypes
import inspect
import time
from threading import Thread
from flask import Flask, request
from flask_cors import CORS
from flask_socketio import SocketIO
import openai
from openai.error import RateLimitError
openai.api_key = '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'
# 不要暴露这个api_key 相当于账号密码的作用

def _async_raise(tid, exctype):
    tid = ctypes.c_long(tid)
    if not inspect.isclass(exctype):
        exctype = type(exctype)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
    if res == 0:
        print("该线程已经被销毁")
    elif res != 1:
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        print("销毁失败")


def stop_thread(thread):
    _async_raise(thread.ident, SystemExit)


app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

user_th = {

}
user_time = {

}

def sendAns(prompt, user_id):
    body = {
        'model': "text-davinci-003",
        'prompt': prompt,
        'max_tokens': 2000,
        'n': 1,
        'top_p': 0.7,
        'temperature': 0.7
    }
    try:
        resp = openai.Completion.create(**body)
    except RateLimitError:
        time.sleep(2)
        resp = openai.Completion.create(**body)

    socketio.emit('recAns', data={'msg': data['choices'][0]['text']}, to=user_id)

@app.route('/getAns/<string:user_id>', methods=['POST'])
def getAns(user_id):
    # 这里必须要使用线程进行推送
    if user_time.get(user_id, 0) >= 10:
        return {'msg': 'failure'}
    prompt = request.json['prompt']
    if user_th.get(user_id, None) is not None:
        stop_thread(user_th[user_id])
    user_th[user_id] = Thread(target=sendAns, args=[prompt, user_id])
    user_th[user_id].start()
    user_time[user_id] = user_time.get(user_id, 0) + 1
    return {"msg": 'success'}
@socketio.on('message')
def handle_message(message):
    print('收到的消息: ' + message['data'])

@socketio.on('connect')
def connect():
    print("连接成功")


@socketio.on('disconnect')
def disconnect():
    print("断开连接")

@app.route('/disconnect/<string:user_id>')
def dis(user_id):
    if user_th.get(user_id, None) is not None:
        stop_thread(user_th[user_id])
        user_th.pop(user_id)
    if user_time.get(user_id, None) is not None:
        user_time.pop(user_id)
    print(user_id, '信息已被重置')
    return {"msg": 'success'}

@app.route('/reSet', methods=['GET'])
def reSetTimes():
    ip = request.args.get('user_ip', None)
    if ip is None:
        user_time.clear()
        for key in user_th.keys():
            stop_thread(user_th[key])
        user_th.clear()
    else:
        user_time[ip] = 0
    return {'msg': 'success'}

@app.route('/users')
def getU():
    return user_time

if __name__ == '__main__':
    socketio.run(host='0.0.0.0', port=80, app=app)
