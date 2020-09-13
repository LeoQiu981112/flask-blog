from flask import url_for
from flask_login import current_user
from PIL import Image
from flask_mail import Message
import os
import secrets
from flaskwebapp import app, mail


# save uploaded picture to filesystem
def save_picture(form_picture):
    # rename picture
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static', 'profile_pics', picture_fn)
    # resize img
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    # remove previous picture
    prev_picture = os.path.join(app.root_path, 'static', 'profile_pics', current_user.image_file)
    if os.path.exists(prev_picture):
        os.remove(prev_picture)
    return picture_fn


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('password reset request',
                  sender='noreply@demo.com',
                  recipients=[user.email])
    msg.body = f""" to reset password, visit the following link: 
    {url_for('reset_token',token=token, _external=True)}
if you did not make this request then simply ignore this email
    """
    mail.send(msg)
