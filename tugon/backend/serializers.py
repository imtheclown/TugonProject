from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import AppUser, Municipality, SiteAdmin, Agency, Rating, AgencyDetails, Comment, Reply, AgencyPhotos, UserProfile, Post
from . import models
from datetime import date

class UserSerializer(serializers.ModelSerializer):#creating an application user
    class Meta:
        model = AppUser
        fields = ["email", "name", "password"]

    def create(self, validated_data):#creates the user
        userid = self.createUserId()
        user = AppUser.objects.create(email=validated_data['email'],name=validated_data['name'], user_id = userid )
        user.set_password(validated_data['password'])
        user.save()
        return user
    
    def createUserId(self):#creates the user id
        id = 0
        lastUser = AppUser.objects.last()
        if(lastUser):
            id = str(lastUser.user_id).split('-')
            id = int(id[1]) + 1
        id = str(id)
        year = str(date.today().year)
        newString = ''
        for i in range(4 - len(id)):
            newString = newString +'0'
        for i in range(len(id)):
            newString = newString + id[i]
        return year + '-' + newString
    
class AgencySerializer(serializers.ModelSerializer):#serializer for agency
    class Meta:
        model = Agency
        fields = ['agency_name', 'location', 'logo']
    def create(self, validated_data):#creates the agency object
        mun_id = Municipality.objects.filter(municipality_name = validated_data['location']).last()
        agency_id = self.createId(validated_data['location'])
        agency = Agency.objects.create(agency_id = agency_id, agency_name = validated_data['agency_name'], location = validated_data['location'], logo = validated_data['logo'], mun_id = mun_id.municipality_id)
        agency.save
        return agency                     
        #municipality should have a 4 character id
    def createId(self, mun_id):#mun id should be string
        id = 0
        stringId = ''
        mun = Municipality.objects.filter(municipality_name = mun_id).first()
        last_user = Agency.objects.filter(mun_id = mun.municipality_id)
        print(last_user)
        if(last_user):#gets the last 4 characters of the last agency created and adds one to become the new agency_id
            id = str(last_user.agency_id).last().split('-')
            id = id[1]
            id = int(id) + 1
        id = str(id)
        for i in range(4- len(id)):
            stringId += '0'
        for i in range(len(id)):
            stringId+= id[i]
        return mun.municipality_id + '-' + stringId
    
    
class AgencyPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgencyPhotos
        fields = ['agency_id', 'photo']
    def create(self, validated_data):
        new_id = self.createId(validated_data['agency_id'])
        new_photo = AgencyPhotos.objects.create(agency_id = validated_data['agency_id'], photo = validated_data["photo"], photo_id = new_id)
        new_photo.save()

    def createId(self, agency_id):
        id = 0
        string_id = ''
        last_agency = AgencyPhotos.objects.filter(agency_id = agency_id).last()
        if(last_agency):
            id = last_agency.photo_id
            id = id.split("-")
            id = int(id[2]) + 1
        id = str(id)
        for i in range(4 - len(id)):
            string_id.append('0')
        for i in range(len(id)):
            string_id.append(id[i])

        return agency_id + string_id
class AgencyGetterSerializer(serializers.ModelSerializer):#this is for retreival of agency only
    class Meta:
        model = Agency
        fields = ['agency_name', 'agency_id', 'location', 'administrator', 'logo', 'rating', 'numberRaters', "agency_id"]

class AgencyDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgencyDetails
        fields = ['agency_id', 'address']#required fields
    



class MunicipalitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Municipality
        fields = ['municipality_name', 'municipality_id']

class MunicipalityCreatorSerializer(serializers.ModelSerializer):#creates municipality object at the database
    class Meta:
        model = Municipality
        fields = ['municipality_name']

    def create(self, validated_data):
        mun_id = self.createID()
        municipality = Municipality.objects.create(municipality_id = mun_id, municipality_name = validated_data['municipality_name'])
        municipality.save()
        return municipality

    def createID(self):
        id = 0
        stringID = ''
        lastMun = Municipality.objects.first()
        if(lastMun):#there is a municipality
            id = int(lastMun.municipality_id) + 1
        id = str(id)
        for i in range(4 - len(id)):
            stringID += '0'
        for i in range(len(id)):
            stringID += id[i]
        print(stringID)
        return stringID

class SiteAdminSerializer(serializers.ModelSerializer):#this is on hold as of the moment
    class Meta:
        model = SiteAdmin
        fields = ['user_id', 'agency_id']
    
    def create(self, validated_data):
        admin_id = self.createID(validated_data['agency_id'])
        municipality = SiteAdmin.objects.create(admin_id = admin_id, user_id = validated_data["user_id"],agency_id = ["agency_id"])
        municipality.save()
        return municipality
        
    def createId(self, agency_id):#mun id should be string
        id = 0
        stringId = ''
        last_user = SiteAdmin.objects.filter(agency_id = agency_id)
        if(last_user):#gets the last 4 characters of the last agency created and adds one to become the new agency_id
            last_user = Agency.objects.filter(agency_id = agency_id)[0]
            id = str(last_user.admin_id).split('-')
            id = id[1]
            current_string = ''
            for i in range(len(id)):
                if id[i] != '0':
                    current_string+=id[i]
            id = int(current_string) + 1
        id = str(id)
        for i in range(4- len(id)):
            stringId += '0'
        for i in range(len(id)):
            stringId+= id[i]
        return agency_id + '-' + stringId
    

class UserLoginSerializer(serializers.Serializer):#for user login

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Incorrect Credentials")
    

class CustomUserSerializer(serializers.ModelSerializer):#serializer for the user
    class Meta:
        model = AppUser
        fields = ("user_id", "name", "email")

class RatingSerializer(serializers.ModelSerializer): #serializer for Rating object
    class Meta:
        model = Rating
        fields = ['rating', 'agency_id', 'user_id']

    def create(self, validated_data):
        newRating = Rating.objects.create(agency_id = validated_data['agency_id'], rating = validated_data['rating'], user_id = validated_data['user_id'])
        newRating.save()
        return newRating
    

    
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ["user_id", "user_photo", "location", "introduction"]

class ProfileGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserProfile
        fields = ["user_name", "user_id", "user_photo", "location", "introduction"]


class AgencyProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AgencyProfile
        fields = ["agency_id", "agency_acronym", "agency_background_photo"]
    def create(self, validated_data):
        new_agency_profile = models.AgencyProfile.objects.create(agency_id = validated_data["agency_id"], agency_background_photo = validated_data["agency_background_photo"], agency_acronym = validated_data["agency_acronym"])
        new_agency_profile.save()
        return new_agency_profile


class PostCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Post
        fields = ["user_id", "agency_id", "content", "photo"]
    def create_id(self, agency_id):
        id = 0
        string_id = ""
        last_post_agency = models.Post.objects.filter(agency_id = agency_id)
        if(last_post_agency):
            last_post_agency = last_post_agency[0]
            id = str(last_post_agency.post_id)
            id = id.split("-")
            id = int(id[2])
            id += 1
        id = str(id)
        for i in range(4 - len(id)):
            string_id += "0"
        for i in range(len(id)):
            string_id += id[i]
        return agency_id + '-' + string_id

            
    def create(self, validated_data):
        new_id = self.create_id(validated_data["agency_id"])
        new_post = models.Post.objects.create(post_id = new_id, user_id = validated_data["user_id"], agency_id = validated_data["agency_id"], content = validated_data["content"], photo = validated_data["photo"])
        new_post.save()
        return new_post
    
class PostGetSerializer(serializers.ModelSerializer):
    class Meta:
        model= Post
        fields = ["user_id", "post_id", "content", "photo", "date_created", "numb_likes",]

class PersoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Post
        fields = ["agency_id", "user_id", "post_id", "content", "photo", "date_created", "numb_likes", "date_created"]
class AgencyIDonly(serializers.ModelSerializer):
    class Meta:
        model = models.Post
        fields = ["agency_id"]
        

class PostReactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PostReaction
        fields = ["user_id", "post_id", "agency_id"]
class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Comment
        fields = ["content", "post_id", "user_id"]
    def createID(self, post_id):
        id = 0
        string_id = ""
        last_comment = models.Comment.objects.filter(post_id = post_id)
        if(last_comment):
            last_comment = last_comment[0]#comments are arranged from the latest to the oldest 
            id = last_comment.comment_id.split("-")
            id = int(id[3]) + 1
        id = str(id)
        for i in range(4 - len(id)):
            string_id += "0"
        for i in range(len(id)):
            string_id += id[i]
        return post_id + "-" + string_id
    def create(self, validated_data):
        new_id = self.createID(validated_data["post_id"])
        new_comment = models.Comment.objects.create(user_id = validated_data["user_id"], post_id = validated_data["post_id"], comment_id = new_id, content = validated_data["content"])
        new_comment.save()
        return new_comment
class CommentGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Comment
        fields = ["comment_id", "content", "numb_likes", "date_created", "user_id", "numb_likes"]

class CommentReactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CommentReaction
        fields = ["user_id", "comment_id", "post_id"]

class ReplyGetterSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Reply
        fields = ["comment_id", "content", "numb_react", "user_id", "reply_id"]

class ReplyCreatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Reply
        fields = ["comment_id", "user_id", "content"]
    def create(self, validated_data):
        new_id = self.createID(validated_data["comment_id"])
        new_reply = models.Reply.objects.create(comment_id = validated_data["comment_id"], user_id = validated_data["user_id"], content = validated_data["content"], reply_id = new_id)
        new_reply.save()
        return new_reply
    def createID(self, comment_id):
        id = 0
        string_id = ""
        comment = models.Reply.objects.filter(comment_id = comment_id)
        if(comment):
            comment = comment[0]#latest created reply
            id = comment.reply_id.split("-")
            id = int(id[4])
            id += 1
        id = str(id)
        for i in range(4 - len(id)):
            string_id += "0"
        for i in range(len(id)):
            string_id += id[i]
        return comment_id + "-" + string_id

class PostNotificationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PostNotification
        fields = ["user_id", "post_id", "notif_type", "trigger_id"]
    def create(self, validated_data):
        new_id = self.createID(validated_data["post_id"])
        new_post_notif = models.PostNotification.objects.create(post_id = validated_data["post_id"], user_id = validated_data["user_id"], notif_type = validated_data["notif_type"], post_notification_id = new_id, trigger_id = validated_data["trigger_id"] )
        new_post_notif.save()
        return new_post_notif
    
    def createID(self, post_id):
        id = 0
        string_id = ""
        last_notif = models.PostNotification.objects.first()
        if(last_notif):
            id = int(last_notif.post_notification_id)
            id += 1
        id = str(id)
        for i in range(20-len(id)):
            string_id += "0"
        for i in range(len(id)):
            string_id += id[i]
        return string_id
class PostNotificationGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PostNotification
        fields = ["user_id", "post_id", "notif_type", "read_status", "trigger_id", "post_notification_id"]





