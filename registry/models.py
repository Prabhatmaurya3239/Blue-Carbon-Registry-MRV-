from django.db import models
import hashlib
import uuid
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils import timezone

# -------------------
# Custom User Model
# -------------------
class User(AbstractUser):
    USER_ROLES = [
        ('NGO', 'NGO'),
        ('COMMUNITY', 'Community'),
        ('ADMIN', 'Admin'),
    ]
    role = models.CharField(max_length=20, choices=USER_ROLES, default='NGO')
    organization = models.CharField(max_length=200, blank=True, null=True)

    # Fix reverse accessor clashes
    groups = models.ManyToManyField(
        Group,
        related_name='custom_user_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='custom_user_permissions_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

# -------------------
# Project Site Model
# -------------------
class ProjectSite(models.Model):
    ECOSYSTEM_TYPES = [
        ('MANGROVE', 'Mangrove'),
        ('SEAGRASS', 'Seagrass'),
        ('MARSH', 'Salt Marsh'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    location_lat = models.DecimalField(max_digits=9, decimal_places=6)
    location_lng = models.DecimalField(max_digits=9, decimal_places=6)
    ecosystem_type = models.CharField(max_length=20, choices=ECOSYSTEM_TYPES)
    area_ha = models.DecimalField(max_digits=10, decimal_places=2)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.ecosystem_type}"

# -------------------
# Plantation Record
# -------------------
class PlantationRecord(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project_site = models.ForeignKey(ProjectSite, on_delete=models.CASCADE)
    date_planted = models.DateField()
    species = models.CharField(max_length=200)
    number_of_plants = models.PositiveIntegerField()
    uploaded_images = models.ImageField(upload_to='plantation_images/', blank=True, null=True)
    verified = models.BooleanField(default=False)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    upload_date = models.DateTimeField(auto_now_add=True)
    verified_date = models.DateTimeField(blank=True, null=True)
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='verified_records'
    )

    def __str__(self):
        return f"{self.species} - {self.project_site.name}"

# -------------------
# Carbon Credit
# -------------------
class CarbonCredit(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project_site = models.ForeignKey(ProjectSite, on_delete=models.CASCADE)
    plantation_record = models.OneToOneField(PlantationRecord, on_delete=models.CASCADE)
    year = models.PositiveIntegerField()
    credits_issued = models.DecimalField(max_digits=10, decimal_places=2)
    txn_hash = models.CharField(max_length=64, unique=True)
    issued_date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.txn_hash:
            # Generate fake blockchain transaction hash
            data = f"{self.project_site.id}{self.credits_issued}{timezone.now().timestamp()}"
            self.txn_hash = hashlib.sha256(data.encode()).hexdigest()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.credits_issued} credits - {self.project_site.name}"
