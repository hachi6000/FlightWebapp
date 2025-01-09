from django.contrib.auth.models import User
from django.db import models

# Create your models here.
class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    first_name = models.CharField(max_length=100, verbose_name='First Name')
    last_name = models.CharField(max_length=100, verbose_name='Last Name')
    middle_name = models.CharField(max_length=100, verbose_name='Middle Name', blank=True, null=True)
    contact_num = models.CharField(max_length=25, verbose_name='Contact Number')
    email = models.EmailField(max_length=255, unique=True, verbose_name='Email Address')
    user_role = models.CharField(max_length=50, verbose_name='User Role')
    id = models.AutoField(primary_key=True)  # Explicitly define the primary key

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
class UserAdditionalInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='additional_info')
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    contact_number = models.CharField(max_length=15, null=True, blank=True)
    user_role = models.CharField(max_length=50, null=True, blank=True)
    is_default_password = models.BooleanField(default=True)  # New field

    def __str__(self):
        return f"{self.user.username} - {self.user_role}"


class Flights(models.Model):
    price = models.IntegerField(verbose_name='Price')
    flight_number = models.CharField(max_length=100, verbose_name='Flight Number')
    discount = models.IntegerField(verbose_name='Discount')
    discount_usage = models.IntegerField(verbose_name='Discount Usage', null=True)
    flight_type = models.CharField(max_length=50, verbose_name='Flight Type')
    departure = models.DateField(verbose_name='Departure')
    arrival = models.DateField(verbose_name='Arrival')
    origin = models.CharField(max_length=100, verbose_name='Origin')
    destination = models.CharField(max_length=100, verbose_name='Destination')
    return_date = models.DateField(verbose_name='Return Date', null=True, blank=True)
    departure_time = models.TimeField(verbose_name='Departure Time', null=True)
    arrival_time = models.TimeField(verbose_name="Arrival Time", null=True)
    return_time = models.TimeField(verbose_name="Return Time", null=True)
    discounted_price = models.IntegerField(verbose_name='Discounted Price', null=True)
    available_seats = models.IntegerField(verbose_name='Available Seats', null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_flights')

    def save(self, *args, **kwargs):
        if self.discount is not None and self.discount > 0:
            discount_amount = (self.discount / 100) * self.price
            self.discounted_price = self.price - discount_amount
        else:
            self.discounted_price = self.price  # No discount applied
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.flight_number} from {self.origin} to {self.destination}"

    




class BookedFlights(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='booked_flights', null=True, blank=True)  # Client
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='admin_booked_flights')  # Admin
    ticket_no = models.CharField(max_length=100, verbose_name='Ticket Number')
    departure = models.DateField(verbose_name='Departure Date')
    arrival = models.DateField(verbose_name='Arrival Date')
    departure_time = models.TimeField(verbose_name="Departure Time", null=True)
    arrival_time = models.TimeField(verbose_name="Arrival Time", null=True)
    origin = models.CharField(max_length=255, verbose_name='Origin')
    destination = models.CharField(max_length=255, verbose_name='Destination')
    seat_num = models.CharField(max_length=10, verbose_name='Seat Number')
    flight_num = models.CharField(max_length=50, verbose_name='Flight Number')
    seat_type = models.CharField(max_length=50, verbose_name='Seat Type')
    reference_num = models.CharField(max_length=100, verbose_name='Reference Number')
    amount = models.IntegerField(verbose_name='Amount')
    payment_status = models.CharField(max_length=50, verbose_name='Payment Status')
    payment_date = models.DateTimeField(verbose_name='Payment Date')
    flight_status = models.CharField(max_length=50, verbose_name='Flight Status')
    return_date = models.DateField(max_length=50, verbose_name='Return Date', null=True)

    def __str__(self):
        return f"{self.ticket_no} - {self.flight_num}"

class Archive(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='archived_flights', null=True, blank=True)
    flight_num = models.CharField(max_length=100, verbose_name='Flight Number')
    ticket_num = models.CharField(max_length=100, verbose_name='Ticket Number')
    last_name = models.CharField(max_length=100, verbose_name='Last Name')
    seat_type = models.CharField(max_length=25, verbose_name='Seat Type')
    boarded = models.CharField(max_length=25, verbose_name='Boarded')
    def __str__(self):
        return f"{self.flight_num} - {self.boarded}"
    
class TicketSales(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ticket_sales', null=True, blank=True)
    card_number = models.CharField(max_length=16, verbose_name='Card Number')
    payment_amount = models.IntegerField(verbose_name='Payment')
    arrival = models.DateField(verbose_name='Arrival Date', null=True, blank=True)
    return_date = models.DateField(max_length=50, verbose_name='Return Date',null=True, blank=True)
    flight_num = models.CharField(max_length=100, verbose_name='Flight Number', null=True, blank=True)
    
    def __str__(self):
        return f"{self.user} - {self.payment_amount}"
    