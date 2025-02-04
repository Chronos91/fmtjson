import os
import json
from flask import Flask, render_template, request

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


def flatten_cookies(input_file):
    with open(input_file, "r", encoding="utf-8") as file:
        data = json.load(file)

    fields_to_remove = ["id", "phishlet", "landing_url", "username", "password", "custom", "body_tokens", "http_tokens"]
    for field in fields_to_remove:
        data.pop(field, None)

    flat_list = []
    if "tokens" in data:
        for domain, cookies in data["tokens"].items():
            for name, attributes in cookies.items():
                flat_list.append({
                    "domain": domain.lstrip("."),
                    "name": attributes.get("Name", ""),
                    "path": attributes.get("Path", "/"),
                    "value": attributes.get("Value", ""),
                    "httpOnly": attributes.get("HttpOnly", False)
                })

    return flat_list


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if "file" not in request.files:
            return "No file part", 400

        file = request.files["file"]
        if file.filename == "":
            return "No selected file", 400

        if file:
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
            file.save(file_path)
            try:
                flattened_result = flatten_cookies(file_path)
            except json.JSONDecodeError:
                return "Invalid JSON file", 400

            return render_template("index.html", result=flattened_result)

    return render_template("index.html", result=None)


# Run the app using the PORT from Vercel
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
