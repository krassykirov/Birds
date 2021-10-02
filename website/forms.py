from django import forms
from website.models import Bird,BirdImage,BirdCategory,BirdSong,BirdUser
from django.conf import settings
from django.http import HttpResponse,HttpRequest

class BirdForm(forms.ModelForm):

    class Meta:
        model= Bird
        # category =  forms.ModelChoiceField(queryset=BirdCategory.objects.all(), required=False,
        #                                    widget=forms.Select())
        # widget=forms.ClearableFileInput(attrs={'multiple': True}
        thumbnail  = forms.CharField(widget=forms.HiddenInput(),required=False)
        user       = forms.ModelChoiceField(queryset=BirdUser.objects.all(),widget=forms.HiddenInput(), required=False)
        photo      = forms.ImageField(widget=forms.ClearableFileInput(),required=False)
        fields     = [ "bird_name","url","photo","bird_description","category"]
        labels     =  {     'photo': 'OR Upload a Photo',
                            'url': 'Provide a Web Image URL'
                       }

        widgets = {
            'bird_name': forms.TextInput(attrs={'placeholder': 'Bird Name'}),
            'url': forms.TextInput(attrs={'placeholder': 'Image URL'}),
            'bird_description': forms.TextInput(attrs={'placeholder': 'Enter a Bird description'}),
        }

    # def __init__(self, *args, **kwargs):
    #     super(BirdForm, self).__init__(*args, **kwargs)
    #     self.fields['photo'].widget.attrs.update({'multiple': True})
    # def __init__(self, *args, **kwargs):
    #     super(FriendForm, self).__init__(*args, **kwargs)
    #     ## add a "form-control" class to each form input
    #     ## for enabling bootstrap
    #     for name in self.fields.keys():
    #         self.fields[name].widget.attrs.update({
    #             'class': 'form-control',
    #         })
    #
    # class Meta:
    #     model = Friend
    #     fields = ("__all__")

class EditBirdForm(forms.ModelForm):

    class Meta:
        model = Bird
        fields = ["bird_name", "bird_description", "category"]

        widgets = {
            'bird_name': forms.TextInput(attrs={'placeholder': 'Bird Name'}),
            'bird_description': forms.TextInput(attrs={'placeholder': 'Short Bird description'}),
            'category': forms.Select()
        }

class BirdImageForm(forms.ModelForm):

    exclude = ['bird']

    class Meta:
        model = BirdImage
        fields = ('image',)

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     for field_name in ('image'):
    #         self.fields[field_name].help_text = ''


class BirdSongForm(forms.ModelForm):
    exclude = ['bird']

    class Meta:
        model = BirdSong
        fields = ('song_name',)

