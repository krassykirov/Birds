from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User,AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import ugettext_lazy as _
from .signals import *

import requests,os
import filetype

def validate_image(url):
    try:
        response = requests.head(url, allow_redirects=True) # ,timeout=0.1
    except requests.exceptions.ConnectionError:
        raise ValidationError('Image Url is invalid or does not exist!')
    if response.status_code != 200:
        raise ValidationError('Image Url is invalid or does not exist!')
    allowedMimeTypes = ['image/png', 'image/jpg', 'image/jpeg','image/gif']
    contentType = response.headers['content-type']
    if contentType not in allowedMimeTypes:
        raise ValidationError('Unknown MIME Type. Please enter a valid image URL (.jpg .jpeg .png .gif)')
    contentLength = int(response.headers['content-length'])
    if contentLength > 3000000:
        raise ValidationError('Image should be lower then 3MB')

def validate_audio(song_name):
    file = song_name
    kind = filetype.guess(file)
    allowedMimeTypes = ["audio/mpeg","audio/wav"]
    allowedFileExtension = ['mp3', 'wav']
    if file:
        if kind is None:
            raise ValidationError("Unknown file type! Please enter a valid audio file '.mp3' or '.wav' )")
        if kind.mime not in allowedMimeTypes and kind.extension not in allowedFileExtension:
            raise ValidationError("Please enter a valid audio file '.mp3' or '.wav' )")
        if file.size > 3000000:
            raise ValidationError('Audio File too large. Please select a file less than 3MB')
    else:
        return file

def validate_image_upload(image):
    file = image
    # kind = filetype.guess(file)
    # allowedMimeTypes = ['image/png', 'image/jpg', 'image/jpeg','image/gif']
    if file:
        if file.size > 3000000:
            raise ValidationError('The Image size should not be greater than 3MB')
        # if kind.extension not in ["jpeg","jpg","png","gif"]:
        #     raise ValidationError("Please enter a valid image URL (.jpg .jpeg .png .gif)")
        # if kind not in allowedMimeTypes:
        #     raise ValidationError('Unknown MIME Type. Please enter a valid image URL (.jpg .jpeg .png .gif)')

# files will be uploaded to MEDIA_ROOT/<user_email>/audio_or_images/<filename>
def user_directory_path(instance, filename):
    if  hasattr(instance, 'image'):
        print('BirdImage instance:',instance)
        return '{0}/{1}/images/{2}'.format(instance.user.email,instance.bird.bird_name,filename)
    elif hasattr(instance, 'song_name'):
         print('BirdSong instance:', instance)
         return '{0}/{1}/audio/{2}'.format(instance.user.email,instance.bird.bird_name,filename)
    elif hasattr(instance, 'photo'):
         print('Photo instance:', instance)
         return '{0}/{1}/images/{2}'.format(instance.user.email,instance.bird_name,filename)

class Bird(models.Model):
    # TODO: add name validation startswith number and others
    bird_name = models.CharField(max_length=100,unique=True,blank=False,editable=True,
                                 validators=[RegexValidator(
                                     regex=  '^[A-Za-z0-9? ,_-]+$', #'[a-zA-Z\u0400-\u04FF]$', # /[\w\u0400-\u04ff\u0500-\u052f\ua640-\ua69f\u1d2b-\u1d78]+/
                                     message='Name should contain only alphabets or numbers not other special characters',
                                     )]
                                 )
    user = models.ForeignKey('BirdUser', null=True, related_name='added_by', on_delete=models.CASCADE)
    url = models.URLField(max_length=255, unique=False,blank=True,null=True,editable=True,
                          verbose_name='Image Url',
                          validators=[validate_image])
    bird_description = models.CharField(max_length=1000, blank=True, null=False, editable=True)
    photo      = models.ImageField(blank=True,null=True,upload_to=user_directory_path,validators=[validate_image_upload],max_length=100)
    category   = models.ForeignKey('BirdCategory', related_name='category',on_delete=models.CASCADE)
    likes      = models.ManyToManyField('BirdUser',blank=True, related_name='likes')
    thumbnail  = models.CharField(max_length=255, blank=True, unique=False)
    created_on = models.DateTimeField(auto_now_add =True)
    updated_on = models.DateTimeField(auto_now = True)

    def get_absolute_url(self):
        if not self.id:
            return None
        return reverse("detail", kwargs={'id': self.id})

    def get_category(self):
        if self.category:
            return self.category
        else:
            return None

    def get_thumbnail(self):
        if self.thumbnail:
            self.thumbnail = self.thumbnail.split('/')[-1]
            return self.thumbnail

    @property
    def total_likes(self):
        return self.likes.count()

    class Meta:
        ordering = ['bird_name']

    def __str__(self):
            return self.bird_name

class BirdImage(models.Model):
    # TODO, Set default = img/default.png
    image = models.ImageField(blank=False,upload_to=user_directory_path,validators=[validate_image_upload],max_length=100)
    bird = models.ForeignKey('Bird', related_name='images',on_delete=models.CASCADE)

    def __str__(self):
       return str(self.image)

class BirdSong(models.Model):
    song_name   = models.FileField(blank=False,upload_to=user_directory_path,validators=[validate_audio],max_length=100)
    bird        = models.OneToOneField('Bird', related_name='songs',on_delete=models.CASCADE)

    def __str__(self):
        return str(self.song_name)

class BirdCategory(models.Model):
    name = models.CharField(max_length=100,blank=True)  #choices=Category_CHOICES
    #birds = models.ManyToManyField()

    def __str__(self):
        return self.name

class BirdUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """
    def create_user(self, email, password, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(email, password, **extra_fields)

class BirdUser(AbstractUser):
    username = None
    email = models.EmailField(_('Email Address'), unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = BirdUserManager()

    def __str__(self):
        return self.email

@receiver(post_save,sender=BirdUser)
def send_email(sender, instance, created, **kwargs):
    print(f'Signal from {sender} has been received received!')
    if created:
         print(f'{instance.email} have been created!')

