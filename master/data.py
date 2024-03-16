from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.query import Query
from appwrite.id import ID
from appwrite.services.storage import Storage
from appwrite.input_file import InputFile

import os


try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass



# STORAGE_URL=f"https://cloud.appwrite.io/v1/storage/buckets/{os.getenv("STORAGE_ID")}/files/{FILE_ID}/view?project={os.getenv("PROJECT_ID")}"

client = Client()


(client
 # Setting API Endpoint
 .set_endpoint('https://cloud.appwrite.io/v1')
 # Setting Project ID
 .set_project(os.getenv('PROJECT_ID'))
 # Setting API Key 
 .set_key(os.getenv('API_KEY'))
 )

databases = Databases(client)
storage = Storage(client)


def getDatabases():
    result = databases.list()
    database=result["databases"]

    db_lists=[]

    for each_database in database :
        
        id=each_database["$id"]
        name=each_database["name"]
        dics={"id":id,"name":name} 
        db_lists.append(dics)
        
    return db_lists

# print(getDatabases())

def getCollection(db_id):
    result = databases.list_collections(db_id,[Query.not_equal("$id", [os.getenv('LOGIN_ID')])])
    collection=result["collections"]
    
    col_lists=[]

    for each_collection in collection :
        
        id=each_collection["$id"]
        name=each_collection["name"].replace('_'," ")
        dics={"id":id,"name":name} 
        col_lists.append(dics)
        
    return col_lists

# print(getCollection(db_id))

def getAttribute(db_id,collection_id):
    result = databases.list_attributes(db_id,collection_id)
    attribute=result['attributes']
    
    att_lists=[]
    
    for each_attribute in attribute :
        
        name=each_attribute["key"]
        type=each_attribute["type"]
        required=each_attribute["required"]
        default=each_attribute["default"]
        # print(each_attribute)
        size=each_attribute["size"] if "size" in each_attribute else 0
     
        dics={"column_name":name,"column_type":type,"required":required,"default":default,"size":size} 
       
        att_lists.append(dics)
        
    return att_lists
    
# print(getAttribute(db_id,collection_id))
def getDocument(db_id,collection_id,query=None):
    result = databases.list_documents(db_id, collection_id,query)
    document=result['documents']
    # print(document)
    doc_list=[]
    attr_lists=getAttribute(db_id,collection_id)

    for each_document in document:
        doc_id=each_document['$id']
        dic={}
        dic['id']=doc_id
        
        for each in attr_lists:
            column_name=each["column_name"]
            if each['column_type']=="datetime" and each_document[column_name] is not None:
                value=each_document[column_name].split("T")[0]
            else:
                value=each_document[column_name]
                
            dic[column_name.replace("_"," ")]=value
        doc_list.append(dic)
        
    return doc_list[::-1],attr_lists


def deleteDocument(db_id,collection_id,document_id):
    try:
        databases.delete_document(db_id, collection_id,document_id)
        return True
    except:
        return False


def addDocument(db_id,collection_id,data):
    try:
        databases.create_document(db_id,collection_id, ID.unique(), data)
        return True
    except:
        return False
    
# deleteDocument("65e2d807b75e8ade83aa","65e2fd824f5c44283c76","65e5756c9255fd882005")



def addStorage(storage_id,file,name):
    try:
    
        file.seek(0)
        c=file.read()
        
        
        file_info = storage.create_file(storage_id,ID.unique(),InputFile.from_bytes(c,name))
        
        
        url=f"https://cloud.appwrite.io/v1/storage/buckets/{storage_id}/files/{file_info['$id']}/view?project={os.getenv('PROJECT_ID')}"
        
        return url
    except:
        return None


def deleteStorage(storage_id,file_url):
    try:
        file_id=file_url.replace(f"https://cloud.appwrite.io/v1/storage/buckets/{storage_id}/files/","").replace(f"/view?project={os.getenv('PROJECT_ID')}","")
        storage.delete_file(storage_id, file_id)   
        return True
    except:
        return False
