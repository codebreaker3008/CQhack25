import os
from flask import render_template, request, redirect, url_for, send_from_directory
from app import app
from qkd.bb84 import bb84_protocol
from qkd.utils import xor_encrypt, xor_decrypt, gibberish
import uuid

UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        message = request.form["message"]
        key = bb84_protocol(32)
        encrypted = xor_encrypt(message, key)
        gibberish_msg = gibberish(encrypted)
        return render_template("encrypt_result.html", original=message, encrypted=gibberish_msg, key=key)
    return render_template("index.html")

@app.route("/decrypt", methods=["GET", "POST"])
def decrypt():
    if request.method == "POST":
        encrypted = request.form["encrypted"]
        key = request.form["key"]
        real_encrypted = ''.join(filter(str.isalnum, encrypted))[:len(key)]  # simplified
        decrypted = xor_decrypt(real_encrypted, key)
        return render_template("decrypt_result.html", decrypted=decrypted, key=key)
    return render_template("decrypt.html")

@app.route("/transfer", methods=["GET", "POST"])
def transfer():
    if request.method == "POST":
        file = request.files["file"]
        if file:
            filename = f"{uuid.uuid4()}_{file.filename}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            key = bb84_protocol(64)
            with open(file_path, "rb") as f:
                content = f.read()

            encrypted_content = bytes([b ^ ord(key[i % len(key)]) for i, b in enumerate(content)])
            enc_filename = f"enc_{filename}"
            enc_path = os.path.join(app.config['UPLOAD_FOLDER'], enc_filename)
            with open(enc_path, "wb") as f:
                f.write(encrypted_content)

            return render_template("transfer_result.html", original=filename, encrypted=enc_filename, key=key)
    return render_template("transfer.html")

@app.route("/download/<filename>")
def download(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename, as_attachment=True)

@app.route("/decrypt-file", methods=["GET", "POST"])
def decrypt_file():
    if request.method == "POST":
        file = request.files["file"]
        key = request.form["key"]
        if file and key:
            filename = f"{uuid.uuid4()}_dec_{file.filename}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            encrypted_content = file.read()
            decrypted_content = bytes([b ^ ord(key[i % len(key)]) for i, b in enumerate(encrypted_content)])

            with open(file_path, "wb") as f:
                f.write(decrypted_content)

            return render_template("decrypted_file_result.html", filename=filename)
    return render_template("decrypt_file.html")
