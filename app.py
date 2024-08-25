from fastapi import FastAPI, HTTPException, status, Request, Response, Header
from pymongo import MongoClient
from fastapi.middleware.cors import CORSMiddleware
from bson.objectid import ObjectId
# from fastapi_pagination import Page, add_pagination
# from fastapi_pagination.ext.pymongo import paginate
from typing import List
from utils.database import connect_to_db
from utils.models import LogInDetails, Category, ImageModel, ImageGroup, BlogPost, Admin, PageContent, EmailNewsletter

#initialize app
app = FastAPI()
"""SET UP CORS"""
origins = ["http://localhost:5173", "https://fyapurplegirls.org"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_headers=["*"],
    allow_methods=["*"]
)

database = connect_to_db()

#auth helpers
def VALIDATE_TOKEN(token):
    auth_collection = database.Admin
    match = auth_collection.find_one({'token':token})
    if match is not None:
        return match
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Admin token not found')
    
@app.post('/api/validate_token/', status_code=status.HTTP_200_OK)
def validate_toke(token:str=Header()):
    if VALIDATE_TOKEN(token):
        return {'status':True, 'valid':True}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Token Invalid')

@app.post("/api/auth/login/", status_code=status.HTTP_200_OK)
def login_doa(login:LogInDetails):
    auth_collection = database.Admin
    login_detail_dict = login.model_dump() #from user
    given_pword = login_detail_dict.get('password')
    given_email = login_detail_dict.get('email')

    data = auth_collection.find_one({'email': given_email}) #from db
    if data == None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='DOA details not found')
    if data.get('password') == given_pword:
        return {'status':True, 'token':data.get('token')}
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='DOA details not found')

#root
@app.get("/")
def root():
    return {"message": "Hello Purple Girls"}

"""
category apis
"""
@app.post('/api/category/', status_code=status.HTTP_201_CREATED)
def create_category(category:Category, token:str=Header()):
    if VALIDATE_TOKEN(token):
        category_data = category.model_dump()
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
def create_image_group(image_group:ImageGroup, token:str=Header()):
    if VALIDATE_TOKEN(token):
        group_data = image_group.model_dump()
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
    serialized_data.reverse()
    return {'status':True, 'groups':serialized_data}


@app.post('/api/add_image/', status_code=status.HTTP_201_CREATED)
def add_image(image:ImageModel, token:str=Header()):
    if VALIDATE_TOKEN(token):
        image_data = image.model_dump()
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
def add_blog_post(blog:BlogPost, token:str=Header()):
    if VALIDATE_TOKEN(token):
        blog_data = blog.model_dump()
        blog_collection = database.BlogPost
        try:
            blog_collection.insert_one(blog_data)
            return {'status':True}
        except:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Failed to add blog post')

#API FOR EDIT BLOG POST
@app.post('/api/edit_blog_content/{b_id}', status_code=status.HTTP_200_OK)
def edit_blog_content(blog_content:BlogPost, b_id:str, token:str=Header()):
    if VALIDATE_TOKEN(token):
        blog_data = blog_content.model_dump()
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
        'body': str(data_target.get('body')),
        'date':str(data_target.get('date')),
    }
    return {'status':True, 'content':ok_data}

#GET ALL BLOG CONTENTS
@app.get('/api/get_blog_posts/')
def get_blog_posts(page:int=1, limit:int=10):
    blog_collection = database.BlogPost
    #get last item in blog
    all = list(blog_collection.find({}))
    last_post = all[-1]
    last_id = last_post.get('_id')
    is_last = False
    print(last_id)
    #get data for serialization
    data = blog_collection.find({}).skip((page-1) * limit).limit(limit)
    serialized_data = []
    for d in data:
        if(last_id == d.get('_id')):
            is_last = True
        serialized_data.append({
            'id':str(d.get('_id')),
            'post_title':str(d.get('post_title')),
            'category_name':str(d.get('category_name')),
            'image_url':str(d.get('image_url')),
            'category_id':str(d.get('category_id')),
            'body':str(d.get('body')),
            'date':str(d.get('date')),
            'short_title': str(d.get('short_title')),
        })
    serialized_data.reverse()
    return {'status':True, 'blogs':serialized_data, 'is_last':is_last}

#DELETE blog CONTENT
@app.delete('/api/del_blog_post/{b_id}/', status_code=status.HTTP_200_OK)
def delete_blog_post(b_id:str, token:str=Header()):
    if VALIDATE_TOKEN(token):
        blog_collection = database.BlogPost
        data = blog_collection.find_one({'_id': ObjectId(b_id)})
        if data == None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Resource not found')
        blog_collection.delete_one(data)
        return {'status':True}

#GET LAST BLOG POST
@app.get('/api/get_last_post/')
def get_last_post():
    blog_collection = database.BlogPost
    #get last item in blog
    all = list(blog_collection.find({}))
    last_post = all[-1]
    #get data for serialization
    serialized_data = {
        'id':str(last_post.get('_id')),
        'post_title':str(last_post.get('post_title')),
        'category_name':str(last_post.get('category_name')),
        'image_url':str(last_post.get('image_url')),
        'category_id':str(last_post.get('category_id')),
        'body':str(last_post.get('body')),
        'date':str(last_post.get('date')),
        'short_title': str(last_post.get('short_title')),
    }
    return {'status':True, 'data':serialized_data}


#GET BLOG POSTS BY CATEGORY
@app.get('/api/get_posts_by_category/')
def get_blog_posts(category_id:str, page:int=1, limit:int=10):
    blog_collection = database.BlogPost
    #get last item in blog
    all = list(blog_collection.find({'category_id':str(category_id)}).skip((page-1) * limit).limit(limit))
    last_post = all[-1]
    last_id = last_post.get('_id')
    is_last = False
    serialized_data = []
    for d in all:
        if(last_id == d.get('_id')):
            is_last = True
        serialized_data.append({
            'id':str(d.get('_id')),
            'post_title':str(d.get('post_title')),
            'category_name':str(d.get('category_name')),
            'image_url':str(d.get('image_url')),
            'category_id':str(d.get('category_id')),
            'body':str(d.get('body')),
            'date':str(d.get('date')),
            'short_title': str(d.get('short_title')),
        })
    serialized_data.reverse()
    return {'status':True, 'blogs':serialized_data, 'is_last':is_last}

#GET LAST 3 POSTS
@app.get('/api/get_recent_posts/')
def get_blog_posts():
    blog_collection = database.BlogPost
    #get last item in blog
    all = list(blog_collection.find({}))
    serialized_data = []
    if len(all) > 3:
        recent_posts = all[-3:]
        #get data for serialization
        for d in recent_posts:
            serialized_data.append({
                'id':str(d.get('_id')),
                'post_title':str(d.get('post_title')),
                'category_name':str(d.get('category_name')),
                'image_url':str(d.get('image_url')),
                'category_id':str(d.get('category_id')),
                'body':str(d.get('body')),
                'date':str(d.get('date')),
                'short_title': str(d.get('short_title')),
            })
        serialized_data.reverse()
        return {'status':True, 'blogs':serialized_data}
    else:
        for d in all:
            serialized_data.append({
                'id':str(d.get('_id')),
                'post_title':str(d.get('post_title')),
                'category_name':str(d.get('category_name')),
                'image_url':str(d.get('image_url')),
                'category_id':str(d.get('category_id')),
                'body':str(d.get('body')),
                'date':str(d.get('date')),
                'short_title': str(d.get('short_title')),
            })
            serialized_data.reverse()
        return {'status':True, 'blogs':serialized_data}


"""
PAGE CONTENT API
"""
#API FOR ADDING PAGE
@app.post('/api/add_page_content/', status_code=status.HTTP_201_CREATED)
def add_blog_post(page_content:PageContent, token:str=Header()):
    if VALIDATE_TOKEN(token):
        page_data = page_content.model_dump()
        page_collection = database.PageContent
        try:
            page_collection.insert_one(page_data)
            return {'status':True}
        except:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Failed to add page content')

#API FOR EDIT PAGE CONTENT
@app.post('/api/edit_page_content/{c_id}', status_code=status.HTTP_200_OK)
def edit_page_content(page_content:PageContent, c_id:str, token:str=Header()):
    if VALIDATE_TOKEN(token):
        page_data = page_content.model_dump()
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
@app.get('/api/edit_page_content/{c_id}', status_code=status.HTTP_200_OK)
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
def delete_page_content(c_id:str, token:str=Header()):
    if VALIDATE_TOKEN(token):
        page_collection = database.PageContent
        data = page_collection.find_one({'_id': ObjectId(c_id)})
        if data == None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Resource not found')
        page_collection.delete_one(data)
        return {'status':True}

"""
Admin home page stat
"""
@app.get('/api/get_stat/')
def get_specific_page_content(token:str=Header()):
    if VALIDATE_TOKEN(token):
        post_count = database.BlogPost.count_documents({})
        cat_count = database.Category.count_documents({})
        return {'status':True, 'number_of_posts':post_count, 'number_of_categories':cat_count}














"""
Email newsletter API
"""

def not_duplicate(email_data):
    newsletter_collection = database.Emails    
    test = newsletter_collection.find_one({'email': email_data.get("email")})
    print(test)
    if test == None:
        return True
    else:
        return False

#API FOR ADDING PAGE
@app.post('/api/register_email/', status_code=status.HTTP_201_CREATED)
def add_email(newsletter:EmailNewsletter):
    email_data = newsletter.model_dump()
    newsletter_collection = database.Emails
    if not_duplicate(email_data):
        try:
            newsletter_collection.insert_one(email_data)
            return {'status':True}
        except:
            return {'status':False}
    else:
        return {'status':False}
        
#GET ALL EMAILS
@app.get('/api/get_emai/')
def get_image_for_blog(token:str=Header()):
    if VALIDATE_TOKEN(token):
        newsletter_collection = database.Emails
        data = newsletter_collection.find({})
        serialized_data = [{
            'id':str(d.get('_id')),
            'email':str(d.get('email'))} for d in data]
        
        return {'status':True, 'contents':serialized_data}
    
