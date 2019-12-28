# Project - Text_Utils
# Coder - Siddhant Shah

from django.http import HttpResponse
from django.contrib import messages
from django.shortcuts import render, redirect


# function to handle call to the homepage
def index(request):
    if request.method == 'POST':
        
        option = request.POST['option']     # fetching user's radio button choice
        text = request.POST['content']  # fetching user's content
        message = ""

        # if user has selected radio button saying 'Remove Punctuations'
        if option == 'remove_punc':
            
            punc_str = """!"#$%&'()*+, -./:;<=>?@[\]^_`{|}~"""

            for char in text:
                if char not in punc_str:
                    message += char
            
            messages.info(request, message)
            return redirect('/')

        # if user has selected radio button saying 'Count Words'
        elif option == 'count_words':
            
            count_words = len(text.split(' '))
            message_count_word = "Word Count : " + str(count_words)

            count_char_w_space = len(text)
            msg_count_char_w_space = "Char Count (with Space) : " + str(count_char_w_space)

            count_char_wo_space = len(text.replace(" ", ""))
            msg_count_char_wo_space = "Char Count (without Space) : " + str(count_char_wo_space)

            outcome = {'result': message_count_word + "\n" + msg_count_char_w_space + "\n" + msg_count_char_wo_space}

            return render(request, 'index.html', outcome)
        
        # if user has selected radio button saying 'Title Case'
        elif option == 'title_case':
            
            message = text.title()
            messages.info(request, message)
            
            return redirect('/')

        # if user has selected radio button saying 'Upper Case'
        elif option == 'upper_case':
            
            message = text.upper()
            messages.info(request, message)
            
            return redirect('/')

        # if user has selected radio button saying 'One Paragraph'
        elif option == 'one_para':
            
            message = text.replace("\\n", " ")
            messages.info(request, message)
            
            return redirect('/')

        # if user has selected radio button saying 'Extra Space Remover '
        elif option == 'extra_space_remover':
            
            prev_char = ""
            message = ""

            for char in text:
            
                if not char == prev_char:
                    message += char
                    prev_char = char

            messages.info(request, message)
            
            return redirect('/')
    
    else:
        return render(request, 'index.html')