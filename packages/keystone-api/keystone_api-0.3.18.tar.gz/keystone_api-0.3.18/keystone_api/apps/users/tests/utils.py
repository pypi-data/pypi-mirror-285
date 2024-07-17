"""Testing utilities specific to dealing with user accounts"""

from apps.users.models import User


def create_test_user(
    username: str,
    password: str = "foobar123",
    first_name: str = "foo",
    last_name: str = "bar",
    email: str = "foo@bar.com",
    **kwargs
) -> User:
    """Create a user account for testing purposes

    Args:
        username: The account username
        password: The account password
        first_name: The first name of the user
        last_name: The last name of the user
        email: The email of the user
        **kwargs: Any other values in the user model

    Return:
        The saved user account
    """

    return User.objects.create_user(username, password, first_name=first_name, last_name=last_name, email=email, **kwargs)
