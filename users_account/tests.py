from django.test import TestCase
from django.urls import reverse
from .models import NovaUser, SurfSpot
from django.core.paginator import Paginator


class UserAuthTests(TestCase):
    def setUp(self):
        self.user = NovaUser.objects.create_user(
            username="testuser",
            email="testuser@anemail.com",
            password="password444",
        )
        self.client.login(username="testuser", password="password444")


    # test valid user registration
    def test_registration_valid(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "newuser",
                "email": "newuser@anemail.com",
                "password1": "astrongpassword",
                "password2": "astrongpassword",
            },
        )
        self.assertEqual(response.status_code, 302)  # Check for redirect after success
        self.assertTrue(
            NovaUser.objects.filter(username="newuser").exists()
        )  # User should be created

    # test invalid user registration
    def test_registration_invalid(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "",
                "email": "invalid-email",
                "password1": "aweirdpassword",
                "password2": "nomatchpassword",
            },
        )
        self.assertEqual(response.status_code, 200)  # Check for redirect after success
        self.assertContains(
            response, "The two password fields didn’t match.", status_code=200
        )

    # test valid user login
    def test_user_login_valid(self):
        response = self.client.post(
            reverse("login"),
            {
                "username": "testuser",
                "password": "password444",
            },
        )
        self.assertEqual(response.status_code, 302)  # Check for redirect after success
        self.assertRedirects(response, reverse("home"))

    # test invalid user login
    def test_user_login_invalid(self):
        response = self.client.post(
            reverse("login"),
            {
                "username": "testuser",
                "password": "invalidpassword",
            },
        )
        self.assertEqual(response.status_code, 200)  # No redirect. remains in login page
        self.assertContains(response, "Invalid username or password", status_code=200)

    # test case for logout:
    def test_user_logout(self):
        # login user.
        self.client.login(username="testuser", password="password444")
        # logout request.
        response = self.client.get(reverse("logout"))
        self.assertEqual(response.status_code, 302)  # Check for redirect after success
        self.assertRedirects(response, reverse("login"))

    # Test access for logged out users cannot access ptotected pages
    def test_home_page_requires_login(self):
        """
        Test that the page requires login and redirects unauthenticated user to login page
        """
        self.client.logout()
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 302)
        # redirect should include "next" parameter in the url
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('home')}")


class SurfSpotTests(TestCase):
    def setUp(self):
        #create a user and log in
        self.user = NovaUser.objects.create_user(
            username="testuser",
            email="testuser@anemail.com",
            password="password444",
        )
        self.client.login(username="testuser", password="password444")

        # Create multiple surf spots for pagination tests
        for i in range(10):
            SurfSpot.objects.create(
                title=f"Surf Spot {i+1}",
                location=f"Location {i+1}",
                description="A great spot.",
                best_seasons="Summer",
                user=self.user,
            )

    def test_pagination(self):
        """
        Test that pagination returns the correct number of posts per page
        and navigates between pages
        """
        #Ensure the correct number of surf spots are created
        print(f"Total surf spots: {SurfSpot.objects.count()}") # Debugging total count

        # Fetch the first page of surf spots
        response = self.client.get(reverse("home") + "?page=1")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Surf Spot 1")
        self.assertContains(response, "Surf Spot 5")
        self.assertNotContains(response, "Surf Spot 6") #Should not be on page 1

        # Fetch the second page of surf spots
        response = self.client.get(reverse("home") + "?page=2")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Surf Spot 6")
        self.assertContains(response, "Surf Spot 10")
        self.assertNotContains(response, "Surf Spot 1") #Should not be on page 2


    def test_surf_spot_detail_view(self):
        """
        Test that the detail view returns the correct surf spot details.
        """
        # Fetch the detail view for a specific surf spot
        spot = SurfSpot.objects.first()
        response = self.client.get(reverse("surf_spot_detail", args=[spot.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, spot.title)
        self.assertContains(response, spot.location)
        self.assertContains(response, spot.description)
        self.assertContains(response, spot.best_seasons)
        self.assertContains(response, spot.user.username)


    def test_create_surf_spot_valid(self):
        response = self.client.post(
            reverse("home"),
            {
                "title": "Valid title",
                "location": "Valid location",
                "description": "A good spot",
                "best_seasons": "Summer",
            },
        )
        self.assertEqual(response.status_code, 302) #redirect after success
        self.assertTrue(SurfSpot.objects.filter(title="Valid title").exists())

    def test_create_surf_spot_invalid_title(self):
        response = self.client.post(
            reverse("home"),
            {
                "title": "T" * 51, # Exceeding max_lenght
                "location": "Valid location",
                "description": "A good spot.",
                "best_seasons": "Summer",
            },
        )
        self.assertEqual(response.status_code, 200) # Stays on the page
        self.assertContains(response, "Ensure this value has at most 50 characters")

    # test valid user registration
    def test_end_to_end_flow(self): 
        #register a new user
        self.client.logout()
        response = self.client.post(
            reverse("register"),
            {
                "username": "newuser",
                "email": "newuser@example.com",
                "password1": "password123",
                "password2": "password123",
            },
        )
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertTrue(NovaUser.objects.filter(username="newuser").exists())
    
        # Login as the new user
        self.client.login(username="newuser", password="password123")

        # Create a new surfspot
        response = self.client.post(
            reverse("home"),
            {
                "title": "New Spot",
                "location": "New location",
                "description": "A great spot for surfing.",
                "best_seasons": "Winter",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(SurfSpot.objects.filter(title="New Spot").exists())

        # Verify the surf spot appears in the homepage
        response = self.client.get(reverse("home"))
        self.assertContains(response, "New Spot")
        self.assertContains(response, "A great spot for surfing.")

    