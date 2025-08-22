import redis
import docker
import json
import os
import threading
import time
import logging


REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
APPS_DIR = "."
COMPOSE_NAME = os.environ.get("COMPOSE_NAME", "mycompose")  # Compose project name fallback
REDIS_CHANNEL = f'{COMPOSE_NAME}-orchestrator'
docker_client = docker.from_env()
r = redis.Redis(host=REDIS_HOST, decode_responses=True)

nodes_list = os.getenv("NODES", "").split(",")
nodes = nodes_list if nodes_list else ['app1', 'app2', 'app3']


# Check if compose name is not in the devices list before adding it
if not r.lrange('devices:list', 0, -1) or COMPOSE_NAME not in r.lrange('devices:list', 0, -1):
    r.rpush('devices:list', COMPOSE_NAME)
# Ensure the components list is fresh for each device
r.delete(f'devices:{COMPOSE_NAME}:nodes')
for node in nodes:
    try:
        r.rpush(f'devices:{COMPOSE_NAME}:nodes', node)
        r.set(f'devices:{COMPOSE_NAME}:{node}:status', 'stopped')
    except redis.RedisError as e:
        print(f"Error pushing component {node} for device {COMPOSE_NAME}: {e}")

# Configure logging


class RedisHandler(logging.Handler):
    def __init__(self, redis_host='localhost', redis_port=6379, redis_key='logs'):
        super().__init__()
        self.redis_key = redis_key

    def emit(self, record):
        try:
            log_entry = self.format(record)
            r.lpush(self.redis_key, log_entry)
        except Exception:
            self.handleError(record)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

redis_handler = RedisHandler(redis_key='orchestrator:logs')
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
redis_handler.setFormatter(formatter)

logger.addHandler(redis_handler)
def handle_command(msg):
    try:
        data = json.loads(msg)
        cmd = data.get("command")
        app = data.get("app")
        container_name = f"{app}"
        app_path = os.path.join(APPS_DIR, app)

        if cmd == "build":
            logger.info(f"🔨 Building image for {app}")
            logger.info(f"📂 Using path: {app_path}")
            # docker_client.images.build(path=app_path, tag=app)
            docker_client.images.build(path=app_path, tag=app, nocache=True)
        
        elif cmd == "up":
            logger.info(f"⬆️ Starting container for {app}")
            # Check if already running
            try:
                c = docker_client.containers.get(container_name)
                if c.status != 'running':
                    c.start()
                    logger.info(f"✅ Container {container_name} started.")
            except docker.errors.NotFound:
                # docker_client.containers.run(app, name=container_name, detach=True)
                docker_client.containers.run(
                    app, 
                    name=container_name, 
                    detach=True, 
                    network_mode="host",
                    ports={'6379/tcp': 6379}
                )
                # docker_client.containers.run(app, name=container_name, detach=True, network_mode="host")
                logger.info(f"✅ Container {container_name} created and started.")
        
        elif cmd == "down":
            logger.info(f"⬇️ Stopping container for {app}")
            try:
                c = docker_client.containers.get(container_name)
                c.stop()
                logger.info(f"✅ Container {container_name} stopped.")
            except docker.errors.NotFound:
                logger.warning(f"⚠️ Container {container_name} not found.")
        
        elif cmd == "remove":
            logger.info(f"⬇️ Removing container for {app}")
            try:
                c = docker_client.containers.get(container_name)
                c.stop()
                c.remove()
                logger.info(f"✅ Container {container_name}removed.")
            except docker.errors.NotFound:
                logger.warning(f"⚠️ Container {container_name} not found.")

        elif cmd == "status":
            print(f"🔎 Checking status for {app}")
            try:
                c = docker_client.containers.get(container_name)
                status = c.status
                health = c.attrs.get("State", {}).get("Health", {}).get("Status")
                print(f"ℹ️ Status for {container_name}: status={status}, health={health}")
            except docker.errors.NotFound:
                print(f"⚠️ Container {container_name} not found.")
        else:
            logger.warning(f"❓ Unknown command: {cmd}")

    except Exception as e:
        logger.error(f"⚠️ Error: {e}")

def listen_loop():
    pubsub = r.pubsub(ignore_subscribe_messages=True)
    pubsub.subscribe(REDIS_CHANNEL)
    logger.info(f"📡 Subscribed to Redis channel '{REDIS_CHANNEL}'")

    for message in pubsub.listen():
        logger.info(f"📨 Received message: {message['data']}")
        handle_command(message['data'])

def heartbeat_loop():
    while True:
        try:
            # Send heartbeat
            r.set(f"devices:{COMPOSE_NAME}:heartbeat", float(time.time()))
            logger.info(f"💓 Heartbeat sent to {COMPOSE_NAME}:heartbeat")

            # Publish container statuses
            for container in docker_client.containers.list(all=True):
                name = container.name
                status = container.status
                if name not in nodes:
                    continue
                # health = container.attrs.get("State", {}).get("Health", {}).get("Status")
                topic = f"devices:{COMPOSE_NAME}:{name}:status"
                r.set(topic, status)
                r.set(f"devices:{COMPOSE_NAME}:{name}:heartbeat", float(time.time()))
                logger.info(f"📦 Status for {name} sent to {topic}: {status}")

        except Exception as e:
            logger.info(f"⚠️ Heartbeat error: {e}")

        time.sleep(2)  # Adjust heartbeat interval as needed

if __name__ == "__main__":
    threading.Thread(target=listen_loop, daemon=True).start()
    threading.Thread(target=heartbeat_loop, daemon=True).start()
    logger.info("🚀 Orchestrator running…")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("👋 Shutting down.")
