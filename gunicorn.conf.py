import multiprocessing

bind = "0.0.0.0:$PORT"
worker_class = "uvicorn.workers.UvicornWorker"
workers = multiprocessing.cpu_count() * 2 + 1
