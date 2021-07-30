import os
import secrets
from flask import url_for, current_app
from flask_mail import Message
from supply import mail
from PIL import Image

#Function to save picture
def save_picture(form_picture):
    #Randomize name of picture file
    random_hex = secrets.token_hex(8)
    #Get extension of image submitted
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/images', picture_fn)

    #Resize Image before Save
    output_size = (195, 158)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    #Save to path
    i.save(picture_path)
    return picture_fn



def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', sender='noreply@demo.com', recipients=[user.email])

    msg.body = f'''To reset your password, visit the following link:
{url_for('users.reset_password_request', token=token, _external=True)}

If you did not make this request then please ignore this email.
    '''
    mail.send(msg)

