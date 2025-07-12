from rest_framework import viewsets, permissions, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Listing, Booking, Payment
from .serializers import ListingSerializer, BookingSerializer

import requests
import uuid
import os


class ListingViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class InitiatePaymentView(APIView):
    # No authentication required to allow testing without token
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        booking_id = request.data.get('booking_id')
        amount = request.data.get('amount')
        currency = request.data.get('currency', 'ETB')

        # For testing: don't filter by user, just get booking by ID
        try:
            booking = Booking.objects.get(id=booking_id)
        except Booking.DoesNotExist:
            available_bookings = Booking.objects.all().values_list('id', flat=True)
            return Response({
                'error': 'Booking not found.',
                'message': f'No booking with ID {booking_id}. Available booking IDs: {list(available_bookings)}'
            }, status=404)

        # Check if a Payment already exists for this booking
        if hasattr(booking, 'payment'):
            return Response({
                'error': 'Payment already initiated.',
                'message': f'A payment record already exists for booking ID {booking_id}.'
            }, status=400)

        transaction_ref = str(uuid.uuid4())
        callback_url = "http://example.com/verify-payment/"  # Replace in prod

        payload = {
            "amount": str(amount),
            "currency": currency,
            "email": "test.user.payment@gmail.com",  # Hardcoded email for testing to bypass validation
            "first_name": booking.user.first_name or "Customer",
            "last_name": booking.user.last_name or "",
            "tx_ref": transaction_ref,
            "callback_url": callback_url,
            "return_url": callback_url,
            "customization": {
                "title": "Booking Payment",  # Shortened to fit within 16 characters
                "description": "Payment for booking"
            }
        }

        headers = {
            "Authorization": f"Bearer {os.getenv('CHAPA_SECRET_KEY')}",
            "Content-Type": "application/json"
        }

        # Log the payload for debugging
        print("Chapa API Payload:", payload)
        try:
            response = requests.post("https://api.chapa.co/v1/transaction/initialize", json=payload, headers=headers)
            if response.status_code == 200:
                data = response.json()
                Payment.objects.create(
                    booking=booking,
                    transaction_id=transaction_ref,
                    amount=amount,
                    currency=currency,
                    status='Pending',
                    chapa_response=data
                )
                return Response({"checkout_url": data['data']['checkout_url']})
            else:
                error_detail = response.text
                return Response({
                    "error": "Failed to initiate payment.",
                    "status_code": response.status_code,
                    "detail": error_detail
                }, status=response.status_code)
        except Exception as e:
            print("Error during Chapa API request:", str(e))
            return Response({
                "error": "Internal server error during payment initiation.",
                "detail": str(e)
            }, status=500)


class VerifyPaymentView(APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def get(self, request, tx_ref):
        print("Verifying payment for tx_ref:", tx_ref)
        headers = {
            "Authorization": f"Bearer {os.getenv('CHAPA_SECRET_KEY')}"
        }
        url = f"https://api.chapa.co/v1/transaction/verify/{tx_ref}"
        try:
            response = requests.get(url, headers=headers)
            print("Chapa API Verification Response Status:", response.status_code)
            if response.status_code == 200:
                result = response.json()
                print("Chapa API Verification Response Data:", result)
                status_from_chapa = result.get('data', {}).get('status', '').lower()
                try:
                    payment = Payment.objects.get(transaction_id=tx_ref)
                    if status_from_chapa == 'success':
                        payment.status = 'Completed'
                    else:
                        payment.status = 'Failed'
                    payment.chapa_response = result
                    payment.save()
                    return Response({'payment_status': payment.status})
                except Payment.DoesNotExist:
                    return Response({'error': 'Payment record not found.'}, status=404)
            else:
                return Response({'error': 'Verification failed.', 'status_code': response.status_code, 'detail': response.text}, status=response.status_code)
        except Exception as e:
            print("Error during Chapa API verification request:", str(e))
            return Response({'error': 'Internal server error during verification.', 'detail': str(e)}, status=500)
