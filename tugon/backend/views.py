from django.shortcuts import render
from django import http
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status, viewsets, permissions
from rest_framework.parsers import MultiPartParser, FormParser
#serializers
from .serializers import UserSerializer, MunicipalitySerializer, AgencySerializer, AgencyGetterSerializer, MunicipalityCreatorSerializer, RatingSerializer
from . import serializers
from . import models
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from rest_framework.permissions import BasePermission, IsAuthenticated, SAFE_METHODS, AllowAny, IsAuthenticatedOrReadOnly
###below are models
from .models import AppUser, Municipality, Agency, SiteAdmin, Rating, AgencyDetails,Comment, AgencyProfile

# Create your views here.

class registerUser(APIView):
    permission_classes = [permissions.AllowAny]
    parser_classes = (MultiPartParser, FormParser)
    def getObject(self, username):
         try:
            return AppUser.objects.get(name = username)
         except AppUser.DoesNotExist:
             return None
    def post(self, request, format=None):
        user = self.getObject(request.data['name'])
        if(user == None):
            serializer = UserSerializer(data = request.data)
            if (serializer.is_valid()):
                serializer.save()
                user = models.AppUser.objects.filter(email = request.data["email"]).last()
                profile = models.UserProfile.objects.create(user_id = user.user_id, user_name = user.name)
                profile.save()
                return Response(status=status.HTTP_201_CREATED)
            else:
                print("Inputs not valid")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            print("user already exists")
            return Response(status=status.HTTP_403_FORBIDDEN)
        
class Home(APIView):
    permission_classes = [permissions.AllowAny]
    def get(self,request): #this will be used to retrieve municipalities from the database
        instance =Municipality.objects.all()
        serializer = MunicipalitySerializer(instance, many=True)
        return Response(serializer.data)
    

class AgencyView(APIView):#creatinga an agency or getting all of the agency
    permission_classes = [permissions.AllowAny]
    parser_classes = (MultiPartParser, FormParser)
    def get(self, request, munName):
        agencies = Agency.objects.filter(location = munName)
        serializer = AgencyGetterSerializer(agencies, many=True)
        data = serializer.data
        for dat in data:
            profile = models.AgencyProfile.objects.filter(agency_id = dat["agency_id"]).first()
            prof_serializer = serializers.AgencyProfileSerializer(profile)
            dat["agency_acronym"] = prof_serializer.data["agency_acronym"]
        return Response(data=data)
    

    def post(self, request, *args, **kwargs):
        mun = Municipality.objects.filter(municipality_name = request.data['location'])
        if(mun.count() ==  0):
            munSerializer = MunicipalityCreatorSerializer(data={"municipality_name" :request.data['location']})
            if(munSerializer.is_valid()):
                munSerializer.save()
        serializer = AgencySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            last_added = models.Agency.objects.filter(location = request.data["location"])
            background = None
            try:
                background = request.data["agency_background_photo"]
            except Exception as e:
                background = None
            data_profile = {"agency_id": last_added[0].agency_id,
                    "agency_acronym": request.data["agency_acronym"],
                    "agency_background_photo": background
                    }
            agency_profile_serializer = serializers.AgencyProfileSerializer(data=data_profile)
            print(data_profile)
            if(agency_profile_serializer.is_valid()):
                agency_profile_serializer.save()
                print("profile saved")
            else:
                print(agency_profile_serializer.error_messages)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            print('error',serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
class UserLoginAPIView(GenericAPIView):
    """
    An endpoint to authenticate existing users using their email and password.
    """

    permission_classes = [permissions.AllowAny]
    serializer_class = serializers.UserLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        serializer = serializers.CustomUserSerializer(user)
        token = RefreshToken.for_user(user)
        data = serializer.data
        data["tokens"] = {"refresh": str(token), "access": str(token.access_token)}
        
        return Response(data, status=status.HTTP_200_OK)
    

class RatingView(APIView):
    permission_classes = [permissions.AllowAny]
    parser_classes = (MultiPartParser, FormParser)
    def post(self, request):
        data = request.data# data includes comments and
        rating = Rating.objects.filter(user_id = data['user_id'], agency_id = data['agency_id'])#edit and here
        print(rating)
        agency = Agency.objects.filter(agency_id = data['agency_id'])
        if(rating.count() and data["rating"]):#if user has previous rating on the specific agency
            prevRating = rating[0].rating
            rating[0].rating = request.data['rating']
            rating[0].save()
            #edit the agency
            agency[0].rating -= prevRating
            agency[0].rating += int(request.data['rating'])
            agency[0].save()
            return Response(status=status.HTTP_200_OK)
        else:
            serializer = RatingSerializer(data = request.data)
            if(serializer.is_valid()):
                agency[0].rating += int(request.data['rating'])
                agency[0].numberRaters += 1
                agency[0].save()
                serializer.save()
                return Response(status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_402_PAYMENT_REQUIRED)
    def get(self, request):
        ratings = models.Rating.objects.filter(agency_id = request.data["agency_id"])
        if(ratings):
            serializer = serializers.RatingSerializer(ratings, many=True)
            return(Response(data=serializer.data))
        else:
            return(Response(status=status.HTTP_204_NO_CONTENT))
            
class ReviewView(APIView):
    permission_classes = [permissions.AllowAny]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):

        data = request.data
        data_post = 0
        data_rating = 0
        print(data)
        try:
            data_post = {"agency_id": request.data["agency_id"], "user_id": request.data["user_id"], "content": request.data["content"]}
        except Exception as e:
            data_post = 0

        if(data_post):#there is existence of a non empty content
            try:
                data_post["photo"] = data["photo"]
            except Exception as e:
                print(e)
                data_post["photo"] = None
        
        try:
            data_rating = {"agency_id": request.data["agency_id"], "user_id": request.data["user_id"], "rating": request.data["rating"]}
        except Exception as e:
            data_rating = 0
        
        if(data_post):
            if(len(data["content"])!= 0):
                post_serializer = serializers.PostCreateSerializer(data=data_post)
                if(post_serializer.is_valid()):
                    post_serializer.save()
                else:
                    return Response(post_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        if(data_rating):
            if(int(data["rating"]) > 0):
                ratingSerializer = serializers.RatingSerializer(data=data_rating)
                if(ratingSerializer.is_valid()):
                    rating = Rating.objects.filter(agency_id = request.data["agency_id"], user_id = request.data["user_id"]).first()
                    agency = Agency.objects.filter(agency_id = request.data["agency_id"]).first()
                    if(rating):#user has existing rating on the specific agency
                        rating = rating
                        prev_rating = rating.rating
                        rating.rating = int(request.data["rating"])#user's rating is modified to accept the new data
                        rating.save() #rating object is modified
                        agency.rating -= prev_rating#user's previous rating is removed
                        agency.rating += int(request.data["rating"])#user's new rating is inserted to the database
                        agency.save()   
                    else:#user has no existing rating to specific agency
                        agency.rating += int(request.data["rating"]) #adds the user's rating to the sum of ratings
                        agency.numberRaters += 1 #updates the number of raters for the agency
                        agency.save()
                        ratingSerializer.save() #new rating object is created
                else:
                    return Response(ratingSerializer.errors ,status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_201_CREATED)
    
class UserProfileView(APIView):
    permission_classes = [permissions.AllowAny]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):#edit the profile
        profile = models.UserProfile.objects.filter(user_id = request.data["user_id"]).last()
        if(profile):
            profile.user_photo = request.data["user_photo"]
            profile.save()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, user_id):
        user_profile = models.UserProfile.objects.filter(user_id = user_id).last()
        if(user_profile):
            profile_serializer = serializers.ProfileSerializer(user_profile)
            profile_data = profile_serializer.data
            user = models.AppUser.objects.filter(user_id = user_id).last()
            profile_data["user_name"] = user.name
            return Response(status=status.HTTP_200_OK, data=profile_data)
        else:
            return Response(status= status.HTTP_404_NOT_FOUND)



class AgencyProfileView(APIView):
    permission_classes = [permissions.AllowAny]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request, agency_id):
        agency_profile = models.AgencyProfile.objects.filter(agency_id = agency_id).last()
        agency = models.Agency.objects.filter(agency_id = agency_id).last()

        agency_profile_serializer = serializers.AgencyProfileSerializer(agency_profile)
        agency_serializer = serializers.AgencySerializer(agency)

        data = agency_serializer.data
        data["agency_acronym"] = agency_profile_serializer.data["agency_acronym"]
        data["agency_background_photo"] = agency_profile_serializer.data["agency_background_photo"]
        return Response(data= data)
    def post(self, request):
        data = request.data
        agencyProfile = AgencyProfile.objects.filter(agency_id = data["agency_id"])
        if(agencyProfile):
            if(len(data["agency_acronym"]) > 0 ):
                agencyProfile.agency_acronym = data["agency_acronym"]
            agencyProfile.agency_background_photo = data["agency_background_photo"]
            agencyProfile.save()
            return (Response(status=status.HTTP_200_OK))
        else:
            serializer = serializers.AgencyProfileSerializer(data=request.data)
            if(serializer.is_valid()):
                serializer.save()
                return Response(status=status.HTTP_201_CREATED)
            else:
                return(Response(serializer.error, status=status.HTTP_201_CREATED))

class PostView(APIView):
    permission_classes = [permissions.AllowAny]
    def get(self,request,agency_id):
        posts = models.Post.objects.filter(agency_id = agency_id)
        post_serializer = serializers.PostGetSerializer(posts, many=True)
        post_data = post_serializer.data
        for post in post_data:
            profile = models.UserProfile.objects.filter(user_id = post["user_id"]).last()
            profile_serializer = serializers.ProfileGetSerializer(profile)
            if(profile):            
                post["user_name"] = profile_serializer.data["user_name"]
                post["user_id"] = profile_serializer.data["user_id"]
                post["user_photo"] = profile_serializer.data["user_photo"]
        return Response(data=post_data)
    
class PostReactionView(APIView):
    permission_classes = [permissions.AllowAny]
    parser_classes = [MultiPartParser, FormParser]
    def post(self, request):#creates a reaction for the post at the PostReaction table
        data = request.data
        post_reaction_serializer = serializers.PostReactionSerializer(data=data)
        if(post_reaction_serializer.is_valid()):
            post_reaction_serializer.save()
            post = models.Post.objects.filter(post_id = data["post_id"]).last()
            post.numb_likes += 1
            post.save()
            return Response(status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
    def get(self, request, agency_id, user_id): #retreives reactions specific to the agency and the current user of the browser
        agency_reactions = 0
        try:
            agency_reactions = models.PostReaction.objects.filter(agency_id = agency_id, user_id= user_id).values("post_id")
        except Exception as e:
            agency_reactions = None
        if(agency_reactions):
            return Response(data=agency_reactions)
        else:
            return Response(status=status.HTTP_204_NO_CONTENT)
    def delete(self, request):
        data = request.data
        reaction = models.PostReaction.objects.filter(post_id = data["post_id"], user_id = data["user_id"])
        try:
            reaction.delete()
            post = models.Post.objects.filter(post_id = data["post_id"]).last()
            post.numb_likes -= 1
            post.save()
            return Response(status= status.HTTP_200_OK)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class CommentView(APIView):
    permission_classes = [permissions.AllowAny]
    parser_classes = [MultiPartParser, FormParser]
    def post(self, request):
        data = request.data
        comment_serializer = serializers.CommentCreateSerializer(data=data)
        if(comment_serializer.is_valid()):
            comment_serializer.save()
            post_instance = models.Post.objects.filter(post_id = data["post_id"]).last()
            print(post_instance)
            if(data["user_id"] != post_instance.user_id):
                notif_data = {
                    "user_id": data["user_id"],
                    "post_id": data["post_id"],
                    "notif_type": 1,
                    "trigger_id": post_instance.user_id
                }
                notif_serializer = serializers.PostNotificationCreateSerializer(data=notif_data)
                if(notif_serializer.is_valid()):
                    notif_serializer.save()
                    print("post notification saved")
                else:
                    print(notif_serializer.error_messages)
                    print("no post notifications saved")
            return Response(status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
    def get(self, request, post_id):
        comments = models.Comment.objects.filter(post_id = post_id).values()
        if(comments.count()):
            for comment in comments:
                user_profile = models.UserProfile.objects.filter(user_id = comment["user_id"]).last()
                user_profile_serializer = serializers.ProfileGetSerializer(user_profile)
                comment["user_name"] = user_profile_serializer.data["user_name"]
            return(Response(data=comments))
        else:
            return Response(data= None)
        
class CommentReactionView(APIView):
    permission_classes = [permissions.AllowAny]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request, post_id, user_id): #retreives reactions specific to the agency and the current user of the browser
        comment_reactions = 0
        try:
            comment_reactions = models.CommentReaction.objects.filter(post_id = post_id, user_id= user_id).values("comment_id")
        except Exception as e:
            comment_reactions = None
        if(comment_reactions):
            return Response(data=comment_reactions)
        else:
            return Response(status=status.HTTP_204_NO_CONTENT)
    def post(self, request):
        data = request.data
        comment_reaction_serializer = serializers.CommentReactionSerializer(data=data)
        if(comment_reaction_serializer.is_valid()):
            comment_reaction_serializer.save()
            comment = models.Comment.objects.filter(comment_id = data["comment_id"]).last()
            comment.numb_likes += 1
            comment.save()
            return Response(status=status.HTTP_201_CREATED)
        else:
            return Response(comment_reaction_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def delete(self, request):
        data = request.data
        comment_reaction = models.CommentReaction.objects.filter(comment_id = data["comment_id"], user_id = data["user_id"])
        try:
            comment_reaction.delete()
            comment = models.Comment.objects.filter(comment_id = data["comment_id"]).last()
            comment.numb_likes -= 1
            comment.save()
            return Response(status=status.HTTP_200_OK)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class ReplyView(APIView):
    permission_classes = [permissions.AllowAny]
    parser_classes = [MultiPartParser, FormParser]
    def get(self, request, comment_id):
        replies = models.Reply.objects.filter(comment_id = comment_id)
        if(replies.count()):
            return Response(data=replies.values())
        else:
            return Response(data=None)
    def post(self, request):
        data = request.data
        reply_serializer = serializers.ReplyCreatorSerializer(data=data)
        if(reply_serializer.is_valid()):
            reply_serializer.save()
            return Response(status=status.HTTP_201_CREATED)
        else:
            return Response(status= status.HTTP_400_BAD_REQUEST)
        
class PostNotificationView(APIView):
    permission_classes = [permissions.AllowAny]
    parser_classes = [MultiPartParser, FormParser]
    def get(self, request, user_id):
        notifs = models.PostNotification.objects.filter(user_id = user_id)
        if(notifs.count()):
            print(notifs)
            notif_serializer = serializers.PostNotificationGetSerializer(notifs, many=True)
            notifs = notif_serializer.data
            for notif in notifs:
                trigger_profile = models.UserProfile.objects.filter(user_id = notif["user_id"]).last()
                trigger_profile_serializer = serializers.ProfileGetSerializer(trigger_profile)
                notif["user_name"] = trigger_profile_serializer.data["user_name"]
            return Response(data=notifs)
        else:
            return Response(data=None)
    def post(self, request):
        data = request.data
        notification_serializer = serializers.PostNotificationCreateSerializer(data=data)
        if(notification_serializer.is_valid()):
            notification_serializer.save()
            return Response(status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
class editNotification(APIView):
    permission_classes = [permissions.AllowAny]
    parser_classes = [MultiPartParser, FormParser]
    def post(self, request):
        data = request.data
        notification = models.PostNotification.objects.filter(post_notification_id = data["post_notification_id"] ).last()
        notification.read_status = True
        notification.save()
        return Response(status=status.HTTP_200_OK)
    
class AdminAgencyView(APIView):
    permission_classes = [permissions.AllowAny]
    def get(self, request):
        agencies = models.Agency.objects.all()
        agency_serializer = serializers.AgencyGetterSerializer(agencies, many=True)
        data_agency = agency_serializer.data
        for agency in data_agency:
            agency_profile = models.AgencyProfile.objects.filter(agency_id = agency["agency_id"]).last()
            agency_profile_serializer = serializers.AgencyProfileSerializer(agency_profile)
            agency["agency_acronym"] = agency_profile_serializer.data["agency_acronym"]
        return Response(data=agency_serializer.data)
class ProfileEditView(APIView):
    permission_classes = [permissions.AllowAny]
    def put(self, request):
        data = request.data
        user_profile = models.UserProfile.objects.filter(user_id = data["user_id"]).first()
        if(user_profile):
            user_profile_serializer = serializers.ProfileSerializer(user_profile, data=data)
            if(user_profile_serializer.is_valid()):
                user_profile_serializer.save()
                return Response(status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)
    def get(self, request, user_id):
        user = models.UserProfile.objects.filter(user_id = user_id).first()
        user_profile_serializer = serializers.ProfileGetSerializer(user)
        return Response(data=user_profile_serializer.data)

class GetPersoReview(APIView):
    permission_classes = [permissions.AllowAny]
    def get(self, request, user_id):
        posts = models.Post.objects.filter(user_id = user_id)
        post_serializer = serializers.PersoSerializer(posts, many=True)
        post_data = post_serializer.data
        for each_data in post_data:
            agency = models.Agency.objects.filter(agency_id = each_data["agency_id"]).last()
            agency_serializer = serializers.AgencyGetterSerializer(agency)
            each_data["agency_name"] = agency_serializer.data["agency_name"]
            each_data["logo"] = agency_serializer.data["logo"]
        return Response(data=post_serializer.data)

class getAgencyFeedback(APIView):
    permission_classes = [permissions.AllowAny]
    def get(self, request, user_id):
        posts = models.Post.objects.distinct().filter(user_id = user_id)
        post_data = serializers.AgencyIDonly(posts, many=True)
        print(post_data.data)
        for post in post_data.data:
            agency = models.Agency.objects.filter(agency_id = post["agency_id"]).first()
            agency_serializer = serializers.AgencyGetterSerializer(agency)
            post["logo"] = agency_serializer.data["logo"]
        return Response(data= [post_data.data] )




 





        
