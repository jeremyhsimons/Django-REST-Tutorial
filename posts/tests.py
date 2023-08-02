from django.contrib.auth.models import User
from .models import Post
from rest_framework import status
from rest_framework.test import APITestCase


class PostListViewTests(APITestCase):

    def setUp(self):
        User.objects.create_user(username='Adam', password="password123")

    def test_can_list_posts(self):
        adam = User.objects.get(username='Adam')
        Post.objects.create(owner=adam, title='a title')
        response = self.client.get('/posts/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_logged_in_user_can_create_post(self):
        self.client.login(username='Adam', password="password123")
        response = self.client.post('/posts/', {'title': 'a title'})
        count = Post.objects.count()
        self.assertEqual(count, 1)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_logged_out_user_cannot_create_post(self):
        response = self.client.post('/posts/', {'title': 'a title'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class PostDetailViewTests(APITestCase):

    def setUp(self):
        adam = User.objects.create_user(username='Adam', password="password123")
        brian = User.objects.create_user(username='Brian', password="password456")
        Post.objects.create(
            owner=adam, title='a title', content='Adam content'
            )
        Post.objects.create(
            owner=brian, title='another title', content='Brian content'
            )

    def test_can_retrieve_post_using_valid_id(self):
        response = self.client.get('/posts/1')
        self.assertEqual(response.data['title'], 'a title')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_cannot_retrieve_post_using_invalid_id(self):
        response = self.client.get('/posts/333')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_can_update_own_post(self):
        self.client.login(username='Adam', password='password123')
        response = self.client.put('/posts/1', {'title': 'a new title'})
        post = Post.objects.filter(pk=1).first()
        self.assertEqual(post.title, 'a new title')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_cannot_edit_other_users_post(self):
        self.client.login(username='Adam', password='password123')
        response = self.client.put('/posts/2', {'title': 'WibblyWobbly'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
