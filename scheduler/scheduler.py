import schedule
import time
from rq import Queue
from redis import Redis
from apps.common.settings import settings
from tasks import reminderFarmingAvailable, reminderNotUsingAccounts

redis_conn = Redis.from_url(settings.REDIS_URL)
rq_queue = Queue(connection=redis_conn)


schedule.every().day.do(rq_queue.enqueue, reminderNotUsingAccounts)
schedule.every().hour.do(rq_queue.enqueue, reminderFarmingAvailable)

while True:
    schedule.run_pending()
    time.sleep(1)
