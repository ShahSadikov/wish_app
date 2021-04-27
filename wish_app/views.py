from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Q
from .models import *
import bcrypt

def index(request):
    return render(request, 'index.html')

#Create/register a new user_________________________________
def register_user(request):
    if request.method == "POST":
        #validation before saving to DB
        errors = User.objects.registration_validator(request.POST)
        if len(errors) > 0:
            for key, value in errors.items():
                messages.error(request, value)
            return redirect('/') 

        #hash the password
        hashed_pw = bcrypt.hashpw(request.POST['password'].encode(), bcrypt.gensalt()).decode()
        
        #create user
        new_user = User.objects.create(
            first_name = request.POST['first_name'],
            last_name = request.POST['last_name'],
            email = request.POST['email'],
            password = hashed_pw
        ) 
        #create a session
        request.session['logged_user'] = new_user.id
        request.session['user_name'] = new_user.first_name
        return redirect("/user/dashboard")
    return redirect('/')    

#Login user_________________________________
def login_user(request):
    if request.method == "POST":
        errors = User.objects.login_validator(request.POST)
        if errors:
            for key, value in errors.items():
                messages.error(request, value)
            return redirect('/')

        this_user = User.objects.filter(email=request.POST['email'])
        if this_user:
            log_user = this_user[0]

            if bcrypt.checkpw(request.POST['password'].encode(), log_user.password.encode()): 
                request.session['logged_user'] = log_user.id  
                request.session['user_name'] = log_user.first_name
                return redirect('/user/dashboard')
            messages.error(request, "email or password are incorrect.")
    return redirect('/')

#User dashboard & display wishes_________________________________
def dashboard(request):
    if 'logged_user' not in request.session:
        messages.error(request, "Please register or log in first!")
        return redirect('/')
    # user = User.objects.get(id=2)
    context = {
        'logged_user': User.objects.get(id=request.session['logged_user']),
        #DB query for ManyToMany field:_________________________________________
        'your_wishes': Wish.objects.filter(Q(user=request.session['logged_user']) & ~Q(granted_users=request.session['logged_user'])),
        'granted_wishes_by_logged_user': Wish.objects.filter(~Q(granted_users = None)),
    }
    return render(request, 'dashboard.html', context)

#Create new wishes__________________________________
def create_new_wish(request):
    if 'logged_user' not in request.session:
        messages.error(request, "Please register or log in first!")
        return redirect('/')
    return render(request, 'create_wish_form.html')

def create_wish_form(request):
    if 'logged_user' not in request.session:
        messages.error(request, "Please register or log in first!")
        return redirect('/')
    if request.method == "POST":
        wish_errors = Wish.objects.wish_validator(request.POST)
        errors = list(wish_errors.values())

        if errors:
            for error in errors:
                messages.error(request, error)
            return redirect('/wishes/new')

        user = User.objects.get(id=request.session['logged_user'])
        wish = Wish.objects.create(
            wish_title = request.POST['wish_title'], 
            description = request.POST['description'],
            user = user,
        )
        return redirect('/user/dashboard')
    return redirect('/wishes/new')

#Remove/delete wish_____________________________________
def delete_wish(request, wish_id):
    if 'logged_user' not in request.session:
        messages.error(request, "Please register or log in first!")
        return redirect('/')
    wish = Wish.objects.get(id=wish_id)
    wish.delete()
    return redirect('/user/dashboard')

#Edit wish________________________________________________
def edit_wish(request, wish_id):
    if 'logged_user' not in request.session:
        messages.error(request, "Please register or log in first!")
        return redirect('/')
    context = {
        "wish_info": Wish.objects.get(id=wish_id)
    }
    return render(request, 'edit_wish_form.html', context)

#Update wish_______________________________________________
def update_wish(request, wish_id):
    if 'logged_user' not in request.session:
        messages.error(request, "Please register or log in first!")
        return redirect('/')
    if request.method == "POST":
        wish_errors = Wish.objects.wish_validator(request.POST)
        errors = list(wish_errors.values())

        if errors:
            for error in errors:
                messages.error(request, error)
            return redirect('/wishes/new')

    wish = Wish.objects.get(id=wish_id)
    wish.wish_title = request.POST['wish_title']
    wish.description = request.POST['description']
    wish.save()
    return redirect('/user/dashboard')

#Granted wish_____________________________________
def grant_wish(request, wish_id):
    if 'logged_user' not in request.session:
        messages.error(request, "Please register or log in first!")
        return redirect('/')
    logged_user = User.objects.get(id = request.session['logged_user'])
    wish = Wish.objects.get(id=wish_id)
    wish.granted_users.add(logged_user) 
    return redirect('/user/dashboard')

#Add like_____________________________
def add_like(request, wish_id):
    if 'logged_user' not in request.session:
        messages.error(request, "Please register or log in first!")
        return redirect('/')

    logged_user = User.objects.get(id = request.session['logged_user'])
    like = Wish.objects.get(id=wish_id)
    like.user_like.add(logged_user) 

    return redirect('/user/dashboard')

#View wish stats page_________________________________________
def wish_stats(request):
    if 'logged_user' not in request.session:
        messages.error(request, "Please register or log in first!")
        return redirect('/')
    granted_wishes = Wish.objects.filter(~Q(granted_users=None)).count()
    my_granted_wishes = Wish.objects.filter(granted_users__isnull=False, user = request.session['logged_user']).count()
    pending_wishes = Wish.objects.filter(granted_users=None, user = request.session['logged_user']).count()
    context = {
        'logged_user': User.objects.get(id=request.session['logged_user']),
        'granted_wishes': granted_wishes,
        'my_granted_wishes': my_granted_wishes,
        'pending_wishes': pending_wishes,
    }
    return render(request, 'wish_stats_page.html', context)

#Logout user_________________________________
def logout_user(request):
    request.session.flush()
    return redirect('/')