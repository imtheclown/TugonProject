from django.contrib import admin
from .models import AppUser, Agency, Municipality, Rating, Comment, UserProfile, AgencyProfile, Reply, Post, PostReaction, CommentReaction, PostNotification

admin.site.register(AppUser)
admin.site.register(Agency)
admin.site.register(Municipality)
admin.site.register(Rating)
admin.site.register(Comment)
admin.site.register(UserProfile)
admin.site.register(AgencyProfile)
admin.site.register(Reply)
admin.site.register(Post)
admin.site.register(PostReaction)
admin.site.register(CommentReaction)
admin.site.register(PostNotification)
# Register your models here.
