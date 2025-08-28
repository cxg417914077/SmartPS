### 数据库

```bash
# 1. 运行 PostgreSQL 容器并指定账号密码和数据库
docker run --name smartps-db \
  -e POSTGRES_USER=admin \
  -e POSTGRES_PASSWORD=admin \
  -e POSTGRES_DB=test_db \
  -p 5432:5432 \
  -d postgres:15
```


alembic revision --autogenerate -m "initial migration"

alembic upgrade head