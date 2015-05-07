from restless.dj import DjangoResource
from restless.preparers import FieldsPreparer
from restless.exceptions import Unauthorized
from django.utils.html import escape
from .models import UserProfile


class UserProfileResource(DjangoResource):
    preparer = FieldsPreparer(fields={
        'id': 'pk',
        'username': 'username',
        'email': 'email',
        'first_name': 'first_name',
        'last_name': 'last_name',
        'full_name': 'full_name',
        'bio': 'bio',
        'phone': 'phone',
    })

    MODIFIABLE_FIELDS = {
        'profile': ['phone', 'bio'],
        'user': ['email', 'first_name', 'last_name'],
    }

    def is_authenticated(self):
        return self.request.user.is_authenticated()

    # GET /api/users/
    # Gets a list of all active users
    def list(self):
        return UserProfile.objects.filter(user__is_active=True)

    # GET /api/users/<pk>/
    # Gets info of user with id=pk
    # Requested user must be active.
    def detail(self, pk):
        return UserProfile.objects.get(user__id=pk, user__is_active=True)

    # PUT /api/users/<pk>/
    # Updates a user's info with id=pk. Assumes specified user exists,
    # otherwise error is returned.  This is to prevent user creation.
    # NOTE: for AJAX calls through jQuery, use JSON.stringify on your data
    def update(self, pk):
        if self.request.user.id != int(pk):
            raise Unauthorized("Not authorized to update "
                               "another user's profile.")

        profile = self.request.user.profile

        for category in self.MODIFIABLE_FIELDS:
            target = profile
            if category == 'user':
                target = profile.user

            for field in self.MODIFIABLE_FIELDS[category]:
                if field in self.data:
                    setattr(target, field, escape(self.data[field]))

        profile.user.save()
        profile.save()
        return profile


class FriendResource(DjangoResource):
    preparer = FieldsPreparer(fields={
        'id': 'pk',
        'username': 'username',
        'email': 'email',
        'first_name': 'first_name',
        'last_name': 'last_name',
        'full_name': 'full_name',
        'bio': 'bio',
        'phone': 'phone',
    })

    def is_authenticated(self):
        return self.request.user.is_authenticated()

    # GET /api/friends/?type=(accepted|incoming|outgoing)
    # Gets a list of friends of the current user.
    # Returns accepted friends if "type" is not specified.
    def list(self):
        list_type = self.request.GET.get('type', 'accepted')

        if list_type == 'incoming':
            return self.request.user.profile.pending_incoming_friends
        elif list_type == 'outgoing':
            return self.request.user.profile.pending_outgoing_friends
        else:
            return self.request.user.profile.friends

    # PUT /api/friends/<pk>/
    # Adds a friendship of current user -> 'pk'
    def update(self, pk):
        other = UserProfile.objects.get(user__id=pk)
        self.request.user.profile.add_friend(other)
        return other

    # DELETE /api/friends/<pk>/
    # Removes a friendship of current user <-> 'pk'
    def delete(self, pk):
        other = UserProfile.objects.get(user__id=pk)
        self.request.user.profile.del_friend(other)