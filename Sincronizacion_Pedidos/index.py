import sys
sys.path.append('/home/sam/Spacionatural/E-Commerce/')


# from apscheduler.schedulers.blocking import BlockingScheduler
from Sincronizacion_Pedidos.src.methods.orders.order import process_orders

process_orders()

# def cron_orders():
#     print("Processing orders...")


# scheduler = BlockingScheduler()
# scheduler.add_job(process_orders, 'interval', minutes=10)
# scheduler.start()
