import os
import uuid
import base64
from flask import render_template, request, send_from_directory, current_app
from app import app
from qkd.bb84 import bb84_protocol
from qkd.utils import xor_encrypt, xor_decrypt, gibberish

UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


# Encrypt route: called when user submits a message to encrypt
@app.route("/encrypt", methods=["POST"])
def encrypt_message():
    message = request.form.get("message", "")
    if not message:
        return render_template("index.html", error="Please enter a message to encrypt.")

    # generate quantum key
    key = bb84_protocol(32)

    # XOR-encrypt (returns a string with possibly non-printable chars)
    encrypted_raw = xor_encrypt(message, key)

    # For safe copy/paste: convert to bytes via latin1 and base64 encode
    encrypted_bytes = encrypted_raw.encode("latin-1")
    encrypted_b64 = base64.b64encode(encrypted_bytes).decode("ascii")

    # A "gibberish" visual we show in UI so the ciphertext looks like random symbols
    gib_display = gibberish(encrypted_raw)

    return render_template(
        "encrypt_result.html",
        original=message,
        encrypted_gib=gib_display,
        encrypted_b64=encrypted_b64,
        key=key
    )


# Decrypt page (GET shows form; POST processes and shows result)
@app.route("/decrypt", methods=["GET", "POST"])
def decrypt_message():
    if request.method == "GET":
        return render_template("decrypt.html")

    # POST: get base64 encrypted string and key
    encrypted_b64 = request.form.get("encrypted_message", "").strip()
    key = request.form.get("quantum_key", "").strip()

    if not encrypted_b64:
        return render_template("decrypt.html", error="Please paste the encrypted Base64 string.")
    if not key:
        return render_template("decrypt.html", error="Please enter the quantum key used for encryption.")

    try:
        # decode base64 -> bytes -> latin1 string (original xor_encrypt output)
        encrypted_bytes = base64.b64decode(encrypted_b64)
        encrypted_raw = encrypted_bytes.decode("latin-1")

        # decrypt using xor_decrypt (symmetric)
        decrypted = xor_decrypt(encrypted_raw, key)
    except Exception as e:
        return render_template("decrypt.html", error=f"Decryption failed: {e}")

    return render_template("decrypt_result.html", encrypted_b64=encrypted_b64, key=key, decrypted_message=decrypted)


# --- file transfer routes left functionally the same (unchanged) ---
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
