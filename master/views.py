from django.shortcuts import redirect, render,HttpResponse
import requests
from . import data as db
from django.core.cache import cache
from django.contrib import messages
from .form import YourForm
from django import forms
import datetime          
import json
from django.core.files.uploadedfile import InMemoryUploadedFile
from PIL import Image
import io

from appwrite.query import Query

import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass




class DateTimeEncoder(json.JSONEncoder):
    def default(self, z):
        if isinstance(z, datetime.datetime):
            return (str(z))
        else:
            return super().default(z)



def updateSite():
    try:
        requests.get(os.getenv("MAIN_SITE"))
        print("done")
    except:
        print("Failed to get site")


def compress_image(uploaded_file):
    img = Image.open(uploaded_file)
    
    # Compress the image (adjust the quality as needed)
    img = img.convert('RGB')
    img_io = io.BytesIO()
    img.save(img_io, format='JPEG', quality=20)
    img_io.seek(0)

    # Create a new InMemoryUploadedFile object with the compressed image data
    compressed_file = InMemoryUploadedFile(
        img_io, None, uploaded_file.name, 'image/jpeg', img_io.tell(), None
    )

    return compressed_file


def remove_old_img(data,field_name):
    data=eval(data)
    
    
    try:
    
        old_img_url=data[field_name]
        r=db.deleteStorage(os.getenv('STORAGE_ID'),old_img_url)
        if not r:
            return False
        return True
    except:
        return False



def login(request):
    if(request.method == 'POST'):
        username=request.POST.get("username")
        pswd=request.POST.get("password")
        
        data,_=db.getDocument(os.getenv('DB_ID'),os.getenv('LOGIN_ID'),[Query.equal("username", [username]), Query.equal("password", [pswd])])
        # print(data)    
        
        if data:
            if data[0]['isadmin']:
                col=db.getCollection(os.getenv('DB_ID'))
                data={
                        "db_id":os.getenv('DB_ID'),
                        "collections":col
                        }
                
                cache.set('collections', col, timeout=None)  # Cache for 1 hour (adjust timeout as needed)   
                
                return render(request,'collections.html',data)

            
            return HttpResponse("Non Admin page")
        
        messages.error(request, 'Login Failed ! Please Check your credentials...')
        return redirect('login')
        
            
        
        #check if the user name and password are in the database and is correct
        #if not correct then render the error message else move to next page
        
    return render(request,'login.html')
    


    
def documents(request):
    if request.method == 'POST':
        db_id = request.POST.get('db_id')
        collection_id = request.POST.get('collection_id')
        col = cache.get('collections')
        
        if col is None:
            col=db.getCollection(os.getenv('DB_ID'))
            cache.set('collections',col,None)
        

        
        
        
        data={
            "db_id":db_id,
            "collection_id": collection_id,
            "collections":col
            }
        
        
        if 'new_data' in request.POST:
            
            
        
            attr_list = cache.get('attr_list_'+str(collection_id))
      
            
            new_det={}
            form = YourForm(attr_list=attr_list, data=request.POST, files=request.FILES)  
            if form.is_valid():
                # Access other form fields dynamically
                for field_name, field_value in form.cleaned_data.items():
                    
                    if isinstance(form.fields[field_name], forms.DecimalField):
                        new_det[field_name.replace(" ","_")] =float(field_value) if (field_value is not "" and field_value is not None) else 0.0
                        continue
                    
                    if isinstance(form.fields[field_name], forms.DateTimeField):
                        # This field is a DateField
                        try:
                            # Attempt to convert the field value to a datetime object
                            raw=json.dumps(field_value,cls=DateTimeEncoder).replace('"',"").replace("'","")
          
                            new_det[field_name.replace(" ","_")] =raw if raw is not "null" else None
                            continue
                        except:
                             pass
                    
                    if "image" in field_name or "Image" in field_name:
                        try:
                            uploaded_file = request.FILES[field_name]
                            compressed_file = compress_image(uploaded_file)
                            url=db.addStorage(os.getenv('STORAGE_ID'),compressed_file.file,uploaded_file.name)
                            
                            new_det[field_name.replace(" ","_")] =url
                            continue
                        except:
                            pass

                        
                  
                    new_det[field_name.replace(" ","_")] =field_value if field_value is not "" else None
            
            
            # print(new_det)
            res=db.addDocument(db_id,collection_id,new_det)
            if not res:
                messages.error(request, 'Somthing went wrong ... Data is not added')
            else:
                messages.success(request, 'Data Added Sucessfully')
            
            updateSite()
                
            data["attr_list"]=attr_list
            form = YourForm(attr_list=attr_list)
            data["form"] = form
            
            #add data to data base        
            return render(request,'docadd.html',data)
        
        
        
        
        if 'update_data' in request.POST:
            
        
            attr_list = cache.get('attr_list_'+str(collection_id))
            doc_id=request.POST.get('doc_id')
      
            
            new_det={}
            form = YourForm(attr_list=attr_list, data=request.POST, files=request.FILES)  
            if form.is_valid(exc=True):
                # Access other form fields dynamically
                for field_name, field_value in form.cleaned_data.items():
                    
                    if isinstance(form.fields[field_name], forms.DecimalField):
                        new_det[field_name.replace(" ","_")] =float(field_value) if (field_value is not "" and field_value is not None) else 0.0
                        continue
                    
                    if isinstance(form.fields[field_name], forms.DateTimeField):
                        # This field is a DateField
                        try:
                            # Attempt to convert the field value to a datetime object
                            raw=json.dumps(field_value,cls=DateTimeEncoder).replace('"',"").replace("'","")
          
                            new_det[field_name.replace(" ","_")] =raw if raw is not "null" else None
                            continue
                        except:
                             pass
                    
                    if "image" in field_name or "Image" in field_name:
                        try:
                            hid=f"old_{field_name}"
                            try:
                                uploaded_file = request.FILES[field_name]
                            
                            
                                # print(uploaded_file);
                                compressed_file = compress_image(uploaded_file)
                                
                                url=db.addStorage(os.getenv('STORAGE_ID'),compressed_file.file,uploaded_file.name)
                                
                                new_det[field_name.replace(" ","_")] =url
                                
                                if(hid not in request.POST):
                                    remove_old_img(request.POST.get("data_dict"),field_name)
                                    # print("function called")
                                    
                                    pass
                                
                                
                                continue
                            except:
                                # print("hid check");
                                
                                
                                if(hid in request.POST):
                                    # print("retain old one");
                                    continue
                                else:
                                    remove_old_img(request.POST.get("data_dict"),field_name)
                                    # print("function called")
                                    pass
                        
                        except:
                            # print("ffdfdfdfdfdf");
                            pass

                        
                  
                    new_det[field_name.replace(" ","_")] =field_value if field_value is not "" else None
            
            else:
                # print("ggrgggrg")
                print(form.errors)
            # print(new_det)
            res=db.updateDocument(db_id,collection_id,doc_id,new_det)
            if not res:
                messages.error(request, 'Somthing went wrong ... Data is not added')
            else:
                messages.success(request, 'Data Updated Sucessfully')
            
            updateSite()
          
            
        if 'add' in request.POST:
            attr_list = cache.get('attr_list_'+str(collection_id))
            
            
            if attr_list is None:
                attr_list=db.getAttribute(db_id,collection_id)
                cache.set('attr_list_'+str(collection_id), attr_list, timeout=None)  # Cache for 1 hour (adjust timeout as needed)
            
            data["attr_list"]=attr_list
            
            # print(attr_list)
            
            form = YourForm(attr_list=attr_list)
            data["form"] = form
            
            return render(request,'docadd.html',data)
        
        if 'delete' in request.POST:
            doc_id = request.POST.get('delete')
            
            key=f'img_{doc_id}[]'
            img_list=request.POST.getlist(key)
            
            for each in img_list:
                r=db.deleteStorage(os.getenv('STORAGE_ID'),each)
                if not r:
                    res=False
                    break
            else:
                res=db.deleteDocument(db_id,collection_id,doc_id)
            
            if not res:
                messages.error(request, 'Somthing went wrong ...')
            else:
                messages.success(request, 'Data Deleted Sucessfully')
                
            updateSite()
                
        
        elif 'edit' in request.POST:
            doc_id = request.POST.get('edit')
            key=f"data_{doc_id}"
            data_dict=request.POST.get(key)
            data_dict=eval(data_dict)
            attr_list = cache.get('attr_list_'+str(collection_id))
            
            
            
            if attr_list is None:
                attr_list=db.getAttribute(db_id,collection_id)
                cache.set('attr_list_'+str(collection_id), attr_list, timeout=None)  # Cache for 1 hour (adjust timeout as needed)
                
            form = YourForm(attr_list=attr_list,default_data=data_dict)
            
            data["attr_list"]=attr_list
            
            # print(attr_list)

            data["form"] = form
            data['doc_id']=doc_id
            data['data_dict']=data_dict
            
            return render(request,'docedit.html',data)
        
        
        

                
        data['data'],attr_list=db.getDocument(db_id,collection_id)
        cache.set('attr_list'+str(collection_id), attr_list, timeout=None) 
            
            
        return render(request,'documents.html',data)
    else:
        return redirect('login')
    
    
    
# def file(request):
#     if request.method == 'POST':
#         try:
#             uploaded_file = request.FILES['upfile']
#             url=db.addStorage(os.getenv('STORAGE_ID'),uploaded_file.file,uploaded_file.name)
#             if url:
#                 return render(request,'file.html',{'url':url})
#             else:
#                 raise Exception
#         except:
#             return render(request,'file.html')
            

        
        
#     else:
#         return render(request,'file.html')