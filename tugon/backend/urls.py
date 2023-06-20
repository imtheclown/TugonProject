from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path("register/", views.registerUser.as_view(), name="register"),
    path('login/', views.UserLoginAPIView.as_view() , name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('home/', views.Home.as_view(), name = "home"),
    path("agency/", views.AgencyView.as_view(), name="create agency"),
    path("agency/<str:munName>/", views.AgencyView.as_view(), name='get agencies'),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("rate/", views.RatingView.as_view(), name="rate"),
    path("comment/", views.CommentView.as_view(), name = "create comment"),
    path("create_review/", views.ReviewView.as_view(), name = "create a review"),
    path("review/<str:agency_id>/", views.ReviewView.as_view(), name="get reviews"),
    path("user_profile/<str:user_id>/", views.UserProfileView.as_view(), name="get user profile"),
    path("profile/", views.UserProfileView.as_view(), name="Create profile"),
    path("agency-profile/<str:agency_id>/", views.AgencyProfileView.as_view(), name = "get agency profile"),
    path("agency-profile/", views.AgencyProfileView.as_view(), name="agency profile creator"),
    path("agency/post/<str:agency_id>/", views.PostView.as_view(), name="load posts"),
    path("agency/post/react/add/", views.PostReactionView.as_view(), name="add react"),
    path("agency/post/react/<str:agency_id>/<str:user_id>/", views.PostReactionView.as_view(), name="get view"),
    path("agency/post/react/delete/", views.PostReactionView.as_view(), name="delete react"),
    path("agency/post/comment/create/", views.CommentView.as_view(), name="create comment"),
    path("agency/post/comment/<str:post_id>/", views.CommentView.as_view(), name= "get comment"),
    path("agency/post/comment/react/<str:post_id>/<str:user_id>/", views.CommentReactionView.as_view(), name="get reactions"),
    path("agency/post/comment/react/create/", views.CommentReactionView.as_view(), name="create comment react"),
    path("agency/post/comment/react/delete/", views.CommentReactionView.as_view(), name="delete reaction"),
    path("agency/post/comment/reply/create/", views.ReplyView.as_view(), name="create reply"),
    path("agency/post/comment/reply/<str:comment_id>/", views.ReplyView.as_view(), name= "get replies"),
    path("notification/<str:user_id>/", views.PostNotificationView.as_view(), name="get post notification"),
    path("notification/get/<str:user_id>/", views.PostNotificationView.as_view(), name="create post notification"),
    path("agency/get_all", views.AdminAgencyView.as_view(), name="get all agency"),
    path("post/edit/", views.editNotification.as_view(), name="edit read status"),
    path("profile/edit/",views.ProfileEditView.as_view(), name="edit profile"),
    path("profile/get/<str:user_id>/",views.ProfileEditView.as_view(), name="get profile"),
    path("post/get/<str:user_id>/", views.GetPersoReview.as_view(), name="Get all posts"),
    path("profile/get_pictures/<str:user_id>/" ,views.getAgencyFeedback.as_view(), name="get agencies")

]

#TokenObtainPairView.as_view()