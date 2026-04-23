# 部署信息汇总

远端有三台机器分别是:
192.168.0.140
192.168.0.141
192.168.0.142
三台机器均配置了免密登录

本地ruoyi-cloud代码存在于E:\RuoYi-Cloud-master中

## 1. Redis 集群

### 节点信息
- `192.168.0.140:7000`
- `192.168.0.140:7001`
- `192.168.0.141:7000`
- `192.168.0.141:7001`
- `192.168.0.142:7000`
- `192.168.0.142:7001`

### 集群拓扑
- `3 主 3 从`
- 状态：`cluster_state=ok`

### 认证信息
- 当前未配置 `requirepass`
- 当前未配置 ACL
- 结论：**Redis 当前无密码**

---

## 2. MySQL

### 基本信息
- 部署节点：`192.168.0.140`
- 版本：`5.7.44`
- 端口：`3306`
- 服务名：`mysqld`

### 访问信息
- Host：`192.168.0.140`
- Port：`3306`
- User：`root`
- Password：`MySQL57_20260327Aa1!`


## 4. Nacos 数据库配置

### 数据库连接信息
- DB Host：`192.168.0.140`
- DB Port：`3306`
- DB Name：`nacos`
- DB User：`nacos`
- DB Password：`Nacos_20260327Aa1!`

---

## 5. Nginx 统一入口

### 基本信息
- 部署节点：`192.168.0.140`
- 服务名：`nginx`
- 监听端口：`80`

### 访问入口
- `http://192.168.0.140/nacos/`

### 作用
- 反向代理到三台 Nacos 节点：
- `192.168.0.140:8848`
- `192.168.0.141:8848`
- `192.168.0.142:8848`

---

## 6. Java 环境

### 已安装版本
- 三台机器均已安装：`OpenJDK 11`

### 节点
- `192.168.0.140`
- `192.168.0.141`
- `192.168.0.142`

---

## 7. 安全提醒

### 当前存在密码的组件
- MySQL root
- `MySQL57_20260327Aa1!`
- Nacos 数据库用户 `nacos`
- `Nacos_20260327Aa1!`

### 当前未做鉴权的组件
- Redis：**无密码**
- Nacos 控制台：**未启用鉴权**

### 建议
- 为 Redis 增加访问密码
- 为 Nacos 启用控制台鉴权
- 为 MySQL root 限制远程访问，改用业务账号
---

## 8. RuoYi-Cloud 后端

### 基本信息
- 后端版本：`RuoYi-Cloud springboot2 3.6.8`
- 部署节点：`192.168.0.142`
- 运行方式：`nohup` 直接启动，未注册 `systemd`
- 源码目录：`/opt/ruoyi-cloud/RuoYi-Cloud-springboot2`
- 日志目录：`/opt/ruoyi-cloud/runtime/logs`

### 后端服务端口
- `192.168.0.142:8080` `ruoyi-gateway`
- `192.168.0.142:9200` `ruoyi-auth`
- `192.168.0.142:9201` `ruoyi-system`
- `192.168.0.142:9202` `ruoyi-gen`
- `192.168.0.142:9203` `ruoyi-job`
- `192.168.0.142:9300` `ruoyi-file`
- `192.168.0.142:9100` `ruoyi-monitor`

### 后端验证结果
- `http://192.168.0.142:8080/actuator/health` -> `UP`
- `http://192.168.0.142:9201/actuator/health` -> `UP`
- `http://192.168.0.142:9202/actuator/health` -> `UP`
- `http://192.168.0.142:9203/actuator/health` -> `UP`

### 后端依赖
- MySQL：`192.168.0.140:3306`
- Nacos：`192.168.0.140:8848`、`192.168.0.141:8848`、`192.168.0.142:8848`
- RuoYi 专用 Redis：`192.168.0.142:6379`

### RuoYi 数据库
- DB Name：`ry-cloud`
- DB Host：`192.168.0.140`
- DB Port：`3306`
- DB User：`root`
- DB Password：`MySQL57_20260327Aa1!`

### RuoYi Nacos 配置
- Group：`DEFAULT_GROUP`
- 已发布配置：
- `application-dev.yml`
- `ruoyi-gateway-dev.yml`
- `ruoyi-auth-dev.yml`
- `ruoyi-system-dev.yml`
- `ruoyi-gen-dev.yml`
- `ruoyi-job-dev.yml`
- `ruoyi-file-dev.yml`
- `ruoyi-monitor-dev.yml`
- `sentinel-ruoyi-gateway`

### 运行相关目录
- PID 目录：`/opt/ruoyi-cloud/runtime/pids`
- 文件上传目录：`/opt/ruoyi-cloud/uploadPath`

---

## 9. RuoYi-Cloud 前端

### 基本信息
- 前端项目：`ruoyi-ui`
- 构建节点：`192.168.0.142`
- 发布节点：`192.168.0.140`
- Nginx 静态目录：`/usr/share/nginx/html/ruoyi-ui`

### 访问入口
- 前端首页：`http://192.168.0.140/`
- 后端 API 代理前缀：`http://192.168.0.140/prod-api/`
- 验证码接口：`http://192.168.0.140/prod-api/code`

### Nginx 路由规则
- `/` -> `ruoyi-ui` 静态前端
- `/prod-api/` -> `192.168.0.142:8080`
- `/nacos/` -> Nacos 集群

### 前端验证结果
- `http://192.168.0.140/` 返回前端 `index.html`
- `http://192.168.0.140/prod-api/code` 返回验证码 JSON
- `http://192.168.0.140/nacos/` 仍可正常访问

---

## 10. RuoYi 默认登录信息

### 后端初始化数据
- 默认管理员账号：`admin`
- 默认密码：`admin123`

### 提示
- 如对外使用，建议尽快修改默认密码
