"""
Initialize DimensionOS Platform database.

Creates tables and seeds resource allocations.
"""

from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

from server.models.user import Base, ResourceAllocation, UserTier


# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://dimensionos:dimensionos@localhost:5432/dimensionos"
)

# Create engine
engine = create_engine(DATABASE_URL, echo=True)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_database():
    """Initialize database - create all tables."""
    print("🚀 Initializing DimensionOS Platform database...")
    print(f"📍 Database URL: {DATABASE_URL}")
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")


def seed_resource_allocations():
    """Seed default resource allocations for each tier."""
    print("🌱 Seeding resource allocations...")
    
    db = SessionLocal()
    
    try:
        # Check if already seeded
        existing = db.query(ResourceAllocation).first()
        if existing:
            print("⚠️  Resource allocations already seeded")
            return
        
        # Define tier allocations
        allocations = [
            ResourceAllocation(
                tier=UserTier.FREE,
                cpu_cores=1,
                ram_gb=4,
                storage_gb=10,
                bandwidth="1Gbps",
                database_type="SQLite",
                ai_assistant=False,
                analytics=False,
                custom_domains=False,
                priority_support=False,
                price_per_month=0.0,
                trial_days=30
            ),
            ResourceAllocation(
                tier=UserTier.STARTER,
                cpu_cores=8,
                ram_gb=64,
                storage_gb=1000,
                bandwidth="10Gbps",
                database_type="PostgreSQL",
                ai_assistant=True,
                analytics=True,
                custom_domains=False,
                priority_support=False,
                price_per_month=10.0,
                trial_days=None
            ),
            ResourceAllocation(
                tier=UserTier.PRO,
                cpu_cores=16,
                ram_gb=128,
                storage_gb=5000,
                bandwidth="100Gbps",
                database_type="PostgreSQL Cluster",
                ai_assistant=True,
                analytics=True,
                custom_domains=True,
                priority_support=True,
                price_per_month=50.0,
                trial_days=None
            ),
            ResourceAllocation(
                tier=UserTier.ENTERPRISE,
                cpu_cores=64,
                ram_gb=512,
                storage_gb=50000,
                bandwidth="1Tbps",
                database_type="PostgreSQL Cluster + Redis",
                ai_assistant=True,
                analytics=True,
                custom_domains=True,
                priority_support=True,
                price_per_month=500.0,
                trial_days=None
            )
        ]
        
        for allocation in allocations:
            db.add(allocation)
            print(f"  ✅ {allocation.tier.value}: {allocation.cpu_cores} cores, {allocation.ram_gb}GB RAM, {allocation.storage_gb}GB storage - ${allocation.price_per_month}/month")
        
        db.commit()
        print("✅ Resource allocations seeded successfully")
        
    except Exception as e:
        print(f"❌ Error seeding resource allocations: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def reset_database():
    """
    Drop all tables and recreate them.
    
    ⚠️  WARNING: This will delete ALL data!
    Only use in development!
    """
    print("⚠️  WARNING: Dropping all tables...")
    response = input("Are you sure? This will delete ALL data! (yes/no): ")
    
    if response.lower() != "yes":
        print("❌ Aborted")
        return
    
    print("🗑️  Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    print("✅ All tables dropped")
    
    print("🔨 Creating tables...")
    init_database()
    
    print("🌱 Seeding resource allocations...")
    seed_resource_allocations()
    
    print("✅ Database reset complete!")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--reset":
        reset_database()
    else:
        init_database()
        seed_resource_allocations()
        print("\n✅ Database initialization complete!")
        print("\n📋 Next steps:")
        print("  1. Start the server: python server/main_platform.py")
        print("  2. Visit API docs: http://localhost:8000/docs")
        print("  3. Test registration: POST /api/auth/register")

