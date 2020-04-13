from django.shortcuts import render, redirect
from django.http import JsonResponse
from Account.models import UserProfile
from django.db.models import Q
from HuntersDen.models import RiddleCategory, RiddleType, Riddle, Den, DenRiddle, Response, Hunter_Den_Mapping
import pandas as pd
import zlib, hashlib, time, os
from datetime import datetime, timedelta, date
from random import choice
import numpy as np

# Create your views here.
def index(request):
    if request.user.is_authenticated:

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
        user_den_map_obj = Hunter_Den_Mapping.objects.filter(participant=user)
        num_of_user_den = user_den_map_obj.count()
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




        # fetching USER RESPONSE ---> Den-den_id, Den-name, Den-desc, Den-admin, Den-active, den-started_at, 
                                    # Number of solved puzzel, Number of Unsolved Puzzle, Total Score, Total Minutes
        userResponse_obj = Response.objects.filter(hunter=user).values()

        df_userResponse = pd.DataFrame(list(userResponse_obj))
        totalScore = df_userResponse['score'].sum()
        
        puzzlesSovled = df_userResponse[(df_userResponse['is_correct'] == True)]['is_correct'].count()
        
        userResponse = {
            "totalScore" : totalScore,
            "puzzlesSovled" : puzzlesSovled
        }
        
        # fetching USER's DEN
        userDenDetails = []
        denDetails_obj = Den.objects.filter(den_id__in=userDen_list)
        
        for den in denDetails_obj:
            admin = den.admin
            if user == den.admin:
                role = "Admin"
            else:
                role = "Participant"

            # Fething all Riddles associated with this den
            riddle_list = df_den_riddle[(df_den_riddle['den_id'] == den.den_id)]['den_riddle_id']
            
            if not riddle_list.empty:
                df_riddle_den = df_userResponse[df_userResponse['den_riddle_id'].isin(riddle_list.tolist())]
                
                # number of solved puzzle
                solved_puzzle_count = df_riddle_den[df_riddle_den['is_correct'] == True].is_correct.count()
                
                # number of wrong answer
                wrong_answer_count = df_riddle_den[df_riddle_den['is_correct'] == False].is_correct.count()

                # total engagement
                response_time = df_riddle_den['response_time'].sum()
                hrs = int(response_time//3600)
                mins = int((response_time%3600)//60)
                sec = int(((response_time%3600)%60))
                engagement_time = f"{hrs:02}:{mins:02}:{sec:02}"
                
                # Total Score
                total_score = df_riddle_den['score'].sum()
            else:
                solved_puzzle_count = 0
                wrong_answer_count = 0
                total_score = 0

            denDict = {
                "name": den.name,
                "desc": den.desc,
                "role": role,
                "active": den.is_active,
                "started_at": den.started_at.strftime("%d/%m/%Y"),
                "solved_puzzle_count": solved_puzzle_count,
                "wrong_answer_count": wrong_answer_count,
                "total_score": total_score,
                "engagement_time": engagement_time

            }

            userDenDetails.append(denDict)
            

        params = {
            'userProfile': userProfile,
            'userDen': userDen,
            'userResponse' : userResponse,
            'userDenDetails': userDenDetails
        }


        return render(request, 'index.html', params)
    else:
        return redirect('/account/login')


def den(request):

    if request.user.is_authenticated:
        user = request.user
        user_id = user.id

    url_path = request.META.get('PATH_INFO')
    den_uin = url_path.split('/')[len(url_path.split('/'))-1]

    den = Den.objects.get(uin_code=den_uin)
    if den:

        den_id = den.den_id
        admin = True if (den.admin == request.user) else False


        # RIDDLES in this den
        riddle_den_s = DenRiddle.objects.filter(den=den_id)
        den_riddle = []



        # RESPONSE
        response_obj = Response.objects.filter(den_riddle_id__in=riddle_den_s).values()
        df_response = pd.DataFrame(list(response_obj))


        
        
        number_riddle_today = 0
        riddle_added_date =[]
        riddle_activated = False
        riddle_expired = False


        for riddle_den in riddle_den_s:
            if datetime.date(riddle_den.added_at) == datetime.date(datetime.now()):
                riddle_added_date.append(riddle_den.added_at.strftime("%Y/%m/%d"))


        for riddle_den in riddle_den_s:
            riddle_den_id = riddle_den.den_riddle_id

            # calculating current user score for this riddle
            condition_den_riddle_user = (df_response['den_riddle_id'] == riddle_den_id) & (df_response['hunter_id'] == user_id)
            user_score_riddle = df_response[condition_den_riddle_user]['score'].sum()

            # calculating if riddle is solved by user or not
            condition_riddle_solved = (df_response['is_correct'] == True)
            check_solved = df_response.loc[(condition_den_riddle_user & condition_riddle_solved), 'is_correct'].count()
            riddle_solved = True if check_solved > 0 else False
            riddle_solved_dict = {'riddle_den_id': riddle_solved}

            # calculating if riddle is attempted by user or not
            check_attempt = df_response.loc[(condition_den_riddle_user),'is_correct'].count()
            riddle_attempt = True if check_attempt > 0 else False

            # making riddle active from pending
            if riddle_den.is_pending:
                is_pending = True if (riddle_den.started_at).timestamp() > time.time() else False
                if not is_pending:
                    den_riddle_active_update(riddle_den, riddle_den_s, den, riddle_added_date)

            # making riddle expire from pending
            if riddle_den.is_active:
                is_active = True if (riddle_den.ending_at).timestamp() > time.time() else False
                if not is_active:

                    den_riddle_expiry_update(riddle_den)

            # adding dfeault image if not available
            if riddle_den.riddle.media == None or riddle_den.riddle.media == '':
                riddle_den.riddle.media = 'image/riddle/text-icon.jpg'

            # checking if riddle is expired
            if (riddle_den.ending_at).timestamp() < time.time():
                has_expired = True
                is_active = False 
            else:
                has_expired = False

            riddle_den_dict = {
                'den_riddle': riddle_den,           # object of den_riddle
                'starting_epoch': (riddle_den.started_at).timestamp(),  # riddle added to den - this wil be used to sort dict
                'riddle_attempt': riddle_attempt,   # true if user have attempted this riddle
                'riddle_solved': riddle_solved,     # true if user have solved this riddle
                'user_score_riddle': user_score_riddle,        # score of the score for this riddle
                'has_expired': has_expired,
                'is_pending': riddle_den.is_pending,
                'expiry': riddle_den.ending_at
            }

            den_riddle.append(riddle_den_dict)

        den_riddle = sorted(den_riddle, key = lambda i: i['starting_epoch'],reverse=True) 



        # PARTICIPANTS in this den
        hunters_den_obj  = Hunter_Den_Mapping.objects.filter(den = den_id)
        hunters = []
        top_hunter = None

        # top hunter id
        df_hunters_score = df_response.groupby('hunter_id').score.sum()
        top_hunter_id = df_hunters_score.idxmax()
        print(df_response['hunter_id'].values)

        # rank of all hunters
        df_hunters_rank = df_response.groupby('hunter_id').sum()
        df_hunters_rank['Rank'] = df_hunters_rank['score'].rank(ascending=False)
        user_rank = None
        
        # creating hunters list
        for hunter_den in hunters_den_obj:

            # rank of hunter 
            rank = (df_hunters_rank.loc[hunter_den.hunter.user.id, 'Rank']).astype(np.int)
            print(rank, type(rank))

            # score of hunter
            if hunter_den.hunter.user.id not in df_response['hunter_id'].values:
                score = 0
            else:
                score = df_hunters_score.loc[hunter_den.hunter.user.id]

            # top hunter
            if hunter_den.hunter.user.id == top_hunter_id and hunter_den is not None:
                top_hunter = hunter_den.hunter

            # user_rank
            if hunter_den.hunter.user.id == user.id:
                user_rank = rank
                user_score = score

            h = {
                'avatar' : hunter_den.hunter.avatar,
                'uin_code' : hunter_den.hunter.uin_code,
                'name' : hunter_den.hunter.name,
                'den_score' : score,
                'correct_answers' : None,
                'admin': admin,
                'rank' : rank,
                'wrong_answers' : None
            }
            hunters.append(h)

        # sorting hunters list on rank
        hunters = sorted(hunters, key = lambda i: i['den_score'],reverse=True)
        print(hunters)


        # PARAMS - DEN
        den_details = { 
            "name" : den.name,                      # DEN
            "avatar" : den.avatar,                  # DEN
            "started_at" : den.started_at,          # DEN
            "ended_at" : den.ended_at,              # DEN
            "is_active" : den.is_active,            # DEN
            "next_riddle_on" : den.next_riddle_on,  # DEN
            "TotalPuzzels" : None,                  # need to calculate - len(riddle)
            "TotalHunters" : len(hunters),          # need to calculate - len(hunter)
            'UserRank': user_rank,
            "UserScore" : user_score if not user_score == None else '-',               # calculated
            "TopHunter" : top_hunter,               # need to calculate - len(hunter)
        }


        params = {'den': den_details, 'hunters': hunters, 'den_riddles': den_riddle}

        return render(request, 'den2.html', params)

    else:
        print("Invalid Den")

    print()
    
    return render(request, 'den2.html')


# function to make an object of Den_Riddle Model as active 
def den_riddle_active_update(dr, den_riddle, den, riddle_added_date):
    if dr.is_active == False and dr.has_expired == False:
        dr.is_pending = False
        dr.is_active = False
        # dr.save()

        den.riddles_per_day = 4
        den.time_bw_riddle = 3
        

        # creating new riddle for current den
        create_den_riddle(den_riddle, den, riddle_added_date)

# function to make an object of Den_Riddle Model as active 
def den_riddle_expiry_update(dr):
    if dr.is_pending == False and dr.has_expired == False:
        dr.is_active = False
        dr.has_expired = True
        dr.save()


# creating new riddle for current den
def create_den_riddle(den_riddle, den, riddle_added_date):
    riddle_in_den = []

    print(datetime.now())

    for dr in den_riddle:
        riddle_in_den.append(dr.riddle.riddle_id)

    # fetching new randome riddles not in den so far
    new_riddle = choice(list(Riddle.objects.filter(~Q(riddle_id__in=riddle_in_den))))

    riddles_per_day = den.riddles_per_day
    riddle_start_time = den.riddle_start_time
    time_bw_riddle = den.time_bw_riddle
    new_riddle_activate_time = None

    # datetime of activavtion of 1st riddle - 2020-04-01 00:05:09.714263
    riddle_activate_time = datetime.combine(date.today(), den.riddle_start_time)

    number_riddle_today = riddle_added_date.count(datetime.now().strftime("%Y/%m/%d"))
    
    # if riddles added today is less then number of riddles allowed per day.
    if number_riddle_today < riddles_per_day:
        # if no rows are added today
        if number_riddle_today == 0:
            
            # if current time is more then the time of 1st riddle of the day
            if riddle_activate_time < datetime.now():
                new_riddle_activate_time = new_riddle_activation_tion(den)
            else:
                new_riddle_activate_time = datetime.combine(date.today(), riddle_start_time)

            print(new_riddle_activate_time)
        else:
            last_added_at = datetime.time(datetime.now() - timedelta(days=1))
            for dr in den_riddle:
                if last_added_at < datetime.time(dr.added_at) and datetime.date(dr.added_at) == datetime.date(datetime.now()):
                    last_added_at = datetime.time(dr.added_at)
            
            new_riddle_activate_time = new_riddle_activation_tion(den)
            print(new_riddle_activate_time)
            pass
    else:
        new_riddle_activate_time = riddle_for_next_day(riddle_start_time)


def riddle_for_next_day(riddle_start_time):
    return datetime.combine(date.today(), riddle_start_time) + timedelta(days=1)


def new_riddle_activation_tion(den):


    riddles_per_day = den.riddles_per_day
    print('den: ', den)
    print('riddles_per_day: ', riddles_per_day)
    print('time_bw_riddle: ', den.time_bw_riddle)
    print('riddle_start_time: ',  den.riddle_start_time)
    riddle_activate_time = datetime.combine(date.today(), den.riddle_start_time)
    print(timedelta(hours=riddles_per_day))
    max_activation_time = riddle_activate_time + timedelta(hours=riddles_per_day*den.time_bw_riddle)
    print(max_activation_time)

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
                print('True')
                counter += 1
            else:
                break

    return new_riddle_activate_time