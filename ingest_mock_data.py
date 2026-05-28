import json
import random
import uuid
import psycopg2
from datetime import datetime, timedelta

# Database connection configuration
DB_CONFIG = {
    "host": "localhost",
    "database": "analytics_db",
    "user": "nick_admin",
    "password": "password123",
    "port": "5432"
}

EVENT_TYPES = ["page_view", "add_to_cart", "checkout_success"]
DEVICES = ["mobile", "desktop", "tablet", None] # Intentionally including None for messiness
PRODUCTS = [
    {"id": "prod_101", "price": 45.00},
    {"id": "prod_202", "price": 120.00},
    {"id": "prod_303", "price": 15.99},
    {"id": "prod_404", "price": 250.00}
]

def generate_messy_event():
    """Generates a single randomized clickstream event payload."""
    event_type = random.choice(EVENT_TYPES)
    user_id = f"usr_{random.randint(1000, 1010)}" # Small pool to simulate repeat users
    
    # Simulate historical timestamps over the last few hours
    time_offset = random.randint(0, 360)
    timestamp = (datetime.utcnow() - timedelta(minutes=time_offset)).isoformat() + "Z"

    event = {
        "event_id": str(uuid.uuid4()),
        "event_type": event_type,
        "timestamp": timestamp,
        "user_id": user_id if random.random() > 0.1 else None, # 10% chance of logged-out/null user
        "device": random.choice(DEVICES),
        "payload_version": random.choice(["1.0", "1.1"])
    }

    # Dynamic metadata based on event type (Simulating schema drift)
    if event_type == "page_view":
        event["metadata"] = {
            "page_url": f"/products/{random.choice(['shoes', 'shirts', 'hats', 'tech'])}",
            "referrer": random.choice(["google.com", "instagram.com", "direct"])
        }
    elif event_type == "add_to_cart":
        prod = random.choice(PRODUCTS)
        event["metadata"] = {
            "product_id": prod["id"],
            "price": prod["price"],
            "currency": "USD",
            "quantity": random.randint(1, 3)
        }
    elif event_type == "checkout_success":
        event["metadata"] = {
            "order_id": f"ord_{random.randint(50000, 60000)}",
            "total_amount": round(random.uniform(20.00, 500.00), 2)
        }

    return event

def bulk_insert_events(num_records=1000):
    """Inserts generated events into the Postgres raw_clickstream table."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        print(f"🚀 Generating and inserting {num_records} messy events into Postgres...")
        
        for _ in range(num_records):
            payload = generate_messy_event()
            # Serialize the Python dict to a JSON string for the JSONB column
            cur.execute(
                "INSERT INTO raw_clickstream (raw_payload) VALUES (%s)",
                (json.dumps(payload),)
            )
            
        conn.commit()
        cur.close()
        conn.close()
        print("✅ Data ingestion complete!")
        
    except Exception as e:
        print(f"❌ Error connecting to or writing to the database: {e}")

if __name__ == "__main__":
    bulk_insert_events(1000) # Generating 1,000 records to start