from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render


def index(request):
    return render(request,'index.html')

def student_login(request):
    return render(request,'std_login.html')

def student_signup(request):
    return render(request,'std_signup.html')

def admin_login(request):
    return render(request,'admin_login.html')
 


