import http from './http'

export const listDatabases = (connId: string) =>
  http.get<string[]>('/databases', { params: { conn_id: connId } }).then(r => r.data)

export const listTables = (connId: string, database: string) =>
  http.get<{ name: string; type: string }[]>(`/databases/${database}/tables`, { params: { conn_id: connId } }).then(r => r.data)

export const listColumns = (connId: string, database: string, table: string) =>
  http.get(`/databases/${database}/tables/${table}/columns`, { params: { conn_id: connId } }).then(r => r.data)

export const listIndexes = (connId: string, database: string, table: string) =>
  http.get(`/databases/${database}/tables/${table}/indexes`, { params: { conn_id: connId } }).then(r => r.data)

export const listForeignKeys = (connId: string, database: string, table: string) =>
  http.get(`/databases/${database}/tables/${table}/foreign_keys`, { params: { conn_id: connId } }).then(r => r.data)

export const getSchema = (connId: string, database: string) =>
  http.get(`/databases/${database}/schema`, { params: { conn_id: connId } }).then(r => r.data)
