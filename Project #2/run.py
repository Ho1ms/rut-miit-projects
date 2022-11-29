from app import  socketio, app, config
import os
if __name__ == '__main__':
    socketio.run(app, '0.0.0.0',port=3001, debug=True, **({'allow_unsafe_werkzeug':True} if os.name != 'nt' else {}))
