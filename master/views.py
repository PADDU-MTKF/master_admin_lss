from django.shortcuts import redirect, render,HttpResponse
from . import data as db
from django.core.cache import cache
from django.contrib import messages
from .form import YourForm
from django import forms
import datetime          
import json

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


# Create your views here.
# def home(request):
#     data={"data":db.getDatabases()}
#     return render(request,'home.html',data)



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
    



# def collections(request):
#     if request.method == 'POST':
#         db_id = request.POST.get('db_id')
#         data={
#             "db_id":db_id,
#             "data":db.getCollection(db_id)
#             }
        
#         return render(request,'collections.html',data)
#     else:
#         return redirect('login')
    
    
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
            form = YourForm(attr_list=attr_list, data=request.POST)  
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
                  
                    new_det[field_name.replace(" ","_")] =field_value if field_value is not "" else None
            

            # print(new_det)
            res=db.addDocument(db_id,collection_id,new_det)
            if not res:
                messages.error(request, 'Somthing went wrong ... Data is not added')
            else:
                messages.success(request, 'Data Added Sucessfully')
                
            data["attr_list"]=attr_list
            form = YourForm(attr_list=attr_list)
            data["form"] = form
            
            #add data to data base        
            return render(request,'docadd.html',data)
        
       
            
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
            
            res=db.deleteDocument(db_id,collection_id,doc_id)
            
            if not res:
                messages.error(request, 'Somthing went wrong ...')
            else:
                messages.success(request, 'Data Deleted Sucessfully')
                
        
        elif 'edit' in request.POST:
            attr_list = request.POST.get('attr_list')
            data["attr_list"]=attr_list
            edit = request.POST.get('edit')
            print("Edit :",attr_list)
        
        
        

                
        data['data'],attr_list=db.getDocument(db_id,collection_id)
        cache.set('attr_list'+str(collection_id), attr_list, timeout=None) 
            
            
        return render(request,'documents.html',data)
    else:
        return redirect('login')
    
    
    
def file(request):
    if request.method == 'POST':
        uploaded_file = request.FILES['upfile']
        print(uploaded_file.file)
        db.addStorage(os.getenv('STORAGE_ID'),uploaded_file.file)
        return render(request,'file.html')

        
        
    else:
        return render(request,'file.html')