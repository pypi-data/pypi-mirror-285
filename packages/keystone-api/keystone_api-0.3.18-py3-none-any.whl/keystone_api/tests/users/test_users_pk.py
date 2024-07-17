"""Tests for the `/users/users/<pk>/` endpoint"""

from rest_framework import status
from rest_framework.test import APITestCase

from apps.users.models import User
from tests.utils import CustomAsserts


class EndpointPermissions(APITestCase, CustomAsserts):
    """Test endpoint user permissions

    Permissions depend on whether the user is a member of the record's associated research group.

    Endpoint permissions are tested against the following matrix of HTTP responses.

    | Authentication              | GET | HEAD | OPTIONS | POST | PUT | PATCH | DELETE | TRACE |
    |-----------------------------|-----|------|---------|------|-----|-------|--------|-------|
    | Anonymous user              | 401 | 401  | 401     | 401  | 401 | 401   | 401    | 401   |
    | User accessing own account  | 200 | 200  | 200     | 403  | 200 | 200   | 403    | 403   |
    | User accessing other user   | 200 | 200  | 200     | 403  | 403 | 403   | 403    | 403   |
    | Staff user                  | 200 | 200  | 200     | 405  | 200 | 200   | 204    | 405   |
    """

    endpoint_pattern = '/users/users/{pk}/'
    fixtures = ['multi_research_group.yaml']

    def test_anonymous_user_permissions(self) -> None:
        """Test unauthenticated users cannot access resources"""

        endpoint = self.endpoint_pattern.format(pk=1)
        self.assert_http_responses(
            endpoint,
            get=status.HTTP_401_UNAUTHORIZED,
            head=status.HTTP_401_UNAUTHORIZED,
            options=status.HTTP_401_UNAUTHORIZED,
            post=status.HTTP_401_UNAUTHORIZED,
            put=status.HTTP_401_UNAUTHORIZED,
            patch=status.HTTP_401_UNAUTHORIZED,
            delete=status.HTTP_401_UNAUTHORIZED,
            trace=status.HTTP_401_UNAUTHORIZED,
        )

    def test_authenticated_user_same_user(self) -> None:
        """Test permissions for authenticated users accessing their own user record"""

        # Define a user / record endpoint from the SAME user
        endpoint = self.endpoint_pattern.format(pk=3)
        user = User.objects.get(username='member_1')
        self.client.force_authenticate(user=user)

        self.assert_http_responses(
            endpoint,
            get=status.HTTP_200_OK,
            head=status.HTTP_200_OK,
            options=status.HTTP_200_OK,
            post=status.HTTP_403_FORBIDDEN,
            put=status.HTTP_200_OK,
            patch=status.HTTP_200_OK,
            delete=status.HTTP_403_FORBIDDEN,
            trace=status.HTTP_403_FORBIDDEN,
            put_body={
                'username': 'foobar',
                'password': 'foobar123',
                'first_name': 'Foo',
                'last_name': 'Bar',
                'email': 'foo@bar.com'},
            patch_body={'email': 'member_3@newdomain.com'},
        )

    def test_authenticated_user_different_user(self) -> None:
        """Test permissions for authenticated users accessing records of another user"""

        # Define a user / record endpoint from a DIFFERENT user
        endpoint = self.endpoint_pattern.format(pk=1)
        user = User.objects.get(username='member_2')
        self.client.force_authenticate(user=user)

        self.assert_http_responses(
            endpoint,
            get=status.HTTP_200_OK,
            head=status.HTTP_200_OK,
            options=status.HTTP_200_OK,
            post=status.HTTP_403_FORBIDDEN,
            put=status.HTTP_403_FORBIDDEN,
            patch=status.HTTP_403_FORBIDDEN,
            delete=status.HTTP_403_FORBIDDEN,
            trace=status.HTTP_403_FORBIDDEN,
        )

    def test_staff_user_permissions(self) -> None:
        """Test staff users have read and write permissions"""

        endpoint = self.endpoint_pattern.format(pk=1)
        user = User.objects.get(username='staff_user')
        self.client.force_authenticate(user=user)

        self.assert_http_responses(
            endpoint,
            get=status.HTTP_200_OK,
            head=status.HTTP_200_OK,
            options=status.HTTP_200_OK,
            post=status.HTTP_405_METHOD_NOT_ALLOWED,
            put=status.HTTP_200_OK,
            patch=status.HTTP_200_OK,
            delete=status.HTTP_204_NO_CONTENT,
            trace=status.HTTP_405_METHOD_NOT_ALLOWED,
            put_body={
                'username': 'foobar',
                'password': 'foobar123',
                'first_name': 'Foo',
                'last_name': 'Bar',
                'email': 'foo@bar.com'},
            patch_body={'email': 'foo@bar.com'},
        )


class CredentialHandling(APITestCase):
    """Test the getting/setting of user credentials"""

    endpoint_pattern = '/users/users/{pk}/'
    fixtures = ['multi_research_group.yaml']

    def test_user_get_own_password(self) -> None:
        """Test a user cannot get their own password"""

        user = User.objects.get(username='generic_user')
        self.client.force_authenticate(user=user)

        response = self.client.get(
            self.endpoint_pattern.format(pk=user.id)
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertNotIn('password', response.json())

    def test_user_set_own_password(self) -> None:
        """Test a user can set their own password"""

        user = User.objects.get(username='generic_user')
        self.client.force_authenticate(user=user)

        response = self.client.patch(
            path=self.endpoint_pattern.format(pk=user.id),
            data={'password': 'new_password123'}
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        user.refresh_from_db()
        self.assertTrue(user.check_password('new_password123'))

    def test_user_get_others_password(self) -> None:
        """Test a user cannot get another user's password"""

        authenticated_user = User.objects.get(username='member_1')
        self.client.force_authenticate(user=authenticated_user)

        other_user = User.objects.get(username='member_2')
        response = self.client.get(
            self.endpoint_pattern.format(pk=other_user.id),
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertNotIn('password', response.data)

    def test_user_set_others_password(self) -> None:
        """Test a user cannot set another user's password"""

        authenticated_user = User.objects.get(username='member_1')
        self.client.force_authenticate(user=authenticated_user)

        other_user = User.objects.get(username='member_2')
        response = self.client.patch(
            path=self.endpoint_pattern.format(pk=other_user.id),
            data={'password': 'new_password123'}
        )

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_staff_get_password(self) -> None:
        """Test a staff user cannot get another user's password"""

        staff_user = User.objects.get(username='staff_user')
        self.client.force_authenticate(user=staff_user)

        generic_user = User.objects.get(username='generic_user')
        response = self.client.get(
            self.endpoint_pattern.format(pk=generic_user.id)
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertNotIn('password', response.json())

    def test_staff_set_password(self) -> None:
        """Test the password field is settable by staff users"""

        staff_user = User.objects.get(username='staff_user')
        self.client.force_authenticate(user=staff_user)

        generic_user = User.objects.get(username='generic_user')
        response = self.client.patch(
            path=self.endpoint_pattern.format(pk=generic_user.id),
            data={'password': 'new_password123'}
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        generic_user.refresh_from_db()
        self.assertTrue(generic_user.check_password('new_password123'))
