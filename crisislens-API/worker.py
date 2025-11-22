# worker.py
import os
import sys
from redis import Redis
from rq import Worker, Queue, SimpleWorker

#Classifier to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

#processing function
from Classifier.production.tasks import process_emergency_call

listen = ['crisislens']
redis_conn = Redis(
    host=os.getenv('REDIS_HOST', 'localhost'),
    port=int(os.getenv('REDIS_PORT', 6379))
)

if __name__ == '__main__':
    print("CrisisLens Worker Starting...")
    print(f"Listening to queues: {listen}")
    print("-" * 60)
    
    qs = list(map(lambda q: Queue(q, connection=redis_conn), listen))
    # Used SimpleWorker instead of Worker for Windows compatibility issues 
    w = SimpleWorker(qs, connection=redis_conn)
    w.work()