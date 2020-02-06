from django.shortcuts import render
from django.http import HttpResponse
import requests, time, json
from bs4 import BeautifulSoup



def live_match_summary(soup, match_detail):
    """
        Method to display summary of match which is going on or just concluded couple of hours back
    """
    scoreboard_summary_block = soup.find('table')   # fetching html 'table' which holds scoreboard summary
    batsman_header_row = scoreboard_summary_block.find('thead')     # fetching 1st 'thead' element which holds header row for batsman
    batsman_header = batsman_header_row.find_all('th')   # fetching all 'th' element inside 1st 'thead' element

    batsman_header_list = []

    # looping through and fetching all fetched 'th' elements
    for match_divs in batsman_header:
        if match_divs.get_text() == 'mat':     # breaking current loop after we have read all required
            break
        else:
            batsman_header_list.append(match_divs.get_text())
    
    # fetching all details of current 2 batsmen
    batsman = batsman_header_row.next_sibling.find_all('tr')
    batsman_summary_list = []

    # looping through the 2 'tr' element which holes batsmen's innings detail
    for batsman_row in batsman:
        td_counter = 1     # holds number of 'td' element
        batsman_list = []

        # looping through and fetching all the batsman details for current innings
        for batsman_detail in batsman_row.find_all('td'):
            if td_counter == 1:    # fteching batsman's name for the 1st 'td' element
                batsman_list.append(batsman_detail.find('a', class_='short-name').get_text())
            elif td_counter == 9:  # breaking out of current loop when we have fetched all required data
                break
            else:
                batsman_list.append(batsman_detail.get_text())

            td_counter = td_counter + 1

        batsman_summary_list.append(batsman_list)
    
    # fetching bowler header details
    bowler_header_row = batsman_header_row.next_sibling.next_sibling # fetching 2nd 'thead' element which holds header row for bowler
    bowler_header = bowler_header_row.find_all('th')    # fetching all 'th' element inside 2nd 'thead' element
    bowler_header_list = []

    # looping through and fetching all fetched 'th' elements
    for match_divs in bowler_header:
        if match_divs.get_text() == 'mat':     # breaking current loop after we have read all required
            break
        else:
            bowler_header_list.append(match_divs.get_text())

    bowler_counter = 1    # holds bowler row count
    partnership_match_divs = ''    # holds element for partnership detail
    recent_ball_match_divs = ''    # holds element for last 18 balls update

    # fetching all details of current 2 bowlers
    bowler = bowler_header_row.next_sibling.find_all('tr')
    bowler_summary_list = []

    # looping through the 'tr' element which holes bowler's innings detail
    for bowler_row in bowler:
        td_counter = 1      # holds number of 'td' element
        bowler_list = []

        # looping through and fetching all the bowler details for current innings
        for bowler_detail in bowler_row.find_all('td'):
            if td_counter == 1:     # fteching bowler's name for the 1st 'td' element
                bowler_list.append(bowler_detail.find('a', class_='short-name').get_text())
            elif td_counter == 11:  # breaking out of current loop when we have fetched all required data
                break
            else:
                bowler_list.append(bowler_detail.get_text())

            td_counter = td_counter + 1     # increasing 'td' element count by 1

        bowler_summary_list.append(bowler_list)

        bowler_counter = bowler_counter + 1     # increasing 'tr' element count by 1
        
        # if 'tr' element count is 3 the we fetch partnership_match_divs and recent_ball_match_divs and break out of loop
        if bowler_counter > 2:
            partnership_match_divs = bowler_row.next_sibling
            if match_detail[4:8] == 'Test':
                recent_ball_match_divs = partnership_match_divs.next_sibling.next_sibling
            else:
                recent_ball_match_divs = partnership_match_divs.next_sibling
            break

    # fetching partnership detail
    current_partnership = partnership_match_divs.find('div', class_=['label', 'full']).get_text() + ' ' + partnership_match_divs.find('span').get_text()

    match_score_summary = {
        'batsman_header_list': batsman_header_list,
        'batsman_summary_list': batsman_summary_list,
        'bowler_header_list': bowler_header_list,
        'bowler_summary_list': bowler_summary_list,
        'current_partnership': current_partnership
    }

    return match_score_summary


def past_match_summary(soup):
    """
        Method to display summary of match which is got conculded 
    """
    match_heading_block = soup.find('article', class_=['top-stories'])
    try:
        print(match_heading_block.h1.get_text())
        print(match_heading_block.p.get_text().replace('"', ''))
    except Exception as e:
        pass
    
    print()
    
    scoreboard_summary_block = soup.find('article', class_=['scorecard-summary'])
    scoreboard_summary_heading = scoreboard_summary_block.find('header', class_='bordered')
    print(scoreboard_summary_heading.get_text())

    # Team's Score Summary:
    for team in scoreboard_summary_heading.next_sibling.children:
        scoreboard_summary_Team = team.h4.get_text()
        print(f'{scoreboard_summary_Team}')
        for batsmen_summary in team.find_all('ul'):
            for batsmen in batsmen_summary.find_all('li'):
                batsmen_name = batsmen.a.get_text()
                batsmen_score = batsmen.span.get_text()
                print(f'\t{batsmen_name}\t{batsmen_score}')
            print()


def index(request):
    
    # url to fetch all matches
    live_match_details = []
    base_url = 'https://www.espncricinfo.com/scores'
    resp_base = requests.get(base_url)

    if resp_base.status_code == 200:
        
        soup_matches = BeautifulSoup(resp_base.text, 'html.parser')

        # fetching element which holds list of all matches for current day.
        live_matches_div = soup_matches.find('div', class_="scoreCollection").find('div', class_='scoreCollection__header')
        
        headline = live_matches_div.find('div', class_='scoreEvent__title').get_text()

        live_match_detail = live_matches_div.next_sibling

        counter = 1
        matchLinks = []     # list of link of all the matches to be played today
        
        # looping for all the divs whihc hold individual match for current day
        for match_divs in live_match_detail.children:
            # skipping the unwanted data
            if match_divs['class'] == ['scorePromo__content', 'scorePromo__content--signup']:
                pass
            else:
                try:

                    # fetching detail of match
                    match_Heading_div = match_divs.find('div', class_='cscore_info-overview')
                    match_Heading = match_Heading_div.get_text().strip()

                    match_current_status_div = match_Heading_div.previous_sibling
                    match_current_status = match_current_status_div.span.get_text()
                    print(match_current_status)

                    # fetching elements that have scores of the 2 teams
                    opponents = match_divs.find('ul', class_='cscore_competitors').children
                    
                    # fetching scores for the two teams
                    match_score = []
                    match_opponents = []
                    s = ' vs '

                    for opponent in opponents:
                        data = opponent.find('div', class_='cscore_team')
                        team_flag = data.previous_sibling.img.get('data-src')
                        team_name = data.find('span', class_='cscore_name--abbrev').get_text()
                        team_score = data.find('div', class_='cscore_score').get_text()
                        match_score.append([team_flag, team_name, team_score])
                        match_opponents.append(team_name)

                    match_status = match_divs.find('div', class_='cscore_commentary--footer').get_text()
                    match_title = s.join(match_opponents)

                    # fetching link of the match and append to the list that holds all the links of the matches.
                    match_link = 'https://www.espncricinfo.com' + match_divs.find('div', class_='cscore_buttonGroup').ul.li.a['href'].replace('scorecard', 'game')
                    matchLinks.append(match_link)

                    live_match_details.append({
                                                    'match_current_status': match_current_status,
                                                    'match_title' : match_title,
                                                    'match_heading': match_Heading, 
                                                    'match_score': match_score, 
                                                    'match_status': match_status,
                                                    'match_link': match_link
                                                })
                    counter = counter+1
                    print(json.dumps(live_match_details, indent=4))

                except Exception as e:
                    print(str(e))
                    break

    params = {'live_match_details': live_match_details}

    return render(request, 'ScoreBuzz/index.html', params)


def scorecard(request):
    if request.method == 'GET' and 'link' in request.GET:
        match_url = request.GET.get('link','')

        url = match_url.split('game')       # using user's input to fetch the match link from the list.
        match_url =  url[0] + 'game' + url[1]   # link to the summary page of the match
        scorecard_url =  url[0] + 'scorecard' + url[1]  # link to the scorecard page of the match

        resp = requests.get(match_url)   # fetching data from the match url
        if resp.status_code == 200:     # executing further only if we have successfully fetched data from the url
            soup = BeautifulSoup(resp.text, 'html.parser')      # parsing data into beautifulsoup object using html parser

            # match data
            match_div = soup.find('div', class_='cscore_overview')
            match_status = match_div.find('span', class_='cscore_time').get_text()  # status of match, live, result, Abandoned, Date of match to be held in future and more
            match_date = match_div.find('span', class_='cscore_date').get_text()    # date of match
            match_detail = match_div.find('div', class_='cscore_info-overview').get_text()  # detail of match played

            # Displying scores for home team
            home_team = soup.find('li', class_='cscore_item--home')     # fetching list match_divs for home team
            home_team_name = home_team.find('span', class_='cscore_name--long').get_text()  # fetching name of home team
            home_team_name_abbrev = home_team.find('span', class_='cscore_name--abbrev').get_text() # fetching short name of homr team
            home_team_score = home_team.find('div', class_='cscore_score').get_text()   # fetching score home team
            
            # Displying scores for away team
            away_team = soup.find('li', class_='cscore_item--away')     # fetching list match_divs for away team
            away_team_name = away_team.find('span', class_='cscore_name--long').get_text()  # fetching name of away team
            away_team_name_abbrev = away_team.find('span', class_='cscore_name--abbrev').get_text() # fetching short name of away team
            away_team_score = away_team.find('div', class_='cscore_score').get_text()   # fetching score away team

            # current detail of match
            score_note = soup.find('span', class_='cscore_notes_game').get_text()

            # dictionary that holds header for the match
            match_header = {
                'status' : match_status,
                'match_detail' : match_detail,
                'score' : [[home_team_name, home_team_name_abbrev, home_team_score], [away_team_name, away_team_name_abbrev, away_team_score]],
                'score_note' : score_note,
            }

            # FETCHING SCORE SUMMARY FOR LIVE PAST MATCH
            if match_status in ['Live', 'Lunch', 'Tea', 'Stumps']:
                match_score_summary = live_match_summary(soup, match_detail)

            # FETCHING SCORE SUMMARY FOR THE PAST MATCH
            elif match_status == 'Result':
                try:
                    refresh_flag = False
                    soup.find('article', class_='current-inning')
                    match_score_summary = live_match_summary(soup, match_detail)
                except Exception as e:
                    past_match_summary(soup)
                    
            # FETCHING SCORECARD FOR THE MATCH
            resp_match = requests.get(scorecard_url)    # fetching data from the match scorecard url

            if resp_match.status_code == 200:   # executing further only if we have successfully fetched data from the scorecard url
                soup_scorecard = BeautifulSoup(resp_match.text, 'html.parser')      # parsing data into beautifulsoup object using html parser

                innings = soup_scorecard.find_all('article', class_='scorecard')    # fetching list of all inings in the match
                
                scorecard_List = {}

                innings_name = ['1st Innings', '2nd Innings', '3rd Innings', '4th Innings']

                innings_count = 0

                for inning in innings:  # looping through all inings inthe match
                    innings_detail_List = []

                    inning_title = inning.div      # fetching the 1st div element for that particular innings that holds title for innings
                    inning_details = inning_title.next_sibling     # the very next sibling match_divs holds all information fo the inning

                    # fetching all children (div for batsmen and bowlers) for this particluar match_divs 
                    inning_details_children = inning_details.children  # inning_details_children = [<div class="scorecard-section batsmen">, <div class="scorecard-section bowler">
                    
                    # looping through 
                    for inning_details in inning_details_children:
                        
                        player_number = 1
                        innings_complete_data = []
                        
                        # fetching datat for the batsman for this innings in the match
                        if inning_details['class'][1] == 'batsmen':

                            batsmen_header_sc_list = []
                            batsmen_stat_sc_list = []
                            
                            # fetching rows of all batsmen
                            all_batsmen = inning_details.children   # all_batsmen = <div class="flex-row">
                            
                            dnb = ''

                            # looping through each batsman
                            for batsman in all_batsmen:     # batsman = [<div class="wrap header">, <div class="wrap batsmen">] for 1st iteration and batsman = <div class="wrap batsmen"> for 2nd iteration
                                
                                batsman_list = []

                                # fetching details of extras conceded by bowling side
                                if batsman.find('div').get('class') == ['wrap', 'extras']:
                                    data_heading = batsman.find('div', class_='cell')
                                    data_value = data_heading.next_sibling
                                    extras = data_heading.get_text() + ': ' + data_value.get_text()

                                # fetching details of total runs scored by batting side
                                elif batsman.find('div').get('class') == ['wrap', 'total']:
                                    data_heading = batsman.find('div', class_='cell')
                                    data_value = data_heading.next_sibling
                                    total = data_heading.get_text() + ': ' + data_value.get_text()

                                # fetching details of fall of wickets and players yest to bat
                                elif batsman.find('div').get('class') == ['wrap', 'dnb']:
                                    for dnb_data in batsman.find_all('div', class_='dnb'):
                                        dnb = dnb + '\n' + dnb_data.get_text()

                                # fetching scorecard for batsmsn
                                else:
                                    # fetching details for the every 1st batsmen, segrating heading for batsmen scorecard and batsman score details
                                    if player_number == 1:
                                        batsman_header = batsman.find('div', class_='header')

                                        for header in batsman_header.children:   # fetching headers for batsman
                                            batsmen_header_sc_list.append(header.get_text())
                                        
                                        # fetching details for batsman
                                        for details in batsman_header.next_sibling.children:   
                                            batsman_list.append(details.get_text())

                                    # fetching details for every other batsman
                                    else:
                                        for details in batsman.find('div', class_='batsmen').children:
                                            batsman_list.append(details.get_text())
                                    
                                    batsmen_stat_sc_list.append(batsman_list)
                                
                                player_number = player_number + 1

                        # fetching datat for the bowlers for this innings in the match
                        elif inning_details['class'][1] == 'bowling':
                            
                            bowler_header_sc_list = []
                            bowler_stat_sc_list = []

                            headings = inning_details.find('thead').tr.children     # fetching element for headings of bowlere

                            # fetching headings
                            for heading in headings:
                                bowler_header_sc_list.append(heading.get_text())
                                
                            body = inning_details.find('tbody').children    # fetching element for details of bowlers
                            
                            # fetching details of each bowler
                            for bowler in body:
                                for bowler_detail in bowler.children:
                                    bowler_stat_sc_list.append(bowler_detail.get_text())
                    
                    innings_complete_data.append(batsmen_header_sc_list)
                    innings_complete_data.append(batsmen_stat_sc_list)
                    innings_complete_data.append(dnb)
                    innings_complete_data.append(extras)
                    innings_complete_data.append(total)
                    innings_complete_data.append(bowler_header_sc_list)
                    innings_complete_data.append(bowler_stat_sc_list)
                    scorecard_List[innings_name[innings_count]] = innings_complete_data
                    
                    # innings_detail_List.append(inning_title.get_text())

                    innings_count += + 1
            else:
                print('Error')
        else:
            print('Error')

        params = {
            'match_summary': match_header,
            'score_summary': match_score_summary,
            'scorecard': scorecard_List
            }


    return render(request, 'ScoreBuzz/scorecard.html', params)


def theme(request):
    return render(request, 'ScoreBuzz/theme.html')

