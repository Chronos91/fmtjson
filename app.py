import os
import json
from flask import Flask, render_template, request

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)


def flatten_cookies(input_file):
    try:
        with open(input_file, "r", encoding="utf-8", errors="ignore") as file:
            data = json.load(file)  # Try loading JSON
    except json.JSONDecodeError as e:
        print(f"JSON Decode Error: {e}")
        return {"error": "Invalid JSON format. Ensure your file contains valid JSON."}

    # Remove unwanted fields
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
                    "httpOnly": attributes.get("HttpOnly", False),
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
            
            # Try to process the file
            try:
                flattened_result = flatten_cookies(file_path)
                if isinstance(flattened_result, dict) and "error" in flattened_result:
                    return flattened_result["error"], 400  # Return JSON error message
            except Exception as e:
                print(f"Error processing file: {e}")
                return f"Unexpected error: {str(e)}", 500  # Catch any unknown errors

            return render_template("index.html", result=flattened_result)

    return render_template("index.html", result=None)


# Run the app using the PORT from Vercel
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
