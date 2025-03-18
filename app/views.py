from django.shortcuts import render,redirect
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

def index(request):
    saved_message = request.session.pop('saved_message', None)
    return render(request,'index.html',{'saved_message':saved_message})

def admin_login(request):
    if request.method =='POST':
        username=request.POST['username']
        password=request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            request.session['Adm_id'] = user.id
            request.session['saved_message'] = 'login_success'
            return redirect('/web/dashboard')
        else: 
            request.session['saved_message'] = 'Invalid Username/Password'
    return redirect('/')

def admin_logout(request):
    del request.session['Adm_id']
    return redirect('/')

def web(request):
    return redirect('/')