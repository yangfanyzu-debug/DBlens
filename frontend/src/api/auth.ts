import http from './http'

export interface CurrentUser {
  user_id: number
  username: string
  nickname?: string | null
  roles: string[]
  permissions: string[]
  is_admin: boolean
}

export function getCurrentUser() {
  return http.get<{ user: CurrentUser }>('/auth/me').then(r => r.data)
}
