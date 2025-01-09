
from django.conf import settings
from django.http import HttpResponse
from django.contrib import messages
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth import update_session_auth_hash
from fpdf import FPDF, HTMLMixin
from django.utils.timezone import now
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
import random
from django.urls import reverse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.contrib.auth import login as auth_login
from functools import wraps
from django.http import HttpResponseForbidden
from django.contrib.auth.models import User
from django.http import JsonResponse
from .models import Flights
from .models import BookedFlights
from .models import Archive
from .models import UserAdditionalInfo
from .models import TicketSales
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Q
import random
import string
import time
from io import BytesIO
from weasyprint import HTML
import os
# Create your views here.





def user_login(request):
    # Ensure "admin" and "gatekeep" roles exist
    accounts = [
        {"email": "adminbook@gmail.com", "username": "Mabuhay Admin", "first_name": "Admin", "last_name": "Book", "password": "mabuhayadmin", "role": "admin"},
        {"email": "gatekeepbook@gmail.com", "username": "Mabuhay Gatekeep", "first_name": "Gate", "last_name": "Keep", "password": "mabuhaygatekeep", "role": "gatekeep"},
        {"email": "restaurantorder@gmail.com", "username": "Restaurant Admin", "first_name": "Restaurant", "last_name": "Order", "password": "mabuhayadmin1", "role": "admin"},
        {"email": "hotelreservation@gmail.com", "username": "Hotel Admin", "first_name": "Hotel", "last_name": "Reservation", "password": "mabuhayadmin2", "role": "admin"},
        {"email": "onlinevote@gmail.com", "username": "Vote Admin", "first_name": "Online", "last_name": "Vote", "password": "mabuhayadmin3", "role": "admin"},
        {"email": "librarymanage@gmail.com", "username": "Library Admin", "first_name": "Library", "last_name": "Manage", "password": "mabuhayadmin4", "role": "admin"},
        {"email": "vetclinic@gmail.com", "username": "Vet Admin", "first_name": "Vet", "last_name": "Clinic", "password": "mabuhayadmin5", "role": "admin"},
        {"email": "elemenroll@gmail.com", "username": "Elemroll Admin", "first_name": "Elementary", "last_name": "Enrollment", "password": "mabuhayadmin6", "role": "admin"},
        {"email": "laboratoryborrow@gmail.com", "username": "Lab Admin", "first_name": "Laboratory", "last_name": "Borrow", "password": "mabuhayadmin7", "role": "admin"},
        {"email": "hiringsystem@gmail.com", "username": "Hiring Admin", "first_name": "Hiring", "last_name": "System", "password": "mabuhayadmin8", "role": "admin"},
    ]

    for account in accounts:
        user, created = User.objects.get_or_create(
            email=account['email'],
            defaults={
                'username': account['username'],
                'first_name': account['first_name'],
                'last_name': account['last_name'],
            }
        )
        if created:
            user.set_password(account['password'])  # Set hashed password
            user.save()

        # Ensure UserAdditionalInfo exists and update role
        additional_info, _ = UserAdditionalInfo.objects.get_or_create(
            user=user,
            defaults={'user_role': account['role'], 'is_default_password': True}  # Set default password flag
        )
        if not created and additional_info.user_role != account['role']:
            additional_info.user_role = account['role']
            additional_info.save()

    # Handle login
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Authenticate the user
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            user = None

        if user:
            # Authenticate using the username
            user = authenticate(request, username=user.username, password=password)

        if user is not None:
            login(request, user)  # Log in the user

            # Check if the user is using a default password
            additional_info = getattr(user, 'additional_info', None)
            if additional_info and additional_info.is_default_password:
                return redirect('force_password_change')  # Redirect to the password change page

            # Store user's name and role in the session
            request.session['user_name'] = user.first_name
            user_role = additional_info.user_role if additional_info else None
            request.session['user_role'] = user_role
            if user_role == 'admin':
                return redirect('admin1')
            elif user_role == 'gatekeep':
                return redirect('gatekeep')
            else:
                return redirect('front')

        return render(request, 'Login.html', {'error': 'Invalid email or password'})

    return render(request, 'Login.html')


def user_logout(request):
    logout(request)
    request.session.flush()
    return redirect('login')


def force_password_change(request):
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if new_password == confirm_password:
            user = request.user
            user.set_password(new_password)
            user.save()

            # Update the is_default_password flag
            user.additional_info.is_default_password = False
            user.additional_info.save()

            update_session_auth_hash(request, user)  # Keep the user logged in
            return redirect('login')

        else:
            return render(request, 'forced_password_change.html', {'error': 'Passwords do not match'})

    return render(request, 'forced_password_change.html')
def register(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        contact_num = request.POST.get('contact_num')

        # Validate passwords match
        if password != confirm_password:
            return render(request, 'Signup.html', {'error': 'Passwords do not match'})

        # Check if email is already in use
        if User.objects.filter(email=email).exists():
            return render(request, 'Signup.html', {'error': 'Email already in use'})

        # Generate OTP
        otp = random.randint(100000, 999999)

        # Save data temporarily in the session
        request.session['temp_user_data'] = {
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'password': password,
            'otp': otp,
            'contact_num' : contact_num
        }

        # Design the email
        email_subject = "Mabuhay Airlines - OTP Verification"
        email_body = f"""
        <html>
            <body style="font-family: Arial, sans-serif;">
                <h2 style="color: #4CAF50;">Welcome to Mabuhay Airlines, {first_name}!</h2>
                <p>Thank you for signing up. To complete your registration, please use the OTP below:</p>
                <h3 style="color: #333;">Your OTP: <strong>{otp}</strong></h3>
                <p style="color: #666;">This OTP is valid for 10 minutes. Please do not share it with anyone.</p>
                <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
                <p style="font-size: 12px; color: #999;">
                    If you did not attempt to register, please ignore this email or contact our support team.
                </p>
            </body>
        </html>
        """

        # Send OTP email
        try:
            email_message = EmailMessage(
                email_subject,
                email_body,
                settings.DEFAULT_FROM_EMAIL,
                [email],
            )
            email_message.content_subtype = 'html'  # Specify the email content type as HTML
            email_message.send()
        except Exception as e:
            return render(request, 'Signup.html', {'error': 'Failed to send OTP. Please try again later.'})

        # Redirect to OTP verification page
        return redirect('verify_otp')

    return render(request, 'Signup.html')

#OTP
def verify_otp(request):
    if request.method == 'POST':
        user_otp = request.POST.get('otp')
        temp_user_data = request.session.get('temp_user_data')

        if not temp_user_data:
            messages.error(request, "Session expired. Please register again.")
            return redirect('register')

        # Validate OTP
        if str(temp_user_data['otp']) == user_otp:
            # Create the user only if OTP is valid
            user = User.objects.create_user(
                username=temp_user_data['email'],
                email=temp_user_data['email'],
                password=temp_user_data['password'],
                first_name=temp_user_data['first_name'],
                last_name=temp_user_data['last_name'],
            )

            # Create or update UserAdditionalInfo for the user
            user_additional_info, created = UserAdditionalInfo.objects.get_or_create(
                user=user,
                defaults={
                    'user_role': 'client',
                    'is_default_password': False,  # Mark as not using the default password
                }
            )

            # If not created, update the fields manually (just in case)
            if not created:
                user_additional_info.user_role = 'client'
                user_additional_info.is_default_password = False
                user_additional_info.save()

            # Clear session data
            del request.session['temp_user_data']

            messages.success(request, "Registration successful! Please log in.")
            return redirect('login')
        else:
            # If OTP is invalid, show an error message
            messages.error(request, "Invalid OTP. Please try again.")
            return render(request, 'otp.html')

    return render(request, 'otp.html')

#para sa permission ni admin
def admin_required(view_func):
    """
    Decorator to restrict access to views for users with an 'admin' role.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Check if the user is authenticated
        if request.user.is_authenticated:
            # Check if the user has the 'admin' role
            try:
                if request.user.additional_info.user_role == 'admin':
                    return view_func(request, *args, **kwargs)
                else:
                    return HttpResponseForbidden("You do not have permission to access this page.")
            except AttributeError:
                # Handle cases where additional_info or user_role is missing
                return HttpResponseForbidden("User role information is missing.")
        else:
            # Redirect to login if the user is not authenticated
            return redirect('login')

    return _wrapped_view
def gatekeep_required(view_func):
    """
    Decorator to restrict access to views for users with an 'admin' role.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Check if the user is authenticated
        if request.user.is_authenticated:
            # Check if the user has the 'admin' role
            try:
                if request.user.additional_info.user_role == 'gatekeep':
                    return view_func(request, *args, **kwargs)
                else:
                    return HttpResponseForbidden("You do not have permission to access this page.")
            except AttributeError:
                # Handle cases where additional_info or user_role is missing
                return HttpResponseForbidden("User role information is missing.")
        else:
            # Redirect to login if the user is not authenticated
            return redirect('login')

    return _wrapped_view
def client_required(view_func):
    """
    Decorator to restrict access to views for users with an 'admin' role.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Check if the user is authenticated
        if request.user.is_authenticated:
            # Check if the user has the 'admin' role
            try:
                if request.user.additional_info.user_role == 'client':
                    return view_func(request, *args, **kwargs)
                else:
                    return HttpResponseForbidden("You do not have permission to access this page.")
            except AttributeError:
                # Handle cases where additional_info or user_role is missing
                return HttpResponseForbidden("User role information is missing.")
        else:
            # Redirect to login if the user is not authenticated
            return redirect('login')

    return _wrapped_view
#another table sa useradditionalinfo
@receiver(post_save, sender=User)
def create_user_additional_info(sender, instance, created, **kwargs):
    if created:
        UserAdditionalInfo.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_additional_info(sender, instance, **kwargs):
    instance.additional_info.save()
@client_required
def front(request):
    # Retrieve the name from session (if needed)
    user_name = request.session.get('user_name', 'Guest')  # Default to 'Guest' if not found

    # Fetch additional info (e.g., profile picture)
    additional_info = UserAdditionalInfo.objects.filter(user=request.user).first()
    profile_picture_url = (
        additional_info.profile_picture.url if additional_info and additional_info.profile_picture 
        else '/static/Media/default_profile.png'  # Default profile picture
    )

    # Get the current date
    today = now().date()

    # Query for the nearest future flight
    nearest_flight = (
        BookedFlights.objects.filter(user=request.user, departure__gte=today)  # Flights departing today or later
        .order_by('departure')  # Order by departure date (ascending)
        .first()  # Get the first flight (nearest date)
    )

    # Context to pass to the template
    context = {
        'user_name': user_name,
        'profile_picture_url': profile_picture_url,
        'nearest_flight': nearest_flight,
    }

    return render(request, 'Flight_front_page(no_css).html', context)

@client_required
def result(request):
    additional_info = UserAdditionalInfo.objects.filter(user=request.user).first()
    profile_picture_url = (
        additional_info.profile_picture.url if additional_info and additional_info.profile_picture 
        else '/static/Media/default_profile.png'  # Default profile picture
    )
    
    if request.method == 'GET':
        # Get search parameters from the request
        from_city = request.GET.get('from')
        to_city = request.GET.get('to')
        departure_date = request.GET.get('departure-date')
        return_date = request.GET.get('return-date')

        # Parse dates to datetime objects
        if departure_date:
            departure_date = datetime.strptime(departure_date, '%Y-%m-%d')
        if return_date:
            return_date = datetime.strptime(return_date, '%Y-%m-%d')

        # Create base filter criteria
        filter_criteria = {
            'origin': from_city,
            'destination': to_city,
            'departure': departure_date,
            'available_seats__gt': 0  # Only include flights with available seats > 0
        }

        # Conditionally add the return_date filter based on its value
        if return_date:
            filter_criteria['return_date'] = return_date
        else:
            filter_criteria['return_date__isnull'] = True

        # Query flights based on the filter criteria
        flights = Flights.objects.filter(**filter_criteria)

        # Pass the flights to the result template
        context = {'flights': flights,
                   'profile_picture_url': profile_picture_url,}
        return render(request, 'Flight_result(no_css).html', context)

    return render(request, 'Flight_result(no_css).html')
def generate_ticket_number():
    """Generate a random 6-digit ticket number."""
    return ''.join(random.choices(string.digits, k=6))

def generate_seat_number():
    """Generate a random seat number like 'A1', 'B3', etc."""
    row = random.choice(string.ascii_uppercase[:6])  # Choose between A-F
    seat = random.randint(1, 30)  # Seat numbers 1-30
    return f"{row}{seat}"


def generate_reference_number():
    """Generate a random 8-character alphanumeric reference number."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
@client_required
def personalInfo(request, flight_id=None):
    # Retrieve the logged-in user
    additional_info = UserAdditionalInfo.objects.filter(user=request.user).first()
    profile_picture_url = (
        additional_info.profile_picture.url if additional_info and additional_info.profile_picture 
        else '/static/Media/default_profile.png'  # Default profile picture
    )
    
    user = request.user
    user_name = user.get_full_name() if user.is_authenticated else 'Guest'

    # Get the selected flight or return a 404 error if not found
    flight = get_object_or_404(Flights, id=flight_id) if flight_id else None

    # Get the selected seat class from the request query parameter
    seat_class = request.GET.get('seat_class', 'economy')  # Default to economy if not provided

    # Adjust price based on seat class
    if seat_class == 'premium economy':
        price = flight.discounted_price * 1.3  # 30% more for Premium Economy
    elif seat_class == 'business':
        price = flight.discounted_price * 2.0  # 200% more for Business Class
    else:
        price = flight.discounted_price  # Economy price as per original

    if request.method == 'POST':
        # Ensure seats are available for booking
        card_number = request.POST.get('card_number')
        
        if flight.available_seats > 0:
            # Generate ticket, seat, and reference numbers
            ticket_no = generate_ticket_number()
            seat_num = generate_seat_number()  # Generate a unique seat number
            if not seat_num:
                return render(
                    request,
                    'personal_info.html',
                    {'flight': flight, 'error': 'Failed to generate a valid seat number.', 'user_name': user_name}
                )

            reference_num = generate_reference_number()
            amount = price  # Use calculated price based on seat class
            payment_status = 'Paid'

            # Create and save the new booking
            new_booking = BookedFlights(
                user=user,  # Associate the booking with the logged-in user
                created_by=flight.created_by,  # Save the admin who created the flight
                ticket_no=ticket_no,
                departure=flight.departure,
                arrival=flight.arrival,
                departure_time=flight.departure_time,
                arrival_time=flight.arrival_time,
                return_date=flight.return_date,
                origin=flight.origin,
                destination=flight.destination,
                seat_num=seat_num,
                flight_num=flight.flight_number,
                seat_type=seat_class,
                reference_num=reference_num,
                amount=amount,
                payment_status=payment_status,
                payment_date=timezone.now(),
                flight_status='Waiting',
            )
            new_booking.save()

            # Decrease the available seats by 1 after a successful booking
            flight.available_seats -= 1
            flight.save()
            
            payment_sales = TicketSales(
                user=user,
                card_number=card_number,
                flight_num=flight.flight_number,
                payment_amount=amount,
                return_date=flight.return_date,
                arrival=flight.arrival,
            )
            payment_sales.save()

            return redirect('front')  # Redirect to the front page or another relevant page
        else:
            # Render error if no seats are available
            return render(
                request,
                'personal_info.html',
                {'flight': flight, 'error': 'No available seats left.', 'user_name': user_name}
            )

    # Context for rendering the template
    context = {
        'flight': flight,
        'price': price,  # Pass the calculated price based on seat class
        'seat_class': seat_class,  # Pass the selected seat class
        'profile_picture_url': profile_picture_url,
        'user_name': user_name  # Include user's name for the template
    }
    return render(request, 'personal_info.html', context)
            
    
def explore(request):
    return render(request, 'Explore.html')

@client_required
def promos(request):
    # Retrieve the name from the session (if needed)
    # Fetch additional info (e.g., profile picture)
    additional_info = UserAdditionalInfo.objects.filter(user=request.user).first()
    profile_picture_url = (
        additional_info.profile_picture.url if additional_info and additional_info.profile_picture 
        else '/static/Media/default_profile.png'  # Default profile picture
    )
    
    user_name = request.session.get('user_name', 'Guest')  # Default to 'Guest' if not found
    
    # Retrieve flights with a non-null and non-zero discount value and a future departure date
    today = timezone.now().date()
    discounted_flights = Flights.objects.filter(discount__isnull=False) \
                                        .exclude(discount=0) \
                                        .filter(departure__gte=today)
    
    # Combine user_name and discounted_flights into a single context
    context = {
        'user_name': user_name,
        'profile_picture_url': profile_picture_url,
        'discounted_flights': discounted_flights
    }
    
    return render(request, 'promos_user.html', context)
@admin_required
def adminpromos(request):
    # Get the current date
    today = timezone.now().date()

    # Filter flights with no discount, only include current or future flights, and filter by the logged-in admin
    flights = Flights.objects.filter(
        discount=0,
        departure__gte=today,
        created_by=request.user  # Filter by the logged-in admin
    )

    # Calculate duration for each flight and add it as a new attribute
    for flight in flights:
        # Calculate duration as the difference between arrival and departure dates
        duration = flight.arrival - flight.departure
        hours, remainder = divmod(duration.total_seconds(), 3600)
        minutes = remainder // 60
        flight.duration = f"{int(hours)}h {int(minutes)}m"  # Store formatted duration

    return render(request, 'promos.html', {'flights': flights})

@admin_required
def adminpromos2(request, flight_id):
    flight = get_object_or_404(Flights, id=flight_id)

    if request.method == 'POST':
        # Get the stocks (which will be used for discount_usage) and discount from the form
        stock = int(request.POST.get('stocks'))  # Value from the stocks dropdown
        discount = int(request.POST.get('discounts'))  # Value from the discount input field

        # Update the discount_usage with the value of the stocks
        flight.discount_usage = stock  # Set the discount_usage to the selected stock value
        flight.discount = discount  # Update the discount
        flight.save()  # This will automatically calculate the discounted price

        # Redirect to the promotions page or any other page as needed
        return redirect('adminpromos')  # Replace with your redirect logic

    # If the request is not a POST, render the page with the flight data
    return render(request, 'promos2.html', {'flight': flight})
@gatekeep_required
def gatekeep(request):
    # Check if the request is a POST request to confirm boarding
    if request.method == 'POST':
        # Get the ticket number from the form
        ticket_no = request.POST.get('ticket_no')
        
        # Retrieve the flight based on the ticket number
        flight = get_object_or_404(BookedFlights, ticket_no=ticket_no)
        
        # Get the user associated with the flight
        user = flight.user
        
        # Update the flight status to 'Boarded'
        flight.flight_status = "Boarded"
        flight.save()

        # Copy the boarded flight to the Archive table, including user_id and last_name
        archive_entry = Archive(
            user=user,  # Associate the user with the archived flight
            flight_num=flight.flight_num,
            ticket_num=flight.ticket_no,
            last_name=user.last_name if user else "Unknown",  # Use "Unknown" if user is None
            seat_type=flight.seat_type,
            boarded="Yes"  # Mark as boarded in the Archive
        )
        archive_entry.save()

        # Delete the boarded flight from the BookedFlights table
        flight.delete()

        # Redirect back to the same page to refresh the data
        return redirect('gatekeep')
    
    # Get the current date and time
    current_datetime = datetime.now().date()
    
    # Check if a ticket number is provided in the GET request
    ticket_no_search = request.GET.get('ticket_no')
    if ticket_no_search:
        # Filter the flight with the provided ticket number
        flights = BookedFlights.objects.filter(ticket_no=ticket_no_search, departure=current_datetime).select_related('user')
    else:
        # If no ticket number is provided, show confirmed flights by default
        flights = BookedFlights.objects.filter(flight_status='Confirmed', departure=current_datetime).select_related('user')
        
    # Fetch user additional info for passenger names
    flights_with_names = []
    for flight in flights:
        user = flight.user
        additional_info = UserAdditionalInfo.objects.filter(user=user).first()
        first_name = user.first_name if user else ""
        last_name = user.last_name if user else ""
        if additional_info:
            first_name = additional_info.user.first_name or first_name
            last_name = additional_info.user.last_name or last_name
        
        # Append additional information to the flight
        flights_with_names.append({
            'flight': flight,
            'first_name': first_name,
            'last_name': last_name,
        })
    
    current_datetime = datetime.now()
    
    context = {
        'flights_with_names': flights_with_names,
        'current_datetime': current_datetime
    }
    
    # Pass the current date and time and flights to the template
    return render(request, 'gate.html', context)

flight_durations = {
    ('Manila', 'Cebu'): 1.5,
    ('Manila', 'Davao'): 2,
    ('Manila', 'Clark'): 1,
    ('Manila', 'Iloilo'): 1.5,
    ('Cebu', 'Manila'): 1.5,
    ('Cebu', 'Davao'): 1,
    ('Cebu', 'Clark'): 1.5,
    ('Cebu', 'Iloilo'): 1,
    ('Davao', 'Manila'): 2,
    ('Davao', 'Cebu'): 1,
    ('Davao', 'Clark'): 2,
    ('Davao', 'Iloilo'): 1.5,
    ('Clark', 'Manila'): 1,
    ('Clark', 'Cebu'): 1.5,
    ('Clark', 'Davao'): 2,
    ('Clark', 'Iloilo'): 1.5,
    ('Iloilo', 'Manila'): 1.5,
    ('Iloilo', 'Cebu'): 1,
    ('Iloilo', 'Davao'): 1.5,
    ('Iloilo', 'Clark'): 1.5,
}
@admin_required
def admin1(request):
    if request.method == 'POST':
        # Define flight durations inside the function
        flight_durations = {
            ('Manila', 'Cebu'): 1.5,
            ('Manila', 'Davao'): 2,
            ('Manila', 'Clark'): 1,
            ('Manila', 'Iloilo'): 1.5,
            ('Cebu', 'Manila'): 1.5,
            ('Cebu', 'Davao'): 1,
            ('Cebu', 'Clark'): 1.5,
            ('Cebu', 'Iloilo'): 1,
            ('Davao', 'Manila'): 2,
            ('Davao', 'Cebu'): 1,
            ('Davao', 'Clark'): 2,
            ('Davao', 'Iloilo'): 1.5,
            ('Clark', 'Manila'): 1,
            ('Clark', 'Cebu'): 1.5,
            ('Clark', 'Davao'): 2,
            ('Clark', 'Iloilo'): 1.5,
            ('Iloilo', 'Manila'): 1.5,
            ('Iloilo', 'Cebu'): 1,
            ('Iloilo', 'Davao'): 1.5,
            ('Iloilo', 'Clark'): 1.5,
        }

        # Retrieve form data from the POST request
        flight_type = request.POST.get('flight-type')
        origin = request.POST.get('from')
        destination = request.POST.get('to')
        departure_date = request.POST.get('departure-date')
        departure_time = request.POST.get('departure-time')
        return_date = request.POST.get('return-date', None)
        return_time = request.POST.get('return-time', None)
        price = request.POST.get('price')

        # Validate and convert price input
        if not price or not price.isdigit():
            price = 0
        else:
            price = int(price)

        # Autogenerate flight number
        flight_number = f"{origin[:3].upper()}{destination[:3].upper()}{random.randint(1000, 9999)}"

        # Parse departure date and time separately
        departure_date_obj = datetime.strptime(departure_date, '%Y-%m-%d').date()
        departure_time_obj = datetime.strptime(departure_time, '%H:%M').time()

        # Combine departure date and time into a full datetime object
        departure_datetime = datetime.combine(departure_date_obj, departure_time_obj)

        # Get the flight duration from the dictionary
        duration = flight_durations.get((origin, destination))
        if duration is None:
            # If no duration is found for the route, set a default duration (e.g., 2 hours)
            duration = 2

        # Calculate the arrival time based on the flight duration
        arrival_datetime = departure_datetime + timedelta(hours=duration)
        arrival_date_obj = arrival_datetime.date()
        arrival_time_obj = arrival_datetime.time()

        # If return_date and return_time are provided, convert them into appropriate objects
        return_date_obj = None
        return_time_obj = None
        if return_date:
            return_date_obj = datetime.strptime(return_date, '%Y-%m-%d').date()
        if return_time:
            return_time_obj = datetime.strptime(return_time, '%H:%M').time()

        # Create and save the new flight record, with the logged-in admin
        new_flight = Flights(
            flight_number=flight_number,
            price=price,
            discount=0,  # Default discount
            flight_type=flight_type,
            departure=departure_date_obj,
            departure_time=departure_time_obj,
            arrival=arrival_date_obj,
            arrival_time=arrival_time_obj,
            origin=origin,
            destination=destination,
            return_date=return_date_obj,
            return_time=return_time_obj,
            available_seats=200,
            created_by=request.user  # Save the logged-in admin
        )
        new_flight.save()

        # Redirect to the flight list page after saving
        return redirect('admin2')

    # Render the form if GET request
    return render(request, 'admin_module.html')


#para sa html to pdf

@admin_required
def admin2(request): 
    # Get the currently logged-in admin
    admin_user = request.user

    if request.method == 'POST':
        # Get the ticket number from the form
        ticket_no = request.POST.get('ticket_no')

        # Retrieve the booked flight based on the ticket number
        flight = get_object_or_404(BookedFlights, ticket_no=ticket_no)

        # Update the flight status to 'Confirmed'
        flight.flight_status = "Confirmed"
        flight.save()

    

        # Render the HTML template with dynamic data using Django's template system
        rendered_html = render_to_string(
            'ticket_template.html',  # Path to your HTML file
            {
                'last_name': flight.user.last_name,
                'first_name': flight.user.first_name,
                'reference_num': flight.reference_num,
                'ticket_no': flight.ticket_no,
                'payment_status': "Confirmed",
                'payment_date': flight.payment_date,
                'flight_num': flight.flight_num,
                'seat_num': flight.seat_num,
                'seat_type': flight.seat_type,
                'origin': flight.origin,
                'destination': flight.destination,
                'departure': flight.departure,
                'departure_time': flight.departure_time,
                'arrival': flight.arrival,
                'arrival_time': flight.arrival_time,
                'return_date': flight.return_date,
                'amount': flight.amount,
            }
        )

        # Create PDF using WeasyPrint
        pdf_file = HTML(string=rendered_html).write_pdf()
        

        # Ensure the media directory exists
        media_dir = settings.MEDIA_ROOT
        if not os.path.exists(media_dir):
            os.makedirs(media_dir)

        # Save the PDF to the media directory
        pdf_path = os.path.join(media_dir, f"{ticket_no}_receipt.pdf")
        with open(pdf_path, 'wb') as f:
            f.write(pdf_file)

        # Send Email
        email = EmailMessage(
            "Your Ticket Confirmation",
            "Please find attached your ticket receipt.",
            "your_email@example.com",  # Replace with the sender's email
            [flight.user.email],  # Send email to the user
        )
        email.attach_file(pdf_path)
        email.send()

        # Redirect back to refresh the page
        return redirect('admin2')

    # If GET request, retrieve booked flights created by the current admin
    flights = BookedFlights.objects.filter(
        flight_num__in=Flights.objects.filter(created_by=admin_user).values_list('flight_number', flat=True),
        flight_status='Waiting'
    ).select_related('user')

    # Pass the flight data to the template
    return render(request, 'Admin_module2.html', {'flights': flights})

def forgot(request):
    return render(request, 'Fogot_pass.html')

def otp(request):
    return render(request, 'otp.html')



def get_provinces_and_cities(request):
    provinces = [
        "Abra", "Albay", "Antique", "Apayao", "Aurora", "Basilan", "Bataan",
        "Batanes", "Batangas", "Benguet", "Biliran", "Bohol", "Bukidnon",
        "Bulacan", "Cagayan", "Camarines Norte", "Camarines Sur", "Camiguin",
        "Capiz", "Catanduanes", "Cavite", "Cebu", "Compostela Valley",
        "Cotabato", "Davao del Norte", "Davao del Sur", "Davao Occidental",
        "Eastern Samar", "Guimaras", "Ifugao", "Ilocos Norte", "Ilocos Sur",
        "Iloilo", "Isabela", "Kalinga", "La Union", "Laguna", "Lanao del Norte",
        "Lanao del Sur", "Leyte", "Maguindanao", "Marinduque", "Masbate",
        "Misamis Occidental", "Misamis Oriental", "Mountain Province", "Negros Occidental",
        "Negros Oriental", "Northern Samar", "Nueva Ecija", "Nueva Vizcaya",
        "Occidental Mindoro", "Oriental Mindoro", "Palawan", "Pampanga",
        "Pangasinan", "Quezon", "Quirino", "Rizal", "Romblon", "Samar",
        "Sarangani", "Siquijor", "Sorsogon", "South Cotabato", "Southern Leyte",
        "Sultan Kudarat", "Surigao del Norte", "Surigao del Sur", "Tarlac",
        "Tawi-Tawi", "Zambales", "Zamboanga del Norte", "Zamboanga del Sur", "Zamboanga Sibugay"
    ]
    # Example city list; customize as needed
    cities = [
        "Quezon City", "Manila", "Cebu City", "Davao City", "Makati", 
        "Caloocan", "Taguig", "Pasig", "Iloilo City", "Baguio", 
        "Cagayan de Oro", "Zamboanga City", "San Fernando", "Las Piñas",
        "Mandaluyong", "Marikina", "Valenzuela", "Muntinlupa"
    ]
    
    return JsonResponse({'provinces': provinces, 'cities': cities})

def search_flights(request):
    flights = []
    if request.method == 'GET':
        # Get search parameters from request
        origin = request.GET.get('origin', '').strip()
        destination = request.GET.get('destination', '').strip()
        departure_date = request.GET.get('departure_date', '').strip()
        
        # Build a query based on provided parameters
        filters = Q()
        if origin:
            filters &= Q(origin__icontains=origin)
        if destination:
            filters &= Q(destination__icontains=destination)
        if departure_date:
            # Assuming departure_date is in 'YYYY-MM-DD' format
            filters &= Q(departure_time__date=departure_date)

        # Query the database for available flights
        flights = Flights.objects.filter(filters, available_seats__gt=0)  # Ensure there are available seats

    return redirect('result', {'flights': flights})

@client_required
def user_prof(request):
    user_name = request.user.first_name
    user_last_name = request.user.last_name
    user_email = request.user.email

    # Retrieve additional user info
    additional_info = UserAdditionalInfo.objects.filter(user=request.user).first()
    profile_picture_url = (
        additional_info.profile_picture.url if additional_info and additional_info.profile_picture 
        else '/static/Media/default_profile.png'  # Default profile picture
    )

    contact_number = additional_info.contact_number if additional_info else ''

    # Retrieve recent flights
    recent_flights = Archive.objects.filter(user=request.user).order_by('-id')[:10]
    upcoming_flights = BookedFlights.objects.filter(user=request.user).order_by('departure')[:10]


    if request.method == 'POST':
        # Check if additional info exists, create if not
        if not additional_info:
            additional_info = UserAdditionalInfo(user=request.user)

        # Handle profile picture upload
        if 'profile_picture' in request.FILES:
            profile_picture = request.FILES['profile_picture']
            additional_info.profile_picture = profile_picture  # Assign uploaded picture

        # Update contact number
        contact_number = request.POST.get('contact_number')
        if contact_number:
            additional_info.contact_number = contact_number

        # Update user fields (first name, last name)
        first_name = request.POST.get('first_name', request.user.first_name)
        last_name = request.POST.get('last_name', request.user.last_name)

        request.user.first_name = first_name
        request.user.last_name = last_name
        request.user.save()

        additional_info.save()  # Save the additional info including the profile picture

        # Redirect to prevent duplicate form submissions
        return redirect('user_prof')

    return render(request, 'user_profile.html', {
        'user_name': user_name,
        'user_last_name': user_last_name,
        'user_email': user_email,
        'profile_picture_url': profile_picture_url,
        'user_contact_number': contact_number,
        'recent_flights': recent_flights,
        'upcoming_flights': upcoming_flights,
    })
@admin_required
def flighthistory(request):
    # Get the flight number from the GET request for sorting
    flight_num = request.GET.get('flight_num', None)

    # Get the current month and year
    current_month = datetime.now().month
    current_year = datetime.now().year

    # Retrieve archived flights for the current month
    if flight_num:
        archived_flights = Archive.objects.filter(
            flight_num=flight_num
        )
    else:
        archived_flights = Archive.objects.all()

    # Get all unique flight numbers for the dropdown list
    flight_numbers = Archive.objects.values_list('flight_num', flat=True).distinct()

    # Calculate total income for the current month
    total_income = TicketSales.objects.filter(
        arrival__year=current_year,
        arrival__month=current_month
    ).aggregate(Sum('payment_amount'))['payment_amount__sum'] or 0

    # Pass the data to the template
    return render(request, 'flights_history.html', {
        'archived_flights': archived_flights,
        'flight_numbers': flight_numbers,
        'total_income': total_income,
    })

def Front_Explore(request):
    return render(request, 'NEW_FRONT.html')

#emails
def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get('email')

        try:
            # Fetch the user using the default User model
            user = User.objects.get(email=email)

            # Generate the password reset token
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(str(user.pk).encode())  # This encodes the user ID
            current_site = get_current_site(request).domain
            # Generate the reset password URL
            reset_link = f"http://{current_site}/reset-password/{uid}/{token}/"

            # HTML email content
            email_subject = 'Password Reset Request'
            email_body = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Password Reset</title>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        margin: 0;
                        padding: 0;
                        background-color: #f5f5f5;
                    }}
                    .container {{
                        width: 100%;
                        max-width: 600px;
                        margin: 0 auto;
                        background-color: #ffffff;
                        padding: 20px;
                        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                    }}
                    h1 {{
                        color: #333;
                        text-align: center;
                    }}
                    p {{
                        font-size: 1rem;
                        line-height: 1.5;
                        color: #555;
                    }}
                    .button {{
                        display: inline-block;
                        padding: 10px 20px;
                        background-color: #007bff;
                        color: white;
                        text-decoration: none;
                        border-radius: 4px;
                        font-size: 1rem;
                        margin-top: 20px;
                        text-align: center;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>Password Reset Request</h1>
                    <p>Hello {user.first_name},</p>
                    <p>We received a request to reset your password. To reset your password, please click the link below:</p>
                    <p><a href="{reset_link}" class="button">Reset Password</a></p>
                    <p>If you didn't request a password reset, please ignore this email.</p>
                    <p>Best regards,<br>Your Company Name</p>
                </div>
            </body>
            </html>
            """

            # Send the HTML email
            send_mail(
                email_subject,
                '',  # Plain text version of the email (empty since we are sending HTML)
                'from@example.com',  # Set your sender email
                [email],
                fail_silently=False,
                html_message=email_body  # HTML version of the email
            )

            # Show success message to the user
            messages.success(request, 'Password reset link has been sent to your email address.')
            return redirect('login')

        except User.DoesNotExist:
            # Handle the case where the user doesn't exist
            messages.error(request, 'No account found with this email address.')
            return render(request, 'fogot_pass.html')

    # Render the forgot password form
    return render(request, 'fogot_pass.html')

def reset_password(request, encoded_email, token):
    try:
        # Decode the user ID from the encoded email
        try:
            uid = urlsafe_base64_decode(encoded_email).decode('utf-8')
            print(f"Decoded user ID: {uid}")
        except Exception as e:
            print(f"Error decoding email: {e}")
            messages.error(request, 'Invalid or expired reset link.')
            return redirect('login')
        
        # Fetch the user based on the decoded ID
        try:
            user = User.objects.get(pk=uid)
        except User.DoesNotExist:
            print(f"User does not exist for ID: {uid}")
            messages.error(request, 'User not found.')
            return redirect('login')
        
        # Check if the token matches the user's reset token
        if default_token_generator.check_token(user, token):
            if request.method == 'POST':
                new_password = request.POST.get('password')
                confirm_password = request.POST.get('confirm_password')
                print(f"new_password: {new_password}, confirm_password: {confirm_password}")

                # Ensure the passwords match
                if new_password == confirm_password:
                    user.set_password(new_password)  # Set the new password
                    user.save()  # Save the user object
                    print("Password reset successfully!")
                    messages.success(request, 'Your password has been reset successfully!')
                    update_session_auth_hash(request, user)  # Keep the user logged in
                    return redirect('login')  # Redirect to login page
                else:
                    messages.error(request, 'Passwords do not match. Please try again.')

            return render(request, 'pass_reset.html', {'uid': encoded_email, 'token': token})

        else:
            print(f"Invalid token for user: {uid}")
            messages.error(request, 'Invalid or expired reset link.')
            return redirect('login')

    except Exception as e:
        print(f"Error occurred: {e}")
        messages.error(request, 'An error occurred during password reset. Please try again later.')
        return redirect('login')
    
#generate pdf

def generate_pdf_view(request):
    # Fetch data for the report
    current_date = datetime.now()
    current_month = current_date.month
    current_year = current_date.year

    sales = TicketSales.objects.filter(
        arrival__month=current_month,
        arrival__year=current_year
    )

    total_income = sales.aggregate(Sum('payment_amount'))['payment_amount__sum'] or 0

    context = {
        'sales': sales,
        'total_income': total_income,
        'month_name': current_date.strftime('%B'),
    }

    html_string = render_to_string('ticket_report_sale.html', context)

    # Get the static file base URL
    base_url = request.build_absolute_uri('/')  # Use your site's domain as the base URL

    # Generate the PDF
    html = HTML(string=html_string, base_url=base_url)
    pdf_file = BytesIO()
    html.write_pdf(pdf_file)

    response = HttpResponse(pdf_file.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="ticket_sales_report.pdf"'
    return response