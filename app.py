from flask import Flask, flash, redirect, render_template, request, session, abort, send_from_directory, url_for
import json
import os
from os.path import join, dirname, realpath
from werkzeug.utils import secure_filename
import sys
from skimage import io
from sklearn.cluster import KMeans
import numpy as np
from flask import Flask, flash, redirect, render_template, request, session, abort, send_from_directory

UPLOAD_FOLDER = 'static'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=["POST", "GET"])
def index():
    if request.method == "POST":
         # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # reading filename
            filenamex = 'static/'+filename
            # reading the image
            image = io.imread(filenamex)
             
            # preprocessing
            rows, cols = image.shape[0], image.shape[1]
            image = image.reshape(rows * cols, 3)

            # modelling
            print('Compressing...')
            print('Note: This can take a while for a large image file.')
            kMeans = KMeans(n_clusters = 16)
            kMeans.fit(image)

            # getting centers and labels
            centers = np.asarray(kMeans.cluster_centers_, dtype=np.uint8)
            labels = np.asarray(kMeans.labels_, dtype = np.uint8)
            labels = np.reshape(labels, (rows, cols))
            print('Almost done.')

            # reconstructing the image
            newImage = np.zeros((rows, cols, 3), dtype=np.uint8)
            for i in range(rows):
                for j in range(cols):
                        # assinging every pixel the rgb color of their label's center
                        newImage[i, j, :] = centers[labels[i, j], :]
            io.imsave(filenamex.split('.')[0] + '-compressed.png', newImage)
            data = request.form['namaFile']

            print('Image has been compressed sucessfully.')
            return render_template('compress.html', foto = data );
    else:
        return render_template('index.html')

if __name__ == "__main__":
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'

    app.run()