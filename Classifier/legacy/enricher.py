import random

def enrich_record(record: dict) -> dict:
    record["caller_gender"] = random.choice(["Male", "Female"])
    record["caller_age_group"] = random.choice(["Child", "Adult", "Senior"])
    record["response_time"] = random.randint(3, 15)  # minutes
    return record
