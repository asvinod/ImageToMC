
from flask import Flask, render_template, url_for, send_from_directory
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SubmitField
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
load_dotenv()
import os, zipfile, shutil
from generate_blocks import image_to_mc 


app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'uploads')
app.config['DEFAULTS_FOLDER'] = os.path.join(app.root_path, 'defaults')

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

class UploadForm(FlaskForm):
    photo = FileField(
        validators=[FileAllowed(['jpg','png','jpeg','gif']), FileRequired()]
    )
    world = FileField(
        validators=[FileAllowed(['zip'])]
    )
    submit = SubmitField('Upload')

@app.route("/", methods=['GET', 'POST'])
def upload():
    form = UploadForm()
    file_url = None
    modified_world_url = None

    if form.validate_on_submit():
        # --- Save uploaded image ---
        img_file = form.photo.data
        img_filename = secure_filename(img_file.filename)
        img_path = os.path.join(app.config['UPLOAD_FOLDER'], img_filename)
        img_file.save(img_path)
        file_url = url_for('get_file', filename=img_filename)

        # --- Handle world zip (uploaded or default) ---
        world_file = form.world.data
        if not world_file or world_file.filename == "":
            # Use default world zip (never delete this)
            world_zip_path = os.path.join(app.config['DEFAULTS_FOLDER'], "defaultsuperflat.zip")
            delete_after = False
        else:
            # Save uploaded world zip into uploads folder
            filename = secure_filename(world_file.filename)
            world_zip_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            world_file.save(world_zip_path)
            delete_after = True

        # --- Extract world zip ---
        temp_world_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'world_tmp')
        if os.path.exists(temp_world_dir):
            shutil.rmtree(temp_world_dir)
        os.makedirs(temp_world_dir, exist_ok=True)

        with zipfile.ZipFile(world_zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_world_dir)

        # --- Find valid world folder by checking for level.dat ---
        world_folder = None
        for f in os.listdir(temp_world_dir):
            candidate = os.path.join(temp_world_dir, f)
            if os.path.isdir(candidate) and os.path.exists(os.path.join(candidate, "level.dat")):
                world_folder = candidate
                break

        if not world_folder:
            shutil.rmtree(temp_world_dir)
            if delete_after:
                os.remove(world_zip_path)
            raise ValueError("No valid Minecraft world folder found in zip!")

        # --- Run your image → MC function ---
        image_to_mc(img_path, world_folder)

        # --- Re-zip modified world ---
        modified_zip_path = os.path.join(app.config['UPLOAD_FOLDER'], 'modified_world.zip')
        shutil.make_archive(modified_zip_path.replace('.zip', ''), 'zip', world_folder)
        modified_world_url = url_for('get_file', filename='modified_world.zip')

        # --- Cleanup ---
        shutil.rmtree(temp_world_dir)
        if delete_after:
            os.remove(world_zip_path)

    return render_template(
        'index.html',
        form=form,
        file_url=file_url,
        modified_world_url=modified_world_url
    )

@app.route('/uploads/<filename>')
def get_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    
@app.route('/examples')
def get_examples():
    return render_template('examples.html')

if __name__ == "__main__":
    app.run(port=8000, debug=True)
