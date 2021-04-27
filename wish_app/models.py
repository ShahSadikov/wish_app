from django.db import models
import re
import bcrypt

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

class UserManager(models.Manager):
    def registration_validator(self, postData):
        errors = {}
        #names_____________________________
        if len(postData['first_name']) < 2:
            errors["first_name"] = "The first name must be at least 2 characters"
        if len(postData['last_name']) < 2:
            errors["last_name"] = "The last name must be at least 2 characters"

        #email______________________________
        if not EMAIL_REGEX.match(postData['email']):
            errors["email"] = "Must be a valid email address"
        # #unique email check:
        current_user = User.objects.filter(email=postData['email'])
        if len(current_user) >= 1:
            errors['duplicate'] = "The email is already in use" 
        #password___________________________
        if len(postData['password']) < 8:
            errors["password"] = "The password must be at least 8 characters long"
        #password match:
        if postData['password'] != postData['confirm_password']:
            errors["mismatch"] = "The passwords must match!"
        
        return errors

    def login_validator(self, postData):
        errors = {}
        existing_user = User.objects.filter(email=postData['email'])
        if len(existing_user) == 0:
            errors['wrong_user'] = "Enter a valid email or password"
        #email check:
        elif len(postData['email']) == 0:
            errors['email'] = "You must enter an email"
        #password check:
        elif len(postData['password']) == 0:
            errors['password'] = "You must enter a password"
        elif len(postData['password']) < 8:
            errors['password'] = "The password isn't long enough."
        #check if the email is in DB
        # if so check to see if the email/password match
        elif bcrypt.checkpw(postData['password'].encode(), existing_user[0].password.encode()) != True:
            errors["password"] = "Email and password do not match"
            
        return errors

class WishManager(models.Manager):
    def wish_validator(self, postData):
        errors = {}
        if len(postData['wish_title']) == 0:
            errors['wish_title'] = "Please enter a wish."
        elif len(postData['wish_title']) < 4:
            errors['wish_title'] = "The wish must be at least 3 characters long."
        if len(postData['description']) == 0:
            errors['description'] = "Please enter your description."
        elif len(postData['description']) < 4:
            errors['description'] = "The wish description must be at least 3 characters long."
        
        return errors

#MODELS__________________________________________
class User(models.Model):
    first_name = models.CharField(max_length=45)
    last_name = models.CharField(max_length=45)
    email = models.CharField(max_length=60)
    password = models.CharField(max_length=60)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = UserManager()
    #user_wishes = []
    #granted_wishers = []
    #user_likes = []

class Wish(models.Model):
    wish_title = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    user = models.ForeignKey(User, related_name="user_wishes", on_delete=models.CASCADE)
    granted_users = models.ManyToManyField(User, related_name="granted_wishers")
    user_like = models.ManyToManyField(User, related_name="user_likes")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = WishManager()

# class Like(models.Model):
#     like = models.IntegerField()
#     user_like = models.ForeignKey(User, related_name="user_likes", on_delete=models.CASCADE)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)    
