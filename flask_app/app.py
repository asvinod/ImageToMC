
from flask import Flask, render_template, url_for, send_from_directory
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SubmitField
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
load_dotenv()
import os, zipfile, shutil
from generate_blocks import image_to_mc 


# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'uploads')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


# Form for uploading image & MC World (Zip File)
class UploadForm(FlaskForm):
    photo = FileField(
        validators=[FileAllowed(['jpg','png','jpeg','gif']), FileRequired()]
    )
    world = FileField(
        validators=[FileAllowed(['zip']), FileRequired()]
    )
    submit = SubmitField('Upload')


# Main route for uploading files and processing the image/world
@app.route("/", methods=['GET','POST'])
def upload():
    form = UploadForm()
    file_url = None
    modified_world_url = None

    # When the form is submitted and valid
    if form.validate_on_submit():
        # Save the uploaded image file
        img_file = form.photo.data
        img_filename = secure_filename(img_file.filename)
        img_path = os.path.join(app.config['UPLOAD_FOLDER'], img_filename)
        img_file.save(img_path)
        file_url = url_for('get_file', filename=img_filename)

        # Save the uploaded Minecraft world zip file
        world_file = form.world.data
        world_zip_filename = secure_filename(world_file.filename)
        world_zip_path = os.path.join(app.config['UPLOAD_FOLDER'], world_zip_filename)
        world_file.save(world_zip_path)

        # Prepare a temporary directory to extract the world zip
        temp_world_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'world_tmp')
        if os.path.exists(temp_world_dir):
            shutil.rmtree(temp_world_dir)  # Remove if it already exists
        os.makedirs(temp_world_dir, exist_ok=True)
        # Extract the world zip file
        with zipfile.ZipFile(world_zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_world_dir)

        # Find the world folder inside the extracted directory
        folders = [f for f in os.listdir(temp_world_dir) if os.path.isdir(os.path.join(temp_world_dir, f))]
        if not folders:
            raise ValueError("No world folder found inside zip!")
        world_folder = os.path.join(temp_world_dir, folders[0])

        # Call the function to convert the image to Minecraft blocks in the world
        image_to_mc(img_path, world_folder)

        # Zip the modified world folder for download
        modified_zip_path = os.path.join(app.config['UPLOAD_FOLDER'], 'modified_world.zip')
        shutil.make_archive(modified_zip_path.replace('.zip',''), 'zip', world_folder)
        modified_world_url = url_for('get_file', filename='modified_world.zip')

        # Clean up temporary files
        shutil.rmtree(temp_world_dir)
        os.remove(world_zip_path)

    # Render the upload form and show download links if available
    return render_template('index.html', form=form, file_url=file_url, modified_world_url=modified_world_url)


# Route to serve uploaded and generated files
@app.route('/uploads/<filename>')
def get_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Run the Flask app in debug mode if this script is executed directly
if __name__ == "__main__":
    app.run(debug=True)
