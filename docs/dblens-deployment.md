# DBLens 部署文档

## 1. 目标

- 部署 `DBLens` 前端到 `192.168.0.140`
- 部署 `DBLens` 后端到 `192.168.0.142`
- 通过 `192.168.0.140` 的 `nginx` 对外提供统一入口
- 复用 `RuoYi-Cloud` 的登录态，不新增 DBLens 独立账号体系

当前推荐入口：

- 前端：`http://192.168.0.140/dblens/`
- 后端 API：`http://192.168.0.140/dblens-api/`

## 2. 部署拓扑

- `192.168.0.140`
  - `nginx`
  - RuoYi 前端静态资源
  - DBLens 前端静态资源
- `192.168.0.142`
  - `RuoYi-Cloud` 后端服务
  - `DBLens` 后端服务

请求路径约定：

- `/dblens/` -> DBLens 前端静态资源
- `/dblens-api/` -> DBLens 后端 HTTP API
- `/dblens-api/ws/` -> DBLens 后端 WebSocket
- `/prod-api/` -> RuoYi gateway

说明：

- 浏览器不会直接连接 `192.168.0.142`
- 包括 SQL 执行使用的 `WebSocket` 在内，所有 DBLens 请求都先到 `192.168.0.140`
- 再由 `nginx` 转发到 `192.168.0.142`

## 3. 目录约定

### 3.1 本地仓库

- 仓库根目录：`D:\traeWK\DBLens`
- 前端目录：`D:\traeWK\DBLens\frontend`
- 后端目录：`D:\traeWK\DBLens\backend`

### 3.2 远端目录

`192.168.0.140`

- DBLens 前端静态目录：`/usr/share/nginx/html/dblens`
- `nginx` 配置文件：`/etc/nginx/nginx.conf`

`192.168.0.142`

- DBLens 后端目录：`/opt/dblens/app/backend`
- DBLens 运行目录：`/opt/dblens/runtime`
- Python 虚拟环境：`/opt/dblens/venv`
- 启停脚本：`/opt/dblens/app/backend/dblensctl.sh`
- 日志目录：`/opt/dblens/runtime/logs`

## 4. 认证与权限模型

- DBLens 不单独维护账号
- 前端从浏览器读取 RuoYi 的 `Admin-Token`
- 前端将 `Admin-Token` 转成 `Authorization: Bearer <token>`
- DBLens 后端拿该 token 请求 RuoYi 的 `/system/user/getInfo`
- DBLens 根据返回的用户信息判断权限

当前权限规则：

- 所有已登录 RuoYi 用户都可以使用 DBLens
- 只有管理员可以新建、编辑、删除、测试连接

部署前提：

- DBLens 与 RuoYi 必须保持同域访问
- `Admin-Token` 的 cookie `Path` 必须覆盖 `/`

## 5. 本地构建

### 5.1 前端构建

```powershell
cd D:\traeWK\DBLens\frontend
npm install
npm run build
```

构建产物目录：

- `D:\traeWK\DBLens\frontend\dist`

### 5.2 后端说明

后端不需要单独打包成 wheel 或镜像，直接同步源码目录即可。

本地启动方式：

```powershell
cd D:\traeWK\DBLens\backend
.\venv\Scripts\python.exe run.py
```

## 6. 前端部署

### 6.1 上传前端静态资源

将本地 `frontend/dist` 的内容覆盖到：

- `/usr/share/nginx/html/dblens`

如果使用压缩包方式，可参考：

```powershell
cd D:\traeWK\DBLens\frontend
tar -cf ..\output\deploy\frontend-dist.tar dist
scp ..\output\deploy\frontend-dist.tar root@192.168.0.140:/tmp/dblens-frontend-dist.tar
```

远端解压示例：

```bash
rm -rf /usr/share/nginx/html/dblens/*
mkdir -p /usr/share/nginx/html/dblens
tar -xf /tmp/dblens-frontend-dist.tar -C /usr/share/nginx/html/dblens --strip-components=1
```

## 7. 后端部署

### 7.0 初始化 DBLens 元数据库

DBLens 后端使用 MySQL 保存元数据，包括连接配置、查询会话和操作日志。

推荐方式是先建库，再由 Alembic 建表：

```sql
CREATE DATABASE IF NOT EXISTS dblens
  DEFAULT CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;
```

也可以直接执行仓库中的建库脚本：

- `D:\traeWK\DBLens\sql\create_dblens_database.sql`

如果目标生产环境不方便运行 Alembic，可以改用完整初始化脚本：

- `D:\traeWK\DBLens\sql\init_dblens_mysql.sql`

完整初始化脚本会创建以下表，并写入 `alembic_version=0003`：

- `connections`
- `query_sessions`
- `operation_logs`
- `alembic_version`

生产环境建议使用 DBLens 专用 MySQL 账号，而不是长期使用 `root`：

```sql
CREATE USER IF NOT EXISTS 'dblens'@'%' IDENTIFIED BY '请替换为强密码';
GRANT ALL PRIVILEGES ON dblens.* TO 'dblens'@'%';
FLUSH PRIVILEGES;
```

### 7.1 同步后端代码

将本地 `backend` 目录中的应用代码同步到：

- `/opt/dblens/app/backend`

注意保留远端已有文件：

- `.env`
- `dblensctl.sh`
- `venv`
- `runtime`

压缩包方式示例：

```powershell
cd D:\traeWK\DBLens
tar -cf output\deploy\backend-app.tar backend\app backend\alembic backend\alembic.ini backend\run.py backend\requirements.txt
scp output\deploy\backend-app.tar root@192.168.0.142:/tmp/dblens-backend-app.tar
```

远端解压示例：

```bash
cd /opt/dblens/app/backend
find . -mindepth 1 -maxdepth 1 ! -name ".env" ! -name "dblensctl.sh" -exec rm -rf {} +
tar -xf /tmp/dblens-backend-app.tar -C /opt/dblens/app/backend --strip-components=1
```

### 7.2 后端环境变量

远端 `.env` 至少需要包含以下配置：

```env
DATABASE_URL=mysql+aiomysql://dblens:请替换为强密码@<mysql-host>:3306/dblens?charset=utf8mb4
DBLENS_SECRET_KEY=请替换为固定高强度密钥
LOCAL_DEV_AUTH_ENABLED=false
RUOYI_BASE_URL=http://<nginx-host>/prod-api
```

说明：

- `DATABASE_URL` 是 DBLens 自己的元数据库
- `DBLENS_SECRET_KEY` 必须固定保存，不能每次部署或重启重新生成，否则已保存的连接密码将无法解密
- `LOCAL_DEV_AUTH_ENABLED=false` 表示生产环境禁用本地开发兜底身份
- `RUOYI_BASE_URL` 指向 `RuoYi gateway` 对外入口

### 7.3 安装依赖并执行数据库迁移

如果使用 Alembic 管理建表，上传后端代码后需要在后端节点执行：

```bash
cd /opt/dblens/app/backend
/opt/dblens/venv/bin/python -m pip install -r requirements.txt
/opt/dblens/venv/bin/python -m alembic upgrade head
```

执行完成后，DBLens 元数据库中应存在：

- `connections`
- `query_sessions`
- `operation_logs`
- `alembic_version`

如果已经执行过 `sql/init_dblens_mysql.sql`，仍可以运行 `alembic upgrade head` 做一致性确认；此时 Alembic 应识别当前版本为 `0003`，不会重复建表。

### 7.4 启停后端

启动：

```bash
cd /opt/dblens/app/backend
./dblensctl.sh start
```

停止：

```bash
cd /opt/dblens/app/backend
./dblensctl.sh stop
```

注意：

- 当前远端 `dblensctl.sh` 的 `restart` 存在行为问题
- 建议暂时不要直接使用 `./dblensctl.sh restart`
- 需要重启时，改为手动执行 `stop` 后再执行 `start`

## 8. Nginx 配置

`192.168.0.140` 的 `nginx` 需要同时代理静态资源、HTTP API 和 WebSocket。

参考配置：

```nginx
location /dblens/ {
    alias /usr/share/nginx/html/dblens/;
    try_files $uri $uri/ /dblens/index.html;
}

location ^~ /dblens-api/ws/ {
    proxy_pass http://192.168.0.142:8000/ws/;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}

location ^~ /dblens-api/ {
    proxy_pass http://192.168.0.142:8000/api/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

配置生效：

```bash
nginx -t
systemctl restart nginx
```

说明：

- 这次部署里，单独 `nginx -s reload` 没有让新增路由立即生效
- 实际以 `systemctl restart nginx` 后生效为准

## 9. RuoYi 菜单接入

推荐方式：

- 在 RuoYi 菜单管理中新增一个外链菜单
- 菜单地址填写：`http://192.168.0.140/dblens/`

也可以使用仓库中的 SQL：

- `D:\traeWK\DBLens\sql\dblens_ruoyi_menu.sql`

注意：

- SQL 中的 `@dblens_menu_path` 默认为 `http://192.168.0.140/dblens/`
- 部署到新生产环境前，需要替换为新的域名或 IP

菜单要求：

- 菜单类型：菜单
- 是否外链：是
- 状态：正常

## 10. 验证步骤

### 10.1 验证前端

```bash
curl -I http://192.168.0.140/dblens/
```

期望：

- 返回 `200 OK`

### 10.2 验证静态资源

```bash
curl -I http://192.168.0.140/dblens/assets/index-*.js
curl -I http://192.168.0.140/dblens/assets/index-*.css
```

期望：

- JS 返回 `application/javascript`
- CSS 返回 `text/css`

### 10.3 验证后端接口

```bash
curl -i http://192.168.0.140/dblens-api/auth/me
```

期望：

- 未登录时返回 `401`
- 返回 JSON，而不是 HTML 页面

### 10.4 验证后端健康状态

```bash
curl http://127.0.0.1:8000/health
```

执行位置：

- `192.168.0.142`

期望：

- 返回健康状态

### 10.5 验证元数据库表

在 DBLens 元数据库中执行：

```sql
SHOW TABLES;
SELECT version_num FROM alembic_version;
```

期望至少包含：

- `connections`
- `query_sessions`
- `operation_logs`
- `alembic_version`

当前版本期望为：

- `0003`

### 10.6 验证 WebSocket

在浏览器打开：

- `http://192.168.0.140/dblens/`

然后执行一条 SQL，确认：

- 浏览器请求地址为 `ws://192.168.0.140/dblens-api/ws/{queryId}` 或 `wss://...`
- 不是直接访问 `192.168.0.142`
- 查询结果可以正常返回到页面

## 11. 常见问题

### 11.1 页面能打开，但提示未登录

检查：

- 当前是否已登录 RuoYi
- `Admin-Token` cookie 是否存在
- cookie 的 `Path` 是否覆盖 `/`
- DBLens 和 RuoYi 是否同域访问

### 11.2 `/dblens-api/auth/me` 返回 HTML

这通常说明：

- `nginx` 路由没有命中 DBLens API
- 请求落到了别的前端站点

优先检查：

- `/dblens-api/` 路由是否已配置
- `nginx` 是否已真正重启生效

### 11.3 SQL 执行一直转圈

优先检查：

- `/dblens-api/ws/` 的 `nginx` WebSocket 转发是否存在
- 是否配置了 `Upgrade` 和 `Connection` 头
- 浏览器是否实际连接到了 `192.168.0.140/dblens-api/ws/...`

### 11.4 本地能用，生产不能用

注意：

- 本地开发允许 `localhost/127.0.0.1` 使用开发兜底身份
- 生产环境依赖真实 RuoYi 登录态
- 生产环境必须确保 `LOCAL_DEV_AUTH_ENABLED=false`

## 12. 当前生产参考值

当前环境已验证的参考值：

- DBLens 前端：`http://192.168.0.140/dblens/`
- DBLens 后端：`http://192.168.0.140/dblens-api/`
- RuoYi gateway：`http://192.168.0.140/prod-api/`
- DBLens backend 运行地址：`http://192.168.0.142:8000`
- DBLens backend 健康检查：`http://127.0.0.1:8000/health`
