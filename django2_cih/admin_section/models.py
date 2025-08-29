from django.db import models
from django.utils import timezone

# Create your models here.
class category(models.Model):
    category_name=models.CharField(max_length=100)

class subcategory(models.Model):
    categories = models.ForeignKey('category',on_delete=models.CASCADE)
    sub_category = models.CharField(max_length=100)

class questions(models.Model):
    category = models.ForeignKey(category, on_delete=models.CASCADE)  
    question=models.CharField(max_length=50)
    option1=models.CharField(max_length=50)
    option2=models.CharField(max_length=50)
    option3=models.CharField(max_length=50)
    answer=models.CharField(max_length=50)
    verify_status=models.IntegerField()
    added_by=models.IntegerField()
    added_on=models.DateTimeField()
    verified_on=models.CharField(max_length=100)
    subcategory= models.ForeignKey(subcategory, on_delete=models.CASCADE) 

class registrations(models.Model):
    name=models.CharField(max_length=50)
    email=models.CharField(max_length=50)
    phone=models.CharField(max_length=11)
   

class registuser(models.Model):
    name=models.CharField(max_length=100)
    email=models.CharField(max_length=100)
    phone=models.CharField(max_length=11)
    categoryd=models.ForeignKey(category,on_delete=models.CASCADE)
    password=models.CharField(max_length=100)  
    added_on=models.DateField()
    added_by=models.IntegerField()

class attempt(models.Model):
    user_id = models.IntegerField()
    category = models.CharField(max_length=50)
    score = models.IntegerField()
    add_id = models.IntegerField()

class attemptresult(models.Model):
    attempt = models.ForeignKey(attempt, on_delete=models.CASCADE, related_name='results')
    question = models.ForeignKey(questions, on_delete=models.CASCADE)
    user_ans = models.CharField(max_length=50)  


class add_exam(models.Model):
    userd = models.ForeignKey(registuser,on_delete=models.CASCADE)
    no_of_questions = models.IntegerField()
    date_of_test = models.CharField(max_length=50)
    time_of_test = models.CharField(max_length=50)

class schedulexam(models.Model):
    questiond = models.ForeignKey(questions,on_delete=models.CASCADE)
    add_id = models.IntegerField()

class registadmin(models.Model):
    name = models.CharField(max_length=50)
    username = models.CharField(max_length=50)
    email = models.CharField(max_length=50)
    phone = models.CharField(max_length=11)
    password = models.CharField(max_length=50)
    status = models.IntegerField()

class permission(models.Model):
    permissions=models.CharField(max_length=200)
    page_url=models.CharField(max_length=50)
    url_icon=models.CharField(max_length=50)

class role(models.Model):
    role_name=models.CharField(max_length=100)
    

class super_users(models.Model):
    name=models.CharField(max_length=50)
    gender=models.CharField(max_length=50)
    date_of_birth=models.CharField(max_length=50)
    email=models.CharField(max_length=100)
    phone=models.CharField(max_length=11)
    password=models.CharField(max_length=50)  
    username=models.CharField(max_length=50)
    roles=models.ForeignKey('role', on_delete=models.CASCADE) 

class role_permission(models.Model):
    roles = models.ForeignKey('role', on_delete=models.CASCADE)
    permissions = models.ForeignKey('permission', on_delete=models.CASCADE)



class quizedits(models.Model):
    added_on = models.DateTimeField()
    q_no = models.ForeignKey('questions',on_delete=models.CASCADE)
    updatedby = models.IntegerField()

class create_examid(models.Model):
    created_by=models.IntegerField()
    created_on=models.DateTimeField()
    created_for=models.CharField(max_length=200)
    catid=models.ForeignKey('category',on_delete=models.CASCADE)
    no_questions=models.IntegerField()
    subcat = models.CharField(max_length=200)
    allowed_time = models.CharField(max_length=50)
    percentage_to_pass = models.IntegerField()

class exam_questions(models.Model):
    question = models.ForeignKey(questions,on_delete=models.CASCADE)
    exam_id = models.IntegerField()

class exam_apply(models.Model):
    exam_id = models.IntegerField()
    userid = models.IntegerField()
    applied_time = models.DateTimeField()
    status = models.IntegerField()

class assign_exam(models.Model):
    examid = models.IntegerField()
    applicationid = models.IntegerField()
    set_date = models.DateField()
    set_time = models.TimeField()
    assigned_by = models.IntegerField()
    assigned_on = models.DateTimeField()

class assigned_attempt(models.Model):
    user_id = models.IntegerField()
    examid = models.IntegerField()
    score = models.IntegerField()
    application_id = models.IntegerField()
    submitted_on=models.DateTimeField()
    exam_status = models.IntegerField()

class assigned_attemptresult(models.Model):
    attempt = models.ForeignKey(assigned_attempt, on_delete=models.CASCADE, related_name='results')
    question = models.ForeignKey(questions, on_delete=models.CASCADE)
    user_ans = models.CharField(max_length=50) 

class exam_planner(models.Model):
    exam_date = models.DateField()
    exam_time = models.TimeField()
    added_on = models.DateTimeField()
    added_by = models.IntegerField()

class planner_list(models.Model):
    planid = models.ForeignKey(exam_planner,on_delete=models.CASCADE)
    applicationid =models.ForeignKey(exam_apply, on_delete=models.CASCADE)
    added_on = models.DateTimeField()
    examid = models.IntegerField()

class save_questions(models.Model):
    userid = models.IntegerField()
    question_id =models.IntegerField()
    applicationid =models.ForeignKey(exam_apply,on_delete=models.CASCADE)