from django.shortcuts import render , redirect,get_object_or_404
from django.http import HttpResponse,HttpResponseRedirect
from django.urls import reverse
from .models import *
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.http import Http404
import json
from datetime import datetime
import logging
from django.contrib.auth import logout
from django.core.paginator import Paginator
# Create your views here.

# def header(request):
#     permissions = request.session.get('permissions', [])
#     return render(request,'header.html',{'permissions': permissions})
def header(request):
    permissions = request.session.get('permissions', [])

    # Sort alphabetically by name (case-insensitive)
    permissions = sorted(permissions, key=lambda x: x['name'].lower())

    return render(request, 'header.html', {'permissions': permissions})
def index(request):
    uid = request.session.get('uid')

    if uid:
        try:
            user = super_users.objects.get(id=uid)

            user_role = user.roles

            role_permissions = role_permission.objects.filter(roles=user_role)

            permissions = [
                {
                    'name': permission.permissions.permissions, 
                    'url': permission.permissions.page_url ,
                    'icon': permission.permissions.url_icon      
                }
                for permission in role_permissions
            ]

            permissions = sorted(permissions, key=lambda x: x['name'].lower())
            context = {
                'user': user,
                'permissions': permissions,
            }
            return render(request, 'index.html', context)
        except super_users.DoesNotExist:
           
            del request.session['uid']
            return redirect('login')
    else:
      
        return redirect('login')


def myfunction(request):
    return HttpResponse("manjima")


# def index(request):
#     uid = request.session.get('uid')
#     return render(request, 'index.html')



def check_category_exists(request):
    category_name = request.GET.get('category_name', '').strip()
    exists = category.objects.filter(category_name__iexact=category_name).exists()
    return JsonResponse({'exists': exists})
    
def newcategory(request):
    cat_details = category.objects.all()
    category_to_edit = None

    permissions = request.session.get('permissions', [])
    permissions = sorted(permissions, key=lambda x: x['name'].lower()) if permissions else []

    if request.method == 'POST':
        cat_name = request.POST.get('categoryname')
        cat_id = request.POST.get('category_id')

        if cat_id: 
            try:
                cat = category.objects.get(id=cat_id)
                cat.category_name = cat_name
                cat.save()
                messages.success(request, 'Category updated successfully!')
            except category.DoesNotExist:
                pass  
        else: 
            cat = category(category_name=cat_name)
            cat.save()
            messages.success(request, 'Category created successfully!')
        return redirect('newcategory')  

    return render(request, 'newcategory.html', {'catdetails': cat_details, 'category_to_edit': category_to_edit, 'permissions': permissions})

    
def updatecat(request, id):
    try:
        category_to_edit = get_object_or_404(category, id=id)
        return render(request, 'newcategory.html', {
            'catdetails': category.objects.all(),
            'category_to_edit': category_to_edit,
        })
    except category.DoesNotExist:
        return HttpResponseRedirect(reverse('index'))
   

def deletecat(request,id):
    delcat=category.objects.get(id=id)
    delcat.delete()
    messages.success(request, f'Category deleted successfully.')
    return HttpResponseRedirect(reverse('newcategory'))




def newquiz(request):
    uid = request.session.get('uid')
    user = super_users.objects.get(id=uid)

    categories = category.objects.all()
    subcategories = subcategory.objects.all()
    permissions = request.session.get('permissions', [])
    permissions = sorted(permissions, key=lambda x: x['name'].lower()) if permissions else []

    if request.method == 'POST':
        cat_id = request.POST.get('categoryname')
        addque = request.POST.get('question')
        opt1 = request.POST.get('option1')
        opt2 = request.POST.get('option2')
        opt3 = request.POST.get('option3')
        correctans = request.POST.get('correctAnswer')
        addedby = request.POST.get('addedby')
        sub_id = request.POST.get('subcategory')
        
        # Check if any required fields are missing
        if not cat_id or not addque or not sub_id:
            messages.error(request, 'All fields are required.')
            return render(request, 'newquiz.html', {'categories': categories, 'subcategories': subcategories, 'permissions': permissions, 'user': user})


        selected_category = get_object_or_404(category, id=cat_id)
        selected_subcategory = get_object_or_404(subcategory, id=sub_id)

        # Create and save the new question
        addquiz = questions(
            category_id=selected_category.id, 
            question=addque,
            option1=opt1,
            option2=opt2,
            option3=opt3,
            answer=correctans,
            verify_status=0,  # Assuming verify_status is 0 initially
            added_by=user.id,
            added_on=datetime.now(),
            verified_on=0,  # Assuming verified_on is 0 initially
            subcategory=selected_subcategory
        )
        addquiz.save()
        messages.success(request, 'Question added successfully.')
        return redirect('newquiz')  # Redirect to the same page after success

    return render(request, 'newquiz.html', {'categories': categories, 'subcategories': subcategories, 'permissions': permissions, 'user': user})




def get_subcategories(request):
    cat_id = request.GET.get('category_id')  # Get category ID from the AJAX request
    subcategories = subcategory.objects.filter(categories_id=cat_id)  # Filter subcategories by category ID
    
    # Prepare the response data with subcategory names and ids
    subcategories_data = [{'id': sub.id, 'sub_category': sub.sub_category} for sub in subcategories]
    
    return JsonResponse({'subcategories': subcategories_data})





def newviewquiz(request):
    category_id = request.GET.get('categoryname', '')  
    getq = questions.objects.select_related('category').exclude(verify_status=0)
    current_page = request.GET.get('page', 1)

    permissions = request.session.get('permissions', []) 
    permissions = sorted(permissions, key=lambda x: x['name'].lower()) if permissions else []
    if category_id:
        getq = getq.filter(category_id=category_id)  

    categories = category.objects.all()  

    # Pagination logic
    paginator = Paginator(getq, 20)  # Show 10 questions per page
    # page_number = request.GET.get('page')  # Get the current page number from GET request
    page_obj = paginator.get_page(current_page)  # Get the Page object for the current page

    # Return the context to the template
    return render(request, 'newviewquiz.html', {
        'quizz': page_obj,  # Pass the Page object (which contains the questions for the current page)
        'categories': categories,
        'selected_category': category_id,
        'permissions': permissions,
        'cp':current_page
    })


def deletequiz(request,id):
    delquiz=questions.objects.get(id=id)
    delquiz.delete()
    return HttpResponseRedirect(reverse('newviewquiz')) 


def newupdatequiz(request, id):
    uid = request.session.get('uid')
    user = super_users.objects.get(id=uid)

    categories = category.objects.all()
    quiz1 = questions.objects.get(id=id)

    subcategories = subcategory.objects.filter(categories=quiz1.category)
    question_subcategory = quiz1.subcategory

    # Get the current page number from the request
    current_page = request.GET.get('page', 1)

    if request.method == 'POST':
        qcat = request.POST.get('categoryname')
        try:
            selected_category = category.objects.get(id=qcat)
        except category.DoesNotExist:
            return render(request, 'newupdatequiz.html', {
                'q_id': quiz1,
                'categories': categories,
                'error': "Selected category does not exist.",
                'current_page': current_page  # pass current page back to the form
            })

        subc_id = request.POST.get('subcategory')
        try:
            selected_subcategory = subcategory.objects.get(id=subc_id)
        except subcategory.DoesNotExist:
            return render(request, 'newupdatequiz.html', {
                'q_id': quiz1,
                'categories': categories,
                'error': "Selected subcategory does not exist.",
                'current_page': current_page  # pass current page back to the form
            })

        addque = request.POST.get('question')
        opt1 = request.POST.get('option1')
        opt2 = request.POST.get('option2')
        opt3 = request.POST.get('option3')
        correctans = request.POST.get('correctAnswer')
        updatedby = request.POST.get('updatedby')

        quiz1.category = selected_category
        quiz1.subcategory = selected_subcategory
        quiz1.question = addque
        quiz1.option1 = opt1
        quiz1.option2 = opt2
        quiz1.option3 = opt3
        quiz1.answer = correctans

        quiz1.save()

        quizedit = quizedits(
            q_no=quiz1,
            updatedby=user.id,
            added_on=timezone.now(),
        )
        quizedit.save()

        messages.success(request, f'Question updated successfully.')

        # Redirect to the same page after update, using the page query parameter
        return HttpResponseRedirect(f'?categoryname={request.GET.get("categoryname", "")}&page={current_page}')
    
    return render(request, 'newupdatequiz.html', {
        'q_id': quiz1,
        'categories': categories,
        'subcategories': subcategories,
        'user': user,
        'question_subcategory': question_subcategory,
        'current_page': current_page  # pass current page back to the form
    })




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


def register_users(request):
    categories = category.objects.all()  
    permissions = request.session.get('permissions', [])
    permissions = sorted(permissions, key=lambda x: x['name'].lower()) if permissions else []
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        ucategory = request.POST.get('category') 
        password = request.POST.get('password') 
        addedon = timezone.now()
        addedby = 1
        print(ucategory)

       
        selected_category = category.objects.get(id=ucategory)
        print(selected_category)
        
        registuser.objects.create(
            name=name,
            email=email,
            phone=phone,
            categoryd=selected_category,
            password=password,
            added_on=addedon,
            added_by=addedby
        )
        messages.success(request, 'User registered successfully!')
        return redirect('register_users')
    return render(request,'register_users.html', {'categories': categories, 'permissions': permissions})


def viewregister(request):
    from_date = request.GET.get('from')
    to_date = request.GET.get('to_date')
    no_results = False
    permissions = request.session.get('permissions', [])
    permissions = sorted(permissions, key=lambda x: x['name'].lower()) if permissions else []

    if from_date and to_date:
        from_date = timezone.datetime.strptime(from_date, '%Y-%m-%d')
        to_date = timezone.datetime.strptime(to_date, '%Y-%m-%d')

        getr = registuser.objects.filter(added_on__gte=from_date, added_on__lte=to_date)
        if not getr.exists():
            no_results = True 
    else:
        getr = registuser.objects.all()

    return render(request, 'viewregister.html', {'details': getr, 'no_results': no_results, 'permissions': permissions})
def deleteuser(request,id):
    deluser=registuser.objects.get(id=id)
    deluser.delete()
    return HttpResponseRedirect(reverse('viewregister')) 




def updateuser(request, id):
    categories = category.objects.all()
    user1 = registuser.objects.get(id=id)

    if request.method == 'POST':
        ucat = request.POST.get('category')
        try:
            selected_category = category.objects.get(id=ucat)
        except category.DoesNotExist:
            return render(request, 'updateregister.html', {
                'u_id': user1,
                'categories': categories,
                'error': "Selected category does not exist."
            })

        user1.categoryd = selected_category
        user1.name = request.POST.get('name')
        user1.email = request.POST.get('email')
        user1.phone = request.POST.get('phone')
        user1.password = request.POST.get('password')
        user1.save()

        messages.success(request, "User updated successfully.")
        
        return redirect('viewregister')

    return render(request, 'updateregister.html', {'u_id': user1, 'categories': categories})


    


def login(request):
    if request.method == 'POST':
        username = request.POST.get('uname')
        password = request.POST.get('password')
        # roles = request.POST.get('roles')

        try:
            user = super_users.objects.get(username=username, password=password)

            request.session['uid'] = user.id
            request.session['role_id'] = user.roles.id 
            request.session['role_name'] = user.roles.role_name  
            request.session['permissions'] = [
                {'name': permission.permissions.permissions, 'url': permission.permissions.page_url, 'icon':permission.permissions.url_icon}
                for permission in role_permission.objects.filter(roles=user.roles)
            ]  

            return redirect('index')  

        except super_users.DoesNotExist:
            context = {'error': 'Invalid credentials. Please try again.'}
            return render(request, 'login.html', context)

    roles_list = role.objects.all()  
    return render(request, 'login.html', {'roles_list': roles_list})



def profile(request):
    uid = request.session.get('uid')
    permissions = request.session.get('permissions', [])
    permissions = sorted(permissions, key=lambda x: x['name'].lower()) if permissions else []
    
    if uid:
        user = get_object_or_404(super_users, id=uid) 
        return render(request, 'profile.html', {'users': [user],'permissions':permissions}) 
    else:
        return redirect('index')



    



def adminlogout(request):
    logout(request)
    return redirect('login')



#scheduling exam in add_exam
def schedule_exam(request):
    users = registuser.objects.all()  
    categories = category.objects.all()
    permissions = request.session.get('permissions', [])
    permissions = sorted(permissions, key=lambda x: x['name'].lower()) if permissions else []
    

    if request.method == 'POST':
       
        user_id = request.POST.get('userid')
        no_q = request.POST.get('question_count')
        doa = request.POST.get('testdate')
        toa = request.POST.get('test_time')
        category_id = request.POST.get('categoryid')  

       
        if not user_id or not no_q or not doa or not toa or not category_id:
            return render(request, 'schedule_exam.html', {
                'users': users,
                'categories': categories,
                'error': "All fields are required."
            })

        try:
           
            user_instance = registuser.objects.get(id=user_id)
            category_instance = category.objects.get(id=category_id)  

           
            add_exam.objects.create(
                userd=user_instance,  
                no_of_questions=no_q,
                date_of_test=doa,
                time_of_test=toa
            )

            questions_in_category = questions.objects.filter(category_id=category_id)

           
            return render(request, 'questions_page.html', {
                'user_id': user_id, 
                'category_id': category_id, 
                'question_count': no_q,
                'exam_date': doa,
                'exam_time': toa,
                'user_name': user_instance.name,
                'category_name': category_instance.category_name,
                'questions': questions_in_category, 
                'permissions': permissions,
            })

        except registuser.DoesNotExist:
            return render(request, 'schedule_exam.html', {
                'users': users,
                'categories': categories,
                'error': "User not found."
            })

    return render(request, 'schedule_exam.html', {
        'users': users,
        'categories': categories,
        'permissions': permissions,

    })


#scheduling exam with selected questions in schedulexam
def submit_selected_questions(request):
    if request.method == 'POST':
       
        user_id = request.POST.get('user_id')
        category_id = request.POST.get('category_id')
        add_id = request.POST.get('add_id') 
        selected_questions = request.POST.getlist('selected_questions') 
        permissions = request.session.get('permissions', [])
 

        if not selected_questions:
            
            return redirect('questions_page', user_id=user_id, category_id=category_id)
 
        last_exam = add_exam.objects.filter(userd=user_id).order_by('-id').first()

        if not last_exam:
           
            return redirect('schedule_exam')

        add_id = last_exam.id

        for question_id in selected_questions:
            question = questions.objects.get(id=question_id) 
            schedulexam.objects.create(
                questiond=question,
                add_id=add_id  
            )
   
        return redirect('index')
    return redirect('schedule_exam')


def attempted_quiz(request, user_id):
    user= registuser.objects.get(id=user_id)
    permissions = request.session.get('permissions', [])
    permissions = sorted(permissions, key=lambda x: x['name'].lower()) if permissions else []

    category_name=user.categoryd.category_name
    
    attempts=attempt.objects.filter(user_id=user_id)

    demo_tests=attempts.filter(add_id=1)
    mock_tests=attempts.filter(add_id=2)
    # aptitude_tests=attempts.exclude(add_id__in=[1, 2])
    aptitude_tests = assigned_attempt.objects.filter(user_id=user_id)

    context = {
        'user': user,
        'category_name': category_name, 
        'demo_tests': demo_tests,
        'mock_tests': mock_tests,
        'aptitude_tests': aptitude_tests,
        'permissions': permissions,
    }

    return render(request, 'attempted_quiz.html', context)




def aptitude_details(request, attempt_id):
    
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
  
    return render(request, 'aptitude_details.html', {
        'details': details,
        'attempt': attempt_instance,
        'user': user_instance,
        'category': category_instance
    })
 

def attempted_result(request, attempt_id):
    
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
  
    return render(request, 'attempted_result.html', {
        'details': details,
        'attempt': attempt_instance,
        'user': user_instance,
        'category': category_instance
    })


def permissions(request):
    # per_details = permission.objects.all()
    per_details = permission.objects.all().order_by('permissions')
    permissions_to_edit = None 
    permissions = request.session.get('permissions', [])
    permissions = sorted(permissions, key=lambda x: x['name'].lower()) if permissions else []

   
    if request.method == 'POST':
        per_name = request.POST.get('permissions')
        per_id = request.POST.get('permission_id')
        p_url = request.POST.get('pageurl')
        p_icon = request.POST.get('urlicon')

        if per_id: 
            try:
                perm = permission.objects.get(id=per_id)
                perm.permissions = per_name
                perm.page_url = p_url
                perm.url_icon = p_icon
                perm.save()
                messages.success(request, 'Permissions updated successfully!')
            except permission.DoesNotExist:
                pass  
        else: 
            perm = permission(permissions=per_name,page_url=p_url,url_icon=p_icon)
            perm.save()
            messages.success(request, 'Permissions created successfully!')
        return redirect('permission')  
    
    return render(request, 'permission.html',{'perdetails':per_details, 'permissions_to_edit': permissions_to_edit,'permissions': permissions,})

def updatepermit(request, id):
    try:
        permissions_to_edit = get_object_or_404(permission, id=id)
        return render(request, 'permission.html', {
            'perdetails': permission.objects.all(),
            'permissions_to_edit': permissions_to_edit,
        })
    except permission.DoesNotExist:
        return HttpResponseRedirect(reverse('index'))
   

def deletepermit(request,id):
    delcat=permission.objects.get(id=id)
    delcat.delete()
    messages.success(request,"Permission deleted successfully.")
    return HttpResponseRedirect(reverse('permission'))




def roles(request):
    permissions1 = permission.objects.all()  
    if request.method == 'POST':
       
        role_name_instance = request.POST.get('role_name')
        permiss = request.POST.getlist('permissions') 
  
        permissions = request.session.get('permissions', [])
        permissions = sorted(permissions, key=lambda x: x['name'].lower()) if permissions else []

        if not role_name_instance or not permiss:
            messages.error(request, 'Role name and permissions are required.')
            return redirect('roles')

        role_instance = role.objects.create(role_name=role_name_instance)

        for permission_id in permiss:
            try:
                permission_instance = permission.objects.get(id=permission_id)
                role_permission.objects.create(roles=role_instance, permissions=permission_instance)
            except permission.DoesNotExist:
                messages.error(request, f"Permission with ID {permission_id} does not exist.")
                return redirect('roles')

        messages.success(request, 'Role and permissions added successfully!')
        return redirect('roles')

    permissions = request.session.get('permissions', [])  
    permissions = sorted(permissions, key=lambda x: x['name'].lower()) if permissions else []

    return render(request, 'role.html', {
        'permissions1': permissions1,
        'permissions': permissions
    })

def view_roles(request):
    roles = role.objects.all()
    role_permissions = []
    permissions = request.session.get('permissions', [])
    permissions = sorted(permissions, key=lambda x: x['name'].lower()) if permissions else []

    for r in roles:
    
        permissions1 = role_permission.objects.filter(roles=r)

        permission_list = [perm.permissions.permissions for perm in permissions1]

        role_permissions.append({
            'role_name': r.role_name,
            'permissions': permission_list,
            'id': r.id 
        })

    return render(request, 'view_roles.html', {'role_permissions': role_permissions,'permissions': permissions})



def update_role(request, role_id):
    roles_to_edit = get_object_or_404(role, id=role_id)
    permissions1 = permission.objects.all()

    role_permissions = role_permission.objects.filter(roles=roles_to_edit).values_list('permissions', flat=True)
    role_permissions = permission.objects.filter(id__in=role_permissions)

    if request.method == 'POST':
        role_name = request.POST.get('role_name')
        permissions_selected = request.POST.getlist('permissions')

        roles_to_edit.role_name = role_name
        roles_to_edit.save()

        role_permission.objects.filter(roles=roles_to_edit).delete()
        for permission_id in permissions_selected:
            perm = permission.objects.get(id=permission_id)
            role_permission.objects.create(roles=roles_to_edit, permissions=perm)

        messages.success(request, 'Role and permissions updated successfully!')
        return redirect('view_roles')

    return render(request, 'update_role.html', {
        'roles_to_edit': roles_to_edit,
        'permissions1': permissions1,
        'role_permissions': role_permissions, 
    })

def delete_role(request, role_id):
    role_to_delete = get_object_or_404(role, id=role_id)
    role_to_delete.delete()
    messages.success(request, f'Role "{role_to_delete.role_name}" deleted successfully.')
    return redirect('view_roles')

def super_check_email(request):
    if request.method == "GET":
        email = request.GET.get('email', None)
        
        if email:
            if super_users.objects.filter(email=email).exists():
                return JsonResponse({'exists': True})  
            else:
                return JsonResponse({'exists': False})  
        else:
            return JsonResponse({'error': 'No email provided'}, status=400) 

    
def superusers(request):
    roled = role.objects.all()  
    permissions = request.session.get('permissions', [])
    permissions = sorted(permissions, key=lambda x: x['name'].lower()) if permissions else []

    if request.method == "POST":
        name = request.POST.get('name')
        gender = request.POST.get('gender')
        dob = request.POST.get('dob')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        srole = request.POST.get('roles') 
        uname = request.POST.get('uname')
        password = request.POST.get('password') 
 
        selected_roles = role.objects.get(id=srole)
        print(selected_roles)
        
        super_users.objects.create(
            name=name,
            gender=gender,
            date_of_birth=dob,
            email=email,
            phone=phone,
            roles=selected_roles,
            password=password,
            username=uname,
            
        )
        messages.success(request, 'User registered successfully!')
        return redirect('superusers')
    return render(request,'super_users.html', {'roled': roled,'permissions': permissions,})

def organisations(request):
    permissions = request.session.get('permissions', [])
    permissions = sorted(permissions, key=lambda x: x['name'].lower()) if permissions else []

    role_filter = request.GET.get('role', None)

    if role_filter:

        individuals = super_users.objects.filter(gender__in=['female', 'male', 'others', 'prefer_not_to_say'], roles__role_name=role_filter)
        organizations = super_users.objects.filter(gender='organisation', roles__role_name=role_filter)
    else:
        individuals =super_users.objects.filter(gender__in=['female', 'male', 'others', 'prefer_not_to_say'])
        organizations = super_users.objects.filter(gender='organisation')

    roles = super_users.objects.values('roles__role_name').distinct()

    return render(request, 'organisations.html', {
        'individuals': individuals,
        'organizations': organizations,
        'roles': roles,
        'permissions': permissions,
    })




def view_superusers(request):
    permissions = request.session.get('permissions', [])
    permissions = sorted(permissions, key=lambda x: x['name'].lower()) if permissions else []

    role_filter = request.GET.get('role', None)

    if role_filter:

        individuals = super_users.objects.filter(gender__in=['female', 'male', 'others', 'prefer_not_to_say'], roles__role_name=role_filter)
        organizations = super_users.objects.filter(gender='organisation', roles__role_name=role_filter)
    else:
        individuals =super_users.objects.filter(gender__in=['female', 'male', 'others', 'prefer_not_to_say'])
        organizations = super_users.objects.filter(gender='organisation')

    roles = super_users.objects.values('roles__role_name').distinct()

    return render(request, 'view_superusers.html', {
        'individuals': individuals,
        'organizations': organizations,
        'roles': roles,
        'permissions': permissions,
    })


def update_superusers(request,id):
    roles = role.objects.all()
    superuser = super_users.objects.get(id=id)
    if request.method == 'POST':
        srole = request.POST.get('roles')
        try:
            selected_role = role.objects.get(id=srole)
        except role.DoesNotExist:
            return redirect (request,'update_superusers.html',{
                'super':superuser,
                'roles':roles,
            })
        superuser.roles = selected_role
        superuser.name = request.POST.get('name')
        superuser.gender = request.POST.get('gender')
        superuser.date_of_birth = request.POST.get('dob')
        superuser.phone = request.POST.get('phone')
        superuser.email = request.POST.get('email')
        superuser.username = request.POST.get('uname')
        superuser.password = request.POST.get('password')
        superuser.save()
        messages.success(request, 'User updated successfully!')
        return redirect('view_superusers')
    return render(request,'update_superusers.html',{'super':superuser,'roles':roles})

def delete_superuser(request, id):
    delsuper = get_object_or_404(super_users, id=id) 
    delsuper.delete()
    messages.success(request, f'User "{delsuper.name}" deleted successfully.')
    return redirect('view_superusers')

def update_organisations(request,id):
    roles = role.objects.all()
    superusers = super_users.objects.get(id=id)
    if request.method == 'POST':
        srole = request.POST.get('roles')
        try:
            selected_role = role.objects.get(id=srole)
        except role.DoesNotExist:
            return redirect (request,'update_organisations.html',{
                'super':superusers,
                'roles':roles,
            })
        superusers.roles = selected_role
        superusers.name = request.POST.get('name')
        superusers.gender = request.POST.get('gender')
        superusers.date_of_birth = request.POST.get('dob')
        superusers.phone = request.POST.get('phone')
        superusers.email = request.POST.get('email')
        superusers.username = request.POST.get('uname')
        superusers.password = request.POST.get('password')
        superusers.save()
        messages.success(request, 'User updated successfully!')
        return redirect('organisations')
    return render(request,'update_organisations.html',{'super':superusers,'roles':roles})

def delete_organisations(request,id):
    delsuper = get_object_or_404(super_users, id=id) 
    delsuper.delete()
    messages.success(request, f'User "{delsuper.name}" deleted successfully.')
    return redirect('organisations')

 



def verify_quiz(request):
    uid = request.session.get('uid')
    user = super_users.objects.get(id=uid)
    selected_category_id = request.GET.get('categoryname', None)
    permissions = request.session.get('permissions', [])
    permissions = sorted(permissions, key=lambda x: x['name'].lower()) if permissions else []

    # Filter the questions based on the selected category
    if selected_category_id:
        quizz = questions.objects.filter(verify_status=0, category_id=selected_category_id)
        selected_category = category.objects.get(id=selected_category_id)
    else:
        quizz = questions.objects.filter(verify_status=0)
        selected_category = None

    # Apply pagination
    paginator = Paginator(quizz, 20)  # Show 10 questions per page
    page_number = request.GET.get('page')  # Get the current page number from GET request
    page_obj = paginator.get_page(page_number)  # Get the Page object for the current page

    categories = category.objects.all()

    # Return the context to the template
    return render(request, 'verify_quiz.html', {
        'quizz': page_obj,  # Pass the Page object, which contains the questions for the current page
        'categories': categories,
        'selected_category': selected_category,
        'permissions': permissions,
        'user': user
    })



def verify_question(request, question_id):
    uid = request.session.get('uid')
    user = super_users.objects.get(id=uid)
    
    if request.method == 'POST':
        try:
            question = questions.objects.get(id=question_id)

            question.verify_status = user.id
            question.verified_on = datetime.now()
            question.save()
            messages.success(request, 'Successfully verified the question.')
            return redirect('verify_quiz')  

        except questions.DoesNotExist:

            return HttpResponse("Question not found", status=404)

    return redirect('verify_quiz')   


def verify_delete(request,id):
    delquiz=questions.objects.get(id=id)
    delquiz.delete()
    messages.success(request, f'Question deleted successfully.')
    return HttpResponseRedirect(reverse('verify_quiz')) 


def verify_update(request, id):
    uid = request.session.get('uid')
    user = super_users.objects.get(id=uid)

    categories = category.objects.all()
    quiz1 = questions.objects.get(id=id)

    subcategories = subcategory.objects.filter(categories=quiz1.category)
    question_subcategory = quiz1.subcategory 

    if request.method == 'POST':
        qcat = request.POST.get('categoryname')
        try:
            selected_category = category.objects.get(id=qcat)
        except category.DoesNotExist:
            return render(request, 'newupdatequiz.html', {
                'q_id': quiz1,
                'categories': categories,
                'error': "Selected category does not exist."
            })
        subc_id = request.POST.get('subcategory')  
        try:
            selected_subcategory = subcategory.objects.get(id=subc_id)  
        except subcategory.DoesNotExist:
            return render(request, 'newupdatequiz.html', {
                'q_id': quiz1,
                'categories': categories,
                'error': "Selected subcategory does not exist."
            })
        addque = request.POST.get('question')
        opt1 = request.POST.get('option1')
        opt2 = request.POST.get('option2')
        opt3 = request.POST.get('option3')
        correctans = request.POST.get('correctAnswer')
        updatedby = request.POST.get('updatedby')

        
        quiz1.category = selected_category
        quiz1.subcategory = selected_subcategory 
        quiz1.question = addque
        quiz1.option1 = opt1
        quiz1.option2 = opt2
        quiz1.option3 = opt3
        quiz1.answer = correctans
        quiz1.verified_on = 0 
        quiz1.save()

        quizedit = quizedits(
            q_no=quiz1, 
            updatedby=user.id, 
            added_on=timezone.now(),
        )
        quizedit.save()

        messages.success(request, f'Question updated successfully.')
        return redirect('verify_quiz')

    return render(request, 'verify_update.html', {
        'q_id': quiz1,
        'categories': categories,
        'subcategories': subcategories, 
        'user': user,
        'question_subcategory': question_subcategory
    })



def get_subcategories_by_category(request):
    category_id = request.GET.get('category_id')
    
    if not category_id:
        return JsonResponse({'error': 'No category_id provided'}, status=400)
    try: 
        selected_category = category.objects.get(id=category_id)
        
        subcategories = subcategory.objects.filter(categories=selected_category)  

        subcategory_data = [{'id': sub.id, 'sub_category': sub.sub_category} for sub in subcategories]

        return JsonResponse({'subcategories': subcategory_data})

    except category.DoesNotExist:
        return JsonResponse({'error': 'Category not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': f'Error retrieving subcategories: {str(e)}'}, status=500)


def subcategories(request):
    categories1 = category.objects.all()  
    permissions = request.session.get('permissions', [])
    permissions = sorted(permissions, key=lambda x: x['name'].lower()) if permissions else []
    if request.method == "POST":
        ucategory = request.POST.get('category') 
        subc = request.POST.get('subcategory') 
        print(ucategory)

       
        selected_category = category.objects.get(id=ucategory)
        print(selected_category)
        
        subcategory.objects.create(
           
            categories=selected_category,
            sub_category=subc
            
        )
        messages.success(request, 'Subcategories added successfully!')
        return redirect('subcategories')
    return render(request,'subcategory.html', {'categories1': categories1, 'permissions': permissions})
   
def view_subcategory(request):
    permissions = request.session.get('permissions', [])
    permissions = sorted(permissions, key=lambda x: x['name'].lower()) if permissions else []
    categories = category.objects.all()

  
    selected_category_id = request.GET.get('categoryname')

    if selected_category_id:
   
        selected_category = category.objects.get(id=selected_category_id)
        getsub = subcategory.objects.filter(categories=selected_category)
    else:
       
        getsub = subcategory.objects.all()
        selected_category = None

    return render(request, 'view_subcategory.html', {
        'getsub': getsub,
        'permissions': permissions,
        'categories': categories,
        'selected_category': selected_category,
    })


def update_subcat(request,id):
    cat = category.objects.all()
    sub = subcategory.objects.get(id=id)
    if request.method == 'POST':
        cats = request.POST.get('category')
        try:
            selected_cate = category.objects.get(id=cats)
        except category.DoesNotExist:
            return redirect (request,'update_subcat.html',{
                'sub':sub,
                'cat':cat,
            })
        sub.categories = selected_cate 
        sub.sub_category = request.POST.get('subcategory')
    
        sub.save()
        messages.success(request, 'Subcategory updated successfully!')
        return redirect('view_subcategory')
    return render(request,'update_subcat.html',{'sub':sub,'cat':cat})

def delete_subcat(request,id):
    delsub = get_object_or_404(subcategory, id=id) 
    delsub.delete()
    messages.success(request, f' "{delsub.sub_category}" deleted successfully.')
    return redirect('view_subcategory')

def viewlog(request, question_id):
    question = get_object_or_404(questions, pk=question_id)
    question.verified_user = super_users.objects.filter(id=question.verify_status).first()
    
    if question.verified_user:
        
        if question.verified_user.roles:
            question.verified_user_role = question.verified_user.roles.role_name
        else:
            question.verified_user_role = "No Role Assigned"
    else:
        question.verified_user_role = "Unknown Role"

    question.added_user = super_users.objects.filter(id=question.added_by).first()

    if question.added_user:
        
        if question.added_user.roles:
            question.added_user_role = question.added_user.roles.role_name
        else:
            question.added_user_role = "No Role Assigned"
    else:
        question.added_user_role = "Unknown Role"

    quiz_edits = quizedits.objects.filter(q_no=question_id)
 
    for edit in quiz_edits:
        edit.updated_by_user = super_users.objects.filter(id=edit.updatedby).first()
        if edit.updated_by_user:

            if edit.updated_by_user.roles:
                edit.updated_by_user_role = edit.updated_by_user.roles.role_name
            else:
                edit.updated_by_user = "No Role Assigned"
        else:
            edit.updated_by_user = "Unknown Role"
        

    return render(request, 'viewlog.html', {'question': question, 'quiz_edits': quiz_edits})



def create_exam(request):
    print(f"URL Accessed: {request.path}")

    uid = request.session.get('uid')
    user = super_users.objects.get(id=uid)
    categories = category.objects.all()
    permissions = request.session.get('permissions', [])
    permissions = sorted(permissions, key=lambda x: x['name'].lower()) if permissions else []

    employer_role = role.objects.get(role_name="Employer")

    # Fetch all users with the "Employer" role
    employer_users = super_users.objects.filter(roles=employer_role)

    if request.method == 'POST':
        cat_id = request.POST.get('categoryname')
        c_for = request.POST.get('createdfor')
        sub_ids = request.POST.getlist('subcategories')
        no_ques = request.POST.get('question_count')
        timelimit = request.POST.get('timelimit')
        percentage = request.POST.get('percentage')

        try:
            selected_category = category.objects.get(id=cat_id)
        except category.DoesNotExist:
            messages.error(request, "Selected category not found.")
            return redirect('create_exam')

        subcategory_ids = ','.join(sub_ids)

        create = create_examid(
            catid=selected_category,
            no_questions=no_ques,
            created_for=c_for,
            created_by=user.id,
            created_on=datetime.now(),
            allowed_time=timelimit,
            subcat=subcategory_ids,
            percentage_to_pass=percentage
        )
        create.save()

        return redirect('create_questions', exam_id=create.id)
        

    return render(request, 'create_exam.html', {
        'categories': categories,
        'permissions': permissions,
        'user': user,
        'employer_users':employer_users
        
    })  

def create_questions(request, exam_id):
    try:
        exam = create_examid.objects.get(id=exam_id)
    except create_examid.DoesNotExist:
        messages.error(request, "Exam not found.")
        return redirect('create_exam')

    selected_category = exam.catid
    subcategory_ids = exam.subcat.split(',')  

    question = questions.objects.filter(
        category=selected_category
    ).filter(
        subcategory__in=subcategory_ids
    )
    question_count = exam.no_questions

    if request.method == 'POST':
       
        selected_questions = request.POST.getlist('selected_questions')

        if not selected_questions:
            messages.error(request, "Please select at least one question.")
            return redirect('create_questions', exam_id=exam_id)

        
        for q_id in selected_questions:
            question_obj = questions.objects.get(id=q_id)
            exam_question = exam_questions(
                question=question_obj,
                exam_id=exam_id
            )
            exam_question.save()

        messages.success(request, "Exam created successfully.")
        return redirect('create_exam') 

    return render(request, 'create_questions.html', {
        'exam_id': exam_id,  
        'category_name': selected_category.category_name,
        'questions': question,
        'question_count':question_count 
        
    })



def view_exams(request):
    permissions = request.session.get('permissions', [])
    permissions = sorted(permissions, key=lambda x: x['name'].lower()) if permissions else []
    catid = category.objects.all()

    selected_category_id = request.GET.get('categoryname')

    if selected_category_id:
        selected_category = category.objects.get(id=selected_category_id)
        getexam = create_examid.objects.filter(catid=selected_category)
    else:
        getexam = create_examid.objects.all()
        selected_category = None

    for exam in getexam:
        subcategory_ids = [id for id in exam.subcat.split(',') if id.isdigit()]
        if subcategory_ids:
            subcategory_names = subcategory.objects.filter(id__in=subcategory_ids).values_list('sub_category', flat=True)
            exam.subcategory_names = list(subcategory_names)  
        else:
            exam.subcategory_names = []
    for application in getexam:
        try:
            
            super = super_users.objects.get(id=application.created_for) 
            application.super_name = super.name
              
        except super_users.DoesNotExist:
            application.super_name = None 
            

    return render(request, 'view_exams.html', {
        'getexam': getexam,
        'permissions': permissions,
        'catid': catid,
        'selected_category': selected_category,
    })

def see_exam_questions(request,exam_id):
    ques=questions.objects.all()
    exam = get_object_or_404(create_examid, id=exam_id)

    question = exam_questions.objects.filter(exam_id=exam_id)

    return render(request, 'see_exam_questions.html', {
        'exam': exam,
        'questions': question,
        'ques':ques
    })


def delete_exam(request,id):
    delexam = get_object_or_404(create_examid, id=id) 
    delexam.delete()
    messages.success(request, ' Exam deleted successfully.')
    return redirect('view_exams')


def view_applied_exams(request):
    permissions = request.session.get('permissions', [])
    permissions = sorted(permissions, key=lambda x: x['name'].lower()) if permissions else []
    categories = category.objects.all()
    e_ids = create_examid.objects.all()

    # Get the selected category from the GET request
    selected_category_id = request.GET.get('categoryname')
    exam_id_filter = request.GET.get('exam_id', '')  # Get the exam_id filter value

    # If a category is selected
    if selected_category_id:
        selected_category = category.objects.get(id=selected_category_id)
        getapplied = exam_apply.objects.filter(
            userid__in=registuser.objects.filter(
                categoryd=selected_category
            ).values('id'),
            status=0
        )
    else:
        # If no category is selected, show all exam applications
        getapplied = exam_apply.objects.filter(status=0)
        selected_category = None

    # Apply exam_id filter if it is provided
    if exam_id_filter:
        getapplied = getapplied.filter(exam_id__icontains=exam_id_filter)  # Perform partial matching on exam_id

    # Add user-related information to the applied exams
    for application in getapplied:
        try:
            user = registuser.objects.get(id=application.userid)
            application.user_name = user.name
            application.user_category = user.categoryd.category_name
        except registuser.DoesNotExist:
            application.user_name = None
            application.user_category = None

    # Render the template with the necessary context
    return render(request, 'view_applied_exams.html', {
        'get_applied': getapplied,
        'permissions': permissions,
        'categories': categories,
        'selected_category': selected_category,
        'eids': e_ids,
        'exam_id_filter': exam_id_filter  # Pass the exam_id filter back to the template for re-populating the field
    })



def already_scheduled(request):
    permissions = request.session.get('permissions', [])
    permissions = sorted(permissions, key=lambda x: x['name'].lower()) if permissions else []
    categories = category.objects.all()

    # Get the selected category from the GET request
    selected_category_id = request.GET.get('categoryname')

    if selected_category_id:
        # Get the selected category object
        selected_category = category.objects.get(id=selected_category_id)
        
        # Filter exam_apply entries based on the category of the associated user
        # We're using Q objects to filter by category_name in the registuser table
        getapplied = exam_apply.objects.filter(
            userid__in=registuser.objects.filter(
                categoryd=selected_category
            ).values('id'),
            status=1
        )
    else:
        # If no category is selected, show all exam applications
        getapplied = exam_apply.objects.filter(status=1)
        selected_category = None

    # Add user-related information to the applied exams
    for application in getapplied:
        try:
            user = registuser.objects.get(id=application.userid)
            application.user_name = user.name
            application.user_category = user.categoryd.category_name
        except registuser.DoesNotExist:
            application.user_name = None
            application.user_category = None


    return render(request, 'already_scheduled.html', {
        'get_applied': getapplied,
        'permissions': permissions,
        'categories': categories,
        'selected_category': selected_category,
    })


def delete_application(request,id):
    delapply = get_object_or_404(exam_apply, id=id) 
    delapply.delete()
    messages.success(request, 'Applied exam deleted successfully.')
    return redirect('view_applied_exams')

def assignexam(request, application_id):
    uid = request.session.get('uid')
    super = super_users.objects.get(id=uid)
    application = get_object_or_404(exam_apply, id=application_id)
    exam_id = application.exam_id  
    user = registuser.objects.get(id=application.userid)
    
    user_name = user.name
    user_category = user.categoryd.category_name

   
    if request.method == 'POST':
        test_date = request.POST.get('testdate') 
        test_time = request.POST.get('test_time') 

        # Create and save the assigned exam details
        assigned_exam = assign_exam(
            examid=exam_id,
            applicationid=application.id,
            set_date=test_date,
            set_time=test_time,
            assigned_by=super.id,
            assigned_on=datetime.now()
        )
        assigned_exam.save()

        exam_application = exam_apply.objects.get(id=application_id)
        exam_application.status = 1 
        exam_application.save()
        
        messages.success(request, 'Exam scheduled successfully.')
        return redirect('view_applied_exams') 

    return render(request, 'assign_exam.html', {
        'exam_id': exam_id,
        'application_id': application_id,
        'user_name': user_name,
        'user_category': user_category
    })



def my_questions(request):
    uid = request.session.get('uid')
    print(f"user id: {uid}")
    category_id = request.GET.get('categoryname', '')  
    # getq = questions.objects.select_related('category').exclude(verify_status=0)
    getq =questions.objects.filter(added_by=uid)

    permissions = request.session.get('permissions', []) 
    permissions = sorted(permissions, key=lambda x: x['name'].lower()) if permissions else []
    if category_id:
        getq = getq.filter(category_id=category_id)  

    categories = category.objects.all()  

    return render(request, 'my_questions.html', {
        'quizz': getq,
        'categories': categories,
        'selected_category': category_id,
        'permissions': permissions
    })



def exam_time_slot(request):
    permissions = request.session.get('permissions', [])
    categories = category.objects.all()
    e_ids = create_examid.objects.all()
    admin_id = request.session.get('uid')
    super = super_users.objects.get(id=admin_id)
    print(f"user id: {admin_id}")

    # Get the selected category from the GET request
    selected_category_id = request.GET.get('categoryname')
    exam_id_filter = request.GET.get('exam_id', '')  # Get the exam_id filter value

    # If a category is selected
    if selected_category_id:
        selected_category = category.objects.get(id=selected_category_id)
        getapplied = exam_apply.objects.filter(
            userid__in=registuser.objects.filter(
                categoryd=selected_category
            ).values('id'),
            status=0
        )

    else:
        # If no category is selected, show all exam applications
        getapplied = exam_apply.objects.filter(status=0)
        selected_category = None

    # Apply exam_id filter if it is provided
    if exam_id_filter:
        getapplied = getapplied.filter(exam_id__icontains=exam_id_filter)  # Perform partial matching on exam_id

    # Add user-related information to the applied exams
    for application in getapplied:
        try:
            user = registuser.objects.get(id=application.userid)
            application.user_name = user.name
            application.user_category = user.categoryd.category_name
        except registuser.DoesNotExist:
            application.user_name = None
            application.user_category = None 

    # Handle form submission
    if request.method == 'POST':
        # Get the selected application IDs
        selected_application_ids = request.POST.getlist('selected_application')
        
        # Get the exam date and time from the form
        exam_date = request.POST.get('testdate')
        exam_time = request.POST.get('test_time')

        # Create a new exam_planner entry
        new_planner = exam_planner(
            exam_date=exam_date,
            exam_time=exam_time,
            added_on=datetime.now(),
            added_by=admin_id # Assuming the user is logged in
        )
        new_planner.save()

        exam_apply.objects.filter(id__in=selected_application_ids).update(status=1)


        # Create entries in planner_list for each selected application
        for application_id in selected_application_ids:
            application = exam_apply.objects.get(id=application_id)
            x_id = application.exam_id
            
            planner_list.objects.create(
                planid=new_planner,
                applicationid=application,
                added_on=datetime.now(),
                examid=x_id
            )

        return redirect('exam_time_slot')  # Redirect to the same page after submission

    # Render the template with the necessary context
    return render(request, 'exam_time_slot.html', {
        'get_applied': getapplied,
        'permissions': permissions,
        'categories': categories,
        'selected_category': selected_category,
        'eids': e_ids,
        'exam_id_filter': exam_id_filter  
    })