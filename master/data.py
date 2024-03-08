from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.query import Query
import os


try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass


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
    result = databases.list_collections(db_id)
    collection=result["collections"]
    
    col_lists=[]

    for each_collection in collection :
        
        id=each_collection["$id"]
        name=each_collection["name"]
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
     
        dics={"column_name":name,"column_type":type,"required":required,"default":default} 
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
            value=each_document[column_name]
            dic[column_name]=value
        doc_list.append(dic)
        
    return doc_list,attr_lists


def deleteDocument(db_id,collection_id,document_id):
    try:
        databases.delete_document(db_id, collection_id,document_id)
        return True
    except:
        return False
    
    
# deleteDocument("65e2d807b75e8ade83aa","65e2fd824f5c44283c76","65e5756c9255fd882005")
