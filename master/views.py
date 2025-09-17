import os
import ast
from django.shortcuts import render, redirect, HttpResponse
from django.contrib import messages
from django.core.cache import cache
from appwrite.query import Query
from . import data as db
from .form import YourForm
from .utils import clean_form_data, updateSite, generate_token

from django.views.decorators.http import require_GET
from django.http import JsonResponse



# from .utils import compress_image, remove_old_img
limit=15


def validate_session(request):
    """
    Check if session is valid:
    - User is logged in
    - Token matches cache
    """
    username = request.session.get('username')
    token = request.session.get('token')

    if not username or not token:
        return False

    active_token = cache.get(f"user_token_{username}")
    if not active_token or active_token != token:
        return False

    return True


def login(request):
    """
    User login.
    - Stores `user` and `is_admin` in session.
    - Redirects admin to collections dashboard.
    """
    
    if validate_session(request):
        col = cache.get('collections')
        if not col:
            col = db.getCollection(os.getenv('DB_ID'))
            cache.set('collections', col, timeout=None)
        return render(request, 'collections.html', {
            "db_id": os.getenv('DB_ID'),
            "collections": col
        })
    
    if request.method == 'POST':
        username = request.POST.get("username")
        pswd = request.POST.get("password")

        data, _ = db.getDocument(
            os.getenv('DB_ID'),
            os.getenv('LOGIN_ID'),
            [Query.equal("username", [username]), Query.equal("password", [pswd])]
        )

        if data:
             # Generate a new token for this login
            token = generate_token()
            request.session['username'] = username
            request.session['token'] = token
            request.session['is_admin'] = data[0].get("isadmin", False)
            request.session.set_expiry(3600)  # 1 hour expiry

            # Store active token in cache to enforce single session
            cache.set(f"user_token_{username}", token, timeout=3600)
            
            if data[0].get('isadmin'):
                col = db.getCollection(os.getenv('DB_ID'))
                cache.set('collections', col, timeout=None)
                return render(request, 'collections.html', {
                    "db_id": os.getenv('DB_ID'),
                    "collections": col
                })
            return HttpResponse("Non Admin page")

        messages.error(request, 'Login Failed! Please check your credentials...')
        return redirect('login')

    return render(request, 'login.html')



@require_GET
def get_documents_batch(request):
    """Return a batch of documents with caching."""
    
    batch={}
    
    if not validate_session(request):
        messages.error(request, 'Session expired or invalid. Please login.')
        batch["sessionExp"]=True
        batch["data"]=[]
        
        return JsonResponse(batch)
   
    
    db_id = request.GET.get('db_id')
    collection_id = request.GET.get('collection_id')

    try:
        offset = int(request.GET.get("offset", 0))
         
    except ValueError:
        offset = 0

    cache_key = f"documents_batch_{offset}_{limit}"
    batch = cache.get(cache_key)

    if not batch:
        batch={}
        batch["sessionExp"]=False
        # Query Appwrite DB
        queries = [
            Query.limit(limit),
            Query.offset(offset),
            Query.order_desc("$createdAt"),
        ]
       
        batch['data'], attr_list = db.getDocument(db_id, collection_id,queries)
        cache.set(f'attr_list_{collection_id}', attr_list, None)
        # cache.set(cache_key, batch, timeout=None)
        # print(batch)

    return JsonResponse(batch)


def documents(request):
    """
    Handles CRUD for documents.
    - Add, update, delete, edit
    - Optional image handling (commented example inside)
    """
    if not validate_session(request):
        messages.error(request, 'Session expired or invalid. Please login.')
        return redirect('login')
    
    if request.method != 'POST':
        return redirect('login')

    db_id = request.POST.get('db_id')
    collection_id = request.POST.get('collection_id')

    col = cache.get('collections') or db.getCollection(os.getenv('DB_ID'))
    cache.set('collections', col, None)
    data = {"db_id": db_id, "collection_id": collection_id, "collections": col}

    # --- Add new ---
    if 'new_data' in request.POST:
        attr_list = cache.get(f'attr_list_{collection_id}')
        form = YourForm(attr_list=attr_list, data=request.POST, files=request.FILES)
        if form.is_valid():
            new_det = clean_form_data(form)

            # Example for image field (uncomment if needed)
            """
            for field_name in request.FILES:
                uploaded_file = request.FILES[field_name]
                compressed = compress_image(uploaded_file, quality=60)
                url = db.addStorage(os.getenv('STORAGE_ID'), compressed.file, compressed.name)
                new_det[field_name] = url
            """

            res = db.addDocument(db_id, collection_id, new_det)
            messages.success(request, 'Data Added Successfully' if res else 'Something went wrong...')
            updateSite()
        else:
            messages.error(request, 'Invalid form submission')
        data["attr_list"] = attr_list
        data["form"] = YourForm(attr_list=attr_list)
        return render(request, 'docadd.html', data)

    # --- Update ---
    if 'update_data' in request.POST:
        doc_id = request.POST.get('doc_id')
        attr_list = cache.get(f'attr_list_{collection_id}')
        form = YourForm(attr_list=attr_list, data=request.POST, files=request.FILES)
        if form.is_valid():
            new_det = clean_form_data(form)

            # Example for image update (uncomment if needed)
            """
            for field_name in request.FILES:
                uploaded_file = request.FILES[field_name]
                compressed = compress_image(uploaded_file, quality=60)
                url = db.addStorage(os.getenv('STORAGE_ID'), compressed.file, compressed.name)
                new_det[field_name] = url
                # Remove old file if replaced
                remove_old_img(request.POST.get("data_dict"), field_name)
            """

            res = db.updateDocument(db_id, collection_id, doc_id, new_det)
            messages.success(request, 'Data Updated Successfully' if res else 'Update failed')
            updateSite()
        else:
            print(form.errors)

    # --- Add form ---
    if 'add' in request.POST:
        attr_list = cache.get(f'attr_list_{collection_id}') or db.getAttribute(db_id, collection_id)
        cache.set(f'attr_list_{collection_id}', attr_list, None)
        data["attr_list"] = attr_list
        data["form"] = YourForm(attr_list=attr_list)
        return render(request, 'docadd.html', data)

    # --- Delete ---
    if 'delete' in request.POST:
        doc_id = request.POST.get('delete')
        img_list = request.POST.getlist(f'img_{doc_id}[]')
        res = all(db.deleteStorage(os.getenv('STORAGE_ID'), each) for each in img_list)
        if res:
            res = db.deleteDocument(db_id, collection_id, doc_id)
        messages.success(request, 'Data Deleted Successfully' if res else 'Delete failed')
        updateSite()

    # --- Edit ---
    if 'edit' in request.POST:
        doc_id = request.POST.get('edit')
        data_dict = ast.literal_eval(request.POST.get(f"data_{doc_id}"))
        attr_list = cache.get(f'attr_list_{collection_id}') or db.getAttribute(db_id, collection_id)
        cache.set(f'attr_list_{collection_id}', attr_list, None)
        form = YourForm(attr_list=attr_list, default_data=data_dict)
        data.update({
            "attr_list": attr_list,
            "form": form,
            "doc_id": doc_id,
            "data_dict": data_dict
        })
        return render(request, 'docedit.html', data)

    # --- Default ---
    queries = [
            Query.limit(limit),
            Query.offset(0),
            Query.order_desc("$createdAt"),
        ]
    data['data'], attr_list = db.getDocument(db_id, collection_id,queries)
    cache.set(f'attr_list_{collection_id}', attr_list, None)
    return render(request, 'documents.html', data)

'''
def file(request):
    """
    Upload a single image file to storage.
    - Only image/* types
    - Max 5 MB
    """
    if request.method == 'POST':
        try:
            uploaded_file = request.FILES.get('upfile')
            if not uploaded_file:
                messages.error(request, 'No file uploaded')
                return render(request, 'file.html')

            if not uploaded_file.content_type.startswith('image/'):
                messages.error(request, 'Only image uploads are allowed.')
                return render(request, 'file.html')

            MAX_SIZE = 5 * 1024 * 1024
            if uploaded_file.size > MAX_SIZE:
                messages.error(request, 'File too large (max 5MB).')
                return render(request, 'file.html')

            compressed = compress_image(uploaded_file, quality=60)
            url = db.addStorage(os.getenv('STORAGE_ID'), compressed.file, compressed.name)
            if url:
                return render(request, 'file.html', {'url': url})
            else:
                messages.error(request, 'Upload failed.')
        except Exception as e:
            print("File upload error:", e)
            messages.error(request, 'Upload error.')
    return render(request, 'file.html')

'''
