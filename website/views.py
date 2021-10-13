from django.shortcuts import render,redirect,get_object_or_404,reverse
from .models import Bird,BirdImage,BirdCategory,BirdSong,BirdUser
from django.template.loader import render_to_string
from django.http import JsonResponse,HttpResponse
from django.db.models import Q,F
from django.db import transaction
from django.conf import settings
import requests,os
import urllib.parse
from .forms import BirdForm,BirdImageForm,BirdSongForm,EditBirdForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods, require_POST,require_GET
from django.views.decorators.csrf import csrf_exempt
from .helper import make_thumbnail,filter_form_errors,has_permission

def urldecode(value):
  return urllib.parse.unquote(value)

# @login_required
@require_POST
def likes(request):
    if request.method == 'POST':
        bird_id = request.POST.get('bird_id',None)
        bird = get_object_or_404(Bird, pk=bird_id)
        print(bird.likes.count())
        if bird.likes.filter(id=request.user.id).exists():
            bird.likes.remove(request.user)
            liked = False
        else:
            bird.likes.add(request.user)
            liked = True
        return JsonResponse({'total_likes':bird.total_likes,'liked':liked})

def about(request):
    return render(request, "about.html")

def grid(request):
    birds = Bird.objects.all()
    images =  [bird.photo for bird in birds]
    return render(request, "grid.html", {'birds': birds, 'images': images})

@login_required
def category(request,**kwargs):
   try:
        user = BirdUser.objects.get(email=kwargs.get('str'))
        user_birds = Bird.objects.filter(user=user)
        categories = {bird.get_category() for bird in user_birds}
        return render(request, "category.html", {'birds': user_birds, 'categories': categories})
   except:
        birds = Bird.objects.all()
        categories = {bird.get_category() for bird in birds}
        return render(request, "category.html", {'birds': birds, 'categories': categories})

@login_required
@csrf_exempt
def birds(request):
    if request.method == 'GET':
        form = BirdForm()  # form = BirdForm(initial={'email':'anonymous@gmail.com'})
        return render(request, "create_bird.html", {'form': form})
    elif request.method == 'POST':
         form = BirdForm(request.POST,request.FILES)
         error_msg = form.errors.as_json()
         message = filter_form_errors(error_msg)
         return render(request, "create_bird.html", {'form': BirdForm(),"message": message})

# @login_required
@transaction.atomic
def create_bird(request):
    """ AJAX Create Bird Record from provided Image Url or Uploaded Image file"""
    """ To Rethink the logic """
    if request.method == 'POST' and request.is_ajax():
        form = BirdForm(request.POST,request.FILES)
        uploaded_photo = request.FILES.get('photo')
        url = request.POST.get('url')
        if not form.is_valid():
            alert = "alert-box alert"
            error_msg = form.errors.as_json()
            message = filter_form_errors(error_msg)
            ctx = {"message": message,
                   'error': message,
                   'alert': alert,
                   'form': BirdForm()}
            html = render_to_string(
                template_name="create_bird_form.html",
                context=ctx
            )
            data_dict = {"html_from_view": html, 'error': message}
            return JsonResponse(data=data_dict, safe=False)

        if (uploaded_photo and url) or (not uploaded_photo and not url):
            message = f'Please choose one of both: Upload Image OR Provide an URL'
            alert = "alert-box alert"
            ctx = {"message": message,
                   'alert': alert,
                   'form': BirdForm()
                   }
            html = render_to_string(
                template_name="create_bird_form.html",
                context=ctx
            )
            data_dict = {"html_from_view": html,'error': message}
            return JsonResponse(data=data_dict, safe=False)

        if form.is_valid():
            inst = form.instance
            uploaded_photo = request.FILES.get('photo')
          # To Add Multiple files upload
            #uploaded_photos = request.FILES.getlist('photo')
            print('uploaded_photo:',uploaded_photo)
            if uploaded_photo and not request.POST.get("url"):
                inst.user = BirdUser.objects.get(email=request.user)
                inst.save()
                ctx = {"message": f'{form.instance.bird_name} have been saved!',
                       'alert': "alert-box alert",
                       'form': BirdForm(),
                       'bird': inst,
                       'url_to_bird':inst.get_absolute_url()}
                html = render_to_string(
                    template_name="create_bird_form.html",
                    context=ctx
                )
                data_dict = {"html_from_view": html,'success': 'success','url_to_bird':inst.get_absolute_url()}
                return JsonResponse(data=data_dict, safe=False)

            if not request.POST.get("url"):
                message = f'Upload an Image or provide an URL to Image!'
                alert = "alert-box alert"
                ctx = {"message": message,
                       'error': message,
                       'alert': alert,
                       'form': BirdForm()}
                html = render_to_string(
                    template_name="create_bird_form.html",
                    context=ctx
                )
                data_dict = {"html_from_view": html,'error': message}
                return JsonResponse(data=data_dict, safe=False)

            bird_name = request.POST.get('bird_name').strip()
            url       = request.POST.get('url')
            response  = requests.get(url)
            user_dir  = request.user.email #.split('@')[0]
            print('user_dir:',user_dir)
            bird_dir  = bird_name
            dir       =  os.path.join(settings.MEDIA_ROOT, user_dir, bird_dir)
            if not os.path.exists(dir):
                os.makedirs(dir,exist_ok=True)
            filename = os.path.join(dir, f'{bird_name}.jpg').replace("\\", "/")
            file = open(filename, "wb")
            file.write(response.content)
            file.close()
            form.save()
            bird = Bird.objects.get(bird_name=bird_name)
            # thumb = make_thumbnail(filename)
            # bird.thumbnail = thumb
            bird.user = BirdUser.objects.get(email=request.user)
            dir_image = os.path.join(user_dir, bird_dir, f'{bird_name}.jpg').replace("\\", "/")
            bird.photo = dir_image
            bird.save()
            # image.bird = bird
            # image.save()
            message = f'{bird_name} has been saved!'
            ctx = {"message": message,
                   'alert': "alert-box alert",
                   'form': BirdForm(),
                   'bird': bird,
                   'url_to_bird': inst.get_absolute_url()
                   }
            html = render_to_string(
                template_name="create_bird_form.html",
                context=ctx
            )
            data_dict = {"html_from_view": html,'success': 'success','url_to_bird':inst.get_absolute_url()}
            return JsonResponse(data=data_dict, safe=False)
        else:
            alert = "alert-box alert"
            error_msg = form.errors.as_json()
            message = filter_form_errors(error_msg)
            ctx = {"message": message,
                   'error': message,
                   'alert': alert,
                   'form': BirdForm()},
            html = render_to_string(
                template_name="create_bird_form.html",
                context=ctx
            )
            data_dict = {"html_from_view": html,'error': message}
            return JsonResponse(data=data_dict, safe=False)

    else:
        form = BirdForm(request.POST,request.FILES)
        error_msg = form.errors.as_json()
        message = filter_form_errors(error_msg)
        return render(request, "create_bird.html", {'form': form,'message':message})

# Ajax Search
def ajax_search(request):
    ctx = {}
    search = request.GET.get("q")
    q_exact = Q(bird_name__iexact=search)
    q_icontains = Q(bird_name__icontains=search)
    if search:
        birds = Bird.objects.filter(q_exact|q_icontains).prefetch_related('images').order_by('bird_name')
    else:
        birds = Bird.objects.all()
    ctx["birds"] = birds
    if request.is_ajax() or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        html = render_to_string(
            template_name="search_partial.html",
            context = ctx
        )
        data_dict = {"html_from_view": html}
        return JsonResponse(data=data_dict, safe=False)

    return render(request, "search.html", context = ctx)

@login_required
@csrf_exempt
def detail_view(request, id):
    bird = get_object_or_404(Bird, pk=id)
    birds = Bird.objects.all().prefetch_related('images')
    edit_bird_form = EditBirdForm(instance=bird)
    return render(request, "bird_detail.html",{'bird': bird,'birds': birds,'edit_bird_form':edit_bird_form})

@login_required
def upload_image(request):
    """ Handle AJAX Image Upload """
    if request.method == 'POST' and request.is_ajax():
        form = BirdImageForm(request.POST, request.FILES)
        id = request.POST.get('id')
        bird = get_object_or_404(Bird, pk=id)
        if not bird.user_id == request.user.id:
            ctx = {"message": "You dont have permissions!",
                   'url_to_bird': bird.get_absolute_url(),
                   'form': BirdImageForm()
                   }
            html = render_to_string(
                template_name="upload_image_ajax-modal.html",
                context = ctx
            )
            data_dict = {"html_from_view": html, 'error': "You dont have permissions to upload!"}
            return JsonResponse(data=data_dict, safe=False)
        # print('bird.images.all.length',len(bird.images))
        if form.is_valid():
                print("Valid Form")
                img_obj = form.instance
                img_obj.bird = bird
                img_obj.user = request.user
                form.save()
                bird = get_object_or_404(Bird, pk=id)
                birds = Bird.objects.all().prefetch_related('images')
                ctx = {"message": 'Image have been saved!',
                       'success': 'success',
                       "bird":bird,
                       "birds":birds
                       }
                html = render_to_string(
                        template_name="MorePhotos.html",
                        context=ctx
                    )
                data_dict = {"html_from_view": html,'success': 'success'}
                return JsonResponse(data=data_dict, safe=False)
        else:
            error_msg = form.errors.as_json()
            error = filter_form_errors(error_msg)
            print('error_msg',error_msg)
            alert = "alert-box alert"
            ctx = { 'alert': alert,
                    "message": error,
                    'form': BirdImageForm()
                   }
            print('context:',ctx)
            html = render_to_string(
                template_name="upload_image_ajax-modal.html",
                context=ctx
            )
            data_dict = {"html_from_view": html,'error': error}
            return JsonResponse(data=data_dict, safe=False) #,status=400

    #return JsonResponse({"message": "Something went wrong"}, status=400)

@login_required
def upload_audio(request):
    """ Handle AJAX Audio Upload """
    if request.method == 'POST' and request.is_ajax():
        form = BirdSongForm(request.POST, request.FILES)
        id = request.POST.get('id')
        bird = get_object_or_404(Bird, pk=id)
        if not bird.user_id == request.user.id:
            print(f"request user: {request.user.id}', 'bird.user_id: {bird.user_id}")
            ctx = {"message": "You dont have permissions!",
                   'url_to_bird': bird.get_absolute_url(),
                   'form': BirdImageForm()
                   }
            html = render_to_string(
                template_name="upload_image_ajax-modal.html",
                context = ctx
            )
            data_dict = {"html_from_view": html, 'error': "You dont have permissions to upload!"}
            return JsonResponse(data=data_dict, safe=False)
        if form.is_valid():
            bird_song = BirdSong.objects.filter(bird_id=bird.id)
            if bird_song:
                bird_song.delete()
                print('Bird_song already exist, it will be deleted and replaced with the new one')
            audio_obj = form.instance
            audio_obj.bird = bird
            audio_obj.user = request.user
            form.save()
            ctx = {"message": 'Audio have been saved!',
                   "success": 'success',
                   'bird': bird}
            html = render_to_string(
                template_name="replace_audio_div.html",
                context=ctx
            )
            data_dict = {"html_from_view": html,
                         "success": 'Audio have been saved!'}
            return JsonResponse(data=data_dict, safe=False)
        else:
            error_msg = form.errors.as_json()
            error = filter_form_errors(error_msg)
            alert = "alert-box alert"
            ctx = { 'alert': alert,
                    "message": error,
                    'form': BirdSongForm()
                   }
            print('context:',ctx)
            html = render_to_string(
                template_name="upload_audio_ajax-modal.html",
                context=ctx
            )
            data_dict = {"html_from_view": html,'error': error}
            return JsonResponse(data=data_dict, safe=False)

    #return JsonResponse({"message": "Something went wrong"}, status=400)

@login_required
def delete_bird(request):
    """ Delete an instance of a Bird | all related images are delete through/in Signals.py  """
    id = request.POST.get('id')
    bird = get_object_or_404(Bird, pk=id)
    print(f'Bird to delete {bird.bird_name} with id {bird.id}')
    if not bird.user_id == request.user.id:
        ctx = {"message": "You dont have permissions!",
               'url_to_bird': bird.get_absolute_url(),
               'form': BirdImageForm()
               }
        html = render_to_string(
            template_name="delete_ajax.html",
            context=ctx
        )
        data_dict = {"html_from_view": html, 'error': "You dont have permissions to upload!"}
        return JsonResponse(data=data_dict, safe=False)
    if request.method == 'POST' and request.is_ajax:
       bird.delete()
       return JsonResponse(data={'success':'success'}, safe=False)
    else:
        ctx = {"message": "Something went wrong"}
        html = render_to_string(
            template_name="delete_ajax.html",
            context=ctx
        )
        data_dict = {"html_from_view": html}
        return JsonResponse(data=data_dict, safe=False)

@login_required
# Edit an existing Bird Instance with AJAX Request
def edit_bird(request):
    if request.method == 'POST' and request.is_ajax():
        id = request.POST.get('id')
        bird = get_object_or_404(Bird, pk=id)
        if not bird.user_id == request.user.id:
            ctx = {"message": "You dont have permissions!",
                   'url_to_bird': bird.get_absolute_url(),
                   'form': BirdImageForm()
                   }
            html = render_to_string(
                template_name="edit_ajax_modal.html",
                context=ctx
            )
            data_dict = {"html_from_view": html, 'error': "error"}
            return JsonResponse(data=data_dict, safe=False)
        form = EditBirdForm(request.POST, instance=bird)
        if form.is_valid():
           form.save()
           ctx = { 'bird': bird,
                   'edit_bird_form': form
                  }
           html = render_to_string(
               template_name="replace_edit_div.html",
               context=ctx
           )
           data_dict = {"html_from_view": html,'success': 'success'}
           return JsonResponse(data=data_dict, safe=False)

        else:
            error_msg = form.errors.as_json()
            error = filter_form_errors(error_msg)
            ctx = { "message": error,
                    'error': error,
                    'edit_bird_form': form
                   }
            print('context:', ctx)
            html = render_to_string(
                template_name="edit_ajax_modal.html",
                context=ctx
            )
            data_dict = {"html_from_view": html, 'error': error}
            return JsonResponse(data=data_dict, safe=False)


