from django.shortcuts import render
from django.http import HttpResponse
import requests, json
import pandas as pd
from datetime import datetime

# Create your views here.
def index(request):
    if request.method == 'GET' and 'gh_username' in request.GET:
        
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
                bio = json_user['bio'].replace('\n', '. ')
                email = json_user['email']
                created_at = json_user['created_at']
                updated_at = json_user['updated_at']
                followers = json_user['followers']
                followings = json_user['following']
                events_url = json_user['events_url']
                
                personal_detail = [avatar, name, bio, company, location, website, github_url]

                # FETCHING REPOSITORIES DETAILS
                language_chart_data = []
                starsPerRepo_chart_data = []
                starsPerLanguage_chart_data = []

                # using repos api link to fetch data about user's repositary
                repos_url = json_user['repos_url']+'?per_page=100'
                resp_repos = requests.get(repos_url)

                if resp_repos.status_code == 200:   # executing if user have atleast one repository
                    json_repos = json.loads(resp_repos.text)    # converting the received reponse object into json

                    repository_details = []

                    # looping through all of repos
                    for repo in json_repos:
                        repo_name = repo['name']
                        repo_desc = repo['description']
                        repo_privary = repo['private']
                        repo_starCount = repo['stargazers_count']
                        repo_viewCount = repo['watchers_count']
                        repo_url = repo['html_url']
                        repo_issuesCount = repo['open_issues']
                        repo_forksCount = repo['forks_count']
                        repo_created_at = repo['created_at']
                        repo_updated_at = repo['updated_at']
                        repo_language = repo['language']
                        repo_size = repo['size']
                        

                        date = datetime.strptime(repo_updated_at, "%Y-%m-%dT%H:%M:%SZ")
                        update_date = date.strftime('%d/%m/%Y')
                        # print(update_date)

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
               
               
                # dataframe that hold all repository details
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

                # Dataframe that hold repository details sorted for UPDATED_DATE values
                update_df = df.sort_values(by='last_updated', ascending=False)
                update_list = update_df.head(9).values.tolist()

                params = {
                    'success': 'true',
                    'personal_detail': personal_detail,
                    'fork_list': fork_list,
                    'size_list': size_list,
                    'star_list': star_list,
                    'update_list': update_list
                }

                return render(request, 'Octaprofile/index.html', params)

            # if the api request page is not found
            elif resp.status_code == 400 or resp.status_code == 404:
                params = {'error': f'Damnnnn!!!! No account found with "{username}" username'}
                return render(request, 'Octaprofile/index.html', params)

            # if the api requested shares not-authorized status code
            elif resp.status_code == 401 or resp.status_code == 403:
                params = {'error': f'Oppsss!!!! You might have exhausted your search limit (30 queries in 60 mins). Please try after 1 hour'}
                return render(request, 'Octaprofile/index.html', params)

            # for anyother status code
            else:
                params = {'error': f'Oppsss!!!! There seems to be an issue with Github API at this moment. Please try after some time.'}
                return render(request, 'Octaprofile/index.html', params)

        else:
            params = {'error': 'Not a valid Username'}
            return render(request, 'Octaprofile/index.html', params)
            
    else:    
        params = {'hello': ''}
        return render(request, 'Octaprofile/index.html', params)