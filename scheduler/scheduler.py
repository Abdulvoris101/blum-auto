import schedule
import time
from rq import Queue
from redis import Redis
from apps.common.settings import settings
from tasks import reminderFarmingAvailable, reminderNotUsingAccounts, cancelOrUpdateSubscriptions

redis_conn = Redis.from_url(settings.REDIS_URL)
rq_queue = Queue(connection=redis_conn)


schedule.every().day.do(rq_queue.enqueue, reminderNotUsingAccounts)
schedule.every().hour.do(rq_queue.enqueue, reminderFarmingAvailable)
schedule.every().day.at("00:00").do(rq_queue.enqueue, cancelOrUpdateSubscriptions)
schedule.every().day.at("20:00").do(rq_queue.enqueue, cancelOrUpdateSubscriptions)

while True:
    schedule.run_pending()
    time.sleep(1)
