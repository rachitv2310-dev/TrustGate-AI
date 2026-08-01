from flask import Flask, render_template, request
from backend.services.verification_service import verify_response

app = Flask(__name__,
            template_folder="frontend/templates",
            static_folder="frontend/static"
            )


@app.route("/")
def home():
    return render_template("index.html")



@app.route("/verify", methods=["GET", "POST"])
def verify():

    result = None

    if request.method == "POST":

        question = request.form.get("question")
        response = request.form.get("response")

        result = verify_response(question, response)

        print("\n========== VERIFICATION RESULT ==========")
        print(result)
        print("=========================================\n")

    return render_template("verify.html", result=result)


if __name__ == "__main__":
    app.run(debug=True)