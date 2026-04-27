-- DBLens 外链菜单接入脚本
-- 建议在 ry-cloud 库中执行

SET @dblens_menu_path = 'http://192.168.0.140/dblens/';
SET @dblens_menu_name = 'DBLens';

INSERT INTO sys_menu (
  menu_name,
  parent_id,
  order_num,
  path,
  component,
  query,
  route_name,
  is_frame,
  is_cache,
  menu_type,
  visible,
  status,
  perms,
  icon,
  create_by,
  create_time,
  update_by,
  update_time,
  remark
)
SELECT
  @dblens_menu_name,
  0,
  91,
  @dblens_menu_path,
  NULL,
  '',
  'DBLens',
  0,
  1,
  'C',
  '0',
  '0',
  '',
  'skill',
  'admin',
  SYSDATE(),
  '',
  NULL,
  'DBLens 外链菜单'
WHERE NOT EXISTS (
  SELECT 1 FROM sys_menu WHERE path = @dblens_menu_path
);

SET @dblens_menu_id = (
  SELECT menu_id
  FROM sys_menu
  WHERE path = @dblens_menu_path
  LIMIT 1
);

INSERT IGNORE INTO sys_role_menu (role_id, menu_id)
SELECT role_id, @dblens_menu_id
FROM sys_role
WHERE status = '0';
