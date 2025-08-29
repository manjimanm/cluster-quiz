from .models import super_users, role_permission

def user_permissions(request):
    """Context processor to get the user's role and permissions."""
    user_role = None
    permissions = []

    # Check if the user is logged in and session has the user id
    user_id = request.session.get('uid')

    if user_id:
        try:
            # Get the user by ID
            user = super_users.objects.get(id=user_id)
            user_role = user.roles.role_name  # Get the user's role name
            
            # Get the permissions associated with the user's role
            role_permissions = role_permission.objects.filter(roles=user.roles)

            permissions = [
                {'name': permission.permissions.permissions, 'url': permission.permissions.page_url, 'icon': permission.permissions.url_icon}
                for permission in role_permissions
            ]
        except super_users.DoesNotExist:
            pass  # If no user found, leave the permissions and role as empty

    return {
        'user_role': user_role,
        'permissions': permissions,
    }
