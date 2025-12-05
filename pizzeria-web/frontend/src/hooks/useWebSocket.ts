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
  const failureCountRef = useRef(0)
  const isConnectingRef = useRef(false)
  
  // Store callbacks in refs to prevent unnecessary re-renders
  const onMessageRef = useRef(onMessage)
  const onOpenRef = useRef(onOpen)
  const onCloseRef = useRef(onClose)
  const onErrorRef = useRef(onError)
  
  // Update refs when callbacks change
  useEffect(() => {
    onMessageRef.current = onMessage
    onOpenRef.current = onOpen
    onCloseRef.current = onClose
    onErrorRef.current = onError
  }, [onMessage, onOpen, onClose, onError])

  const connect = useCallback(() => {
    // Prevent multiple simultaneous connection attempts
    if (isConnectingRef.current || wsRef.current?.readyState === WebSocket.OPEN || wsRef.current?.readyState === WebSocket.CONNECTING) {
      return
    }

    // Don't try to connect if URL is invalid
    if (!url || url === 'undefined/ws' || url.includes('undefined')) {
      console.warn('WebSocket URL is invalid, skipping connection')
      shouldReconnectRef.current = false // Stop trying
      return
    }

    // Check if we've already failed too many times
    if (failureCountRef.current >= 3) {
      shouldReconnectRef.current = false // Stop trying after 3 failures
      return
    }

    try {
      // Convert http:// to ws:// and https:// to wss://
      let wsUrl = url
      if (wsUrl.startsWith('http://')) {
        wsUrl = wsUrl.replace('http://', 'ws://')
      } else if (wsUrl.startsWith('https://')) {
        wsUrl = wsUrl.replace('https://', 'wss://')
      }
      
      // Don't try to connect if URL is still invalid after conversion
      if (!wsUrl || wsUrl === 'ws://undefined/ws' || wsUrl === 'wss://undefined/ws') {
        console.warn('WebSocket URL is invalid after conversion, skipping connection')
        shouldReconnectRef.current = false
        return
      }
      
      isConnectingRef.current = true
      failureCountRef.current = 0 // Reset failure count on new connection attempt
      const ws = new WebSocket(wsUrl)
      wsRef.current = ws

      ws.onopen = () => {
        isConnectingRef.current = false
        failureCountRef.current = 0 // Reset on successful connection
        setIsConnected(true)
        onOpenRef.current?.()
        
        // Subscribe as admin if needed
        if (url.includes('admin')) {
          ws.send(JSON.stringify({ type: 'subscribe_admin' }))
        }
      }

      ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data)
          setLastMessage(message)
          onMessageRef.current?.(message)
        } catch (error) {
          console.error('Error parsing WebSocket message:', error)
        }
      }

      ws.onclose = (event) => {
        isConnectingRef.current = false
        setIsConnected(false)
        onCloseRef.current?.()

        // Only reconnect if it wasn't a normal closure (code 1000) and we should reconnect
        // Normal closure means the connection was closed intentionally
        if (event.code === 1000) {
          // Normal closure - don't reconnect
          shouldReconnectRef.current = false
          return
        }

        // Increment failure count
        failureCountRef.current += 1

        // Only reconnect if we haven't exceeded max attempts and should reconnect
        if (shouldReconnectRef.current && autoConnect && failureCountRef.current < 3) {
          // Wait before reconnecting
          reconnectTimeoutRef.current = setTimeout(() => {
            if (shouldReconnectRef.current && !isConnectingRef.current) {
              connect()
            }
          }, reconnectInterval)
        } else {
          // After max attempts, stop trying silently
          shouldReconnectRef.current = false
        }
      }

      ws.onerror = (error) => {
        isConnectingRef.current = false
        // Silently handle WebSocket errors - it's optional functionality
        // The onclose handler will handle reconnection logic
        onErrorRef.current?.(error)
      }
    } catch (error) {
      isConnectingRef.current = false
      failureCountRef.current += 1
      console.error('Error creating WebSocket connection:', error)
    }
  }, [url, reconnectInterval, autoConnect]) // Removed callbacks from dependencies - using refs instead

  const disconnect = useCallback(() => {
    shouldReconnectRef.current = false
    isConnectingRef.current = false
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
      reconnectTimeoutRef.current = null
    }
    if (wsRef.current) {
      // Close with normal closure code to prevent reconnection
      wsRef.current.close(1000, 'Intentional disconnect')
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
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [autoConnect]) // Only depend on autoConnect to prevent infinite loops

  return {
    isConnected,
    lastMessage,
    connect,
    disconnect,
    sendMessage,
  }
}

