from flask import render_template, request
from app import app
from qkd.bb84 import bb84_protocol
from qkd.utils import xor_encrypt, xor_decrypt

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        message = request.form['message']
        key = bb84_protocol(32)  # Generate a 32-bit key using BB84
        encrypted = xor_encrypt(message, key)
        decrypted = xor_decrypt(encrypted, key)
        return render_template('result.html', 
                               original=message, 
                               encrypted=encrypted, 
                               decrypted=decrypted, 
                               key=key)
    return render_template('index.html')


@app.route('/decrypt', methods=['GET', 'POST'])
def decrypt():
    if request.method == 'POST':
        encrypted = request.form['encrypted']
        key = request.form['key']
        decrypted = xor_decrypt(encrypted, key)
        return render_template('decrypt.html', decrypted=decrypted, encrypted=encrypted, key=key)
    return render_template('decrypt.html')
