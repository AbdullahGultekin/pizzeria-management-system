import { useEffect, useRef, useState, useCallback } from 'react'

interface WebSocketMessage {
  type: string
  timestamp?: string
  data?: any
  order_id?: number
  role?: string
}

interface UseWebSocketOptions {
  url?: string
  onMessage?: (message: WebSocketMessage) => void
  onOpen?: () => void
  onClose?: () => void
  onError?: (error: Event) => void
  reconnectInterval?: number
  autoConnect?: boolean
}

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

export const useWebSocket = (options: UseWebSocketOptions = {}) => {
  const {
    url = `${API_BASE_URL.replace('/api/v1', '')}/ws`,
    onMessage,
    onOpen,
    onClose,
    onError,
    reconnectInterval = 3000,
    autoConnect = true,
  } = options

  const [isConnected, setIsConnected] = useState(false)
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null)
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const shouldReconnectRef = useRef(true)

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN || wsRef.current?.readyState === WebSocket.CONNECTING) {
      return
    }

    // Don't try to connect if URL is invalid
    if (!url || url === 'undefined/ws') {
      console.warn('WebSocket URL is invalid, skipping connection')
      return
    }

    try {
      // Convert http:// to ws:// and https:// to wss://
      const wsUrl = url.replace(/^http:/, 'ws:').replace(/^https:/, 'wss:')
      const ws = new WebSocket(wsUrl)
      wsRef.current = ws

      ws.onopen = () => {
        setIsConnected(true)
        onOpen?.()
        
        // Subscribe as admin if needed
        if (url.includes('admin')) {
          ws.send(JSON.stringify({ type: 'subscribe_admin' }))
        }
      }

      ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data)
          setLastMessage(message)
          onMessage?.(message)
        } catch (error) {
          console.error('Error parsing WebSocket message:', error)
        }
      }

      ws.onclose = (event) => {
        setIsConnected(false)
        onClose?.()

        // Only reconnect if it wasn't a normal closure and we should reconnect
        // Don't spam reconnect attempts if backend is not available
        if (shouldReconnectRef.current && autoConnect && event.code !== 1000) {
          // Limit reconnect attempts - exponential backoff
          const attemptCount = (wsRef.current as any)?._reconnectAttempts || 0
          const maxAttempts = 2 // Only try 2 times, then give up
          
          if (attemptCount < maxAttempts) {
            (wsRef.current as any)._reconnectAttempts = attemptCount + 1
            reconnectTimeoutRef.current = setTimeout(() => {
              connect()
            }, reconnectInterval * Math.pow(2, attemptCount)) // Exponential backoff
          }
        }
      }

      ws.onerror = (error) => {
        // Silently handle WebSocket errors - it's optional functionality
        // Don't spam console with errors if backend doesn't support WebSocket
        onError?.(error)
      }
    } catch (error) {
      console.error('Error creating WebSocket connection:', error)
    }
  }, [url, onMessage, onOpen, onClose, onError, reconnectInterval])

  const disconnect = useCallback(() => {
    shouldReconnectRef.current = false
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
    }
    if (wsRef.current) {
      wsRef.current.close()
      wsRef.current = null
    }
    setIsConnected(false)
  }, [])

  const sendMessage = useCallback((message: any) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message))
    } else {
      console.warn('WebSocket is not connected. Message not sent:', message)
    }
  }, [])

  useEffect(() => {
    if (autoConnect) {
      connect()
    }

    return () => {
      disconnect()
    }
  }, [autoConnect, connect, disconnect])

  return {
    isConnected,
    lastMessage,
    connect,
    disconnect,
    sendMessage,
  }
}

