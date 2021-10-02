from PIL import Image
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
import json, requests, os

def get_app_config_data_from_key_vault():

    msi_endpoint = os.environ.get("MSI_ENDPOINT")
    msi_secret = os.environ.get("MSI_SECRET")
    token_auth_uri = f"{msi_endpoint}?resource=https://vault.azure.net&api-version=2017-09-01"
    head_msi = {'Secret': msi_secret}
    resp = requests.get(token_auth_uri, headers=head_msi)
    access_token = resp.json()['access_token']
    con_str = "https://krassykeyvault.vault.azure.net/secrets/connstr?api-version=2016-10-01"
    app_config = "https://krassykeyvault.vault.azure.net/secrets/data?api-version=2016-10-01"
    headers = {'Authorization': 'Bearer {}'.format(access_token)}
    constr = requests.get(con_str, headers=headers).json()
    app_data = requests.get(app_config, headers=headers).json()
    constr = constr.get('value')
    app_data = json.loads(app_data.get('value'))
    return constr, app_data

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