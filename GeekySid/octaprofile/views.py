from django.shortcuts import render
from django.http import HttpResponse
import requests, json
import pandas as pd
from datetime import datetime

# Create your views here.
def index(request):
    if request.method == 'GET' and 'gh_username' in request.GET:
        # try:
        username = request.GET.get('gh_username', '')

        if not username == '':
            
            github_url = 'https://api.github.com/users/'+username   # creating a api url
            resp = requests.get(github_url)    # making api requests to githb to collect data for the user's username
            
            # if the api request returns validity of the account
            if resp.status_code == 200:

                # fetching basic data from the api
                json_user = json.loads(resp.text)
                name = json_user['name']
                company = json_user['company']
                website = json_user['blog']
                Username = json_user['login']
                avatar = json_user['avatar_url']
                location = json_user['location']
                github_url = json_user['html_url']
                try:
                    bio = json_user['bio']
                    if '\n' in bio:
                        bio.replace('\n', '.')
                except:
                    bio = ''
                email = json_user['email']
                created_at = json_user['created_at']
                updated_at = json_user['updated_at']
                followers = json_user['followers']
                followings = json_user['following']
                events_url = json_user['events_url']
                repos_count = json_user['public_repos']
                
                date = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ")
                joined_on = date.strftime('%B %d, %Y')

                personal_detail = [avatar, name, bio, company, location, website, github_url, joined_on, repos_count, followers, followers]

                # FETCHING REPOSITORIES DETAILS
                language_chart_data = {}
                starsPerRepo_chart_data = []
                starsPerLanguage_chart_data = {}
                sizePerLanguage_chart_data = {}

                # using repos api link to fetch data about user's repositary
                repos_url = json_user['repos_url']+'?per_page=100'
                resp_repos = requests.get(repos_url)
                if resp_repos.status_code == 200:   # executing if user have atleast one repository
                    json_repos = json.loads(resp_repos.text)    # converting the received reponse object into json
                    
                    if len(json_repos) > 0:
                        
                        repository_details = []

                        # looping through all of repos
                        for repo in json_repos:
                            repo_name = repo['name']
                            repo_desc = repo['description']
                            repo_starCount = int(repo['stargazers_count'])
                            repo_url = repo['html_url']
                            repo_forksCount = int(repo['forks_count'])
                            repo_created_at = repo['created_at']
                            repo_updated_at = repo['updated_at']
                            repo_language = repo['language']
                            repo_size = repo['size']
                            repo_size_int = int(repo['size'])
                            
                            date = datetime.strptime(repo_updated_at, "%Y-%m-%dT%H:%M:%SZ")
                            update_date = date.strftime('%d/%m/%Y')

                            # dict of all repos with required details to be displayed
                            repository_details.append({
                                'repo': repo_name,
                                'detail': repo_desc,
                                'language': repo_language,
                                'fork_count': int(repo_forksCount),
                                'star_count': int(repo_starCount),
                                'last_updated': update_date,
                                'size': int(repo_size),
                                'size_KB': '{:,} KB'.format(int(repo_size))
                            })
                    
                            # creating list of dictonary that has language and its counts to get languages used in repos
                            if repo_language in [x for x in language_chart_data.keys()]:
                                language_chart_data[repo_language] += 1
                            else:
                                language_chart_data[repo_language] = 1
                            
                            # creating list of dictonary that has repos and its starcounts to get star count per repos
                            if repo_name in [x['repo'] for x in starsPerRepo_chart_data]:
                                for item in starsPerRepo_chart_data:
                                    if repo_name == item['repo']:
                                        item['starCount'] = int(item['starCount']) + int(repo_starCount)
                            else:
                                # starsPerRepo_chart_data[repo_name] = 'starCount': int(repo_starCount)
                                starsPerRepo_chart_data.append({'repo': repo_name, 'starCount': int(repo_starCount)})

                            # creating list of dictonary that has language and its starcounts to get star count per languages
                            if repo_language in [x for x in starsPerLanguage_chart_data.keys()]:
                                starsPerLanguage_chart_data[repo_language] += repo_starCount
                            else:
                                starsPerLanguage_chart_data[repo_language] = repo_starCount

                            # creating list of dictonary that has language and its sizes to get star count per languages
                            if repo_language in [x for x in sizePerLanguage_chart_data.keys()]:
                                sizePerLanguage_chart_data[repo_language] += repo_size_int
                            else:
                                sizePerLanguage_chart_data[repo_language] = repo_size_int

                        df = pd.DataFrame(repository_details)

                        # Dataframe that hold repository details sorted for FORK_COUNT values
                        fork_df = df.sort_values(by='fork_count', ascending=False)
                        fork_list = fork_df.head(9).values.tolist()

                        # Dataframe that hold repository details sorted for SIZE values
                        size_df = df.sort_values(by='size', ascending=False)
                        size_list = size_df.head(9).values.tolist()

                        # Dataframe that hold repository details sorted for STAR_COUNT values
                        star_df = df.sort_values(by='star_count', ascending=False)
                        star_list = star_df.head(9).values.tolist()

                        # Dataframe that hold StarPerRepo data sorted by STAR COUNT values
                        df2 = pd.DataFrame(starsPerRepo_chart_data)
                        starsPerRepo_df = df2.sort_values(by='starCount', ascending=False)
                        starsPerRepo_list = starsPerRepo_df.head(6).values.tolist()
                        starsPerRepo_dict = {}

                        for item in starsPerRepo_list:
                            starsPerRepo_dict[item[0]] = item[1]
                        
                        params = {
                            'username': username,
                            'success': 'true',
                            'personal_detail': personal_detail,
                            'fork_list': fork_list,
                            'size_list': size_list,
                            'star_list': star_list,
                            'starsPerLanguage_data': json.dumps(starsPerLanguage_chart_data),
                            'starsPerRepo_data': json.dumps(starsPerRepo_dict),
                            'languageCount_data': json.dumps(language_chart_data)
                        }
                    else:
                        params = {
                            'username': username,
                            'success': 'true',
                            'personal_detail': personal_detail,
                            'fork_list': [],
                            'size_list': [],
                            'star_list': [],
                            'starsPerLanguage_data': '',
                            'starsPerRepo_data': '',
                            'languageCount_data': ''
                            }

                else:
                    params = {
                        'username': username,
                        'success': 'true',
                        'personal_detail': personal_detail,
                        'fork_list': [],
                        'size_list': [],
                        'star_list': [],
                        'starsPerLanguage_data': '',
                        'starsPerRepo_data': '',
                        'languageCount_data': ''
                    }
                    
                return render(request, 'octaprofile/index.html', params)

            # if the api request page is not found
            elif resp.status_code == 400 or resp.status_code == 404:
                params = {'error': f'Damnnnn!!!! No account found with "{username}" username'}
                return render(request, 'octaprofile/index.html', params)

            # if the api requested shares not-authorized status code
            elif resp.status_code == 401 or resp.status_code == 403:
                params = {'error': f'Oppsss!!!! You might have exhausted your search limit (30 queries in 60 mins). Please try after 1 hour'}
                return render(request, 'octaprofile/index.html', params)

            # for anyother status code
            else:
                params = {'error': f'Oppsss!!!! There seems to be an issue with Github API at this moment. Please try after some time.'}
                return render(request, 'octaprofile/index.html', params)

        else:
            params = {'error': 'Not a valid Username'}
            return render(request, 'octaprofile/index.html', params)
        # except Exception as e:
        #     params = {'error': f'Oh no!!!! Something went wrong. Try again later!\n {str(e)}'}
        #     return render(request, 'octaprofile/index.html', params)    
    else:    
        params = {'hello': ''}
        return render(request, 'octaprofile/index.html', params)