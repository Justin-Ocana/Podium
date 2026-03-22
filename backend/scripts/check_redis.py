"""
Script to check if Redis is running and accessible.
"""
import redis

def check_redis():
    try:
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        print("✅ Redis is running and accessible!")
        print(f"Redis version: {r.info()['redis_version']}")
        return True
    except redis.ConnectionError:
        print("❌ Redis is NOT running!")
        print("\nTo start Redis:")
        print("  - Windows: Install Memurai from https://www.memurai.com/get-memurai")
        print("  - Docker: docker run -d -p 6379:6379 redis:latest")
        print("  - WSL: sudo service redis-server start")
        return False
    except Exception as e:
        print(f"❌ Error connecting to Redis: {e}")
        return False

if __name__ == '__main__':
    check_redis()
