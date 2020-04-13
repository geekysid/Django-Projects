from django.shortcuts import render
from django.http import HttpResponse
import requests, json, time, csv, os, mimetypes
from datetime import datetime
from InstagramAPI import InstagramAPI
from random import choice
from django.http import JsonResponse

# GLOBAL VARIABLES
posts_list = []     # holds list of all post related to the tag in the form of dictionary
user_id_set = set()     # holds set of ids of all users related to the posts
user_list = []     # holds list of all users related to the posts in the form of dictionary
max_post_count = 200    # holds maximum number of post to  be fetched
hashtag = ''        # holds hashtag
post_file = hashtag+'_post.csv'  # holds name of post data file
user_file = hashtag+'_user.csv' # holds name of user data fil
cred_file_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
cred_file_name = os.path.join(cred_file_path, 'userdetails.json')
csv_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'csv/instagram')


# Create your views here.
def index(request):
    
    # checking of view device is mobile or not
    MOBILE_TABLET_FLAG = device_check(request)
    
    params = {'MOBILE_TABLET_FLAG': MOBILE_TABLET_FLAG}
    
    return render(request, 'instagramscraper/index.html', params)


# downloading file
def save_file(request):
    if (request.method == 'GET') and ('file_name' in request.GET):
        if not request.GET.get('file_name') == '' or request.GET.get('file_name') == None:
            file_name = request.GET.get('file_name')
            file_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            file = os.path.join(file_path, file_name)

            data_list = []
            with open (file, 'r') as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')
                line_count = 0
                for row in csv_reader:
                    if line_count == 0:
                        csv_header = row
                        line_count += 1
                    else:
                        data_list.append(row)
                        line_count += 1

            for item in file_name.split('/'):
                print(item)

            resp = HttpResponse(content_type='application/x-download')
            resp = HttpResponse(content_type='text/csv')
            resp['Content-Disposition'] = 'attachment; filename="'+(file_name.split('/'))[2]+'"'
            print(resp['Content-Disposition'])
            writer = csv.writer(resp)
            writer.writerow(csv_header)
            for data in data_list:
                writer.writerow(data)
            return resp


def exceptionCheck(file, e):
    with open(file, 'w') as error_log:
        error_log.write(str(e))


def fetch_data(request):

    # exceptionCheck('dummy_file.txt', 'Juts a dummy File')
    

    # accessing global variables
    global hashtag
    global max_post_count
    global posts_list
    global user_list
    global user_id_set
    global post_file
    global user_file
    global cred_file_name
    global csv_file_path

    # checking if valid request is made during ajax call
    if (request.method == 'POST') and ('insta_hashtag' in request.POST) and ('max_post_count' in request.POST):
        # try:
        hashtag = request.POST.get('insta_hashtag', '').strip().replace(' ', '').replace('#', '')    # fetching hashtag from user and cleaning it
        max_post_count = int(request.POST.get('max_post_count', 0).strip().replace(' ', ''))    # fetching count of maximum post to be extracted from user and cleaning it   
        
        post_file = os.path.join(csv_file_path, hashtag+'_post.csv')
        user_file = os.path.join(csv_file_path, hashtag+'_user.csv')        
        
        if not(hashtag == '' or max_post_count == 0):
            
            print(f'Initiating search for hashtag: #{hashtag}')

            start_time = time.time()
            main()
            end_time = time.time()

            execution_time = end_time-start_time

            execution_time_hrs = int(execution_time//3600)
            execution_time_mins = int((execution_time%3600)//60)
            execution_time_secs = int((execution_time%3600)%60)

            print()
            print('*'*50)
            print(f'Total Execution Time: {execution_time_hrs} hrs, {execution_time_mins} mins, {execution_time_secs} seconds')
            print(f'Total Execution Time in Seconds: {int(execution_time)} seconds')
            print('*'*50)
            print()

            params = {
                'hashtag': hashtag,
                'success': 'true',
                'max_post_count': max_post_count,
                'post_fetched_count': len(posts_list),
                'user_fetched_count': len(user_id_set),
                # 'post_file': '/'.join(post_file.split('/')[len(post_file.split('/'))-3:]),
                'post_file': '/'.join(post_file.split('/')[len(post_file.split('/'))-3:]),
                'user_file': '/'.join(user_file.split('/')[len(user_file.split('/'))-3:]),
                'execution_time_hrs': f'{execution_time_hrs} hrs, {execution_time_mins} mins, {execution_time_secs} seconds',
                'execution_time_mins': execution_time_mins,
                'execution_time_secs': execution_time_secs,
                'execution_time': execution_time,
                'error': ''
            }
                    
            # return HttpResponse('')
            return JsonResponse(params)

        else:
            params = {'error': 'Not valid Arguments'}
            # return HttpResponse('')
            return JsonResponse(params)
        # except Exception as e:
        #     params = {'error': f'Oh no!!!! Something went wrong. Try again later!\n {str(e)}'}
        #     return render(request, 'octaprofile/index.html', params)    
    else:
        params = {'error': 'Not valid Request'}
        # return HttpResponse('')
        return JsonResponse(params)

    # except Exception as e:
    #     exceptionCheck('error_log_fetch_data.txt', e)

# MAIN ----- STARTS
def main():
    # try:
    fetch_post_from_hashtag()    # fetching post related to the hastag
    save_post_data_to_csv()      # saving post data to csv file

    fetch_user_data()            # fetching post related to the hastag
    save_user_data_to_csv()      # saving user data to csv file
    # except Exception as e:
    #     exceptionCheck('error_log_main.txt', e)
# MAIN ----- ENDS


# FETCHING CREDENTIALS FROM FILE STARTS
def fetch_login_credentials():
    # try:
    global cred_file_name
    with open(cred_file_name, 'r') as cred:
        credentials = json.load(cred)

    username_list = credentials.keys()
    username = choice(list(username_list))
    password = credentials[username]
    
    return [username, password]
    # return ['pythonfreak01', 'pythonfreak0101']
    
    # except Exception as e:
    #     exceptionCheck('error_log_fetch_login_credentials.txt', e)
    #     return ['','']
# FETCHING CREDENTIALS FROM FILE ENDS


# LOGIN TO INSTAGRAM AND RETURNING LOGGED IN OBJECT --- START
def user_login():
    # try:
    credentials = fetch_login_credentials()
    api = InstagramAPI(credentials[0], credentials[1])
    api.login()
    return api
    # except Exception as e:
    #     exceptionCheck('error_log_user_login.txt', e)
# LOGIN TO INSTAGRAM AND RETURNING LOGGED IN OBJECT --- END


# FUNCTION TO FETCH POSTS RELATED TO GIVEN HASHTAG ----- STARTS
def fetch_post_from_hashtag():
    # try:
    # accesing global variable
    global posts_list
    global user_id_set
    global hashtag
    global max_post_count

    # few defaults values set
    posts_ids = []          # holds list ids of all post
    has_more_posts = True   # holds True if page there are more page else holds False
    page_count = 0          # holds number of pages fetched
    max_id = ''             # holds a value which is used if there is next page else is blank
    loopcount = 0           # counts number of loops. is used to create a new user login after every predefined number
    new_login_after = 10     # value that defines number of loops after which a new user login is created 

    # login using a new user
    api_logged = user_login()
    
    # started fetching posts
    while has_more_posts:

        # printing page count to know how many pages are scraped
        page_count = page_count + 1

        # using getHashtagFeed() from API to get list of post
        api_logged.getHashtagFeed(hashtag, maxid=max_id)
        result = api_logged.LastJson    # fetching json from the fetched data

        # looping through all the posts if valie is fetched
        if 'items' in result.keys():
            print(f'Page # {page_count}')
            for post in result['items']:
                try:
                    indv_post = {}
                    # fetching post info
                    post_id = post['pk']
                    indv_post['post_id'] = post_id
                    try:
                        field = 'post_media_type'
                        media_type = post['media_type']
                        indv_post[field] = media_type
                    except Exception as e:
                        post_data_exception_free(indv_post, field, post_id, e)
                    try:
                        field = 'post_caption'
                        indv_post[field] = post['caption'].get('text', '')
                    except Exception as e:
                        post_data_exception_free(indv_post, field, post_id, e)
                    try:
                        field = 'post_created_date_utc'
                        indv_post[field] = time.strftime('%Y-%m-%d', time.localtime(int(post['caption'].get('created_at_utc', ''))))
                    except Exception as e:
                        post_data_exception_free(indv_post, field, post_id, e)
                    try:
                        field = 'post_created_at_time_utc'
                        indv_post[field] = time.strftime('%H:%M:%S', time.localtime(int(post['caption'].get('created_at_utc', ''))))
                    except Exception as e:
                        post_data_exception_free(indv_post, field, post_id, e)
                    try:
                        field = 'post_created_at_date'
                        indv_post[field] = time.strftime('%Y-%m-%d', time.localtime(int(post['caption'].get('created_at', ''))))
                    except Exception as e:
                        post_data_exception_free(indv_post, field, post_id, e)
                    try:
                        field = 'post_created_at_time'
                        indv_post[field] = time.strftime('%H:%M:%S', time.localtime(int(post['caption'].get('created_at', ''))))
                    except Exception as e:
                        post_data_exception_free(indv_post, field, post_id, e)
                    try:
                        field = 'post_image_url'
                        if media_type == 8:
                            media_url = []
                            if 'carousel_media' in post.keys():
                                if int(post['carousel_media_count']) > 0:
                                    for media in post['carousel_media']:
                                        url = media['image_versions2']['candidates'][0].get('url', '')
                                        media_url.append(url)
                            if len(media_url) > 0:
                                indv_post[field] = ', '.join(media_url)
                        else:
                            indv_post[field] = post['image_versions2']['candidates'][0].get('url', '')
                    except Exception as e:
                        post_data_exception_free(indv_post, field, post_id, e)
                    try:
                        field = 'post_location'
                        indv_post[field] = post['location'].get('name', '')
                    except Exception as e:
                        post_data_exception_free(indv_post, field, post_id, e)
                    try:
                        field = 'post_location_short_name'
                        indv_post[field] = post['location'].get('short_name', '')
                    except Exception as e:
                        post_data_exception_free(indv_post, field, post_id, e)
                    try:
                        field = 'post_location_lng'
                        indv_post[field] = post['location'].get('lng', '')
                    except Exception as e:
                        post_data_exception_free(indv_post, field, post_id, e)
                    try:
                        field = 'post_location_lat'
                        indv_post[field] = post['location'].get('lat', '')
                    except Exception as e:
                        post_data_exception_free(indv_post, field, post_id, e)
                    try:
                        field = 'post_like_count'
                        indv_post[field] = post.get('like_count', '')
                    except Exception as e:
                        post_data_exception_free(indv_post, field, post_id, e)
                    try:
                        field = 'post_user_id'
                        indv_post[field] = post['user'].get('pk', '')
                    except Exception as e:
                        post_data_exception_free(indv_post, field, post_id, e)
                    try:
                        field = 'post_comment_count'
                        indv_post[field] = post.get('comment_count', '')
                    except Exception as e:
                        post_data_exception_free(indv_post, field, post_id, e)
                    try:
                        field = 'post_video_codec'
                        indv_post[field] = post.get('video_codec', '')
                    except Exception as e:
                        post_data_exception_free(indv_post, field, post_id, e)
                    try:
                        field = 'post_video_versions'
                        indv_post[field] = post['video_versions'][0].get('url', '')
                    except Exception as e:
                        post_data_exception_free(indv_post, field, post_id, e)
                    try:
                        field = 'post_has_audio'
                        indv_post[field] = post.get('has_audio', False)
                    except Exception as e:
                        post_data_exception_free(indv_post, field, post_id, e)
                    try:
                        field = 'post_video_duration'
                        indv_post[field] = post.get('video_duration', '')
                    except Exception as e:
                        post_data_exception_free(indv_post, field, post_id, e)
                    try:
                        field = 'post_video_versions'
                        indv_post[field] = post['user']['video_versions'][0].get('url', '')
                    except Exception as e:
                        post_data_exception_free(indv_post, field, post_id, e)
                    
                    try:
                        post_likers_id = []
                        if 'likers' in post.keys():
                            if int(post['like_count']) > 0:
                                for like_user in post['likers']:
                                    post_likers_id.append(str(like_user['pk']))

                        if len(post_likers_id) > 0:
                            indv_post['post_likers_id'] = ', '.join(post_likers_id)
                        else:
                            indv_post['post_likers_id'] = ''
                    except Exception as e:
                        print(f'Post Likes Missing from Post ID: {post_id}')
                        print(f'**ERROR** {str(e)}')

                    try:
                        post_tagged_users_id = []
                        if 'usertags' in post.keys():
                            if len(post['usertags']['in']) > 0:
                                for tagged_user in post['usertags']['in']:
                                    post_tagged_users_id.append(str(tagged_user['user']['pk']))

                        if len(post_likers_id) > 0:
                            indv_post['post_tagged_users_id'] = ', '.join(post_tagged_users_id)
                        else:
                            indv_post['post_tagged_users_id'] = ''
                    except Exception as e:
                        print(f'People Tagged Missing from Post ID: {post_id}')
                        print(f'**ERROR** {str(e)}')

                    posts_list.append(indv_post)
            
                except Exception as e:
                    print(f'***EXPECTION: {str(e)}')
            
            has_more_posts = result.get('more_available', '') #fetching detail if there are more post after this page

            # evaluating stop condition to fetch given number of posts
            if len(posts_list) >= max_post_count:
                posts_list = posts_list[0:max_post_count]   # truncate post list to given number of posts
                has_more_posts = False  # stopping loop
                print(f'FETCHED {max_post_count} number of posts for given hashtag')

            # evaluating next page condition
            elif has_more_posts:
                # evaluating new login condition
                if loopcount % new_login_after == 0:
                    api_logged = user_login()
                max_id = result.get('next_max_id', '')
                time.sleep(2)

            loopcount = loopcount + 1

            # if loopcount == 2:
            #     print('Terminating after 1 loop')
            #     break
        else:
            print('There seems to be no data fetched. Please try again with proper hashtag')
            break
    
    print(f'Total Posts Fetched: {len(posts_list)}')
    fetch_userid_from_post()
    
    # except Exception as e:
    #     exceptionCheck('error_log_fetch_login_credentials.txt', e)
    #     return ['','']
# FUNCTION TO FETCH POSTS RELATED TO GIVEN HASHTAG ----- ENDS


# FUNCTION TO FETCH USERID FROM POSTS ----- STARTS
def fetch_userid_from_post():

    # accesing global variable
    global posts_list
    global user_id_set
    
    if len(posts_list) > 0:
        for post in posts_list:
            user_id_set.add(post['post_user_id'])

    print(f'Total Unique User Fetched: {len(user_id_set)}')
# FUNCTION TO FETCH USERID FROM POSTS ----- ENDS


# FUNCTION TO FETCH DAAT OF USERS FETCHED USING POST FETCH ----- STARTS
def fetch_user_data():

    # accessing global variable
    global user_id_set
    global user_list

    user_count = 1  # number of users data fetched
    api_logged = user_login()    # logging into system

    #  looping through user_id set
    for userid in user_id_set:
        try:
            api_logged.getUsernameInfo(userid)  # fetching user data from api
            user_data = api_logged.LastJson  # converting fetched data into json
            
            user = {}  # dict of user data

            # fetching user info
            try:
                field = 'username'
                user[field] = user_data['user'].get('username', '')
            except Exception as e:
                user_data_exception_free(user, field, userid, e)
            try:
                field = 'full_name'
                user[field] = user_data['user'].get('full_name', '')
            except Exception as e:
                user_data_exception_free(user, field, userid, e)
            try:
                field = 'is_private'
                user[field] = user_data['user'].get('is_private', True)
            except Exception as e:
                user_data_exception_free(user, field, userid, e)
            try:
                field = 'is_verified'
                user[field] = user_data['user'].get('is_verified', False)
            except Exception as e:
                user_data_exception_free(user, field, userid, e)
            try:
                field = 'media_count'
                user[field] = user_data['user'].get('media_count', 0)
            except Exception as e:
                user_data_exception_free(user, field, userid, e)
            try:
                field = 'follower_count'
                user[field] = user_data['user'].get('follower_count', 0)
            except Exception as e:
                user_data_exception_free(user, field, userid, e)
            try:
                field = 'following_count'
                user[field] = user_data['user'].get('following_count', 0)
            except Exception as e:
                user_data_exception_free(user, field, userid, e)
            try:
                field = 'biography'
                user[field] = user_data['user'].get('biography', '')
            except Exception as e:
                user_data_exception_free(user, field, userid, e)
            try:
                field = 'external_url'
                user[field] = user_data['user'].get('external_url', '')
            except Exception as e:
                user_data_exception_free(user, field, userid, e)
            try:
                field = 'total_igtv_videos'
                user[field] = user_data['user'].get('total_igtv_videos', '')
            except Exception as e:
                user_data_exception_free(user, field, userid, e)
            try:
                field = 'hd_profile_pic_url'
                user[field] = user_data['user']['hd_profile_pic_url_info'].get('url', '')
            except Exception as e:
                user_data_exception_free(user, field, userid, e)
            try:
                field = 'is_business'
                user[field] = user_data['user'].get('is_business', False)
            except Exception as e:
                user_data_exception_free(user, field, userid, e)
            try:
                field = 'category'
                user[field] = user_data['user'].get('category', '')
            except Exception as e:
                user_data_exception_free(user, field, userid, e)
            try:
                field = 'city_id'
                user[field] = user_data['user'].get('city_id', '')
            except Exception as e:
                user_data_exception_free(user, field, userid, e)
            try:
                field = 'city_name'
                user[field] = user_data['user'].get('city_name', '')
            except Exception as e:
                user_data_exception_free(user, field, userid, e)
            try:
                field = 'contact_phone_number'
                user[field] = user_data['user'].get('contact_phone_number', '')
            except Exception as e:
                user_data_exception_free(user, field, userid, e)
            try:
                field = 'latitude'
                user[field] = user_data['user'].get('latitude', '')
            except Exception as e:
                user_data_exception_free(user, field, userid, e)
            try:
                field = 'longitude'
                user[field] = user_data['user'].get('longitude', '')
            except Exception as e:
                user_data_exception_free(user, field, userid, e)
            try:
                field = 'public_email'
                user[field] = user_data['user'].get('public_email', '')
            except Exception as e:
                user_data_exception_free(user, field, userid, e)
            try:
                field = 'public_phone_number'
                user[field] = user_data['user'].get('public_phone_number', '')
            except Exception as e:
                user_data_exception_free(user, field, userid, e)
            try:
                field = 'phone_country_code'
                user[field] = user_data['user'].get('public_phone_country_code', '')
            except Exception as e:
                user_data_exception_free(user, field, userid, e)
            try:
                field = 'zip'
                user[field] = user_data['user'].get('zip', '')
            except Exception as e:
                user_data_exception_free(user, field, userid, e)
            
            # apending fetched user data to the list
            user_list.append(user)

            user_count = user_count + 1     # increasing value of users fetched by 1 with every loop
            
            print(f'User with Userid {userid} added')
            
            # evaluating new login condition
            if user_count % 20 == 0:
                api_logged = user_login()

        except Exception as e:
            print(f'Some Error occured while fetching dada for user with userid: {userid}')
            print(f'**ERROR**: {str(e)}'
            )
    print(f'Total Users Added: {len(user_list)}')
# FUNCTION TO FETCH DAAT OF USERS FETCHED USING POST FETCH ----- ENDS


# STORING POSTS DATA IN CSV FILE ----- STARTS
def save_post_data_to_csv():

    # accessing gloabl variable
    global posts_list
    global hashtag
    global post_file

    # running loop if 1 or more then 1 post is fetched
    if len(posts_list) > 0:
        csv_header = [x for x in posts_list[0].keys()]      # to be used as header in csv
        filename = post_file       # name of csv
        
        # creating a csv file
        with open(filename, 'w') as file:
            writer = csv.DictWriter(file, fieldnames = csv_header)  # creating a DictWriter object
            writer.writeheader()    # writing headers in csv
            for data in posts_list:  # looping thorogh each post in posts_list
                writer.writerow(data)   # saving each post in csv file
            print(f'\nSuccessfully Added Posts Data to {filename}')

        
        # download_file = HttpResponse(content_type='text/csv') 
        # download_file['Content-Disposition'] = 'attachment; filename='+hashtag+'_post.csv'
        
        # writer = csv.writer(download_file)  # creating a DictWriter object
        # writer.writeheader()    # writing headers in csv
        # for data in posts_list:  # looping thorogh each post in posts_list
        #     writer.writerow(data)   # saving each post in csv file
        # print(f'\nSuccessfully Added Posts Data to {filename}')
        # return download_file
# STORING POSTS DATA IN CSV FILE ----- ENDS


# STORING USERS DATA IN CSV FILE ----- STARTS
def save_user_data_to_csv():

    # accessing gloabl variable
    global user_list
    global hashtag
    global user_file

    # running loop if 1 or more users is fetched
    if len(user_list) > 0:
        csv_header = [x for x in user_list[0].keys()]      # to be used as header in csv
        filename = user_file      # name of csv

        # creating a csv file
        with open(filename, 'w') as file:
            writer = csv.DictWriter(file, fieldnames = csv_header)  # creating a DictWriter object
            writer.writeheader()    # writing headers in csv
            for data in user_list:  # looping thorogh each post in user_list
                writer.writerow(data)   # saving each user in csv file
            print(f'\nSuccessfully Added User Data to {filename}')
# STORING USERS DATA IN CSV FILE ----- ENDS


# METHOD TO MAKE SURE NO ERROR OCCURES WHILE FETCHING POST DATA ----- STARTS
def post_data_exception_free(post, field, post_id, e):
    post[field] = ''
    # print(f'Unable to fetch {field} from Post with Postid: {post_id}')
    # print(f'**ERROR** {str(e)}')
# METHOD TO MAKE SURE NO ERROR OCCURES WHILE FETCHING POST DATA ----- ENDS


# METHOD TO MAKE SURE NO ERROR OCCURES WHILE FETCHING USER DATA ----- STARTS
def user_data_exception_free(user, field, userid, e):
    user[field] = ''
    # print(f'Unable to fetch {field} from user with userid: {userid}')
    # print(f'**ERROR** {str(e)}')
# METHOD TO MAKE SURE NO ERROR OCCURES WHILE FETCHING USER DATA ----- ENDS


def device_check(request):
    if (request.user_agent.is_mobile == True) or (request.user_agent.is_tablet == True):
        return 'true'
    else:
        return 'false'

