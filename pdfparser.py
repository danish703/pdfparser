from flask import Flask, escape, request,render_template,flash,redirect
from forms import FileForm
import PyPDF2 as p2
import pdftotext
from werkzeug.utils import secure_filename
from parse import Parse
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = '5b6429d29520c532b5e045c887bf8b32'

@app.route('/',methods=['GET','POST'])
def hello():
    form = FileForm()
    if form.validate_on_submit():
        f = request.files['file']
        f.save(secure_filename('test.pdf'))
        Parse()
        flash('Parsed successfully','success')
        return redirect('/')
    return render_template('index.html',title='Pdf Parser',form=form)



if __name__ == '__main__':
    app.run(debug=True)