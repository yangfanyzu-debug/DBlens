import { useQueryStore } from '@/stores/query'

export class QueryWebSocket {
  private ws: WebSocket | null = null
  private queryId: string
  private pollTimer: number | null = null
  private stopped = false

  constructor(queryId: string) {
    this.queryId = queryId
  }

  connect(): Promise<void> {
    const protocol = location.protocol === 'https:' ? 'wss' : 'ws'
    const wsUrl = `${protocol}://${location.host}/dblens-api/ws/${this.queryId}`
    console.log('[WS] Connecting to', wsUrl)

    return new Promise((resolve) => {
      let settled = false
      const settle = () => {
        if (settled) return
        settled = true
        resolve()
      }
      const timeout = window.setTimeout(settle, 1500)

      try {
        this.ws = new WebSocket(wsUrl)
        this.ws.onopen = () => {
          console.log('[WS] Connected', this.queryId)
          window.clearTimeout(timeout)
          settle()
        }
        this.ws.onmessage = (e) => {
          console.log('[WS] onmessage fired, data length:', e.data.length, 'data:', e.data.slice(0, 200))
          try {
            const data = JSON.parse(e.data)
            console.log('[WS] Parsed, type:', data.type, 'status:', data.status)
            useQueryStore().setResult(this.queryId, data)
          } catch (err) {
            console.error('[WS] JSON parse error:', err, 'raw:', e.data)
          }
        }
        this.ws.onerror = (e) => {
          console.log('[WS] onerror', e)
          window.clearTimeout(timeout)
          settle()
        }
        this.ws.onclose = (e) => {
          console.log('[WS] onclose, code:', e.code, 'reason:', e.reason, 'wasClean:', e.wasClean)
          this.ws = null
          window.clearTimeout(timeout)
          settle()
          if (!this.stopped) {
            console.log('[WS] Unclean close, starting polling fallback')
            this.startPolling()
          }
        }
      } catch (err) {
        console.log('[WS] Exception', err)
        window.clearTimeout(timeout)
        this.startPolling()
        settle()
      }
    })
  }

  send(data: object) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data))
    } else {
      console.log('[WS] send failed, readyState:', this.ws?.readyState)
    }
  }

  private startPolling() {
    if (this.stopped) return
    console.log('[WS] Polling started')
    let attempts = 0
    this.pollTimer = window.setInterval(() => {
      attempts++
      const res = useQueryStore().getResult(this.queryId)
      if (res && res.status !== 'running') {
        console.log('[WS] Polling found result:', res.status)
        this.stop()
        return
      }
      if (attempts >= 120) {
        console.log('[WS] Polling timeout')
        this.stop()
      }
    }, 500)
  }

  stop() {
    this.stopped = true
    if (this.ws) {
      console.log('[WS] Closing, readyState:', this.ws.readyState)
      this.ws.close()
      this.ws = null
    }
    if (this.pollTimer) {
      clearInterval(this.pollTimer)
      this.pollTimer = null
    }
  }
}
