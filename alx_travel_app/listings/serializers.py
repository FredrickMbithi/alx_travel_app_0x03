from rest_framework import serializers
from .models import Listing, Booking, Review, Payment


class ListingSerializer(serializers.ModelSerializer):
    """Serializer for Listing model"""
    class Meta:
        model = Listing
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class BookingSerializer(serializers.ModelSerializer):
    """Serializer for Booking model"""
    listing_details = ListingSerializer(source='listing', read_only=True)
    
    class Meta:
        model = Booking
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'total_price']

    def validate(self, data):
        """Custom validation for booking dates"""
        if data.get('start_date') and data.get('end_date'):
            if data['start_date'] >= data['end_date']:
                raise serializers.ValidationError(
                    "End date must be after start date"
                )
        return data


class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for Review model"""
    class Meta:
        model = Review
        fields = '__all__'
        read_only_fields = ['id', 'created_at']
    
    def validate_rating(self, value):
        """Validate rating is between 1 and 5"""
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5")
        return value


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for Payment model"""
    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = [
            'id', 
            'created_at', 
            'updated_at', 
            'transaction_id',
            'chapa_reference',
            'checkout_url',
            'payment_method',
            'paid_at'
        ]


class PaymentInitiateSerializer(serializers.Serializer):
    """Serializer for payment initiation request"""
    booking_id = serializers.UUIDField(required=False, allow_null=True)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    email = serializers.EmailField()
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    callback_url = serializers.URLField()
    return_url = serializers.URLField()
    currency = serializers.CharField(max_length=3, default='ETB')
    
    def validate_amount(self, value):
        """Validate amount is positive"""
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than 0")
        return value


class PaymentVerifySerializer(serializers.Serializer):
    """Serializer for payment verification response"""
    status = serializers.CharField()
    message = serializers.CharField()
    data = serializers.DictField()
