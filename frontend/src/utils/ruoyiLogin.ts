export interface RuoYiLoginUrlOptions {
  configuredLoginUrl?: string
  origin: string
  currentPath: string
  currentSearch: string
  currentHash: string
}

export function buildRuoYiLoginUrl(options: RuoYiLoginUrlOptions) {
  const configuredUrl = options.configuredLoginUrl?.trim()
  const loginUrl = new URL(configuredUrl || '/login', options.origin)
  const redirectTarget = `${options.currentPath}${options.currentSearch}${options.currentHash}`

  loginUrl.searchParams.set('redirect', redirectTarget)

  return loginUrl.href
}
