from fastapi import FastAPI, HTTPException, status, Request, Response
import pymongo
from pymongo import MongoClient
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from bson.objectid import ObjectId

#initialize app
app = FastAPI()

"""SET UP CORS"""
origins = ["http://localhost:5173"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_headers=["*"],
    allow_methods=["*"]
)


#design schemas
class Category(BaseModel):
    name:str
    description:str

class ImageGroup(BaseModel):
    title:str
    description:str


class ImageModel(BaseModel):
    orignal_filename:str
    url:str
    asset_id:str
    image_title:str
    image_group_id:str

class BlogPost(BaseModel):
    image_url:str
    category_id:str
    category_name:str
    post_title:str
    short_title:str
    body:str

class PageContent(BaseModel):
    image_url:str
    content_title:str
    body:str
    page:str



#set up db
password = 'wHs2mEqKAo9urlIR'
username= 'PGAdmin'
connection_uri = MongoClient(f"mongodb+srv://PGAdmin:{password}@clusterpg1.vyvxp8e.mongodb.net/?retryWrites=true&w=majority")
database = connection_uri['Websitedata']
print(database)

#root
@app.get("/")
def root():
    return {"message": "Hello Purple Girls"}




"""
category apis
"""
@app.post('/api/category/', status_code=status.HTTP_201_CREATED)
def create_category(category:Category):
    category_data = category.dict()
    category_collection = database.BlogCategories
    try:
        category_collection.insert_one(category_data)
        return {'status':True}
    except:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Failed to create catgory')

@app.get('/api/category/')
def get_categories():
    category_collection = database.BlogCategories
    data = category_collection.find({})
    serialized_data = [{'id':str(d.get('_id')), 'name':str(d.get('name')), 'description':str(d.get('description'))} for d in data]
    return {'status':True, 'categories':serialized_data}


"""
Image Management
"""
@app.post('/api/imagegroup/', status_code=status.HTTP_201_CREATED)
def create_image_group(image_group:ImageGroup):
    group_data = image_group.dict()
    group_collection = database.ImageGroup
    try:
        group_collection.insert_one(group_data)
        return {'status':True}
    except:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Failed to create image Group')

@app.get('/api/imagegroup/')
def get_imagegroup():
    group_collection = database.ImageGroup
    data = group_collection.find({})
    serialized_data = [
                        {'id':str(d.get('_id')), 
                        'title':str(d.get('title')), 
                        'description':str(d.get('description'))} for d in data]
    return {'status':True, 'groups':serialized_data}


@app.post('/api/add_image/', status_code=status.HTTP_201_CREATED)
def add_image(image:ImageModel):
    image_data = image.dict()
    image_collection = database.Image
    try:
        image_collection.insert_one(image_data)
        return {'status':True}
    except:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Failed to add image')

@app.get('/api/get_image_for_blog/')
def get_image_for_blog():
    image_collection = database.Image
    data = image_collection.find({'image_group_id':''})
    serialized_data = [{
        'id':str(d.get('_id')),
        'title':str(d.get('image_title')), 
        'img_url':str(d.get('url'))} for d in data]
    return {'status':True, 'images':serialized_data}


@app.get('/api/get_gallery_images/{gallery_id}')
def get_gallery_images(gallery_id):
    image_collection = database.Image
    data = image_collection.find({'image_group_id':gallery_id})
    serialized_data = [{
        'id':str(d.get('_id')),
        'img_url':str(d.get('url'))} for d in data]
    return {'status':True, 'images':serialized_data}




"""
 BLOG APIS
"""
@app.post('/api/add_post/', status_code=status.HTTP_201_CREATED)
def add_blog_post(blog:BlogPost):
    blog_data = blog.dict()
    blog_collection = database.BlogPost
    try:
        blog_collection.insert_one(blog_data)
        return {'status':True}
    except:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Failed to add blog post')


#API FOR EDIT BLOG POST
@app.post('/api/edit_blog_content/{b_id}', status_code=status.HTTP_200_OK)
def edit_blog_content(blog_content:BlogPost, b_id:str):
    blog_data = blog_content.dict()
    blog_collection = database.BlogPost
    data_target = blog_collection.find_one({'_id': ObjectId(b_id)})
    if data_target == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Resource not found')
    blog_collection.update_one(
        {'_id': ObjectId(b_id)},
        {'$set':{
                'image_url': blog_data.get('image_url'),
                'post_title': blog_data.get('post_title'),
                'category_name': blog_data.get('category_name'),
                'category_id': blog_data.get('category_id'),
                'short_title': blog_data.get('short_title'),
                'body': blog_data.get('body'),
            }
        })
    return {'status':True}


#GET SPECIFIC BLOG POST
@app.get('/api/get_blog_content/{b_id}', status_code=status.HTTP_201_CREATED)
def get_blog_content(b_id:str):
    blog_collection = database.BlogPost
    data_target = blog_collection.find_one({'_id': ObjectId(b_id)})
    if data_target == None:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Resource not found')
    ok_data = {
        'id': str(data_target.get('_id')),
        'image_url': str(data_target.get('image_url')),
        'post_title': str(data_target.get('post_title')),
        'category_name': str(data_target.get('category_name')),
        'category_id': str(data_target.get('category_id')),
        'short_title': str(data_target.get('short_title')),
        'body': str(data_target.get('body'))
    }
    return {'status':True, 'content':ok_data}

#GET ALL BLOG CONTENTS
@app.get('/api/get_blog_posts/')
def get_blog_posts():
    blog_collection = database.BlogPost
    data = blog_collection.find({})
    serialized_data = [{
        'id':str(d.get('_id')),
        'post_title':str(d.get('post_title')),
        'category_name':str(d.get('category_name')),
        'image_url':str(d.get('image_url')),
        'category_id':str(d.get('category_id')),
        'body':str(d.get('body')),
        'short_title': str(d.get('short_title'))} for d in data]
    return {'status':True, 'blogs':serialized_data}

#DELETE PAGE CONTENT
@app.delete('/api/del_blog_post/{b_id}/', status_code=status.HTTP_200_OK)
def delete_blog_post(b_id:str):
    blog_collection = database.BlogPost
    data = blog_collection.find_one({'_id': ObjectId(b_id)})
    if data == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Resource not found')
    blog_collection.delete_one(data)
    return {'status':True}






"""
PAGE CONTENT API
"""

#API FOR ADDING PAGE
@app.post('/api/add_page_content/', status_code=status.HTTP_201_CREATED)
def add_blog_post(page_content:PageContent):
    page_data = page_content.dict()
    page_collection = database.PageContent
    try:
        page_collection.insert_one(page_data)
        return {'status':True}
    except:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Failed to add page content')


#API FOR EDIT PAGE CONTENT
@app.post('/api/edit_page_content/{c_id}', status_code=status.HTTP_200_OK)
def edit_page_content(page_content:PageContent, c_id:str):
    page_data = page_content.dict()
    page_collection = database.PageContent
    data_target = page_collection.find_one({'_id': ObjectId(c_id)})
    if data_target == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Resource not found')
    page_collection.update_one(
        {'_id': ObjectId(c_id)},
        {'$set':{
                'image_url': page_data.get('image_url'),
                'content_title': page_data.get('content_title'),
                'body': page_data.get('body'),
                'page': page_data.get('page')
            }
        })
    return {'status':True}

    
#GET SPECIFIC PAGE CONTENT
@app.get('/api/edit_page_content/{c_id}', status_code=status.HTTP_201_CREATED)
def get_page_content(c_id:str):
    page_collection = database.PageContent
    data_target = page_collection.find_one({'_id': ObjectId(c_id)})
    if data_target == None:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Resource not found')
    ok_data = {
        'id': str(data_target.get('_id')),
        'image_url': str(data_target.get('image_url')),
        'content_title': str(data_target.get('content_title')),
        'body': str(data_target.get('body')),
        'page': str(data_target.get('page'))
    }
    return {'status':True, 'content':ok_data}

#GET ALL PAGE CONTENTS
@app.get('/api/get_page_content/')
def get_image_for_blog():
    image_collection = database.PageContent
    data = image_collection.find({})
    serialized_data = [{
        'id':str(d.get('_id')),
        'content_title':str(d.get('content_title')),
        'page': str(d.get('page'))} for d in data]
    
    return {'status':True, 'contents':serialized_data}




#GET SPECIFIC PAGE CONTENTS
@app.get('/api/get_specific_page_content/{page}')
def get_specific_page_content(page:str):
    page_collection = database.PageContent
    data = page_collection.find({'page':page})
    serialized_data = [{
        'id':str(d.get('_id')),
        'content_title':str(d.get('content_title')),
        'image_url':str(d.get('image_url')),
        'body':str(d.get('body')),
        'page': str(d.get('page'))} for d in data]
    return {'status':True, 'contents':serialized_data}




#DELETE PAGE CONTENT
@app.delete('/api/del_page_content/{c_id}/', status_code=status.HTTP_200_OK)
def delete_page_content(c_id:str):
    page_collection = database.PageContent
    data = page_collection.find_one({'_id': ObjectId(c_id)})
    if data == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Resource not found')
    page_collection.delete_one(data)
    return {'status':True}
