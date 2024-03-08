from django.shortcuts import redirect, render,HttpResponse
from . import data as db
from django.core.cache import cache
from django.contrib import messages

from appwrite.query import Query

import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass


# Create your views here.
# def home(request):
#     data={"data":db.getDatabases()}
#     return render(request,'home.html',data)



def login(request):
    if(request.method == 'POST'):
        username=request.POST.get("username")
        pswd=request.POST.get("password")
        
        data,_=db.getDocument(os.getenv('DB_ID'),os.getenv('LOGIN_ID'),[Query.equal("username", [username]), Query.equal("password", [pswd])])
        print(data)    
        
        if data:
            if data[0]['isadmin']:
                data={
                        "db_id":os.getenv('DB_ID'),
                        "data":db.getCollection(os.getenv('DB_ID'))
                        }   
                
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
        warning=False
        
        
        
        data={
            "db_id":db_id,
            "collection_id": collection_id
            }
        
        
        if 'new_data' in request.POST:
            
            post_keys = request.POST.keys()
            attr_list = cache.get('attr_list_'+str(collection_id))
            print(attr_list)
            
            data["attr_list"]=attr_list
            
            messages.error(request, 'Data Added Sucessfully')
            #add data to data base        
            return render(request,'docadd.html',data)
        
       
            
        if 'add' in request.POST:
            attr_list = cache.get('attr_list_'+str(collection_id))
            
            
            if attr_list is None:
                attr_list=db.getAttribute(db_id,collection_id)
                cache.set('attr_list_'+str(collection_id), attr_list, timeout=None)  # Cache for 1 hour (adjust timeout as needed)
            
            data["attr_list"]=attr_list
            
            return render(request,'docadd.html',data)
        
        if 'delete' in request.POST:
            doc_id = request.POST.get('delete')
            
            res=db.deleteDocument(db_id,collection_id,doc_id)
            
            if not res:
                warning=True
                
        
        elif 'edit' in request.POST:
            attr_list = request.POST.get('attr_list')
            data["attr_list"]=attr_list
            edit = request.POST.get('edit')
            print("Edit :",attr_list)
        
        
        

                
        data['data'],attr_list=db.getDocument(db_id,collection_id)
        cache.set('attr_list'+str(collection_id), attr_list, timeout=None) 
        data['warning']=warning
            
            
        return render(request,'documents.html',data)
    else:
        return redirect('collections')