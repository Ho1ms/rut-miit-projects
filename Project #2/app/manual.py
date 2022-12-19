from . import app
from flask import render_template

@app.route('/manual')
def manual():
    return render_template('manual.html')
    
@app.route('/career/conditions')
def conditions():
    return render_template('conditions.html')