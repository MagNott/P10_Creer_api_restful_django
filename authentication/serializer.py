from rest_framework.serializers import ModelSerializer
from .models import CustomUser
from datetime import date
from rest_framework.serializers import ValidationError


class CustomUserSerializer(ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            'id',
            'username',
            'first_name',
            'last_name',
            'date_birth',
            'can_be_contacted',
            'can_data_be_shared'
        ]

    def validate_date_birth(self, input_date_birth):

        today = date.today()

        # Calcul de l'âge en années
        age = today.year - input_date_birth.year

       # Vérifie si l'anniversaire est encore à venir cette année
        if (today.month, today.day) < (input_date_birth.month, input_date_birth.day):
            age -= 1  # on enlève 1 à l'âge

        # On vérifie l'âge minimum
        if age < 15:
            raise ValidationError("Vous devez avoir au moins 15 ans pour vous inscrire.")

        return input_date_birth
