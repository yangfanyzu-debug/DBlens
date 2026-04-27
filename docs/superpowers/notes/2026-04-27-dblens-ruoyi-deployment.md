# DBLens RuoYi 接入说明

## 目标

- 不改 RuoYi 前端源码
- 通过 `sys_menu` 外链菜单接入 DBLens
- 复用 RuoYi 当前登录态
- 所有已登录用户可使用 DBLens
- 只有管理员可维护连接配置

## 推荐部署形态

- RuoYi 前端入口：`http://192.168.0.140/`
- RuoYi 网关入口：`http://192.168.0.140/prod-api/`
- DBLens 前端入口：`http://192.168.0.140/dblens/`
- DBLens 后端入口：`http://192.168.0.140/api/`

这样做的原因：

- `DBLens` 与 `RuoYi` 保持同域，浏览器可直接携带 `Admin-Token` cookie
- DBLens 前端已实现从 cookie 读取 `Admin-Token`，并转成 `Authorization: Bearer <token>`
- DBLens 后端会将该 token 转发给 RuoYi `/system/user/getInfo`
- 无需为 DBLens 单独建设用户体系

## Nginx 接入要点

- 为 `/dblens/` 增加静态资源或前端反向代理
- 为 `/api/` 增加 DBLens 后端反向代理
- 保持现有 `/prod-api/` 路由不变
- 确认 `Admin-Token` cookie 的 `Path` 覆盖 `/`，否则 DBLens 页面读不到该 cookie

## 菜单接入

- 直接执行仓库中的 `sql/dblens_ruoyi_menu.sql`
- 或在 RuoYi 菜单管理中手工新增：
  - 菜单类型：菜单
  - 是否外链：是
  - 路由地址：`http://192.168.0.140/dblens/`
  - 状态：正常
  - 可见：显示

## 当前权限边界

- 后端已强制要求登录用户才能访问连接与数据库能力
- 连接的新建、编辑、删除、测试仅管理员可执行
- 前端仅做管理员按钮隐藏，最终权限以后端校验为准

## 本地开发补充

- 当前代码为 `localhost` / `127.0.0.1` 保留了本地开发兜底管理员身份
- 该兜底仅用于本机开发联调，不影响生产走 RuoYi 登录态
