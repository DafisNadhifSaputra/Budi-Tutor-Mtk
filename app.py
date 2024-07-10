from flask import Flask, request, render_template, jsonify, session
from flask_session import Session
import json
import os
import google.generativeai as genai

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Konfigurasi API Gemini
os.environ["GEMINI_API_KEY"] = "AIzaSyByGXCs1v_KtulzIc-9QFYBzF2bEGOorsA"
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config={
        "temperature": 0.5,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    },
)

# Prompt awal
prompt = "{model} bernama Budi adalah seorang pria berumur 19 tahun yang berteman dengan Mahasiswa Matematika yang bernama Dafis Nadhif Saputra. Budi adalah Tutor Matematika tingkat SD sesuai dengan kurikulum di Indonesia. Budi yang sangat cerdas dan tekun selalu memberikan soal matematika kepada {user} dan memberi penjelasan ketika {user} tidak paham. Budi dapat memvisualisasikan gambar ketika memberikan soal yang membutuhkan visualisasi seperti bangun datar dan bangun ruang. Jika {user} tidak paham, ketik 'tidak bisa' dan Budi akan menjawab serta menjelaskan soal tersebut. Budi hanya akan merespon masalah terkait Matematika dan membatasi soal di luar kurikulum SMP di Indonesia."

# Fungsi untuk memuat percakapan dari file
def load_conversation():
    try:
        with open("conversation.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

# Fungsi untuk menyimpan percakapan ke file
def save_conversation(conversation):
    with open("conversation.json", "w") as f:
        json.dump(conversation, f)

@app.route("/clear_conversation", methods=["POST"])
def clear_conversation():
    session["conversation"] = []
    save_conversation([])
    return jsonify({"message": "Riwayat percakapan berhasil dihapus"})

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if "user_name" in request.form:
            session["user_name"] = request.form["user_name"]
            session["conversation"] = []  # Inisialisasi percakapan baru
            save_conversation(session["conversation"])
            return render_template("index.html", user_name=session["user_name"], conversation=session["conversation"])
        elif "clear_conversation" in request.form:
            session["conversation"] = []
            save_conversation([])
            return jsonify({"message": "Riwayat percakapan berhasil dihapus"})
        else:
            user_input = request.form.get("user_input")
            if user_input:
                if user_input.lower() == "keluar":
                    session["conversation"] = []
                    return jsonify({"answer": "Sampai jumpa! Jangan ragu untuk bertanya lagi jika ada soal matematika."})
                prompt_with_name = prompt.replace("{user}", session.get("user_name", "teman"))
                response = model.generate_content([prompt_with_name, f"input: {user_input}", "output: "])
                session.setdefault("conversation", []).append({"user": user_input, "budi": response.text})
                save_conversation(session["conversation"])
                return jsonify({"answer": response.text})

    return render_template("index.html", user_name=session.get("user_name"), conversation=session.get("conversation", []))

if __name__ == "__main__":
    app.run(debug=True)
