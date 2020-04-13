from django.shortcuts import render, redirect
from django.http import JsonResponse
from Account.models import UserProfile, ErrorCode
from django.db.models import Q
from RiddleChamp.models import *
import pandas as pd
from datetime import datetime, timedelta, date, time
from random import choice
import numpy as np
from django.core.files.storage import FileSystemStorage
from .forms import *
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import zlib, hashlib, time, os, smtplib, emoji,json
from geekysid import cvEmailer, settings


__BASE_SCORE = 50
# Base_url = 'http://127.0.0.1:8000/'
Base_url = 'http://www.geekysid.com/'

# method that returns data to show alert depending on url like index/s/8768
def get_AlertDataFromUrl(url):
    url_path = url.split('/')
    status = url_path[len(url_path)-2]
    code = url_path[len(url_path)-1]

    type_ = 'success' if status == 's' else ('error' if status == 'e' else None)

    if type_ is not None:
        error_obj = ErrorCode.objects.filter(hash_code=code, Type=type_)
        if len(error_obj) == 1:
            # print(error_obj[0])
            return (error_obj[0])
        else:
            return (None)
    else:
        return (None)


# Create your views here.
def index(request):
    if request.user.is_authenticated:

        # this is to make show alert depending on url like index/s/8768
        alertData = get_AlertDataFromUrl(request.META.get('PATH_INFO'))

        user = request.user

        # Fetching USER PROFILE Details
        userProfile_obj = UserProfile.objects.get(user=user)
        userProfile = {
                        "name": userProfile_obj.name,
                        "gender": userProfile_obj.gender,
                        "mobile": userProfile_obj.mobile,
                        "city": userProfile_obj.city,
                        "country": userProfile_obj.country,
                        "avatar": userProfile_obj.avatar
                }

        # fetching USER DEN object
        userDen_list = []
        user_den_map_obj = Hunter_Den_Mapping.objects.filter(hunter=userProfile_obj, member_status=True)

        # TOP 5 DEN DATA
        Top5Den_data = {}

        userDen = {
            'count': len(userDen_list)
        }
        userResponse = {
            'riddlesSovled': 0,
            'totalScore': 0
        }
        userDenDetails= {}

        if user_den_map_obj.count() > 0:
            for user_den_map in user_den_map_obj:
                userDen_list.append(user_den_map.den.den_id)

            userDen = {
                'count': len(userDen_list),
                'den_list' : userDen_list
            }

            # RIDDLES & DEN RELATIONSHIP
            den_riddle_obj = DenRiddle.objects.filter(den__in=userDen_list).values()
            df_den_riddle = pd.DataFrame(list(den_riddle_obj))

            # USER RESPONSE
            userResponse_obj = Response.objects.filter(hunter=user).values()

            # User Response Dataframe
            df_userResponse = pd.DataFrame(list(userResponse_obj))
            # print(df_userResponse)

            # pending riddles
            pending_riddle_count = df_den_riddle.loc[(df_den_riddle['is_pending'] == True, 'is_pending')].count()
            # print(pending_riddle_count)

            # Active and expired riddles count
            available_riddle_count = int(df_den_riddle.loc[(df_den_riddle['is_pending'] == False, 'is_pending')].count())
            # print(available_riddle_count)

            # USER WITH NO RESPOSE
            if not df_userResponse.empty:
                # total score of the hunter
                totalScore = df_userResponse['score'].sum()

                # number of riddles attempted by hunter
                riddles_attempted = int (len(df_userResponse.groupby('den_riddle_id')))

                # number of riddles solved
                riddlesSovled = int(df_userResponse[(df_userResponse['is_correct'] == True)]['is_correct'].count())

                # number of correct answers by hunter
                right_response = riddlesSovled
                # number of wrong answers by hunter
                wrong_response = int(df_userResponse[(df_userResponse['is_correct'] == False)]['is_correct'].count())

                ResponseChart_data = {
                    "Right Response": right_response,
                    "Wrong Response": wrong_response,
                }

                userResponse = {
                    "totalScore" : totalScore,
                    "riddlesSovled" : riddlesSovled
                }
            else:
                riddlesSovled = 0
                riddles_attempted = 0
                userResponse = {
                    "totalScore" : 0,
                    "riddlesSovled" : 0
                }
                ResponseChart_data = {
                    "Right Response": 0,
                    "Wrong Response": 0,
                }

            riddlesUnsovled = riddles_attempted - riddlesSovled

            #  RIDDLE STATUS CHART
            RiddleStatusChart_data = {
                "SOLVED": riddlesSovled,
                "UNSOLVED" : riddlesUnsovled,
                "Not Attempted": available_riddle_count - riddles_attempted
            }

            # fetching USER's DEN
            userDenDetails = []
            denDetails_obj = Den.objects.filter(den_id__in=userDen_list)

            for den in denDetails_obj:

                # Total Riddle
                total_condition = (df_den_riddle['den_id'] == den.den_id)
                total_riddle_count = df_den_riddle.loc[total_condition, 'den_id'].count()

                # Active Riddles
                active_condition = (df_den_riddle['is_active'] == True) & (df_den_riddle['den_id'] == den.den_id)
                active_riddle_count = df_den_riddle.loc[active_condition, 'is_active'].count()

                # Pending Riddles
                pending_condition = (df_den_riddle['is_pending'] == True) & (df_den_riddle['den_id'] == den.den_id)
                pending_riddle_count = df_den_riddle.loc[pending_condition, 'is_pending'].count()

                if user == den.admin:
                    role = "Admin"
                else:
                    role = "Participant"

                # Fething all Riddles associated with this den
                riddle_list = df_den_riddle[(df_den_riddle['den_id'] == den.den_id)]['den_riddle_id']

                # checking if there us riddle and response for given den
                if not riddle_list.empty and not df_userResponse.empty:
                    df_response = df_userResponse[df_userResponse['den_riddle_id'].isin(riddle_list.tolist())]

                    # number of solved riddle
                    solved_riddle_count = df_response[df_response['is_correct'] == True].is_correct.count()


                    # print(f"{den.name} - Riddle: {len(riddle_list)} - Solved: {solved_riddle_count}")

                    # Total Score
                    total_score = df_response['score'].sum()
                else:
                    solved_riddle_count = 0
                    total_score = 0

                denDict = {
                    "name": den.name,
                    "desc": den.desc,
                    "role": role,
                    "active": den.is_active,
                    "total_count": total_riddle_count,
                    "solved_count": solved_riddle_count,
                    "total_score": f"{total_score:.2f}",
                    "link": '/riddlechamp/den/'+den.uin_code,
                    'active_count': active_riddle_count,
                    'pending_count': pending_riddle_count
                }

                Top5Den_data[den.name] = float(f"{total_score:.2f}")

                userDenDetails.append(denDict)
        else:
            Top5Den_data = {}
            RiddleStatusChart_data = {
                "SOLVED": 0,
                "UNSOLVED" : 0,
                "Not Attempted": 0
            }
            ResponseChart_data = {
                "Right Response": 0,
                "Wrong Response": 0,
            }

        params = {
            'userProfile': userProfile,
            'userDen': userDen,
            'userResponse' : userResponse,
            'userDenDetails': userDenDetails,
            'alertData': alertData,
            "RiddleStatusChart_data" : json.dumps(RiddleStatusChart_data),
            "ResponseChart_data" : json.dumps(ResponseChart_data),
            "Top5Den_data" : json.dumps(Top5Den_data)
        }

        return render(request, 'riddlechamp/index.html', params)
    else:
        return redirect('/account/login/e/7955')


# Den Page View
def den(request):

    if request.user.is_authenticated:
        user = request.user
        user_id = user.id

        alertData = get_AlertDataFromUrl(request.META.get('PATH_INFO'))

        url_path = request.META.get('PATH_INFO')
        url_list = url_path.split('/')

        den_index = url_list.index('den')
        den_uin = url_list[den_index+1]
        current_epoch = datetime.now().timestamp()

        den = Den.objects.filter(uin_code=den_uin)
        userProfile_obj = UserProfile.objects.get(user=user)

        if len(den) > 0:

            try:
                user_den_map = Hunter_Den_Mapping.objects.filter(hunter=userProfile_obj, den=den[0], member_status=True)
                if len(user_den_map) == 1:
                    user_den_map = user_den_map[0]

                    den = den[0]

                    den_id = den.den_id
                    admin = True if (den.admin == request.user) else False

                    # RIDDLES in this den
                    riddle_den_s = DenRiddle.objects.filter(den=den_id)
                    total_riddles = len(riddle_den_s)
                    den_riddle = []

                    # RESPONSE
                    response_obj = Response.objects.filter(den_riddle_id__in=riddle_den_s).values()
                    df_response = pd.DataFrame(list(response_obj))

                    riddle_added_date =[]

                    for riddle_den in riddle_den_s:
                        if datetime.date(riddle_den.added_at) == datetime.date(datetime.now()):
                            riddle_added_date.append(riddle_den.added_at.strftime("%Y/%m/%d"))

                    for riddle_den in riddle_den_s:

                        riddle_den_id = riddle_den.den_riddle_id

                        # score for riddle right answer
                        right_answer_score = riddle_den.riddle.riddle_level.kills*riddle_den.riddle.riddle_level.positive_score_percent

                        # score for riddle right answer
                        wrong_answer_score = (riddle_den.riddle.riddle_level.kills*riddle_den.riddle.riddle_level.negetive_score_percent)/(riddle_den.riddle.max_calls-1)

                        # calculating current user score for this riddle
                        if not df_response.empty:
                            condition_den_riddle_user = (df_response['den_riddle_id'] == riddle_den_id) & (df_response['hunter_id'] == user_id)
                            user_score_riddle = df_response[condition_den_riddle_user]['score'].sum()

                            # calculating if riddle is solved by user or not
                            condition_riddle_solved = (df_response['is_correct'] == True)
                            check_solved = df_response.loc[(condition_den_riddle_user & condition_riddle_solved), 'is_correct'].count()
                            riddle_solved = True if check_solved > 0 else False

                            # calculating if riddle is attempted by user or not
                            check_attempt = df_response.loc[(condition_den_riddle_user),'is_correct'].count()
                            riddle_attempt = True if check_attempt > 0 else False
                        else:
                            riddle_attempt = False
                            user_score_riddle=0
                            riddle_solved = False

                        # making riddle active from pending
                        if riddle_den.is_pending:
                            is_pending = True if (riddle_den.started_at).timestamp() > current_epoch else False
                            if is_pending == False:
                                # FUNCTION NEEDS TO BE ADDED FOR NEW RIDDLE
                                new_riddle = den_riddle_active_update(riddle_den, riddle_den_s, den, riddle_added_date)
                                den_riddle.append({
                                    'den_riddle': new_riddle,           # object of den_riddle
                                    'starting_epoch': (new_riddle.started_at).timestamp(),
                                    'expiry': new_riddle.ending_at.timestamp(),
                                    'riddle_attempt': 0,   # true if user have attempted this riddle
                                    'riddle_solved': 0,     # true if user have solved this riddle
                                    'user_score_riddle': 0,        # score of the score for this riddle
                                    'is_pending': new_riddle.is_pending,
                                    'is_active': new_riddle.is_active,
                                    'has_expired': new_riddle.has_expired,
                                    'uin_code' : new_riddle.uin_code,
                                    'right_ans_score': new_riddle.riddle.riddle_level.positive_score_percent*__BASE_SCORE,
                                    'score_percent': 0,
                                    'wrong_ans_score': new_riddle.riddle.riddle_level.negetive_score_percent*__BASE_SCORE
                                    })

                        # making riddle expire from pending
                        if riddle_den.is_active:
                            is_active = True if (riddle_den.ending_at).timestamp() > current_epoch else False
                            if not is_active:
                                den_riddle_expiry_update(riddle_den)

                        # adding dfeault image if not available
                        if riddle_den.riddle.media == None or riddle_den.riddle.media == '':
                            riddle_den.riddle.media = 'image/riddle/text-icon.jpg'

                        # checking if riddle is expired
                        if (riddle_den.ending_at).timestamp() < current_epoch:
                            is_active = False

                        riddle_den_dict = {
                            'den_riddle': riddle_den,           # object of den_riddle
                            'starting_epoch': (riddle_den.started_at).timestamp(),
                            'expiry': riddle_den.ending_at.timestamp(),
                            'riddle_attempt': riddle_attempt,   # true if user have attempted this riddle
                            'riddle_solved': riddle_solved,     # true if user have solved this riddle
                            'user_score_riddle': user_score_riddle,        # score of the score for this riddle
                            'is_pending': riddle_den.is_pending,
                            'is_active': riddle_den.is_active,
                            'has_expired': riddle_den.has_expired,
                            'uin_code' : riddle_den.uin_code,
                            'right_ans_score': f"{right_answer_score:.2f}",
                            'wrong_ans_score': f"{wrong_answer_score:.2f}",
                            'score_percent': (user_score_riddle*100)/(riddle_den.riddle.riddle_level.positive_score_percent*__BASE_SCORE)
                        }
                        den_riddle.append(riddle_den_dict)

                    den_riddle = sorted(den_riddle, key = lambda i: i['starting_epoch'],reverse=True) 

                    # HUNTERS in this den
                    hunters_den_obj  = Hunter_Den_Mapping.objects.filter(den = den_id, member_status=True)
                    hunters = []
                    top_hunter = None

                    if df_response.empty:
                        top_hunter_id = None
                        user_rank = '-'
                    else:
                        # top hunter id
                        df_hunters_score = 0
                        df_hunters_score = df_response.groupby('hunter_id').score.sum()
                        # print("========", df_hunters_score)
                        top_hunter_id = df_hunters_score.idxmax()
                        # print(df_response['hunter_id'].values)

                        # rank of all hunters
                        df_hunters_rank = df_response.groupby('hunter_id').sum()
                        df_hunters_rank['Rank'] = df_hunters_rank['score'].rank(ascending=False)
                        user_rank = None

                    Top_skRatio_score = 0
                    Top_skRatio_hunter = userProfile_obj.name
                    Top_skRatio_avatar = userProfile_obj.avatar
                    top_hunter = userProfile_obj

                    # creating hunters list
                    for hunter_den in hunters_den_obj:

                        # top hunter
                        if hunter_den.hunter.user.id == top_hunter_id and hunter_den is not None:
                            top_hunter = hunter_den.hunter

                        # if den has atleast one response 
                        if df_response.empty:
                                score = 0
                                hunters_correct_resp = 0
                                hunters_total_resp = 0
                                rank = 0
                        else:
                            # print(df_response['hunter_id'].values)

                            #  If user has atleast one response
                            if hunter_den.hunter.user.id in df_response['hunter_id'].values:

                                # score of hunter
                                score = df_hunters_score.loc[hunter_den.hunter.user.id]

                                # rank of hunter 
                                rank = (df_hunters_rank.loc[hunter_den.hunter.user.id, 'Rank']).astype(np.int)

                                # total number of correct responses
                                condition = (df_response['hunter_id'] == hunter_den.hunter.user.id) & (df_response['is_correct'] == True) 
                                hunters_correct_resp = df_response.loc[condition, 'is_correct'].count()

                                # total number of wrong responses
                                condition = (df_response['hunter_id'] == hunter_den.hunter.user.id) & (df_response['is_correct'] == False) 

                                # total number of responses
                                condition = (df_response['hunter_id'] == hunter_den.hunter.user.id)
                                hunters_total_resp = df_response.loc[condition, 'response_id'].count()

                            else:
                                score = 0
                                rank = "-"
                                hunters_correct_resp = 0
                                hunters_total_resp = 0

                        # calculating skRation
                        if hunters_total_resp > 0:
                            skRatio_score =  hunters_correct_resp / hunters_total_resp
                            if skRatio_score > Top_skRatio_score:
                                Top_skRatio_score = skRatio_score
                                Top_skRatio_hunter = hunter_den.hunter

                            elif (hunters_correct_resp == 0) and (skRatio_score == 0):
                                if Top_skRatio_hunter == None:
                                    Top_skRatio_hunter = hunter_den.hunter

                        # user_rank
                        if hunter_den.hunter.user.id == user.id:
                            user_rank = rank
                            user_score = score

                        h = {
                            'hunter' : hunter_den.hunter,
                            'den_score' : score,
                            # 'last_activity': "NOT KNOWN",
                            'correct_answers' : None,
                            'admin': admin,
                            'rank' : rank,
                            'last_activity': datetime.now().date,
                            'wrong_answers' : None
                        }
                        hunters.append(h)

                    # sorting hunters list on rank
                    hunters = sorted(hunters, key = lambda i: i['den_score'],reverse=True)
                    # print(hunters)

                    # PARAMS - DEN
                    den_details = {
                        "den_id" : den.den_id,
                        "admin": den.admin,
                        "uin_code" : den.uin_code,
                        'total_riddles': total_riddles,
                        "name" : den.name,
                        "avatar" : den.avatar,
                        "started_at" : den.started_at,
                        "ended_at" : den.ended_at,
                        "is_active" : den.is_active,
                        "next_riddle_on" : den.next_riddle_on,
                        "TotalPuzzels" : None,
                        "TotalHunters" : len(hunters),
                        'UserRank': user_rank,
                        "UserScore" : user_score if not user_score == None else '-',
                        "TopHunter" : top_hunter,
                        "Top_skRatio_hunter": Top_skRatio_hunter,
                        "Top_skRatio_score": Top_skRatio_score,
                        "Top_skRatio_avatar": Top_skRatio_avatar,
                        "BASE_SCORE": __BASE_SCORE
                    }

                    params = {'den': den_details, 'hunters': hunters, 'den_riddles': den_riddle, "alertData": alertData}

                    return render(request, 'riddlechamp/den2.html', params)

                else:
                    # NOT A MEMBER OF DEN OR MEMBERSHIP NOT APPROVED
                    return redirect('/riddlechamp/index/e/49a7')
            except:
                return redirect('/riddlechamp/index/e/8966')
        else:
            # DEN NOT FOUND
            return redirect('/riddlechamp/index/e/8aa6')

    else:
        return redirect('/account/login/e/7955')


# data to be displated in riddle page when called and form is submitted
def denRiddle(request):
    params = None

    if request.user.is_authenticated:

        # when page is called
        if request.method=='GET':

            IS_MOBILE = False

            if request.user_agent.is_mobile:
                IS_MOBILE = True
                # print(IS_MOBILE)

            # print(request.user_agent.is_mobile) # returns True
            # print(request.user_agent.is_tablet) # returns False
            # print(request.user_agent.is_pc) # returns False

            user = request.user
            user_id = user.id
            current_epoch = datetime.now().timestamp()

            url_path = request.META.get('PATH_INFO')

            den_riddle_uin_list = url_path.split('/')[len(url_path.split('/'))-1].split('?')
            den_riddle_uin = den_riddle_uin_list[len(den_riddle_uin_list)-1]

            den_riddle_obj = DenRiddle.objects.filter(uin_code=den_riddle_uin)

            if len(den_riddle_obj) == 1:

                den_riddle = den_riddle_obj[0]

                userPor_obj = UserProfile.objects.get(user=request.user)
                hunter_den_map_obj = Hunter_Den_Mapping.objects.filter(den=den_riddle.den, hunter=userPor_obj, member_status=True)

                if len(hunter_den_map_obj) == 1:
                    # if an active riddle is opened for 1st time and current time has crossed expiry time then mark riddle as expired
                    if den_riddle.is_active and (den_riddle.ending_at.timestamp() < current_epoch):
                        den_riddle.is_pending = False
                        den_riddle.is_active = False
                        den_riddle.has_expired = True
                        den_riddle.save()
                        # print('='*15, 'Active Riddle Marked as Expired Riddle')

                    # if a pending riddle is opened for 1st time and current time fas crossed expiry time then mark riddle as expired 
                    if den_riddle.is_pending and (den_riddle.ending_at.timestamp() < current_epoch):
                        den_riddle.is_pending = False
                        den_riddle.is_active = False
                        den_riddle.has_expired = True
                        den_riddle.save()
                        # print('='*15, 'Pending Riddle Marked as Expired Riddle')

                    # if a pending riddle is opened for 1st time and current time has crossed activation time then mark riddle as active 
                    if den_riddle.is_pending and (den_riddle.started_at.timestamp() < current_epoch):
                        den_riddle.is_pending = False
                        den_riddle.is_active = True
                        den_riddle.has_expired = False
                        den_riddle.save()
                        # print('='*15, 'Pending Riddle Marked as Active Riddle')

                    # Fetching responses for this den-riddle
                    response_obj = Response.objects.filter(den_riddle = den_riddle, hunter=user_id)
                    number_of_attempt = len(response_obj)
                    score = 0
                    response = []
                    is_solved = False
                    solved_ans = None

                    if len(response_obj) > 0:
                        is_solved = False

                        for rsp in response_obj:
                            score += rsp.score
                            r = {
                                'response_at': rsp.response_at.strftime('%d/%m/%y %I:%M%p'),
                                'answer': rsp.answer,
                                'score': rsp.score,
                                'is_correct': rsp.is_correct,
                                'image': rsp.image,
                            }
                            response.append(r)

                            if rsp.is_correct  == True:
                                is_solved = True
                                solved_ans = rsp.answer

                    # score for riddle right answer
                    right_answer_score = den_riddle.riddle.riddle_level.kills*den_riddle.riddle.riddle_level.positive_score_percent

                    # score for riddle right answer
                    wrong_answer_score = (den_riddle.riddle.riddle_level.kills*den_riddle.riddle.riddle_level.negetive_score_percent)/(den_riddle.riddle.max_calls-1)

                    print(wrong_answer_score)

                    ending_epoch = (den_riddle.ending_at).timestamp()
                    starting_epoch = (den_riddle.started_at).timestamp()

                    params = {
                            'denRiddle': den_riddle, 
                            'ending_epoch': ending_epoch, 
                            'starting_epoch': starting_epoch,
                            'number_of_attempt': number_of_attempt,
                            'score': score,
                            'is_solved': is_solved,
                            'solved_ans': solved_ans,
                            'responses': sorted(response, key = lambda i: i['response_at'],reverse=True),
                            'right_ans_score': f"{right_answer_score:.2f}",
                            'wrong_ans_score': f"{wrong_answer_score:.2f}",
                            'IS_MOBILE': IS_MOBILE
                        }

                    return render(request, 'riddlechamp/riddle.html', params)
                else:
                    # USER NOT PART OF DEN
                    return redirect('/riddlechamp/index/e/db23')

            else:
                # DEN RIDDLE DOESNOT EXIST
                return redirect('/riddlechamp/index/e/da63')

        #  when user sumits an answer
        # elif request.method=='POST' and request.FILES['user_pic']:
        elif request.method=='POST':
            user = request.user
            user_id = user.id

            url_path = request.META.get('PATH_INFO')

            den_riddle_uin_list = url_path.split('/')[len(url_path.split('/'))-1].split('?')
            uin_code = den_riddle_uin_list[len(den_riddle_uin_list)-1]

            den_riddle = DenRiddle.objects.filter(uin_code=uin_code)

            if len(den_riddle) == 1:

                den_riddle = den_riddle[0]
                answer = request.POST.get('answer', None).lower().strip().replace(" ", "")

                # answer = 'Pencil lead'.lower()
                if (
                    den_riddle.riddle.answer_1.lower().strip().replace(" ", "") == answer or 
                    den_riddle.riddle.answer_2.lower().strip().replace(" ", "") == answer or 
                    den_riddle.riddle.answer_3.lower().strip().replace(" ", "") == answer or 
                    den_riddle.riddle.answer_4.lower().strip().replace(" ", "") == answer or 
                    den_riddle.riddle.answer_5.lower().strip().replace(" ", "") == answer or 
                    den_riddle.riddle.answer_6.lower().strip().replace(" ", "") == answer or 
                    den_riddle.riddle.answer_7.lower().strip().replace(" ", "") == answer or 
                    den_riddle.riddle.answer_8.lower().strip().replace(" ", "") == answer or 
                    den_riddle.riddle.answer_9.lower().strip().replace(" ", "") == answer
                ):
                    # score for riddle right answer
                    score = round(den_riddle.riddle.riddle_level.kills*den_riddle.riddle.riddle_level.positive_score_percent, 2)

                    is_correct = True
                    result = "?s=301"
                else:
                    # score for riddle right answer
                    score = round((den_riddle.riddle.riddle_level.kills*den_riddle.riddle.riddle_level.negetive_score_percent)/(den_riddle.riddle.max_calls-1), 2)
                    is_correct = False
                    result = "?e=901"

                current_time_epoch = int(datetime.now().strftime('%s'))
                activate_time_epoch = int(den_riddle.started_at.strftime('%s'))

                # # File Handeling
                # extenstion = (request.FILES['user_pic'].name).split('.')[len(request.FILES['user_pic'].name.split('.'))-1]
                # pic_name = str(user_id) + '_' + str(current_time_epoch) + '.' + extenstion
                # # fs = FileSystemStorage(location='media/image/response/')
                # fs = FileSystemStorage(location='home/siddhant/geekysid/media/image/response/')
                # filename = fs.save(pic_name, request.FILES['user_pic'])
                # fs.base_url = 'image/response/'
                # uploaded_file_url = fs.url(filename)

                response = Response.objects.create(
                        den_riddle = den_riddle,
                        hunter = request.user,
                        answer = answer,
                        # image = uploaded_file_url,
                        is_correct = is_correct,
                        score = score,
                        response_at = datetime.now(),
                        response_time = current_time_epoch - activate_time_epoch
                )

                response.save()

                link = '/riddlechamp/den/riddle/'+uin_code+result
                return redirect(link)

            else:
                # INVALID REQUEST
                return redirect('/riddlechamp/index/e/da63')
            # den_riddle_obj = DenRiddle.objects.filter(uin_code=den_riddle_uin)
        else:
            return redirect('/riddlechamp/index/e/8be6')
    else:
        return redirect('/account/login/e/7955')


# Function to create new den
def denCreate(request):
    if request.user.is_authenticated:
        if request.is_ajax():
            try:
                name = request.POST['name']
                desc = request.POST['desc']

                riddle_per_day = int(request.POST['riddle_per_day'])
                riddle_start = int(request.POST['riddle_start'])
                hours_bw_riddle = int(request.POST['hours_bw_riddle'])
                if riddle_start == 1:
                    riddle_start = "08:00 AM"
                elif riddle_start == 2:
                    riddle_start = "10:00 AM"
                elif riddle_start == 3:
                    riddle_start = "12:00 Noon"
                elif riddle_start == 4:
                    riddle_start = "02:00 PM"
                else:
                    riddle_start = "01:00 PM"

                am = riddle_start.split(':')[1].split(" ")[1]
                hr = riddle_start.split(':')[0]
                hr = str(int(hr)+12) if am == "PM" else hr
                activate_time_str = f"{hr}:00:00"
                activate_time = datetime.time(datetime.strptime(activate_time_str, '%H:%M:%S'))

                userProfile_obj = UserProfile.objects.get(user=request.user.id)

                current_time_epoch = int(datetime.now().strftime('%s'))

                # File Handeling
                extenstion = (request.FILES['avatar'].name).split('.')[len(request.FILES['avatar'].name.split('.'))-1]
                pic_name = str(userProfile_obj.user.id) + '_' + str(current_time_epoch) + '.' + extenstion
                # fs = FileSystemStorage(location='media/image/profile_photo/')
                fs = FileSystemStorage(location='home/siddhant/geekysid/media/image/profile_photo/')

                filename = fs.save(pic_name, request.FILES['avatar'])
                fs.base_url = 'image/profile_photo/'
                uploaded_file_url = fs.url(filename)

                invitation_code = str(zlib.crc32(str(hashlib.sha256(str(current_time_epoch).encode())).encode()))
                uin_code = str(zlib.adler32(str(hashlib.sha256(str(current_time_epoch).encode())).encode()))

                den_obj = Den.objects.create(
                    admin = request.user,
                    name = name,
                    desc = desc,
                    avatar = uploaded_file_url,
                    score = 0.0,
                    is_active = True,
                    riddle_start_time = activate_time,
                    riddles_per_day = riddle_per_day,
                    time_bw_riddle = hours_bw_riddle,
                    started_at = datetime.now() + timedelta(days=1),
                    invitation_code = invitation_code,
                    uin_code = uin_code
                )
                den_obj.save()

                # Hunter_Den_Mapping 
                hntr_den_map_obj = Hunter_Den_Mapping.objects.create(den=den_obj, hunter=userProfile_obj, member_status=True)

                hntr_den_map_obj.save()

                add_riddle_to_new_den(den_obj)

                return JsonResponse({"succesFlag": True, "den_uincode": den_obj.uin_code})

            except Exception as e:
                # print(str(e))
                return JsonResponse({"succesFlag": False, "msg": "Exception", "Exception": str(e)})
        else:
            return render(request, 'riddlechamp/newDen.html')
    else:
        return JsonResponse({"succesFlag": False, "msg": "Login Required"})


# JOIN DEN
def joinDen(request):
    if request.user.is_authenticated:

        if request.method == 'GET' :
            if 'cl' in request.GET:
                cl = request.GET.get('cl', '')

                if cl == '':
                    return redirect('/riddlechamp/index/e/8be6')
                else:
                    hunter_den_map_obj = Hunter_Den_Mapping.objects.filter(invitation_code=cl)
                    if len(hunter_den_map_obj) == 1:
                        hunter_den_map = hunter_den_map_obj[0]
                        if hunter_den_map.member_status == True:
                            # Hunter already added to DEN
                            return redirect('/riddlechamp/index/e/1954')
                        else:
                            if hunter_den_map.den.admin == request.user:
                                hunter_den_map.member_status = True
                                hunter_den_map.save()

                                subject = f"Riddle Champ - Approved to join Den {hunter_den_map.den.name} by {hunter_den_map.den.admin}" + emoji.emojize(':sign_of_the_horns:')
                                body = f"Hello, <p>Your request to join the Den ({hunter_den_map.den}) has been approved by the admin ({hunter_den_map.hunter}). You can now go to the den and enjoy hunting.\
                                    <p><br />--<br />{settings.EMAIL_SIGNATURE}"

                                to_ = hunter_den_map.hunter.email

                                mail_sent = cvEmailer.mailer(subject, '', to_, body)

                                return redirect('/riddlechamp/index/s/db15')
                            else:
                                # user is not admin of den
                                return redirect('/riddlechamp/index/e/1bd4')
                    else:
                        # invalid invitation code
                        return redirect('/riddlechamp/index/e/1a94')
            else:
                # simple page request
                return render(request, 'riddlechamp/joinden.html')

        elif request.is_ajax():
            den_code = request.POST.get('denCode', '')

            if den_code == '':
                return JsonResponse({'successFlag': False, 'error': 'Missing Data', 'message': 'Den Code is not provided'})
            else:
                den_obj = Den.objects.filter(uin_code=den_code)
                hunter = UserProfile.objects.filter(user=request.user)[0]

                if len(den_obj) == 1:
                    den = den_obj[0]
                    hunter_den_map_obj = Hunter_Den_Mapping.objects.filter(den=den, member_status=True, hunter=hunter)

                    if len(hunter_den_map_obj) > 0:
                        return JsonResponse({'successFlag': False, 'error': 'Already Den Member','message': 'You are already member of this den.'})
                    else:
                        # generate sha512
                        uniqueString = str(den.den_id) + '-' + str(datetime.timestamp(datetime.now()))
                        invitation_code = str(hashlib.sha256(str(uniqueString).encode()).hexdigest())

                        hunter_den_map_obj = Hunter_Den_Mapping.objects.create(den=den, hunter=hunter, member_status=False, invitation_code=invitation_code)
                        hunter_den_map_obj.save()
                        # print("ADDED TO HUNTER_DEN_MAP")

                        # // Sent approval MAIL to admin
                        admin_email = den.admin.email
                        joinee = hunter
                        joinee_email = hunter.email

                        msg = MIMEMultipart()
                        msg['To'] = admin_email
                        msg['Subject'] = f"Riddle Champ - {hunter} Requests to Join Your Den ({den}) "+emoji.emojize(':sign_of_the_horns:')

                        confirmation_link = f"{Base_url}riddlechamp/den/join/?cl={invitation_code}"
                        subject = f"Riddle Champ - {hunter} Requests to Join Your Den ({den}) "+emoji.emojize(':sign_of_the_horns:')
                        body = f"Hello,<p>\
                                {joinee}({joinee_email}) have requested to join your den ({den}).</p>\
                                <p><a href='{confirmation_link}'>Click here</a> to allow him to be part of your Den</p><p><br />--<br />{settings.EMAIL_SIGNATURE}"

                        msg.attach(MIMEText(body, 'html'))

                        mail_sent = cvEmailer.mailer(subject, joinee_email, admin_email, msg)

                        if mail_sent:
                            # print("MAILE SENT")
                            return JsonResponse({'successFlag': True, 'success': 'Mail Sent to Admin', 'message': 'Mail has been sent to the admin of the den. You can access the den once he confirms your joining.'})
                        else:
                            # print("MAILE Failed")
                            return JsonResponse({'successFlag': False, 'error': 'Mail to Admin Failed', 'message': 'We were not able to sent mail to the admin of the den. please try again after sometime.'})
                else:
                    return JsonResponse({'successFlag': False, 'error': 'Invalid Code', 'message': 'No Den exsit with this code.'})
        else:
            # INVALID REQUEST
            return redirect('/riddlechamp/index/e/8be6')
    else:
        # USER NOT LOGGED IN
        return redirect('/account/login/e/7955')


# function 
def user_response_handler(request):
    try:
        if request.is_ajax() and request.method=="POST":
            # print('True')
            return JsonResponse({'success': True})
        else:
            # print('Flase')
            return JsonResponse({'success': False})
    except Exception as e:
        # print(str(e))
        pass


# function to make an object of Den_Riddle Model as active 
def den_riddle_active_update(dr, den_riddle, den, riddle_added_date):
    if dr.is_active == False and dr.has_expired == False:
        dr.is_pending = False
        dr.has_expired = False
        dr.is_active = True
        dr.save()

        den.riddles_per_day = 4
        den.time_bw_riddle = 3

        # creating new riddle for current den
        new_riddle = create_den_riddle(den_riddle, den, riddle_added_date)
        return new_riddle


# function to make an object of Den_Riddle Model as active
def den_riddle_expiry_update(dr):
    if dr.is_pending == False and dr.has_expired == False:
        dr.is_pending = False
        dr.is_active = False
        dr.has_expired = True
        dr.save()


# creating new riddle for current den
def create_den_riddle(den_riddle, den, riddle_added_date):
    riddle_in_den = []

    for dr in den_riddle:
        riddle_in_den.append(dr.riddle.riddle_id)

    # fetching new randome riddles not in den so far
    new_riddle = choice(list(Riddle.objects.filter(~Q(riddle_id__in=riddle_in_den))))

    riddles_per_day = den.riddles_per_day
    riddle_start_time = den.riddle_start_time
    new_riddle_activate_time = None

    current_time_epoch = int(datetime.now().strftime('%s'))
    uniqueString = f"{den.den_id}-{new_riddle.riddle_id}-{current_time_epoch}"
    uin_code = str(zlib.adler32(str(hashlib.sha256(str(uniqueString).encode())).encode()))

    # datetime of activavtion of 1st riddle - 2020-04-01 00:05:09.714263
    riddle_activate_time = datetime.combine(date.today(), den.riddle_start_time)

    number_riddle_today = riddle_added_date.count(datetime.now().strftime("%Y/%m/%d"))

    # if riddles added today is less then number of riddles allowed per day.
    if number_riddle_today < riddles_per_day:
        # if no rows are added today
        if number_riddle_today == 0:

            # if current time is more then the time of 1st riddle of the day
            if riddle_activate_time < datetime.now():
                new_riddle_activate_time = new_riddle_activation(den)
            else:
                new_riddle_activate_time = datetime.combine(date.today(), riddle_start_time)

            # print(new_riddle_activate_time)
        else:
            last_added_at = datetime.time(datetime.now() - timedelta(days=1))
            for dr in den_riddle:
                if last_added_at < datetime.time(dr.added_at) and datetime.date(dr.added_at) == datetime.date(datetime.now()):
                    last_added_at = datetime.time(dr.added_at)

            new_riddle_activate_time = new_riddle_activation(den)
            # print(new_riddle_activate_time)
            pass
    else:
        new_riddle_activate_time = riddle_for_next_day(riddle_start_time)

    ending_at = new_riddle_activate_time+timedelta(minutes=new_riddle.riddle_level.time)


    den_riddle_obj = DenRiddle.objects.create(
        den = den, riddle = new_riddle, added_at = datetime.now(), started_at = new_riddle_activate_time, ending_at = ending_at, is_pending = True, is_active = False, uin_code = uin_code, has_expired = False
    )

    den_riddle_obj.save()

    return den_riddle_obj


# Function to add riddle to den when den is created
def add_riddle_to_new_den(den): 

    # fetching new randome riddles not in den so far
    new_riddle = Riddle.objects.order_by("?").first()
    riddle_activateTime = riddle_for_next_day(den.riddle_start_time)
    riddle_expiryTime= riddle_for_next_day(den.riddle_start_time) + timedelta(minutes=new_riddle.riddle_level.time)

    uniqueString = str(den.den_id) + '-' + str(datetime.timestamp(datetime.now()))
    uin_code = str(zlib.crc32(str(hashlib.sha256(uniqueString.encode())).encode()))

    den_riddle_obj = DenRiddle.objects.create(den = den, riddle = new_riddle, added_at = datetime.now(), started_at = riddle_activateTime, ending_at = riddle_expiryTime, is_pending = True, is_active = False, uin_code = uin_code, has_expired = False)

    den_riddle_obj.save()


# function to return time of activation of riddle for next day
def riddle_for_next_day(riddle_start_time):
    return datetime.combine(date.today(), riddle_start_time) + timedelta(days=1)


# function to activate riddle
def new_riddle_activation(den):
    riddles_per_day = den.riddles_per_day
    # print('den: ', den)
    # print('riddles_per_day: ', riddles_per_day)
    # print('time_bw_riddle: ', den.time_bw_riddle)
    # print('riddle_start_time: ',  den.riddle_start_time)
    riddle_start_time = den.riddle_start_time
    riddle_activate_time = datetime.combine(date.today(), den.riddle_start_time)
    # print(timedelta(hours=riddles_per_day))
    max_activation_time = riddle_activate_time + timedelta(hours=riddles_per_day*den.time_bw_riddle)
    # print(max_activation_time)

    counter = 1

    while True:
        # datetime of activation of (counter+1)th riddle - 2020-04-01 06:05:09.714263 when counter is 1
        new_riddle_activate_time = riddle_activate_time + timedelta(hours=counter*den.time_bw_riddle)

        # checking if activation time for nex riddle is at date greatyer then today
        is_next_day = (new_riddle_activate_time - riddle_activate_time).days

        if is_next_day > 0:
            # if yes the we assume the next riddle as 1st riddle of next day and sets its activation time accordingly.
            new_riddle_activate_time = riddle_for_next_day(riddle_start_time)
            break

        else:
            # if our counter of while loop is same as number of riddles allowed per day the we assume the next riddle as 
            # 1st riddle of next day and sets its activation time accordingly. This is because we will end up have 
            # activation time which is not in schedule.
            if counter == riddles_per_day:

                new_riddle_activate_time = riddle_for_next_day(riddle_start_time)
                break

            # if current time is greater then riddle activation time
            if datetime.now() > new_riddle_activate_time:
                # print('True')
                counter += 1
            else:
                break

    return new_riddle_activate_time


# handelling request to sent invites to den
def sent_den_invites(request):

    global Base_url

    if request.user.is_authenticated:
        if request.is_ajax():
            if request.method == 'POST':
                email_list = request.POST.getlist('email_list[]', '')
                den_id = request.POST.get('den_id', '')

                new_user = []
                sender_obj = UserProfile.objects.get(user=request.user.id)

                den_obj = Den.objects.get(den_id=den_id)

                # message setting for self mail
                from_ = sender_obj.email
                subject = f"Riddle Champ - Invitation to join DEN by {sender_obj.name}" + emoji.emojize(":sign_of_the_horns:")

                for email in email_list:

                    guest_obj = UserProfile.objects.filter(email=email)

                    if len(guest_obj) == 0:
                        # NEED TO SENT NEW USER LINK TO GENERATE NEW ACCOUNT AND ALSO ACCEPT INVITATION 
                        new_user.append(email)

                        return JsonResponse({'successFlag': False, 'error': 'NEW USER', 'message': 'The email address is not a Hunter yet. Email not registered with us. Please ask user to register with us 1st and then sent hin an invite to den.'})
                    else:
                        # checking if guest is already part of den
                        hunter_den_map_obj = Hunter_Den_Mapping.objects.filter(den=den_obj, hunter=guest_obj[0], member_status=True)

                        if len(hunter_den_map_obj) == 0:
                            msg = MIMEMultipart()
                            msg['To'] = email
                            msg['Subject'] = f"Riddle Champ - Invitation to join DEN by {sender_obj.name}" + emoji.emojize(":sign_of_the_horns:")

                            unique_string = "den"+ sender_obj.email +str(den_obj.den_id) + '' + str(datetime.now().timestamp())
                            invite_code = str(zlib.crc32(str(hashlib.sha256(unique_string.encode())).encode()))

                            invitation_link = f"{Base_url}riddlechamp/den/invite/guest?email={email}&invite_code={invite_code}&from={sender_obj.email}"

                            body = f"Hello,<br/>\
                                    You have been invited to join {den_obj.name} by {sender_obj.name}\
                                    <p>Please <a href='{invitation_link}'>click here</a> to Be part of his den.</p><p><br />--<br />"+settings.EMAIL_SIGNATURE

                            msg.attach(MIMEText(body, 'html'))

                            den_invite_obj = DenInvitee.objects.create(
                                                invitee = sender_obj,
                                                den = den_obj,
                                                email_to = email,
                                                invite_code = invite_code,
                                                sent_on = datetime.now(),
                                                status = False
                                            )
                            den_invite_obj.save()

                            mail_sent = cvEmailer.mailer(subject, from_, email, msg)

                            if mail_sent:
                                return JsonResponse({'successFlag': True, 'message': 'Invitation Mail sent successfully to '+email})
                            else:
                                return JsonResponse({'successFlag': "Exception", 'error': 'UNABLE TO SENT MAIL', 'message': "An exception occurred while sending mail. Please contact system admin."})

            else:
                return JsonResponse({'successFlag': False, 'error': 'Invalid Request',  'message': 'There was some error in sending email. Please try again.'})
        else:
            return JsonResponse({'successFlag': False, 'error': 'Invalid Request', 'message': 'User not Logged in'})
    else:
        return JsonResponse({'successFlag': False, 'error': 'Login Required', 'message': 'User not Logged in'})


# activating invites to den
def accept_den_invite(request):
    if request.user.is_authenticated:
        if request.method == 'GET' and 'email' in request.GET and 'invite_code' in request.GET and 'from' in request.GET:
            guest_email = request.GET.get('email', None)
            invite_code = request.GET.get('invite_code', None)
            invitee_email = request.GET.get('from', None)

            if guest_email is None or invite_code == None or invitee_email == None:
                # NOT A VALID REQUEST
                return redirect("/riddlechamp/index/e/8be6")
            else:
                # checking if invited user is registered user or not.
                try:
                    if guest_email == request.user.email:
                        guest_obj = UserProfile.objects.filter(email=guest_email)
                        if guest_obj == 0:
                            # RETURN TO REGISTER PAGE AS USER IS NOT REGISTERED
                            return redirect("/riddlechamp/index/e/8a56")
                        else:
                            hunter_obj = guest_obj[0]
                            try:
                                invite_obj = DenInvitee.objects.get(invite_code=invite_code, email_to=guest_email)
                            except:
                                # RETURN TO ERROR PAGE AS EXCEPTION HAS OCCURRED
                                # print("HELLO")
                                return redirect("/riddlechamp/index/e/8826")
                            try:
                                if invite_obj:
                                    hntr_den_map_obj = Hunter_Den_Mapping.objects.filter(den=invite_obj.den, hunter=hunter_obj, member_status=True)
                                    if len(hntr_den_map_obj) == 0:
                                        invitee = invite_obj.invitee
                                        if invitee_email == invitee.email:
                                            # all is well and register user:
                                            invite_obj.accepted_on = datetime.now()
                                            invite_obj.status = True
                                            invite_obj.save()

                                            Hunter_Den_Mapping.objects.filter(den=invite_obj.den, hunter=hunter_obj).delete()
                                            hntr_den_map_obj = Hunter_Den_Mapping.objects.create(den=invite_obj.den, hunter=hunter_obj, member_status=True)
                                            hntr_den_map_obj.save()

                                            return redirect("/riddlechamp/den/"+invite_obj.den.uin_code+'/s/4f97')
                                        else:
                                            # invalid request - sender not matching
                                            return redirect("/riddlechamp/index/e/4957")
                                    else:
                                        # RETURN TO ERROR PAGE AS USER IS ALREADY PART OF DEN
                                        return redirect("/riddlechamp/den/"+invite_obj.den.uin_code+'/e/4817')
                                else:
                                    # RETURN TO ERROR PAGE AS USER IS NOT BEEN INVITED
                                    return redirect("/riddlechamp/index/e/4bd7")

                            except Exception as e:
                                # print(str(e))
                                # RETURN TO ERROR PAGE AS EXCEPTION HAS OCCURRED
                                return redirect("/riddlechamp/index/e/8b16")
                    else:
                        # invited user and loggedin user not same.
                        return redirect("/riddlechamp/index/e/4957")
                except Exception as e:
                    # print(str(e))
                    # Exception Occurred
                    return redirect("/riddlechamp/index/e/4a97")
        else:
            # invalid request
            return redirect("/riddlechamp/index/e/8be6")
    else:
            return redirect("/account/login/e/7955")

