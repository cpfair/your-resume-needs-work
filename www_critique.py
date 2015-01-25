from flask import Flask, render_template, request
import random
app = Flask(__name__)


@app.route('/')
def resume_upload():
    return render_template('upload.html')

@app.route('/upload', methods=['GET', 'POST'])
def resume_critique():
    from critique import Critiquer
    ct = Critiquer()
    if request.method == 'POST':
        file = request.files['file']
        file.save("static/uploaded.pdf")
    problems_list = ct.critique("static/uploaded.pdf")

    return render_template('critique.html', problems=problems_list, random=random.random() * 100)

if __name__ == '__main__':
    app.run(debug=True)
