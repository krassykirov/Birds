from PIL import Image
import json, requests, os
from msrestazure.azure_active_directory import AADTokenCredentials
import adal
from .signals import *
from .models import BirdUser
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def get_cred_from_key_vault():
    authority_host_uri = 'https://login.microsoftonline.com/{domain}.onmicrosoft.com'
    resource_uri = 'https://vault.azure.net'
    CLIENT_ID = ''
    CLIENT_SECRET = ''
    context = adal.AuthenticationContext(authority_host_uri, api_version=None)
    mgmt_token = context.acquire_token_with_client_credentials(resource_uri, CLIENT_ID, CLIENT_SECRET)
    credentials = AADTokenCredentials(mgmt_token, CLIENT_ID)
    token = credentials.token['access_token']
    print('token:', token)
    user = "https://{KEYVAULT}.vault.azure.net/secrets/user?api-version=2016-10-01"
    password = "https://{KEYVAULT}.vault.azure.net/secrets/passwd?api-version=2016-10-01"
    headers = {'Authorization': 'Bearer {}'.format(token)}
    user = requests.get(user, headers=headers).json()
    passwd = requests.get(password, headers=headers).json()
    print('user_value,pass_value', user, passwd)
    user = user.get('value')
    password = passwd.get('value')
    return user, password

#@receiver(post_save,sender=BirdUser)
def send_email(sender, instance, created, **kwargs):
    if created:
        u, p = get_cred_from_key_vault()
        print(f'{instance.email} have been created!')
        s = smtplib.SMTP(host='smtp-mail.outlook.com', port=587)
        s.starttls()
        s.login(user=u,password=p)

        msg = MIMEMultipart()
        message = f"Signal from {sender} has been received received! f'{instance.email} have been created!'"
        msg['From'] = f'{u}'
        msg['To'] = '{}@{}).com'
        msg['Subject'] = "This is a TEST"

        msg.attach(MIMEText(message, 'plain'))
        s.send_message(msg)

def make_thumbnail(filename):
    allowed_types = ['jpg', 'jpeg', 'gif']
    file = filename
    file_ext = file.split('.')[-1]
    file = file.split('.')[1::-1][1]
    image = Image.open(filename)
    print('size:', image.size)
    width, height = image.size

    try:
        if file_ext in allowed_types:
            image = Image.open(filename)
            if width > 800 or height > 600:
                image.thumbnail((width / 3, height / 3))
                print('thumb_size:', image.size)
                image.save(f'{file}_thumbnail.jpg', quality=95)
                path = f'{file}_thumbnail.jpg'
                return path
            else:
                image.thumbnail((width / 2, height / 2))
                print('thumb_size:', image.size)
                image.save(f'{file}_thumbnail.jpg', quality=95)
                path = f'{file}_thumbnail.jpg'
                return path

        elif file_ext == 'png':
            print('Entering png')
            image = Image.open(filename)
            rgb_im = image.convert('RGB')
            if width > 800 or height > 600:
                rgb_im.thumbnail((width / 3, height / 3))
                print('thumb_size:', rgb_im.size)
                rgb_im.save(f'{file}_thumbnail.jpg', quality=95)
                path = f'{file}_thumbnail.jpg'
                return path
            else:
                rgb_im.thumbnail((width / 2, height / 2))
                print('thumb_size:', rgb_im.size)
                rgb_im.save(f'{file}_thumbnail.jpg', quality=95)
                path = f'{file}_thumbnail.jpg'
                return path

    except Exception as e:
        print(f'Something went wrong, Unable to save thumbnail, Details: {e}')
        pass

def filter_form_errors(error_msg):
    ctx = json.loads(error_msg)
    message = ''
    if ctx.get('url'):
        message =  ctx['url'][0].get('message')
    elif ctx.get('bird_name'):
        message =  ctx['bird_name'][0].get('message')
    elif ctx.get('photo'):
        message =  ctx['photo'][0].get('message')
    elif ctx.get('image'):
        message =  ctx['image'][0].get('message')
    elif ctx.get('song_name'):
        message =  ctx['song_name'][0].get('message')

    return message

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    HTTP_USER_AGENT = request.META.get('HTTP_USER_AGENT')
    print('HTTP_USER_AGENT', HTTP_USER_AGENT)
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


#Resizes an image and keeps aspect ratio. Set mywidth to the desired with in pixels.

# import PIL
# from PIL import Image
#
# mywidth = 300
#
# img = Image.open('someimage.jpg')
# wpercent = (mywidth/float(img.size[0]))
# hsize = int((float(img.size[1])*float(wpercent)))
# img = img.resize((mywidth,hsize), PIL.Image.ANTIALIAS)
# img.save('resized.jpg')