import json
import time
import random
import logging
from functools import wraps
import redis
from redis.exceptions import ConnectionError, TimeoutError

from backend.app.core.config import settings


class RedisCache:
    """
    Redis缓存工具类，提供简单易用的缓存操作接口，解决缓存常见问题

    特性：
    - 连接池管理，确保高效使用连接
    - 自动序列化/反序列化（JSON）
    - 防止缓存穿透（空值缓存）
    - 防止缓存击穿（分布式锁）
    - 防止缓存雪崩（随机过期时间）
    - 函数结果缓存装饰器
    - 验证码管理功能
    - 速率限制器
    - 完善的错误处理和日志记录
    """

    def __init__(self, host='localhost', port=6379, db=0, password=None,
                 max_connections=50, decode_responses=True,
                 default_expire=3600, retry_on_error=True,
                 logger=None):
        """
        初始化Redis缓存连接

        :param host: Redis服务器地址
        :param port: Redis端口
        :param db: 使用的数据库编号
        :param password: Redis密码
        :param max_connections: 最大连接数
        :param decode_responses: 是否自动解码响应为字符串
        :param default_expire: 默认过期时间（秒）
        :param retry_on_error: 是否在连接错误时重试
        :param logger: 自定义日志记录器
        """
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self.max_connections = max_connections
        self.decode_responses = decode_responses
        self.default_expire = default_expire
        self.retry_on_error = retry_on_error
        self.logger = logger or logging.getLogger(__name__)

        # 创建连接池
        self.connection_pool = redis.ConnectionPool(
            host=self.host,
            port=self.port,
            db=self.db,
            password=self.password,
            max_connections=self.max_connections,
            decode_responses=self.decode_responses
        )

        # 创建Redis客户端
        self.client = redis.Redis(connection_pool=self.connection_pool)

        # 测试连接
        try:
            self.client.ping()
            self.logger.info(f"成功连接到Redis服务器: {self.host}:{self.port}, DB: {self.db}")
        except Exception as e:
            self.logger.error(f"连接Redis失败: {str(e)}")
            if self.retry_on_error:
                self.logger.info("尝试重新连接...")
                time.sleep(1)
                try:
                    self.client = redis.Redis(connection_pool=self.connection_pool)
                    self.client.ping()
                    self.logger.info("重新连接成功")
                except Exception as e:
                    self.logger.error(f"重新连接失败: {str(e)}")
                    raise ConnectionError("无法连接到Redis服务器") from e
            else:
                raise ConnectionError("无法连接到Redis服务器") from e

    def get(self, key):
        """
        获取缓存值

        :param key: 缓存键
        :return: 缓存值，如果不存在返回None
        """
        try:
            value = self.client.get(key)
            if value is not None:
                # 如果值是JSON格式，尝试解析
                try:
                    return json.loads(value)
                except (TypeError, json.JSONDecodeError):
                    return value
            return None
        except (ConnectionError, TimeoutError) as e:
            self.logger.error(f"获取缓存失败 (key: {key}): {str(e)}")
            return None

    def set(self, key, value, expire=None, use_random_expire=False):
        """
        设置缓存值

        :param key: 缓存键
        :param value: 缓存值
        :param expire: 过期时间（秒），None表示使用默认值
        :param use_random_expire: 是否使用随机过期时间（防止缓存雪崩）
        :return: 是否设置成功
        """
        try:
            # 处理过期时间
            if expire is None:
                expire = self.default_expire

            if use_random_expire:
                # 在基础过期时间上增加随机偏移（最多增加20%）
                random_expire = expire * (1 + random.uniform(0, 0.2))
                expire = int(random_expire)

            # 序列化值（如果不是字符串或字节）
            if not isinstance(value, (str, bytes)):
                value = json.dumps(value)

            # 设置缓存
            result = self.client.setex(key, expire, value)
            return result
        except (ConnectionError, TimeoutError) as e:
            self.logger.error(f"设置缓存失败 (key: {key}): {str(e)}")
            return False

    def delete(self, key):
        """
        删除缓存

        :param key: 缓存键
        :return: 删除的键数量
        """
        try:
            return self.client.delete(key)
        except (ConnectionError, TimeoutError) as e:
            self.logger.error(f"删除缓存失败 (key: {key}): {str(e)}")
            return 0

    def exists(self, key):
        """
        检查缓存是否存在

        :param key: 缓存键
        :return: 是否存在
        """
        try:
            return self.client.exists(key) == 1
        except (ConnectionError, TimeoutError) as e:
            self.logger.error(f"检查缓存是否存在失败 (key: {key}): {str(e)}")
            return False

    def ttl(self, key):
        """
        获取缓存剩余生存时间

        :param key: 缓存键
        :return: 剩余时间（秒），-2表示键不存在，-1表示永不过期
        """
        try:
            return self.client.ttl(key)
        except (ConnectionError, TimeoutError) as e:
            self.logger.error(f"获取缓存TTL失败 (key: {key}): {str(e)}")
            return -1

    def get_or_set(self, key, fetch_func, expire=None, use_random_expire=False, force_refresh=False):
        """
        获取缓存数据，如果不存在则调用fetch_func获取并缓存

        :param key: 缓存键
        :param fetch_func: 获取数据的函数
        :param expire: 过期时间（秒）
        :param use_random_expire: 是否使用随机过期时间
        :param force_refresh: 是否强制刷新缓存
        :return: 缓存数据
        """
        if not force_refresh:
            # 尝试获取缓存
            value = self.get(key)
            if value is not None:
                return value

        # 缓存不存在或需要刷新，从数据源获取
        try:
            value = fetch_func()
            # 设置缓存
            self.set(key, value, expire, use_random_expire)
            return value
        except Exception as e:
            self.logger.error(f"获取数据失败: {str(e)}")
            # 如果获取数据失败，但缓存中已有数据，返回旧数据
            if not force_refresh:
                cached_value = self.get(key)
                if cached_value is not None:
                    self.logger.warning("使用过期缓存数据")
                    return cached_value
            raise

    def get_with_lock(self, key, fetch_func, expire=None, lock_timeout=10, max_retries=3):
        """
        使用分布式锁解决缓存击穿问题

        :param key: 缓存键
        :param fetch_func: 获取数据的函数
        :param expire: 过期时间（秒）
        :param lock_timeout: 锁的超时时间（秒）
        :param max_retries: 最大重试次数
        :return: 缓存数据
        """
        # 尝试获取缓存
        value = self.get(key)
        if value is not None:
            return value

        # 获取分布式锁
        lock_key = f"{key}:lock"
        acquired = self.client.setnx(lock_key, "1")

        if acquired:
            try:
                # 设置锁的过期时间，防止死锁
                self.client.expire(lock_key, lock_timeout)

                # 重新检查缓存（双重检查）
                value = self.get(key)
                if value is not None:
                    return value

                # 从数据源获取数据
                value = fetch_func()
                # 设置缓存
                self.set(key, value, expire)
                return value
            finally:
                # 释放锁
                self.client.delete(lock_key)
        else:
            # 等待并重试
            retry_count = 0
            while retry_count < max_retries:
                time.sleep(0.1 * (retry_count + 1))
                value = self.get(key)
                if value is not None:
                    return value
                retry_count += 1

            # 重试失败，直接调用fetch_func（可能造成数据库压力）
            self.logger.warning(f"获取缓存失败，直接调用数据源 (key: {key})")
            return fetch_func()

    def cache_with_fallback(self, key, fetch_func, fallback_func, expire=None, use_random_expire=False):
        """
        带降级策略的缓存获取

        :param key: 缓存键
        :param fetch_func: 获取数据的函数
        :param fallback_func: 降级函数
        :param expire: 过期时间（秒）
        :param use_random_expire: 是否使用随机过期时间
        :return: 缓存数据或降级数据
        """
        try:
            return self.get_or_set(key, fetch_func, expire, use_random_expire)
        except Exception as e:
            self.logger.error(f"缓存获取失败，使用降级策略 (key: {key}): {str(e)}")
            return fallback_func()

    def set_empty_cache(self, key, expire=60):
        """
        设置空值缓存，防止缓存穿透

        :param key: 缓存键
        :param expire: 过期时间（秒）
        :return: 是否设置成功
        """
        return self.set(key, "__NULL__", expire)

    def is_empty_cache(self, value):
        """
        检查是否为空值缓存

        :param value: 值
        :return: 是否为空值缓存
        """
        return value == "__NULL__"

    def close(self):
        """
        关闭Redis连接
        """
        try:
            self.connection_pool.disconnect()
            self.logger.info("Redis连接已关闭")
        except Exception as e:
            self.logger.error(f"关闭Redis连接失败: {str(e)}")

    def cache(self, key_prefix="", expire=None, use_random_expire=False, empty_cache_expire=60):
        """
        缓存装饰器，用于函数结果缓存

        :param key_prefix: 缓存键前缀
        :param expire: 过期时间（秒）
        :param use_random_expire: 是否使用随机过期时间
        :param empty_cache_expire: 空值缓存的过期时间
        :return: 装饰器
        """

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # 生成缓存键
                key = self._generate_cache_key(key_prefix, func, args, kwargs)

                # 尝试获取缓存
                value = self.get(key)
                if value is not None:
                    if self.is_empty_cache(value):
                        return None
                    return value

                try:
                    # 执行函数获取数据
                    value = func(*args, **kwargs)

                    # 如果结果为None，设置空值缓存
                    if value is None:
                        self.set_empty_cache(key, empty_cache_expire)
                        return None

                    # 设置缓存
                    self.set(key, value, expire, use_random_expire)
                    return value
                except Exception as e:
                    self.logger.error(f"缓存装饰器执行失败: {str(e)}")
                    # 尝试获取旧数据
                    old_value = self.get(key)
                    if old_value is not None and not self.is_empty_cache(old_value):
                        self.logger.warning("使用过期缓存数据")
                        return old_value
                    raise

            return wrapper

        return decorator

    def _generate_cache_key(self, key_prefix, func, args, kwargs):
        """
        生成缓存键

        :param key_prefix: 缓存键前缀
        :param func: 函数
        :param args: 位置参数
        :param kwargs: 关键字参数
        :return: 缓存键
        """
        # 获取函数模块和名称
        module = func.__module__
        name = func.__name__

        # 处理参数
        params = []
        for arg in args:
            params.append(str(arg))
        for k, v in sorted(kwargs.items()):
            params.append(f"{k}={v}")

        # 生成唯一键
        params_str = ":".join(params)
        return f"{key_prefix}{module}:{name}:{params_str}"

    def rate_limiter(self, key, limit=100, window=60):
        """
        速率限制器

        :param key: 速率限制键（如用户ID）
        :param limit: 时间窗口内允许的请求数
        :param window: 时间窗口（秒）
        :return: 是否允许请求
        """
        current = int(time.time())
        # 使用时间窗口的开始时间作为键的一部分
        window_start = current - (current % window)
        key = f"rate_limit:{key}:{window_start}"

        try:
            # 增加计数
            count = self.client.incr(key)

            # 如果是第一个请求，设置过期时间
            if count == 1:
                self.client.expire(key, window)

            # 检查是否超过限制
            return count <= limit
        except (ConnectionError, TimeoutError) as e:
            self.logger.error(f"速率限制检查失败: {str(e)}")
            # Redis不可用时，允许请求（降级）
            return True

    def can_send_otp(self, email, min_interval=60):
        """
        检查是否可以发送验证码（防止频繁发送）

        :param email: 邮箱
        :param min_interval: 最小发送间隔（秒）
        :return: 是否可以发送
        """
        key = f"otp:last:{email}"
        last_sent = self.get(key)
        if last_sent and int(time.time()) - int(last_sent) < min_interval:
            return False
        return True

    def store_otp(self, email, otp_code, expire=300):
        """
        存储验证码

        :param email: 邮箱
        :param otp_code: 验证码
        :param expire: 过期时间（秒）
        :return: 是否存储成功
        """
        key = f"otp:{email}"
        result = self.set(key, otp_code, expire)
        if result:
            # 记录上次发送时间
            self.set(f"otp:last:{email}", int(time.time()), min(expire, 3600))
        return result

    def verify_otp(self, email, user_input_otp):
        """
        验证验证码

        :param email: 邮箱
        :param user_input_otp: 用户输入的验证码
        :return: (是否验证成功, 消息)
        """
        key = f"otp:{email}"
        stored_otp = self.get(key)
        if not stored_otp:
            return False, "验证码已过期或不存在"
        if stored_otp == user_input_otp:
            self.delete(key)  # 验证成功后立即删除
            return True, "验证成功"
        return False, "验证码错误"


# 初始化Redis缓存
cache = RedisCache(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    password=settings.REDIS_PASSWORD,
    default_expire=3600
)

"""
# 初始化Redis缓存
cache = RedisCache(
    host="localhost",
    port=6379,
    db=0,
    password=None,
    default_expire=3600
)

# 设置缓存
cache.set("user:1001:name", "John Doe")

# 获取缓存
name = cache.get("user:1001:name")
print(name)  # 输出: John Doe

# 删除缓存
cache.delete("user:1001:name")

2. 获取或设置缓存
def get_user_from_db(user_id):
    "模拟从数据库获取用户"
    print("从数据库获取用户...")
    return {"id": user_id, "name": "John Doe", "email": "john@example.com"}

# 获取用户，如果缓存不存在则从数据库获取并缓存
user = cache.get_or_set("user:1001", lambda: get_user_from_db(1001))
print(user)

# 再次获取，这次会从缓存中读取
user = cache.get_or_set("user:1001", lambda: get_user_from_db(1001))
print(user)

3. 使用缓存装饰器
@cache.cache(key_prefix="user:", expire=1800)
def get_user(user_id):
    "获取用户信息（结果会被缓存）"
    print(f"从数据库获取用户 {user_id}...")
    return {"id": user_id, "name": "John Doe", "email": "john@example.com"}

# 第一次调用会执行函数并缓存结果
user = get_user(1001)
print(user)

# 第二次调用会直接从缓存获取
user = get_user(1001)
print(user)

4. 验证码功能
import random

def send_otp_email(email):
    "模拟发送验证码邮件"
    otp_code = str(random.randint(100000, 999999))
    print(f"发送验证码 {otp_code} 到 {email}")
    return otp_code

# 检查是否可以发送验证码
email = "user@example.com"
if cache.can_send_otp(email):
    # 生成并存储验证码
    otp_code = send_otp_email(email)
    cache.store_otp(email, otp_code)
else:
    print("请求过于频繁，请稍后再试")

# 验证用户输入的验证码
user_input = "123456"
is_valid, message = cache.verify_otp(email, user_input)
print(f"验证码验证结果: {message}")

4.速率限制
def handle_request(user_id):
    "处理用户请求"
    if not cache.rate_limiter(f"user:{user_id}", limit=5, window=60):
        return "请求过于频繁，请稍后再试"
    
    # 处理请求...
    return "请求处理成功"

# 模拟用户请求
for i in range(10):
    result = handle_request("123")
    print(f"请求 {i+1}: {result}")


6. 高级用法：解决缓存击穿
def get_hot_data():
    "获取热点数据"
    print("从数据库获取热点数据...")
    return {"data": "hot_data_content"}

# 使用分布式锁解决缓存击穿问题
hot_data = cache.get_with_lock("hot_data", get_hot_data, expire=300)
print(hot_data)
"""

if __name__ == "__main__":
    # 设置缓存
    cache.set("user:1001:name", "John Doe")
    # 获取缓存
    name = cache.get("user:1001:name")
    print(name)  # 输出: John Doe
    # 删除缓存
    cache.delete("user:1001:name")