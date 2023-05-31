from datetime import datetime, timedelta
from django.db import IntegrityError
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
import socket
from django.contrib.sites.shortcuts import get_current_site
from .models import User
import jwt
from rest_framework import views
from rest_framework_simplejwt.tokens import RefreshToken

from django.contrib.auth.hashers import make_password, check_password

from std_reg import settings
from stu_cou_reg.models import StudentData,CourseData,RegisteredData
from stu_cou_reg.models import User
from django.core.mail import send_mail 
from std_reg.settings import EMAIL_HOST_USER 
from django.urls import reverse 

from django.http import HttpResponse 
from django.template import loader
from django.shortcuts import redirect, render

# def course_reg_page(request):
#     return render(request,'course_reg.html')

def stu_profile_page(request):
    return render(request,'std_profile.html')

def admin_portal_page(request):
    return render(request,'admin_port.html')

# def admin_portal_std_page(request):
#     return render(request,'admin_port_std.html')

def admin_portal_course_page(request):
    return render(request,'admin_port_course.html')

def admin_portal_approval_page(request):
    return render(request,'admin_port_approval.html')

is_active_verify = False


#student signup
def student_signup_form(request):
    try:
        if request.user.is_authenticated:
           return redirect('stu_profile_page')
        else:
            if request.method == 'POST':
                first_name = request.POST['first_name']
                last_name = request.POST['last_name']
                username = request.POST['username']
                email = request.POST['email']
                password = request.POST['password']
                image=request.FILES['image']
                print('image=',image)
                message1 = 0 #this will be popped when repeated email is used
                message2 = 0 #this will be popped when user created and asked to verify email (student_login page)
                exists = User.objects.filter(email=email)
                print('user data=',exists)
                if not exists :
                    user = User.objects.create_user( username = username, email=email, password=password, is_active = is_active_verify , first_name = first_name, last_name=last_name )
                    user.save();
                    student_data = StudentData.objects.create(user=user , student_image=image)
                    student_data.save();
                    print('data received')
                    s_id_data = StudentData.objects.filter( user=user ).first()
                    s_id = s_id_data.student_id
                    print(s_id)
                    reg_id = "UNI"+ str(s_id)
                    s_id_data.stu_reg_id = reg_id
                    s_id_data.save()
                    print(s_id_data.stu_reg_id)
                    user_email = User.objects.get(email=email)
                    token = RefreshToken.for_user(user_email).access_token
                    token.set_exp(lifetime=timedelta(days=36500))
                    current_site = get_current_site(request).domain
                    relativeLink = reverse('email_verify')
                    Email = email
                    absUrl = 'http://' + current_site + relativeLink + "?token=" + str(token)
                    Subject = " Hello " + "Verification pending"
                    Message = "Click below link to activate your account \n " + absUrl + "\n Your Student ID is \t" + str(s_id_data.stu_reg_id)  +"\n login with this id"
                    send_mail(Subject, Message, EMAIL_HOST_USER, [Email])
                    print('pass1')
                    print(absUrl)
                    message2 = 1
                    return render(request, 'std_login.html', { 'message2' : message2 })
                else :
                    message1 = 1
                    return render(request,'std_signup.html',{'message1' : message1 })
    except IntegrityError:
        print('pass2')
        return render(request, 'std_signup.html', { 'integrityerror': "These is some error please try again" })
    print('pass3')
    return render(request, 'std_signup.html.html', { 'error' :  "error" })

class VerifyEmail(views.APIView):
    def get(self, request):
        token = request.GET.get('token')
        print('token=', token)
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            print(payload)

            user = User.objects.get(id=payload['user_id'])
            print(user)
            if not user.is_active:
                user.is_active = True
                user.save()

            return render(request, 'email_verify.html')
        except jwt.ExpiredSignatureError as identifier:
            return render(request, 'email_verify.html')

#student login
def student_login_form(request):
    if request.method == 'POST':
        stu_reg_id = request.POST["student_id"]
        password = request.POST["password"]
        incorrect_credentials = 0
        stu_data = StudentData.objects.filter( stu_reg_id = stu_reg_id ).first()
        print(stu_data)
        print(stu_data.user_id)
        user_id = int(stu_data.user_id)   
        print(user_id)
        stu_user_data = User.objects.filter( id= user_id ).first()        
        print(stu_user_data.username)
        username = str(stu_user_data.username)
        print(username,password)
        user = authenticate( username = username, password = password)
        print(user)
        print('001')
        if User.objects.filter( username = username ).exists():
            print('002')
            if  User.is_active == True :
                is_active_verify = True
                print('003')
                login(request, user)
                print('logged in after 003')
                return render(request, 'std_profile.html')
            else :
                # print('004')
                # is_active_verify = False
                # login(request, user)
                # print('logged in after 004')
                # return render(request, 'home.html', {'is_active': is_active_verify})
                if user:
                    print('004')
                    is_active_verify = False
                    login(request, user)
                    print('logged in after 004')
                    return render(request, 'std_profile.html', {'user': User.objects.filter(id= user_id), 'std' : StudentData.objects.filter( user_id = user_id ), 'cou' : CourseData.objects.all(), 'reg' : RegisteredData.objects.filter( student_id_id = stu_data.student_id ) })
                else:
                    print('005')
                    error = 1
                    return render(request, 'std_login.html', {'error': error})
        else:
            incorrect_credentials = 1
            return render(request,'std_login.html', {'incorrect' : incorrect_credentials})

#student logout
def student_logout(request):
    print('logout1')
    logout(request)
    print("logout2")
    return render(request,'std_login.html',{ 'logged_out' : "Logged out successfully"})


#edit student profile
def edit_student_profile_click(request):
    if request.method == 'POST':
        print("pass edit 1")
        stu_reg_id = request.POST["student_id_pre"]
        stu_data_pre = StudentData.objects.filter( stu_reg_id = stu_reg_id ).first()
        print(stu_data_pre)
        print(stu_data_pre.user_id)
        user_id = int(stu_data_pre.user_id)
        return render(request,'edit_student_profile.html',{'user': User.objects.filter(id= user_id), 'std' : StudentData.objects.filter( user_id = user_id )})

def edit_student_profile(request):
    if request.method == 'POST':
        stu_reg_id = request.POST["student_id_pre_2"]
        stu_data_pre_2 = StudentData.objects.filter( stu_reg_id = stu_reg_id ).first()
        print('PASS 1')
        print(stu_data_pre_2)
        stu_user_id = stu_data_pre_2.user_id
        user = User.objects.filter( id = stu_user_id ).first()
        if 'edit' in request.POST:
            print('PASS 2')
            print(user)
            print(user.first_name)
            print(user.last_name)
            user.first_name = request.POST["student_first_name_pre_2"]
            user.last_name = request.POST["student_last_name_pre_2"]
            user.save();
            print("new",user.first_name)
            print("new",user.last_name)
            return render(request, 'std_profile.html', {'user': User.objects.filter( id = stu_user_id ), 'std' : StudentData.objects.filter( user_id = stu_user_id ), 'cou' : CourseData.objects.all(), 'reg' : RegisteredData.objects.filter( student_id_id = stu_data_pre_2.student_id ) })
        elif 'back' in request.POST:
            return render(request, 'std_profile.html', {'user': User.objects.filter( id = stu_user_id ), 'std' : StudentData.objects.filter( user_id = stu_user_id ), 'cou' : CourseData.objects.all(), 'reg' : RegisteredData.objects.filter( student_id_id = stu_data_pre_2.student_id )  })
        elif 'change_password' in request.POST:
            return render(request, 'std_change_pass.html', {'user': User.objects.filter( id = stu_user_id ), 'std' : StudentData.objects.filter( user_id = stu_user_id ), 'cou' : CourseData.objects.all() })
    else:
        return render(request,'edit_student_profile.html')

def stu_change_pass(request):
    if request.method == 'POST':
        stu_reg_id = request.POST["student_id_pre_3"]
        stu_data_pre_3 = StudentData.objects.filter( stu_reg_id = stu_reg_id ).first()
        stu_user_id = stu_data_pre_3.user_id
        user = User.objects.filter( id = stu_user_id ).first()
        print(user,'password didnt changed yet')
        if 'change_password' in request.POST:
            print('entered change pass conditoin')
            current_password = request.POST["current_password"]
            print(current_password)
            print(user.password)
            checkpassword = check_password(current_password, user.password)
            print(checkpassword)
            if checkpassword == True :
                print('checked old pass')
                new_password = request.POST["new_password"]
                new_password2 = request.POST["new_password_2"]
                if new_password == new_password2 :
                    print('entered into new pass condition')
                    user.set_password(new_password)
                    user.save();
                    stu_data_pre_3.save();
                    print('password successfully changed')
                    print('password changed')
                    return render(request,'edit_student_profile.html',{'user': User.objects.filter(id= stu_user_id), 'std' : StudentData.objects.filter( user_id = stu_user_id ), 'password_changed' : "Password Successfully changed"})
                else :
                    print('entered into new pass condition but failed')
                    return render(request, 'std_change_pass.html', {'user': User.objects.filter( id = stu_user_id ), 'std' : StudentData.objects.filter( user_id = stu_user_id ), 'cou' : CourseData.objects.all(), 'message1' : 'new password doesnt match' })
            else:
                print('old pass doesnt match')
                return render(request, 'std_change_pass.html', {'user': User.objects.filter( id = stu_user_id ), 'std' : StudentData.objects.filter( user_id = stu_user_id ), 'cou' : CourseData.objects.all(), 'message2' : 'old password doesnt match' })
        elif 'back' in request.POST: 
            print('back')
            return render(request,'edit_student_profile.html',{'user': User.objects.filter(id= stu_user_id), 'std' : StudentData.objects.filter( user_id = stu_user_id )})
    else:
        return render(request, 'std_change_pass.html', {'user': User.objects.filter( id = stu_user_id ), 'std' : StudentData.objects.filter( user_id = stu_user_id ), 'cou' : CourseData.objects.all()})


def delete_student(request, id):
    print(id)
    user = User.objects.get( id = id )
    print(user)
    user.delete()
    return render(request,'std_login.html',{"del":"account successfully deleted"})  

#forget password
def forgot_pass_to_mail(request):
    if request.method == 'POST':
        reg_id = request.POST['stu_reg_id']
        email = request.POST['email']
        stu_data = StudentData.objects.filter( stu_reg_id = reg_id ).first()
        print(stu_data)
        id = stu_data.user_id
        print(id)
        user = User.objects.filter( id = id, email = email ).first()
        print(user)
        
        user_email = User.objects.get( email = email )
        token = RefreshToken.for_user(user_email).access_token
        token.set_exp(lifetime=timedelta(days=36500))
        current_site = get_current_site(request).domain
        relativeLink = reverse('email_for_pass')
        Email = email
        absUrl = 'http://' + current_site + relativeLink + "?token=" + str(token)
        Subject = " Hello " + "Verification pending"
        Message = "Click below link to activate your account \n " + absUrl + "\n Your Student ID is \t" + str(stu_data.stu_reg_id)  +"\n login with this id"
        send_mail(Subject, Message, EMAIL_HOST_USER, [Email])
        print('pass1')
        print(absUrl)
        return render(request, 'std_login.html',{ 'forgot_email': "set new password, link has been sent to your mail" })
    else:
        return render(request,'forgot_pass.html')

class Forgot_Pass_Email(views.APIView):
    def get(self, request):
        token = request.GET.get('token')
        print('token=', token)
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            print(payload)

            user = User.objects.get(id=payload['user_id'])
            print(user)

            return render(request, 'change_forgot_pass.html', { 'user_id' : user.id })
        except jwt.ExpiredSignatureError as identifier:
            return render(request, 'change_forgot_pass.html', { 'user_id' : user.id })

def change_forgot_pass(request):
    if request.method == 'POST':
        id = request.POST['id']
        password_1 = request.POST['password_1']
        password_2 = request.POST['password_2']
        stu_data = StudentData.objects.filter( user_id = id ).first()
        print(stu_data)
        u_id = stu_data.user_id
        print(u_id)
        user = User.objects.filter( id = u_id ).first()
        print(user)
        print("password not changed yet")
        if password_1 == password_2:
            print("passed the pass condition")
            user.set_password(password_1)
            user.save();
            print("password updated")
            return render(request, 'std_login.html', { 'pass_updated' : "password successfully updated, try logging in " })
        else:
            return render(request, 'change_forgot_pass.html', { 'user_id' : user.id , 'password_condition' : "Passwords doesent match"})
        
    else:
        return render(request, 'change_forgot_pass.html', { 'user_id' : user.id })

#course reg
def course_reg_page(request, id):
    print(id)
    user = User.objects.get( id = id )
    print(user)
    return render(request,'course_reg.html',{ 'user_id' : id , 'all_courses_data' : CourseData.objects.all().values()})

#course view
def course_reg_form(request):
    all_courses_data = CourseData.objects.all().values()
    print('course not yest updated')
    if request.method == 'POST':
        print('course not yest updated 1')
        user_id = request.POST['user_id']
        reg_id = request.POST['course_reg_radios']
        stu_data = StudentData.objects.filter( user_id = user_id ).first()
        print(stu_data)
        print(stu_data.student_id)
        user = User.objects.filter( id = user_id ).first()
        print(user)
        print(user.id)
        reg_data = RegisteredData.objects.create( student_id_id = stu_data.student_id )
        stu_data.save();
        print(reg_data)
        if 'Register' in request.POST:
            exists = RegisteredData.objects.filter( course_id_id = reg_id )
            if not exists :
                reg_data.course_id_id = reg_id
                reg_data.course_status = 0
                stu_data.save();
                user.save();
                reg_data.save();
                print('course not yest updated 2')
                print(reg_data.course_id_id)
                print(reg_data.course_status)
                print("registered successfully")
                return render(request, 'std_profile.html', {'user': User.objects.filter( id = user_id ), 'std' : StudentData.objects.filter( user_id = user_id ), 'cou' : CourseData.objects.all(), 'reg' : RegisteredData.objects.filter( student_id_id = stu_data.student_id ) })
            else:
                return render(request, 'std_profile.html', {'user': User.objects.filter( id = user_id ), 'std' : StudentData.objects.filter( user_id = user_id ), 'cou' : CourseData.objects.all(), 'reg' : RegisteredData.objects.filter( student_id_id = stu_data.student_id ) })
        elif 'Back' in request.POST:
            return render(request, 'std_profile.html', {'user': User.objects.filter( id = user_id ), 'std' : StudentData.objects.filter( user_id = user_id ), 'cou' : CourseData.objects.all(),'reg' : RegisteredData.objects.filter( student_id_id = stu_data.student_id ) } )
    else:
        pass

#---------------------------------------------ADMIN------------------------------------------------------------------

#admin login
def admin_login_form(request):
    error = 0
    if request.method == 'POST':
        username = request.POST["username"]
        password = request.POST["password"]
        incorrect_credentials = 0
        user = authenticate(username = username, password = password)
        data = User.objects.filter(username=username).first()
        print(username,password)
        print(user)
        print(data)
        print('001')
        if User.objects.filter(username = username ).exists():
            print('002')
            if  data.is_active == True and data.is_staff == True:
                print('003')
                login(request, user)
                print('logged in after 003')
                return render(request, 'admin_port.html')
            else :
                if user and data.is_staff == False:
                    return render(request, 'admin_login.html', { 'admin_p' : "admin perms are not given to this account" })
                else:
                    print('005')
                    error = 1
                    return render(request, 'admin_login.html', {'error': error})
        else:
            print('006')
            incorrect_credentials = 1
            return render(request,'admin_login.html', {'incorrect' : incorrect_credentials})
    else:
        error == 1
        return render(request, 'admin_login.html', {'error': error})

#admin logout
def admin_logout(request):
    print('logout1')
    logout(request)
    print("logout2")
    return render(request,'admin_login.html',{ 'logged_out_a' : "Logged out successfully"})

#student view - admin
def student_view(request):
    all_students = User.objects.filter(is_staff=False).values()
    all_students_data = StudentData.objects.all().values()
    all_courses_data = CourseData.objects.all().values()
    return render(request, 'admin_port_std.html',{'all_students': all_students, 'all_students_data' :all_students_data , 'all_courses_data' : all_courses_data,  'reg' : RegisteredData.objects.all().values() })

#course adding - admin
def course_add(request):
    if request.method == 'POST':
        course_name = request.POST["course_name"]
        description = request.POST["description"]
        course_add_data = CourseData.objects.create( course_name = course_name, description = description )
        course_add_data.save()
        print(course_add_data)
        return redirect('course_view')
    else:
        return render(request, 'add_course.html')
    
#edit course details - admin
def course_edit_click(request, pk):
    print(pk)
    course_edit_data1 = CourseData.objects.filter( course_id = pk ).first()
    course_name = course_edit_data1.course_name
    course_id = course_edit_data1.course_id
    print(course_name)
    return render(request, 'edit_course.html', {'course_name_1' : course_name , 'course_id' : course_id })

#course view -admin
def course_view(request):
    all_courses_data = CourseData.objects.all().values()
    return render(request, 'admin_port_course.html',{ 'all_courses_data' : all_courses_data })

def course_edit(request):
    if request.method == 'POST':
        course_id = request.POST["course_id"]
        course_edit_data2 = CourseData.objects.filter( course_id = course_id ).first()
        course_name = course_edit_data2.course_name
        if 'course_delete' in request.POST:
            course_edit_data2.delete()
            return redirect('course_view')
        elif 'course_edit' in request.POST:
            course_edit_data2.course_name=request.POST["course_name"]
            course_edit_data2.description=request.POST["description"]
            course_edit_data2.save()
            print(course_edit_data2)
            return redirect('course_view')
    else:
        return render(request, 'edit_course.html', {'course_name_1' : course_name })

#course approvel - admin
def std_reg_status_approval(request, id, course_id):
    print("entered approval function")
    user = User.objects.filter( id = id ).first()
    print(user)
    stu_data = StudentData.objects.filter( user_id = id ).first()
    print(stu_data)
    reg_data = RegisteredData.objects.filter( student_id_id = stu_data.student_id, course_id_id = course_id ).first()
    print(reg_data)
    reg_data.course_status = 1
    reg_data.save();
    stu_data.save();
    user.save();
    print("got approved")
    #to show all the students
    all_students = User.objects.filter(is_staff=False).values()
    all_students_data = StudentData.objects.all().values()
    all_courses_data = CourseData.objects.all().values()
    return render(request, 'admin_port_std.html',{'all_students': all_students, 'all_students_data' :all_students_data , 'all_courses_data' : all_courses_data,'reg' : RegisteredData.objects.filter( student_id_id = stu_data.student_id ) })

def std_reg_status_reject(request, id, course_id ):
    print("entered rejecting function")
    user = User.objects.filter( id = id ).first()
    print(user)
    stu_data = StudentData.objects.filter( user_id = id ).first()
    print(stu_data)
    reg_data = RegisteredData.objects.filter( student_id_id = stu_data.student_id, course_id_id = course_id ).first()
    print(reg_data)
    reg_data.course_status = -1
    reg_data.save();
    stu_data.save();
    user.save();
    print("got rejected")
    #to show all the students
    all_students = User.objects.filter(is_staff=False).values()
    all_students_data = StudentData.objects.all().values()
    all_courses_data = CourseData.objects.all().values()
    return render(request, 'admin_port_std.html',{'all_students': all_students, 'all_students_data' :all_students_data , 'all_courses_data' : all_courses_data , 'reg' : RegisteredData.objects.filter( student_id_id = stu_data.student_id )})