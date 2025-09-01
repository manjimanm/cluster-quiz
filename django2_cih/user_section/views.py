from django.shortcuts import render,redirect,get_object_or_404
from admin_section.models import *
from django.http import HttpResponse
import random
import json
from django.http import JsonResponse
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.urls import reverse
from django.contrib.auth import logout
from datetime import timedelta
import re 
from urllib.parse import urlencode

import base64

# Create your views here.


def navbar(request):
    if 'user_uid' in request.session:
        user_id = request.session['user_uid']
        try:
            user = registuser.objects.get(id=user_id)
            category_name = user.categoryd.id
        except registuser.DoesNotExist:
            user = None
            category_name = ""
    else:
        user = None
        category_name = ""
        
   
    context = {'user': user, 'category_name': category_name}
    return render(request,'navbar.html',context)

#email check in registration using Ajax
def check_email(request):
    if request.method == "GET":
        email = request.GET.get('email', None)
        
        if email:
            if registuser.objects.filter(email=email).exists():
                return JsonResponse({'exists': True})  
            else:
                return JsonResponse({'exists': False})  
        else:
            return JsonResponse({'error': 'No email provided'}, status=400) 

#registration
def newregister(request):
    categories = category.objects.all()  
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        ucategory = request.POST.get('category') 
        password = request.POST.get('password') 
        addedon = timezone.now()
        addedby = 2
        
        selected_category = category.objects.get(id=ucategory)
        
       
        registuser.objects.create(
            name=name,
            email=email,
            phone=phone,
            categoryd=selected_category,
            password=password,
            added_on=addedon,
            added_by=addedby
        )
        messages.success(request, "You have successfully registered. Please log in to continue.")
        return redirect('/')

    return render(request, 'newregister.html', {'categories': categories})




#demo test
def questionare(request):
    user_uid = request.session.get('user_uid') 
    selected_category = None  
    user = None  
    if user_uid:
        user = get_object_or_404(registuser, id=user_uid) 
       
        if hasattr(user, 'categoryd') and user.categoryd:
            selected_category = user.categoryd.id

    if selected_category:
        questions_list = list(questions.objects.filter(category_id=selected_category))
        random_questions = random.sample(questions_list, min(10, len(questions_list)))
    else:
        random_questions = []
        print(random_questions)

    if request.method == "POST":
        user_uid = request.POST.get('uiuser_uidd')
        print("User ID from POST:", user_uid)
        
        selected_category=request.POST.get('category_name')
        print(selected_category)
        aid = request.POST.get('aid')
        score = request.POST.get('score')
        
        attempts = attempt.objects.create(
            user_id=user_uid, 
            category=selected_category,
            add_id=aid,
            score=score
        )
        print(attempts)
 

    
        q_id=request.POST.getlist('qid')
        user_answers= [request.POST.get(f'options-{i}') for i in range(len(q_id))]
        for i, quiz in enumerate(q_id):
                
                user_ans = user_answers[i]  
                if user_ans:  
                    results = attemptresult.objects.create(
                        attempt=attempts,
                        question_id=quiz,
                        user_ans=user_ans
                    )
        print(results)
        return redirect('results', score=score)
    context = {
        'questions': random_questions,
        'selected_category': selected_category,
        'uid': user_uid,
        'user': user,
    }
    return render(request, 'questionare.html', context)  




def results(request, score):
    user_uid = request.session.get('user_uid')
    
    latest_attempt = attempt.objects.filter(user_id=user_uid).order_by('-id').first()

    attempt_results = attemptresult.objects.filter(attempt=latest_attempt)

    correct_answers = sum(1 for result in attempt_results if result.user_ans == result.question.answer)
    total_questions = attempt_results.count()

    if total_questions > 0:
        correct_percentage = (correct_answers / total_questions) * 100
    else:
        correct_percentage = 0

    pass_fail_status = "Passed" if correct_percentage >= 70 else "Failed"

    context = {
        'score': score,
        'attempt_results': attempt_results,
        'latest_attempt': latest_attempt,
        'correct_percentage': correct_percentage,
        'pass_fail_status': pass_fail_status,
    }

    return render(request, 'results.html', context)




#mocktest
def exam(request):
    user_uid = request.session.get('user_uid')
    selected_category = None
    user = None

    if user_uid:
        user = get_object_or_404(registuser, id=user_uid)
        user_name = user.name

        if hasattr(user, 'categoryd') and user.categoryd:
            selected_category = user.categoryd.id

    if selected_category:
        existing_attempt = attempt.objects.filter(user_id=user_uid, category=selected_category,add_id=2).first()
        if existing_attempt:
            return render(request, 'already_attempted.html')

        questions_list = list(questions.objects.filter(category_id=selected_category))
        random_questions = random.sample(questions_list, min(10, len(questions_list)))
    else:
        random_questions = []
        print(random_questions)

    if request.method == "POST":
   
        user_uid = request.POST.get('user_uid')
        print("User ID from POST:", user_uid)

        selected_category = request.POST.get('category_name')
        print(selected_category)
        aid = request.POST.get('aid')
        score = request.POST.get('score')

   
        attempts = attempt.objects.create(
            user_id=user_uid,
            category=selected_category,
            add_id=aid,
            score=score
        )
        print(attempts)

        # Process user answers
        q_id = request.POST.getlist('qid')
        user_answers = [request.POST.get(f'options-{i}') for i in range(len(q_id))]
        for i, quiz in enumerate(q_id):
            user_ans = user_answers[i]
            if user_ans:
                attemptresult.objects.create(
                    attempt=attempts,
                    question_id=quiz,
                    user_ans=user_ans
                )
        print(results)
        
        # Redirect to results page
        return redirect('results', score=score)

    context = {
        'questions': random_questions,
        'selected_category': selected_category,
        'uid': user_uid,
        'user': user,
    }

    
    
    return render(request, 'exam.html', context)



#aptitude test
def aptitude_test(request):
    user_uid = request.session.get('user_uid')
    users = get_object_or_404(registuser, id=user_uid)
    if not user_uid:
        return redirect('ulogin')

    user_instance = get_object_or_404(registuser, id=user_uid)

   
    latest_add_exam_instance = add_exam.objects.filter(userd=user_instance).order_by('-id').first()

  
    if not latest_add_exam_instance:
        
        return render(request, 'no_exam.html', {
            'uname': user_instance.name,
            'selected_category': user_instance.categoryd.category_name,
        })

    already_attempted = attempt.objects.filter(add_id=latest_add_exam_instance.id).exists()

    if not already_attempted:
        scheduled_exams = schedulexam.objects.filter(add_id=latest_add_exam_instance.id)
        questions_list = [scheduled_exam.questiond for scheduled_exam in scheduled_exams]
    else:
        return render(request, 'already_attempted.html', {
            'uname': user_instance.name,
            'selected_category': user_instance.categoryd.category_name,
        })

    context = {
        'questions': questions_list,
        'selected_category': user_instance.categoryd,
        'uid': user_uid,
        'uname': user_instance.name,
        'add': latest_add_exam_instance,
        'user':users
    }

    if request.method == "POST":
        selected_category = request.POST.get('category_name')
        aid = request.POST.get('aid')
        score = request.POST.get('score')

        if not selected_category:
            return render(request, 'home.html', context)

        attempts = attempt.objects.create(
            user_id=user_uid,
            category=selected_category,
            add_id=aid,
            score=score
        )

        q_id = request.POST.getlist('qid')
        user_answers = [request.POST.get(f'options-{i}') for i in range(len(q_id))]
        for i, quiz in enumerate(q_id):
            user_ans = user_answers[i]
            if user_ans:
                attemptresult.objects.create(
                    attempt=attempts,
                    question_id=quiz,
                    user_ans=user_ans
                )

        return redirect('results', score=score)

    return render(request, 'aptitude_test.html', context)

def user_profile(request):
    return render (request,'user_profile.html')

def see_test_results(request, user_id):
    try:
      
        user = registuser.objects.get(id=user_id)
        category_name = user.categoryd.category_name
        
        assigned=assigned_attempt.objects.filter(user_id=user_id)
        attempts = attempt.objects.filter(user_id=user_id)
        demo_tests = attempts.filter(add_id=1)
        mock_tests = attempts.filter(add_id=2)
        aptitude_tests = assigned_attempt.objects.filter(user_id=user_id)
        
        context = {
            'user': user,
            'category_name': category_name,
            'demo_tests': demo_tests,
            'mock_tests': mock_tests,
            'aptitude_tests': aptitude_tests,
        }

        return render(request, 'see_test_results.html', context)
    except registuser.DoesNotExist:
       
        return redirect('/')
    


def results_details(request, attempt_id):
    
    attempt_instance = get_object_or_404(attempt, id=attempt_id)
     
    attempt_results = attemptresult.objects.filter(attempt=attempt_instance)

    user_instance = get_object_or_404(registuser, id=attempt_instance.user_id)
  
    category_instance = get_object_or_404(category, id=user_instance.categoryd.id)

    details = []
    
    for result in attempt_results:
       
        question = get_object_or_404(questions, id=result.question.id)
    
        details.append({
            'id':question.id,
            'question': question.question,
            'option1': question.option1,
            'option2': question.option2,
            'option3': question.option3,
            'correct_answer': question.answer,
            'user_answer': result.user_ans,
        })
  
    return render(request, 'results_details.html', {
        'details': details,
        'attempt': attempt_instance,
        'user': user_instance,
        'category': category_instance
    })



def assessment_details(request, attempt_id):
    
    attempt_instance = get_object_or_404(assigned_attempt, id=attempt_id)
     
    attempt_results = assigned_attemptresult.objects.filter(attempt=attempt_instance)

    user_instance = get_object_or_404(registuser, id=attempt_instance.user_id)
  
    category_instance = get_object_or_404(category, id=user_instance.categoryd.id)

    details = []
    
    for result in attempt_results:
       
        question = get_object_or_404(questions, id=result.question.id)
    
        details.append({
            'id':question.id,
            'question': question.question,
            'option1': question.option1,
            'option2': question.option2,
            'option3': question.option3,
            'correct_answer': question.answer,
            'user_answer': result.user_ans,
        })
  
    return render(request, 'results_details.html', {
        'details': details,
        'attempt': attempt_instance,
        'user': user_instance,
        'category': category_instance
    })







def test(request):
    user_uid = request.session.get('user_uid')
    selected_category = None
    user = None
    # aid  = 1

    if user_uid:
        user = get_object_or_404(registuser, id=user_uid)

        if hasattr(user, 'categoryd') and user.categoryd:
            selected_category = user.categoryd.id

    if selected_category:
        # Check if the user has already attempted the test in this category
        existing_attempt = attempt.objects.filter(user_id=user_uid, category=selected_category,add_id=1).first()
        if existing_attempt:
            # If an attempt exists, redirect to 'no_exam.html'
            return render(request, 'already_attempted.html')# Make sure you have a URL for 'no_exam'

        # Get random questions from the selected category
        questions_list = list(questions.objects.filter(category_id=selected_category))
        random_questions = random.sample(questions_list, min(10, len(questions_list)))
    else:
        random_questions = []
        print(random_questions)

    if request.method == "POST":
        # Handle form submission
        user_uid = request.POST.get('user_uid')
        print("User ID from POST:", user_uid)

        selected_category = request.POST.get('category_name')
        print(selected_category)
        aid = request.POST.get('aid')
        score = request.POST.get('score')

        # Create a new attempt record for the user
        attempts = attempt.objects.create(
            user_id=user_uid,
            category=selected_category,
            add_id=aid,
            score=score
        )
        print(attempts)

        # Process user answers
        q_id = request.POST.getlist('qid')
        user_answers = [request.POST.get(f'options-{i}') for i in range(len(q_id))]
        for i, quiz in enumerate(q_id):
            user_ans = user_answers[i]
            if user_ans:
                attemptresult.objects.create(
                    attempt=attempts,
                    question_id=quiz,
                    user_ans=user_ans
                )
        print(results)
        
        # Redirect to results page
        return redirect('results', score=score)

    context = {
        'questions': random_questions,
        'selected_category': selected_category,
        'uid': user_uid,
        'user': user,
    }

    return render(request, 'test.html', context)





# def logout_view(request):
#     logout(request)  
#     return redirect('/')  
def logout_view(request):
    if 'user_uid' in request.session:
        del request.session['user_uid']
    return redirect('/')




def ulogin(request):
    if request.method == 'POST':
        username = request.POST.get('email')
        password = request.POST.get('password')

        try:
           
            user = registuser.objects.get(email=username, password=password)
            request.session['user_uid'] = user.id

            next_url = request.GET.get('next', 'home')

            return redirect(next_url) 

        except registuser.DoesNotExist:
            context = {'error': 'Invalid credentials. Please try again.'}
            return render(request, 'ulogin.html', context)

    return render(request, 'ulogin.html')



def home(request):
    exams = create_examid.objects.all().distinct()
    
    user = None
    category_name = "No category"

    if 'user_uid' in request.session:
        user_id = request.session['user_uid']
        try:
            user = registuser.objects.get(id=user_id)

            if user.categoryd:
                category_name = user.categoryd.id
            else:
                category_name = "No category"
            
           

        except registuser.DoesNotExist:
            user = None
            category_name = "No category"
            exam = None
    else:
        messages.error(request, "You need to log in first.")
        return redirect('/')  
    latest_exam_application = exam_apply.objects.filter(userid=user_id).order_by('-applied_time').first()
    if latest_exam_application:
        # If there's a recent exam application, set the link to the assessment page
        # assessment_link = 'planned_exam' 
        assessment_link = 'assessment'  # Name of the URL for the assessment page (use URL name)
    else:
        # If no exam application, set the link to the 'no exams' page or whatever is suitable
        assessment_link = None  
    
    
    # Pass the exam (if any) to the context along with the list of all exams
    context = {
        'user': user,
        'category_name': category_name,
        'exams': exams,
        # 'exam': exam,  # This will be the assigned exam or None
        'assessment_link': assessment_link
    }

    return render(request, 'home.html', context)




def exam_invite(request, encoded_exam_id):
   
    try:
        # Decode the Base64-encoded exam ID
        decoded_exam_id = base64.b64decode(encoded_exam_id).decode('utf-8')

        # Print the decoded string for debugging purposes
        print(f"Decoded exam ID: {decoded_exam_id}")

        # The decoded string is in the format '/exam_invite/43/', so we need to get the ID correctly
        # Strip any leading or trailing slashes and split by '/'
        parts = decoded_exam_id.strip('/').split('/')

        # Debug: Print the parts to see the result of splitting
        print(f"Split parts: {parts}")

        # Check if the decoded string is in the expected format
        if len(parts) > 1 and parts[1].isdigit():
            exam_id = int(parts[1])  # This extracts the '43' part
        else:
            raise ValueError("Invalid format for the exam ID.")

    except Exception as e:
        messages.error(request, f"Error decoding the exam ID: {e}")
        return redirect('home')

    

    # Continue processing with the decoded exam ID
    # Retrieve the exam from the database using exam_id
    exam = get_object_or_404(create_examid, id=exam_id)

    # Retrieve the user from the session
    user_uid = request.session.get('user_uid')
    if not user_uid:
        messages.error(request, "You need to log in first.")
        return redirect(f"/?next={request.path}")  

    user = get_object_or_404(registuser, id=user_uid)

    # Retrieve the exam from the database using the decoded exam ID
    # exam = get_object_or_404(create_examid, id=exam_id)
    print(f"Session keys: {request.session.keys()}")



    if user.categoryd != exam.catid:
        messages.error(request, "This exam is not for your category.")
        return redirect('home')  

    invite_link = request.build_absolute_uri(f'/exam_invite/{encoded_exam_id}/')

    if request.method == "POST":
        userid = request.POST.get('userid')
        addedon = datetime.now()

        exam_apply.objects.create(
            userid=user.id,
            exam_id=exam.id,
            applied_time=addedon,
            status=0
        )

        messages.success(request, "You have successfully applied.")
        return redirect('home')

    return render(request, 'exam_invite.html', {
        'exam': exam,
        'invite_link': invite_link,
        'user': user
    })






def assigned_exam(request, exam_id):
    # Ensure user is logged in
    user_uid = request.session.get('user_uid')
    if not user_uid:
        messages.error(request, "You need to log in first.")
        return redirect(f"/?next={request.path}")  

    user = get_object_or_404(registuser, id=user_uid)
    print(f"User ID: {user.id}")  # Debugging line

    # Ensure user has applied for the exam
    applied_exam = exam_apply.objects.filter(userid=user.id, exam_id=exam_id).order_by('-id').first()
    print(f"Applied Exam: {applied_exam}")  # Debugging line

    if not applied_exam:
        print("Applied exam does not exist. Redirecting to no_exam.html.")
        return render(request, 'no_exam.html')  # No applied exam

    if applied_exam.status == 0:
        print("Exam status is 0. Redirecting to no_exam.html.")
        return render(request, 'no_exam.html')

    # Set applied_exam ID in session
    request.session['applied_exam_id'] = applied_exam.id
    request.session.save()

    # Fetch the assigned exam details
    try:
        assigned_exam_obj = assign_exam.objects.filter(examid=exam_id).order_by('-id').first()
        if not assigned_exam_obj:
            raise assign_exam.DoesNotExist
        print(f"Assigned Exam: {assigned_exam_obj}")
    except assign_exam.DoesNotExist:
        print(f"Exam with id {exam_id} does not exist in assigned_exam.")
        return render(request, 'no_exam.html')

    # Retrieve exam time and calculate end time
    set_date = assigned_exam_obj.set_date
    set_time = assigned_exam_obj.set_time
    created_exam = get_object_or_404(create_examid, id=exam_id)
    allowed_time_str = created_exam.allowed_time

    allowed_time_duration = convert_to_duration(allowed_time_str)
    hours, remainder = divmod(allowed_time_duration.seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    formatted_allowed_time = f"{hours} hours {minutes} minutes" if hours else f"{minutes} minutes"

    scheduled_datetime = datetime.combine(set_date, set_time)
    end_datetime = scheduled_datetime + allowed_time_duration

    current_datetime = datetime.now()
    if current_datetime < scheduled_datetime:
        return render(request, 'exam_not_yet_started.html', {'exam': assigned_exam_obj})
    elif current_datetime > end_datetime:
        return render(request, 'exam_already_ended.html', {'exam': assigned_exam_obj})

    # Fetch the questions for this exam
    exam_question_ids = exam_questions.objects.filter(exam_id=exam_id)
    question_list = []
    for exam_question in exam_question_ids:
        question = get_object_or_404(questions, id=exam_question.question.id)
        question_list.append(question)

    context = {
        'exam': assigned_exam_obj,
        'questions': question_list,
        'user': user,
        'allowed_time': formatted_allowed_time,
        'applied_exam': applied_exam,  # Add the applied_exam object to context
    }

    # Handle form submission
    if request.method == "POST":
        print(f"Session ID on POST: {request.session.session_key}")

        # Retrieve applied_exam_id from session
        applied_exam_id = request.session.get('applied_exam_id')
        print(f"Applied Exam ID from session: {applied_exam_id}")

        if not applied_exam_id:
            print("Applied Exam ID is missing from session. Redirecting to no_exam.html.")
            return render(request, 'no_exam.html')

        # Fetch applied_exam from database using the session's applied_exam_id
        applied_exam = get_object_or_404(exam_apply, id=applied_exam_id)
        print(f"Applied Exam (POST): {applied_exam}")

        if applied_exam is None or applied_exam.status == 0:
            print("Exam status is 0 after POST. Redirecting to no_exam.html.")
            return render(request, 'no_exam.html')

        # Process form submission and save attempt
        aid = request.POST.get('aid')
        score = request.POST.get('score')
        estatus = request.POST.get('examstatus')

        attempts = assigned_attempt.objects.create(
            user_id=user.id,
            examid=exam_id,
            application_id=applied_exam.id,  # Use the application_id from applied_exam
            score=score,
            submitted_on=datetime.now(),
            exam_status=estatus
        )

        # Handle user answers
        q_id = request.POST.getlist('qid')
        user_answers = [request.POST.get(f'options-{i}') for i in range(len(q_id))]
        for i, quiz in enumerate(q_id):
            user_ans = user_answers[i]
            if user_ans:
                assigned_attemptresult.objects.create(
                    attempt=attempts,
                    question_id=quiz,
                    user_ans=user_ans
                )

        # Redirect to the home page after successful submission
        return redirect('home')

    return render(request, 'assigned_exam.html', context)







# In views.py
def exam_not_scheduled(request):
    return render(request, 'exam_not_scheduled.html')





def assigned_exam_results(request, attempt_id):
    attempt = get_object_or_404(assigned_attempt, id=attempt_id)
    exam_id = attempt.examid
    passmark = None
    percentage = get_object_or_404(create_examid, id=exam_id)
    passmark =percentage.percentage_to_pass
    print(f"exam id:{exam_id}")
    print(f"percenatge:{passmark}")
    
    attempt_results = assigned_attemptresult.objects.filter(attempt=attempt)

    total_questions = attempt_results.count()
    correct_answers = sum(1 for result in attempt_results if result.user_ans == result.question.answer)
    score = correct_answers
    correct_percentage = (correct_answers / total_questions) * 100 if total_questions else 0

    pass_fail_status = "Passed" if correct_percentage >= passmark else "Failed"

    # Render the result template with the necessary context
    return render(request, 'assigned_exam_results.html', {
        'score': score,
        'attempt_results': attempt_results,
        'correct_percentage': correct_percentage,
        'pass_fail_status': pass_fail_status,
    })



def convert_to_duration(time_str):
    """
    Convert a time string (e.g., '2:30', '2 hours 30 minutes', '150 minutes') to a timedelta object.
    """
    if "hour" in time_str or "minute" in time_str:  # If the string has 'hours' or 'minutes'
        time_parts = time_str.split()
        hours = 0
        minutes = 0
        for i in range(0, len(time_parts), 2):
            value = int(time_parts[i])
            unit = time_parts[i + 1]
            if "hour" in unit:
                hours = value
            elif "minute" in unit:
                minutes = value
        return timedelta(hours=hours, minutes=minutes)
    else:
        # If the time string is in format like '2:30' (HH:MM)
        time_parts = time_str.split(':')
        hours = int(time_parts[0])
        minutes = int(time_parts[1]) if len(time_parts) > 1 else 0
        return timedelta(hours=hours, minutes=minutes)



def assessment(request):
    user_uid = request.session.get('user_uid')
    
    if not user_uid:
        messages.error(request, "You need to log in first.")
        return redirect(f"/?next={request.path}")  
    
    user = get_object_or_404(registuser, id=user_uid)
    
    # Retrieve the latest exam application for this user (most recent application)
    latest_exam_application = exam_apply.objects.filter(userid=user.id).order_by('-applied_time').first()

    if latest_exam_application:
        # Check if the user has already attempted the exam based on the application_id
        if assigned_attempt.objects.filter(application_id=latest_exam_application.id).exists():
            # If the user has already attempted the exam, redirect to 'already_attempted.html'
            return render(request, 'already_attempted.html', {'exam': latest_exam_application.exam_id})
        
        if latest_exam_application.status == 0:
            # If the status is 0, redirect the user to the 'exam_not_yet_started.html' page
            return render(request, 'exam_not_scheduled.html')

        if latest_exam_application.status == 1:
            # If the status is 1, check for the corresponding entry in the 'assign_exam' table
            assigned_exam = assign_exam.objects.filter(applicationid=latest_exam_application.id).first()

            if assigned_exam:
                set_date = assigned_exam.set_date
                set_time = assigned_exam.set_time
                
                # Get the corresponding 'create_examid' object using the examid integer
                exam_object = get_object_or_404(create_examid, id=assigned_exam.examid)

                allowed_time_str = exam_object.allowed_time  # Now you can access allowed_time correctly
                
                allowed_time_duration = convert_to_duration(allowed_time_str)
                hours, remainder = divmod(allowed_time_duration.seconds, 3600)
                minutes, _ = divmod(remainder, 60)
                formatted_allowed_time = f"{hours} hours {minutes} minutes" if hours else f"{minutes} minutes"

                scheduled_datetime = datetime.combine(set_date, set_time)
                end_datetime = scheduled_datetime + allowed_time_duration
                print(f"ending time:{end_datetime}")

                current_datetime = datetime.now()
                if current_datetime < scheduled_datetime:
                    return render(request, 'exam_not_yet_started.html', {
                        'exam': assigned_exam,
                        'set_date': set_date,
                        'set_time': set_time
                    })
                elif current_datetime > end_datetime:
                    return render(request, 'exam_already_ended.html', {
                        'exam': assigned_exam,
                        'set_date': set_date,
                        'set_time': set_time
                    })

                # If the current time is within the allowed time, render the exam page
                # Fetch questions related to this exam (from the 'exam_questions' table)
                exam_questions_list = exam_questions.objects.filter(exam_id=assigned_exam.examid)

                questions_list = []
                for exam_question in exam_questions_list:
                    question = get_object_or_404(questions, id=exam_question.question.id)
                    questions_list.append(question)

                if request.method == 'POST':
                    score = request.POST.get('score')  # Get the score directly from the input field

                    # Create the entry in the 'assigned_attempt' table first
                    attempt = assigned_attempt.objects.create(
                        user_id=user_uid,
                        examid=assigned_exam.examid,  # Corrected this line
                        score=score,  # Store the score from the input field
                        application_id=latest_exam_application.id,
                        submitted_on=datetime.now(),
                        exam_status=1  # exam_status = 1 means the exam is completed
                    )

                    # Now that we have the 'assigned_attempt' entry, we can save the answers to the 'assigned_attemptresult' table
                    for i, question in enumerate(questions_list):
                        selected_answer = request.POST.get(f"options-{i}")
                        
                        if selected_answer:
                            # Save the result in the 'assigned_attemptresult' table
                            assigned_attemptresult.objects.create(
                                attempt=attempt,  # Referencing the attempt from 'assigned_attempt'
                                question=question,
                                user_ans=selected_answer
                            )

                    # After saving both tables, redirect the user to the 'assigned_exam_results' page
                    return redirect('assigned_exam_results', attempt_id=attempt.id)  # Pass attempt ID for fetching results

                # If the form is not yet submitted, display the exam and questions
                return render(request, 'assessment.html', {
                    'set_date': set_date,
                    'set_time': set_time,
                    'examid': assigned_exam.examid,  # Corrected this line
                    'exam': assigned_exam.examid,  # Corrected this line
                    'questions': questions_list,
                    'formatted_allowed_time':formatted_allowed_time,
                    'end_datetime':end_datetime
                })

            else:
                return render(request, 'exam_not_yet_started.html', {'set_date': set_date, 'set_time': set_time})

    else:
        return render(request, 'exam_not_yet_started.html', {'set_date': set_date, 'set_time': set_time})







def exam_already_ended(request, set_date, set_time, allowed_time_str):
    # Convert string inputs for set_date and set_time to datetime objects
    set_date_obj = datetime.strptime(set_date, "%Y-%m-%d").date()
    set_time_obj = datetime.strptime(set_time, "%H:%M:%S").time()
    scheduled_datetime = datetime.combine(set_date_obj, set_time_obj)
    
    # Convert allowed_time_str to a timedelta object
    allowed_time_duration = convert_to_duration(allowed_time_str)
    end_datetime = scheduled_datetime + allowed_time_duration

    # Get current date and time
    current_datetime = timezone.now()

    # If the current date and time is later than the exam end time, render the page
    if current_datetime > end_datetime:
        context = {
            'set_date': set_date_obj,
            'set_time': set_time_obj,
        }
        return render(request, 'exam_already_ended.html', context)
    else:
        # If the exam hasn't ended, redirect to another page
        return redirect('exam_in_progress')      


def planned_exam(request):
    user_uid = request.session.get('user_uid')
    
    if not user_uid:
        messages.error(request, "You need to log in first.")
        return redirect(f"/?next={request.path}")  
    
    user = get_object_or_404(registuser, id=user_uid)

    latest_exam_application = exam_apply.objects.filter(userid=user.id).order_by('-applied_time').first()
    print(f"apply id:{latest_exam_application}")

    if latest_exam_application:
        # Check if the user has already attempted the exam based on the application_id
        if assigned_attempt.objects.filter(application_id=latest_exam_application.id).exists():
            # If the user has already attempted the exam, redirect to 'already_attempted.html'
            return render(request, 'already_attempted.html', {'exam': latest_exam_application.exam_id})
        
        if latest_exam_application.status == 0:
            # If the status is 0, redirect the user to the 'exam_not_yet_started.html' page
            return render(request, 'exam_not_scheduled.html')

        if latest_exam_application.status == 1:
            # If the status is 1, check for the corresponding entry in the 'assign_exam' table
            assigned_exam = planner_list.objects.filter(applicationid=latest_exam_application.id).first()

            if assigned_exam:
                plan_id = assigned_exam.planid.id
                planners = get_object_or_404(exam_planner, id=plan_id)
                p_date = planners.exam_date
                p_time = planners.exam_time
                set_date = p_date
                set_time = p_time
                
                # Get the corresponding 'create_examid' object using the examid integer
                exam_object = get_object_or_404(create_examid, id=assigned_exam.examid)

                q_count = exam_object.no_questions

                
        

                allowed_time_str = exam_object.allowed_time  # Now you can access allowed_time correctly
                
                allowed_time_duration = convert_to_duration(allowed_time_str)
                hours, remainder = divmod(allowed_time_duration.seconds, 3600)
                minutes, _ = divmod(remainder, 60)
                formatted_allowed_time = f"{hours} hours {minutes} minutes" if hours else f"{minutes} minutes"

                scheduled_datetime = datetime.combine(set_date, set_time)
                end_datetime = scheduled_datetime + allowed_time_duration
                print(f"ending time:{end_datetime}")

                current_datetime = datetime.now()
                if current_datetime < scheduled_datetime:
                    return render(request, 'exam_not_yet_started.html', {
                        'exam': assigned_exam,
                        'set_date': set_date,
                        'set_time': set_time
                    })
                elif current_datetime > end_datetime:
                    return render(request, 'exam_already_ended.html', {
                        'exam': assigned_exam,
                        'set_date': set_date,
                        'set_time': set_time
                    })
                # If the current time is within the allowed time, render the exam page
                # Fetch questions related to this exam (from the 'exam_questions' table)
                exam_questions_list = exam_questions.objects.filter(exam_id=assigned_exam.examid)

                questions_list = []
                for exam_question in exam_questions_list:
                    question = get_object_or_404(questions, id=exam_question.question.id)
                    questions_list.append(question)
                random_questions = random.sample(questions_list, min(q_count, len(questions_list)))
                print(f"Randomly selected questions: {random_questions}")

                # Loop over the random questions and save them
                for i in random_questions:
                    print(f"Saving question {i.id}")
                    
                    # Save each selected question in the 'save_questions' table
                    save_quiz = save_questions.objects.create(
                        userid=user_uid,
                        applicationid=latest_exam_application,  # Use the id, not the object
                        question_id=i.id
                    )
                    
                    # No need to call save() explicitly here since create() already saves it
                    print(f"Question {i.id} saved successfully.")

                # Print final random questions for debugging
                print(f"Final randomly selected questions: {random_questions}")


                if request.method == 'POST':
                    score = request.POST.get('score')  # Get the score directly from the input field

                    # Create the entry in the 'assigned_attempt' table first
                    attempt = assigned_attempt.objects.create(
                        user_id=user_uid,
                        examid=assigned_exam.examid,  # Corrected this line
                        score=score,  # Store the score from the input field
                        application_id=latest_exam_application.id,
                        submitted_on=datetime.now(),
                        exam_status=1  # exam_status = 1 means the exam is completed
                    )

                    # Now that we have the 'assigned_attempt' entry, we can save the answers to the 'assigned_attemptresult' table
                    for i, question in enumerate(questions_list):
                        selected_answer = request.POST.get(f"options-{i}")
                        
                        if selected_answer:
                            # Save the result in the 'assigned_attemptresult' table
                            assigned_attemptresult.objects.create(
                                attempt=attempt,  # Referencing the attempt from 'assigned_attempt'
                                question=question,
                                user_ans=selected_answer
                            )

                    # After saving both tables, redirect the user to the 'assigned_exam_results' page
                    return redirect('assigned_exam_results', attempt_id=attempt.id)  # Pass attempt ID for fetching results

                # If the form is not yet submitted, display the exam and questions
                return render(request, 'planned_exam.html', {
                    'set_date': set_date,
                    'set_time': set_time,
                    'examid': assigned_exam.examid,  # Corrected this line
                    'exam': assigned_exam.examid,  # Corrected this line
                    # 'questions': questions_list,
                    'questions': random_questions,
                    'formatted_allowed_time':formatted_allowed_time,
                    'end_datetime':end_datetime
                })

            else:
                return render(request, 'exam_not_yet_started.html', {'set_date': set_date, 'set_time': set_time})

    else:
        return render(request, 'exam_not_yet_started.html', {'set_date': set_date, 'set_time': set_time})
    
    

def exam_not_yet_started(request, set_date, set_time):
    # Convert string inputs for set_date and set_time to datetime objects
    set_date_obj = datetime.strptime(set_date, "%Y-%m-%d").date()
    set_time_obj = datetime.strptime(set_time, "%H:%M:%S").time()
    scheduled_datetime = datetime.combine(set_date_obj, set_time_obj)

    current_datetime = timezone.now()


    if current_datetime < scheduled_datetime:
        context = {
            'set_date': set_date_obj,
            'set_time': set_time_obj,
        }
        return render(request, 'exam_not_yet_started.html', context)
    else:
        return redirect('exam_in_progress')