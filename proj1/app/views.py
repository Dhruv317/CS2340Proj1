
from django import forms
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import LoginForm
from bson.objectid import ObjectId
from hashlib import sha256
# from mongo_connector import get_mongo_connection
from proj1.mongo_connector import get_mongo_connection
import requests
import os
def hash_password(password):
    """Hash the password using SHA-256 for storing in MongoDB."""
    return sha256(password.encode('utf-8')).hexdigest()


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            # Hash the password before checking in the database
            hashed_password = hash_password(password)

            # Get MongoDB connection
            db = get_mongo_connection()

            # Look for the user in the MongoDB collection
            user = db.users.find_one(
                {'username': username, 'password': hashed_password})

            if user:
                # Assuming you store session data or some form of session management
                request.session['user_id'] = str(
                    user['_id'])  # Save user session
                # Redirect to the home page after successful login
                return redirect('home')
            else:
                messages.error(request, 'Invalid username or password')
    else:
        form = LoginForm()

    return render(request, 'app/login.html', {'form': form})





class RegisterForm(forms.Form):
    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            # Hash the password
            hashed_password = sha256(password.encode('utf-8')).hexdigest()

            # Insert the user into MongoDB
            db = get_mongo_connection()
            db.users.insert_one(
                {'username': username, 'password': hashed_password})

            return redirect('login')
    else:
        form = RegisterForm()

    return render(request, 'app/register.html', {'form': form})


API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')
print(API_KEY)
PLACES_SEARCH_URL = "https://maps.googleapis.com/maps/api/place/textsearch/json"


def restaurants_map(request):
    # Example location: Latitude/Longitude of Empire State Building
    location = "40.748817,-73.985428"
    query = "restaurant"

    # Fetch restaurant data using Google Places API
    restaurants = search_restaurants(query, location)

    # Pass restaurant data and API key to the template
    return render(request, 'app/restaurants_map.html', {'api_key': API_KEY, 'restaurants': restaurants})


def restaurants_near_location(request, lat, lng):
    """
    This view fetches and displays restaurants near a given location (latitude and longitude).
    """
    location = f"{lat},{lng}"  # Format the latitude and longitude
    radius = 1500  # 1500 meters (1.5km) search radius

    # Fetch restaurant data from Google Places API
    restaurants = search_restaurants_nearby(location, radius)

    # Pass the location and restaurant data to the template
    return render(request, 'restaurants_map.html', {
        'api_key': API_KEY,
        'restaurants': restaurants,
        'lat': lat,
        'lng': lng
    })

def search_restaurants(query, location, radius=1500):
    """
    Fetch restaurants based on a query and location using Google Places API.
    """
    try:
        # Prepare the request parameters
        params = {
            'query': query,
            'location': location,
            'radius': radius,
            'key': API_KEY
        }

        # Send the request
        response = requests.get(PLACES_SEARCH_URL, params=params)
        data = response.json()

        # Extract relevant restaurant details
        if data['status'] == 'OK':
            restaurants = []
            for result in data.get('results', []):
                restaurant = {
                    'name': result.get('name'),
                    'address': result.get('formatted_address'),
                    'lat': result['geometry']['location']['lat'],
                    'lng': result['geometry']['location']['lng'],
                    'rating': result.get('rating', 'No rating')
                }
                restaurants.append(restaurant)
            return restaurants
        else:
            return []
    except Exception as e:
        print(f"Error: {e}")
        return []
