import os
import sys
import django
from datetime import datetime, timedelta
from decimal import Decimal
import random

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blue_carbon_registry.settings')
django.setup()

from registry.models import User, ProjectSite, PlantationRecord, CarbonCredit

def create_dummy_data():
    print("Creating dummy data for Blue Carbon MRV Registry...")
    
    # Create admin user
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@bluecarbon.org',
            'role': 'ADMIN',
            'organization': 'National Climate Change Registry',
            'first_name': 'Admin',
            'last_name': 'User'
        }
    )
    if created:
        admin_user.set_password('admin123')
        admin_user.save()
        print("✓ Created admin user")
    
    # Create NGO users
    ngo_users_data = [
        {
            'username': 'ocean_guardians',
            'email': 'contact@oceanguardians.org',
            'organization': 'Ocean Guardians Foundation',
            'first_name': 'Sarah',
            'last_name': 'Johnson'
        },
        {
            'username': 'coastal_restore',
            'email': 'info@coastalrestore.org',
            'organization': 'Coastal Restoration Initiative',
            'first_name': 'Michael',
            'last_name': 'Chen'
        },
        {
            'username': 'blue_planet_ngo',
            'email': 'team@blueplanet.org',
            'organization': 'Blue Planet Conservation',
            'first_name': 'Emma',
            'last_name': 'Rodriguez'
        }
    ]
    
    ngo_users = []
    for user_data in ngo_users_data:
        user, created = User.objects.get_or_create(
            username=user_data['username'],
            defaults={
                'email': user_data['email'],
                'role': 'NGO',
                'organization': user_data['organization'],
                'first_name': user_data['first_name'],
                'last_name': user_data['last_name']
            }
        )
        if created:
            user.set_password('password123')
            user.save()
            print(f"✓ Created NGO user: {user.username}")
        ngo_users.append(user)
    
    # Create community users
    community_users_data = [
        {
            'username': 'sundarbans_community',
            'email': 'leader@sundarbans.org',
            'organization': 'Sundarbans Community Group',
            'first_name': 'Rajesh',
            'last_name': 'Kumar'
        },
        {
            'username': 'kerala_fishers',
            'email': 'contact@keralafishers.org',
            'organization': 'Kerala Fishers Association',
            'first_name': 'Priya',
            'last_name': 'Nair'
        }
    ]
    
    community_users = []
    for user_data in community_users_data:
        user, created = User.objects.get_or_create(
            username=user_data['username'],
            defaults={
                'email': user_data['email'],
                'role': 'COMMUNITY',
                'organization': user_data['organization'],
                'first_name': user_data['first_name'],
                'last_name': user_data['last_name']
            }
        )
        if created:
            user.set_password('password123')
            user.save()
            print(f"✓ Created community user: {user.username}")
        community_users.append(user)
    
    all_users = ngo_users + community_users
    
    # Create project sites
    project_sites_data = [
        {
            'name': 'Sundarbans Mangrove Restoration',
            'location_lat': Decimal('22.2587'),
            'location_lng': Decimal('89.9375'),
            'ecosystem_type': 'MANGROVE',
            'area_ha': Decimal('150.75')
        },
        {
            'name': 'Kerala Backwater Seagrass Project',
            'location_lat': Decimal('9.9312'),
            'location_lng': Decimal('76.2673'),
            'ecosystem_type': 'SEAGRASS',
            'area_ha': Decimal('85.50')
        },
        {
            'name': 'Gujarat Salt Marsh Conservation',
            'location_lat': Decimal('23.0225'),
            'location_lng': Decimal('72.5714'),
            'ecosystem_type': 'MARSH',
            'area_ha': Decimal('200.25')
        },
        {
            'name': 'Andaman Mangrove Initiative',
            'location_lat': Decimal('11.7401'),
            'location_lng': Decimal('92.6586'),
            'ecosystem_type': 'MANGROVE',
            'area_ha': Decimal('120.00')
        },
        {
            'name': 'Tamil Nadu Coastal Restoration',
            'location_lat': Decimal('11.1271'),
            'location_lng': Decimal('78.6569'),
            'ecosystem_type': 'SEAGRASS',
            'area_ha': Decimal('95.75')
        },
        {
            'name': 'Odisha Mangrove Sanctuary',
            'location_lat': Decimal('20.2961'),
            'location_lng': Decimal('85.8245'),
            'ecosystem_type': 'MANGROVE',
            'area_ha': Decimal('175.50')
        }
    ]
    
    project_sites = []
    for i, site_data in enumerate(project_sites_data):
        site, created = ProjectSite.objects.get_or_create(
            name=site_data['name'],
            defaults={
                **site_data,
                'created_by': all_users[i % len(all_users)]
            }
        )
        if created:
            print(f"✓ Created project site: {site.name}")
        project_sites.append(site)
    
    # Create plantation records
    species_by_ecosystem = {
        'MANGROVE': ['Rhizophora mucronata', 'Avicennia marina', 'Sonneratia alba', 'Bruguiera gymnorrhiza'],
        'SEAGRASS': ['Zostera marina', 'Halophila ovalis', 'Cymodocea serrulata', 'Thalassia hemprichii'],
        'MARSH': ['Spartina alterniflora', 'Salicornia europaea', 'Juncus roemerianus', 'Distichlis spicata']
    }
    
    plantation_records = []
    for site in project_sites:
        # Create 3-5 plantation records per site
        num_records = random.randint(3, 5)
        for j in range(num_records):
            species_list = species_by_ecosystem[site.ecosystem_type]
            species = random.choice(species_list)
            
            # Random date within last 2 years
            days_ago = random.randint(30, 730)
            plant_date = datetime.now().date() - timedelta(days=days_ago)
            
            record = PlantationRecord.objects.create(
                project_site=site,
                date_planted=plant_date,
                species=species,
                number_of_plants=random.randint(500, 5000),
                verified=random.choice([True, True, True, False]),  # 75% verified
                uploaded_by=site.created_by,
                upload_date=datetime.now() - timedelta(days=days_ago-5)
            )
            
            if record.verified:
                record.verified_by = admin_user
                record.verified_date = datetime.now() - timedelta(days=days_ago-10)
                record.save()
                
                # Create carbon credits for verified records
                base_credits_per_plant = Decimal('0.5')
                ecosystem_multiplier = {
                    'MANGROVE': Decimal('1.5'),
                    'SEAGRASS': Decimal('1.2'),
                    'MARSH': Decimal('1.0'),
                }
                
                multiplier = ecosystem_multiplier.get(site.ecosystem_type, Decimal('1.0'))
                total_credits = record.number_of_plants * base_credits_per_plant * multiplier
                
                CarbonCredit.objects.create(
                    project_site=site,
                    plantation_record=record,
                    year=plant_date.year,
                    credits_issued=round(total_credits, 2)
                )
            
            plantation_records.append(record)
    
    print(f"✓ Created {len(plantation_records)} plantation records")
    
    # Print summary
    total_sites = ProjectSite.objects.count()
    total_records = PlantationRecord.objects.count()
    verified_records = PlantationRecord.objects.filter(verified=True).count()
    total_credits = CarbonCredit.objects.aggregate(total=django.db.models.Sum('credits_issued'))['total'] or 0
    
    print("\n" + "="*50)
    print("DUMMY DATA CREATION COMPLETE!")
    print("="*50)
    print(f"👥 Users created: {User.objects.count()}")
    print(f"🏝️  Project sites: {total_sites}")
    print(f"🌱 Plantation records: {total_records}")
    print(f"✅ Verified records: {verified_records}")
    print(f"🪙 Carbon credits issued: {total_credits}")
    print("\nLogin credentials:")
    print("Admin: admin / admin123")
    print("NGO: ocean_guardians / password123")
    print("Community: sundarbans_community / password123")
    print("="*50)

if __name__ == '__main__':
    create_dummy_data()
