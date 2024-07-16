import logging
import os


def create_folder(path):
    if not os.path.exists(str(path)):
        os.makedirs(str(path))


def setup_logger(env="NA", job_id="NA"):
    create_folder("/tmp/logs")
    logging.basicConfig(
        level="INFO",
        format="%(asctime)s.%(msecs)05d %(levelname)s %(pathname)s:%(lineno)s [env="
        + env
        + "] %(message)s",
        datefmt="%d-%b-%y %H:%M:%S",
        force=True,
        handlers=[
            logging.FileHandler(f"/var/logs/caas_{job_id}.log"),
            logging.StreamHandler(),
        ],
    )
    logging.getLogger("azure").setLevel(logging.WARNING)


def add_info_logs(job_id, msg):
    logging.info(f"[job_id={job_id}] [{msg}]")


def add_error_logs(job_id, msg):
    logging.error(f"[job_id={job_id}] [{msg}]")


def add_warning_logs(job_id, msg):
    logging.warn(f"[job_id={job_id}] [{msg}]")
