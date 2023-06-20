from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

#user class
class UserManager(BaseUserManager):

    use_in_migration = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is Required')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff = True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser = True')

        return self.create_user(email, password, **extra_fields)


class AppUser(AbstractUser):

    username = None
    user_id = models.CharField(max_length=9, unique=True)
    name = models.CharField(max_length=100, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'user_id']

    def __str__(self):
        return self.name

#municipality class 
class Municipality(models.Model):
    municipality_name = models.CharField(max_length=30)
    municipality_id = models.CharField(max_length=4, unique=True, primary_key=True)
    date_created = models.DateTimeField(auto_now_add=True)


    class Meta:
        ordering = ['-date_created']
        verbose_name = 'Municipality'
        verbose_name_plural = 'Municipalities'

#site admin

class SiteAdmin(models.Model):
    user_id = models.CharField(max_length=9)
    admin_id = models.CharField(max_length=14, primary_key=True, unique=True);#create a serializer for this
    agency_id = models.CharField(max_length=9)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_created']
        verbose_name = 'Agency Administrator'
        verbose_name_plural = 'Agency Administrators'

def upload_to(instance, filename):
    return 'images/{filename}'.format(filename=filename)
class Agency(models.Model):
    agency_id = models.CharField(max_length=9, unique=True, primary_key = True) #generate this one
    agency_name =models.CharField(max_length=50) #from forms
    mun_id = models.CharField(max_length=4) #id of the municipality
    administrator = models.CharField(max_length=50, default="NONE") 
    date_created = models.DateTimeField(auto_now_add=True)
    logo = models.ImageField(upload_to=upload_to, null=True, blank=True)
    location = models.CharField(max_length= 30, blank= True, null=True, default='')
    rating = models.IntegerField(default=0)
    numberRaters = models.IntegerField(default=0)

    class Meta:
        ordering = ['-date_created']
        verbose_name = "Agency"
        verbose_name_plural = "Agencies"
class AgencyProfile(models.Model):
    agency_id = models.CharField(max_length=9)
    agency_background_photo = models.ImageField(upload_to=upload_to, null=True, blank=True)
    agency_acronym = models.CharField(max_length=50)


class AgencyDetails(models.Model):#should have a one to one relationship to agency; will be created when an agency is created
    agency_id = models.CharField(max_length=9)#place the id of agency during creation
    background = models.TextField(blank=True, null=True)#this will be the 'about us'
    address = models.CharField(max_length=200)#place loation of the agency when creating
    landmark = models.TextField(max_length=200, blank=True, null=True)
    officeHours_start = models.TimeField(null= True, blank=True)#should be set up by the admin
    officeHours_end = models.TimeField(null=True, blank=True) #should be set up by the admin


class AgencyPhotos(models.Model):
    agency_id = models.CharField(max_length=9)
    photo = models.ImageField(upload_to=upload_to, null=True, blank= True)
    photo_id = models.CharField(max_length=14)
    date_created = models.DateTimeField(auto_now_add=True)
    comment_id = models.CharField(max_length=14, default="", blank=True, null= True)

    class Meta:
        ordering = ['-date_created']


class Rating(models.Model):#one per user; many to one on agency
    agency_id = models.CharField(max_length=9) #should be assigned during creation
    user_id = models.CharField(max_length=9) #should be added during creation
    rating = models.IntegerField() #should be added during creation
    date_posted = models.DateTimeField(auto_now_add = True) #should be editable, will change if user rerate the same agency



class UserProfile(models.Model):
    #upon creation of user, create the profile with only the user_name and user_id in it.
    user_id = models.CharField(max_length=9)
    user_name = models.CharField(max_length=50)
    user_photo = models.ImageField(upload_to=upload_to, null=True, blank=True)
    introduction = models.TextField(default="")
    location = models.CharField(max_length=50, default="")



class Post(models.Model):
    post_id = models.CharField(max_length=14, unique=True)
    user_id = models.CharField(max_length=9)
    agency_id = models.CharField(max_length=9)
    content = models.TextField()
    photo = models.ImageField(upload_to=upload_to, null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    numb_likes = models.IntegerField(default=0)

    class Meta:
        verbose_name = "Post"
        verbose_name_plural = "Posts"
        ordering = ["-date_created"]

class PostReaction(models.Model):
    user_id = models.CharField(max_length=9)
    post_id = models.CharField(max_length=14)
    agency_id = models.CharField(max_length=9)



class Comment(models.Model):
    post_id = models.CharField(max_length=14)
    user_id = models.CharField(max_length=9)
    comment_id = models.CharField(max_length=19)
    content = models.TextField()
    numb_likes = models.IntegerField(default=0)
    date_created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Comment'
        verbose_name_plural = "Comments"
        ordering = ["-date_created"]

class CommentReaction(models.Model):
    user_id = models.CharField(max_length=9)
    comment_id = models.CharField(max_length=19)
    post_id = models.CharField(max_length=14)

class Reply(models.Model):
    comment_id = models.CharField(max_length=19)
    user_id = models.CharField(max_length=9)
    content = models.TextField()
    num_react = models.IntegerField(default=0)
    date_created = models.DateTimeField(auto_now_add=True)
    reply_id = models.CharField(max_length=24)
    
    class Meta:
        verbose_name = "Reply"
        verbose_name_plural = "Replies"
        ordering = ["-date_created"]

class ReplyReact(models.Model):
    comment_id = models.CharField(max_length=19)
    user_id = models.CharField(max_length=9)
    reply_id = models.CharField(max_length=24)

class PostNotification(models.Model):
    post_id = models.CharField(max_length=14)
    read_status = models.BooleanField(default=False)
    user_id = models.CharField(max_length=9)
    post_notification_id = models.CharField(max_length=20)
    notif_type = models.IntegerField()
    trigger_id = models.CharField(max_length=9)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date_created"]

    



    

