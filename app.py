from flask import Flask, render_template

app = Flask("NLP", template_folder='templates')

@app.route('/')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
