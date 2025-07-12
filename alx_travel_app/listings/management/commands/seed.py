from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from listings.models import Listing, Booking, Review
from datetime import date, timedelta
from decimal import Decimal
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Populate the database with sample listings, users, bookings, and reviews.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Seeding database..."))
        self.clear_data()
        users = self.create_users()
        listings = self.create_listings()
        self.create_bookings(users, listings)
        self.create_reviews(users, listings)
        self.final_summary()

    def clear_data(self):
        self.stdout.write("Clearing old data...")
        Review.objects.all().delete()
        Booking.objects.all().delete()
        Listing.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()

    def create_users(self):
        self.stdout.write("Creating users...")
        user_data = [
            ("alex_taylor", "Alex", "Taylor", "alex.taylor@example.com"),
            ("maria_lee", "Maria", "Lee", "maria.lee@example.com"),
            ("dylan_wong", "Dylan", "Wong", "dylan.wong@example.com"),
            ("sophia_kim", "Sophia", "Kim", "sophia.kim@example.com"),
        ]
        users = [
            User(
                username=u, email=e, first_name=f, last_name=l
            ) for u, f, l, e in user_data
        ]
        for user in users:
            user.set_password("password123")
        User.objects.bulk_create(users)
        self.stdout.write(f"Created {len(users)} users")
        return list(User.objects.filter(is_superuser=False))

    def create_listings(self):
        self.stdout.write("Creating listings...")
        listings_data = [
            ("Sunny Beach Bungalow", "A bright and cozy bungalow right on the sandy shores.", 180),
            ("Downtown Modern Flat", "Sleek apartment with city views and fast wifi.", 130),
            ("Rustic Mountain Lodge", "Cabin surrounded by forest, perfect for hiking enthusiasts.", 150),
            ("Urban Studio", "Compact and stylish studio, perfect for solo travelers.", 90),
            ("Country Villa", "Spacious villa with large garden and countryside views.", 220),
        ]
        listings = []
        for title, description, price in listings_data:
            start_date = date.today() + timedelta(days=random.randint(1, 30))
            end_date = start_date + timedelta(days=random.randint(60, 300))
            listings.append(Listing(
                title=title,
                description=description,
                price_per_night=Decimal(str(price)),
                available_from=start_date,
                available_to=end_date
            ))
        Listing.objects.bulk_create(listings)
        self.stdout.write(f"Created {len(listings)} listings")
        return list(Listing.objects.all())

    def create_bookings(self, users, listings):
        self.stdout.write("Creating bookings...")
        bookings = []
        for _ in range(4):
            listing = random.choice(listings)
            user = random.choice(users)
            start_date = listing.available_from + timedelta(days=random.randint(0, 30))
            end_date = start_date + timedelta(days=random.randint(2, 7))
            if end_date <= listing.available_to:
                bookings.append(Booking(
                    listing=listing,
                    user=user,
                    start_date=start_date,
                    end_date=end_date
                ))
        Booking.objects.bulk_create(bookings)
        self.stdout.write(f"Created {len(bookings)} bookings")

    def create_reviews(self, users, listings):
        self.stdout.write("Creating reviews...")
        reviews_data = [
            (5, "Absolutely loved the location and vibe! Will come back."),
            (4, "Nice and clean place, great communication with the host."),
            (5, "Perfect weekend getaway spot, highly recommended!"),
        ]
        created_count = 0
        for rating, comment in reviews_data:
            listing = random.choice(listings)
            user = random.choice(users)
            try:
                review, created = Review.objects.get_or_create(
                    listing=listing,
                    user=user,
                    defaults={
                        'rating': rating,
                        'comment': comment
                    }
                )
                if created:
                    created_count += 1
            except Exception as e:
                self.stdout.write(f"Error creating review: {str(e)}")
        self.stdout.write(f"Created {created_count} reviews")

    def final_summary(self):
        self.stdout.write(self.style.SUCCESS(
            f"\n Seeding complete!\n"
            f" Users: {User.objects.filter(is_superuser=False).count()}\n"
            f" Listings: {Listing.objects.count()}\n"
            f" Bookings: {Booking.objects.count()}\n"
            f" Reviews: {Review.objects.count()}"
        ))
