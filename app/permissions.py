from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of a trip to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the trip.
        # For Trip objects
        if hasattr(obj, "owner"):
            return obj.owner == request.user

        # For Column objects (check through trip)
        if hasattr(obj, "trip_id"):
            return obj.trip_id.owner == request.user

        # For Attraction objects (check through column -> trip)
        if hasattr(obj, "column_id"):
            return obj.column_id.trip_id.owner == request.user

        # For VisitedAttraction objects (check through attraction -> column -> trip)
        if hasattr(obj, "attraction_id"):
            return obj.attraction_id.column_id.trip_id.owner == request.user

        return False


class IsTripOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of a trip to access it.
    More restrictive - doesn't allow read access to non-owners.
    """

    def has_object_permission(self, request, view, obj):
        # For Trip objects
        if hasattr(obj, "owner"):
            return obj.owner == request.user

        # For Column objects (check through trip)
        if hasattr(obj, "trip_id"):
            return obj.trip_id.owner == request.user

        # For Attraction objects (check through column -> trip)
        if hasattr(obj, "column_id"):
            return obj.column_id.trip_id.owner == request.user

        # For VisitedAttraction objects (check through attraction -> column -> trip)
        if hasattr(obj, "attraction_id"):
            return obj.attraction_id.column_id.trip_id.owner == request.user

        return False


class IsPostAuthorOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow authors of a post to edit or delete it.
    Anyone can read posts.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the author of the post
        return obj.author == request.user
