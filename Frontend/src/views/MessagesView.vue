<template>
  <div class="sm-messages-wrapper">
    <div class="sm-messages-container">

      <!-- ==========================================
           LEFT SIDEBAR: Conversation List
      ========================================== -->
      <aside class="sm-sidebar">
        <!-- Header -->
        <div class="sidebar-header">
          <div class="title-row">
            <h2>Messages</h2>
            <button class="sm-icon-btn" type="button" title="New Message">
              ✏️
            </button>
          </div>

          <!-- Search Input -->
          <div class="search-box">
            <span class="search-icon">🔍</span>
            <input 
              v-model="searchQuery" 
              type="text" 
              placeholder="Search conversations..." 
            />
          </div>
        </div>

        <!-- Chat List Container -->
        <div class="conversations-list">
          <template v-if="filteredConversations.length > 0">
            <div 
              v-for="chat in filteredConversations" 
              :key="chat.id"
              :class="['chat-item', { active: activeChat?.id === chat.id }]"
              @click="selectChat(chat)"
            >
              <div class="avatar-box">
                {{ getInitials(chat.name) }}
                <span v-if="chat.online" class="online-badge"></span>
              </div>

              <div class="chat-details">
                <div class="chat-name">{{ chat.name }}</div>
                <div class="chat-sub">
                  <span class="preview-text">{{ chat.lastMessage }}</span>
                  <span class="dot" v-if="chat.time">•</span>
                  <span>{{ chat.time }}</span>
                </div>
              </div>

              <div v-if="chat.unread" class="unread-badge"></div>
            </div>
          </template>

          <!-- Empty Conversations State -->
          <div v-else class="empty-list">
            <p>No conversations found</p>
          </div>
        </div>
      </aside>

      <!-- ==========================================
           RIGHT MAIN: Active Chat Room
      ========================================== -->
      <main class="sm-chat-main">
        <template v-if="activeChat">
          <!-- Room Header -->
          <header class="chat-header">
            <div class="header-user">
              <div class="avatar-box small">
                {{ getInitials(activeChat.name) }}
              </div>
              <div class="user-info">
                <div class="user-name">{{ activeChat.name }}</div>
                <div class="user-status">
                  {{ activeChat.online ? 'Online' : 'Offline' }}
                </div>
              </div>
            </div>

            <div class="header-actions">
              <button class="action-btn" type="button" title="View Details">ℹ️</button>
            </div>
          </header>

          <!-- Messages Body -->
          <div ref="messageContainer" class="messages-body">
            <template v-if="messages.length > 0">
              <div 
                v-for="msg in messages" 
                :key="msg.id" 
                :class="['msg-row', msg.sender === 'me' ? 'me' : 'them']"
              >
                <div v-if="msg.sender !== 'me'" class="avatar-box tiny">
                  {{ getInitials(activeChat.name) }}
                </div>

                <div class="msg-content">
                  <div class="msg-bubble">
                    <p>{{ msg.text }}</p>
                  </div>
                  <span class="msg-time">{{ msg.time }}</span>
                </div>
              </div>
            </template>

            <!-- Empty Messages inside selected chat -->
            <div v-else class="empty-chat-body">
              <p>This is the start of your conversation with <strong>{{ activeChat.name }}</strong>.</p>
            </div>
          </div>

          <!-- Bottom Input Bar -->
          <footer class="chat-footer">
            <form @submit.prevent="sendMessage" class="input-form">
              <button type="button" class="tool-btn" title="Attach file">📎</button>

              <div class="input-pill">
                <input 
                  v-model="newMessage" 
                  type="text" 
                  placeholder="Type a message..." 
                />
              </div>

              <button type="submit" class="send-btn" :disabled="!newMessage.trim()">
                Send
              </button>
            </form>
          </footer>
        </template>

        <!-- Placeholder when no conversation is selected -->
        <div v-else class="empty-selection-state">
          <div class="empty-icon">💬</div>
          <h3>Your Messages</h3>
          <p>Select a conversation from the left to start messaging on ServiceMarket.</p>
        </div>
      </main>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick } from 'vue'

// Reactive state
const searchQuery = ref('')
const activeChat = ref(null)
const newMessage = ref('')
const messageContainer = ref(null)

// Dynamic State – you will inject data here from your backend REST API (e.g., Django)
const conversations = ref([
  // Example structure:
  // { id: 1, name: 'John Doe', lastMessage: 'Hey there!', time: '10:45 AM', unread: 2, online: true }
])

// Messages for the currently active chat
const messages = ref([
  // Example:
  // { id: 1, sender: 'them', text: 'Hello!', time: '10:40 AM' }
  // { id: 2, sender: 'me', text: 'Hi!', time: '10:42 AM' }
])

// Computed: filter conversations based on search query
const filteredConversations = computed(() => {
  const q = searchQuery.value.toLowerCase().trim()
  if (!q) return conversations.value
  return conversations.value.filter(c => 
    c.name.toLowerCase().includes(q) || 
    (c.lastMessage && c.lastMessage.toLowerCase().includes(q))
  )
})

// Select a chat and mark it as read
const selectChat = (chat) => {
  activeChat.value = chat
  chat.unread = false
  scrollToBottom()
}

// Send a new message
const sendMessage = () => {
  if (!newMessage.value.trim() || !activeChat.value) return

  messages.value.push({
    id: Date.now(),
    sender: 'me',
    text: newMessage.value.trim(),
    time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  })

  const chat = conversations.value.find(c => c.id === activeChat.value.id)
  if (chat) {
    chat.lastMessage = `You: ${newMessage.value}`
  }

  newMessage.value = ''
  scrollToBottom()
}

// Helper: get initials from a name
const getInitials = (name) => {
  if (!name) return 'SM'
  return name
    .split(' ')
    .map(part => part[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
}

// Scroll the message container to the bottom
const scrollToBottom = async () => {
  await nextTick()
  if (messageContainer.value) {
    messageContainer.value.scrollTop = messageContainer.value.scrollHeight
  }
}
</script>

<style scoped>
*, *::before, *::after {
  box-sizing: border-box;
}

/* Base ServiceMarket Theme Wrapper */
.sm-messages-wrapper {
  width: 100%;
  min-height: calc(100vh - 90px);
  background-color: #f8fafc;
  color: #1e293b;
  font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  display: flex;
  justify-content: center;
  padding: 20px 16px;
}

.sm-messages-container {
  width: 100%;
  max-width: 1200px;
  height: calc(100vh - 130px);
  min-height: 580px;
  background-color: #ffffff;
  border-radius: 16px;
  border: 1px solid #e2e8f0;
  display: flex;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
}

/* Sidebar Styles */
.sm-sidebar {
  width: 340px;
  flex-shrink: 0;
  background-color: #ffffff;
  border-right: 1px solid #e2e8f0;
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  padding: 20px 16px 12px 16px;
  border-bottom: 1px solid #f1f5f9;
}

.title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
}

.title-row h2 {
  font-size: 20px;
  font-weight: 700;
  color: #0f172a;
  margin: 0;
}

.sm-icon-btn {
  background: #f1f5f9;
  border: none;
  color: #475569;
  width: 34px;
  height: 34px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  transition: background 0.2s;
}

.sm-icon-btn:hover {
  background: #e2e8f0;
}

.search-box {
  position: relative;
}

.search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 13px;
  color: #94a3b8;
}

.search-box input {
  width: 100%;
  padding: 9px 12px 9px 36px;
  background-color: #f1f5f9;
  border: 1px solid transparent;
  border-radius: 10px;
  color: #0f172a;
  font-size: 13.5px;
  outline: none;
  transition: all 0.2s;
}

.search-box input:focus {
  background-color: #ffffff;
  border-color: #cbd5e1;
  box-shadow: 0 0 0 3px rgba(224, 82, 82, 0.1);
}

.conversations-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.chat-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: 12px;
  cursor: pointer;
  transition: background 0.2s;
}

.chat-item:hover {
  background-color: #f8fafc;
}

.chat-item.active {
  background-color: #fef2f2;
}

.avatar-box {
  position: relative;
  width: 42px;
  height: 42px;
  background-color: #fee2e2;
  color: #dc2626;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 14px;
  flex-shrink: 0;
}

.avatar-box.small {
  width: 36px;
  height: 36px;
  font-size: 12px;
}

.avatar-box.tiny {
  width: 28px;
  height: 28px;
  font-size: 10px;
}

.online-badge {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 11px;
  height: 11px;
  background-color: #22c55e;
  border: 2px solid #ffffff;
  border-radius: 50%;
}

.chat-details {
  flex: 1;
  min-width: 0;
}

.chat-name {
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.chat-sub {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #64748b;
  margin-top: 2px;
}

.preview-text {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 150px;
}

.unread-badge {
  width: 9px;
  height: 9px;
  background-color: #e05252;
  border-radius: 50%;
  flex-shrink: 0;
}

.empty-list {
  padding: 30px 16px;
  text-align: center;
  color: #94a3b8;
  font-size: 13px;
}

/* Main Chat Area Styles */
.sm-chat-main {
  flex: 1;
  background-color: #ffffff;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.chat-header {
  height: 65px;
  padding: 0 20px;
  background-color: #ffffff;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-shrink: 0;
}

.header-user {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-name {
  font-size: 15px;
  font-weight: 600;
  color: #0f172a;
}

.user-status {
  font-size: 12px;
  color: #64748b;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  background: transparent;
  border: none;
  font-size: 16px;
  padding: 8px;
  border-radius: 50%;
  cursor: pointer;
  color: #64748b;
}

.action-btn:hover {
  background-color: #f1f5f9;
}

.messages-body {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  background-color: #f8fafc;
}

.msg-row {
  display: flex;
  align-items: flex-end;
  gap: 8px;
}

.msg-row.me {
  justify-content: flex-end;
}

.msg-content {
  display: flex;
  flex-direction: column;
  max-width: 68%;
}

.msg-row.me .msg-content {
  align-items: flex-end;
}

.msg-bubble {
  padding: 10px 16px;
  border-radius: 16px;
  font-size: 14px;
  line-height: 1.45;
  word-break: break-word;
}

.msg-row.them .msg-bubble {
  background-color: #ffffff;
  color: #1e293b;
  border: 1px solid #e2e8f0;
  border-bottom-left-radius: 4px;
}

.msg-row.me .msg-bubble {
  background-color: #e05252; /* ServiceMarket Red Accent */
  color: #ffffff;
  border-bottom-right-radius: 4px;
}

.msg-time {
  font-size: 11px;
  color: #94a3b8;
  margin-top: 4px;
  padding: 0 2px;
}

.empty-chat-body {
  margin: auto;
  text-align: center;
  color: #64748b;
  font-size: 13.5px;
}

/* Chat Input Footer */
.chat-footer {
  padding: 14px 20px;
  background-color: #ffffff;
  border-top: 1px solid #e2e8f0;
  flex-shrink: 0;
}

.input-form {
  display: flex;
  align-items: center;
  gap: 10px;
}

.tool-btn {
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
  padding: 8px;
  border-radius: 50%;
  color: #64748b;
  transition: background 0.2s;
}

.tool-btn:hover {
  background-color: #f1f5f9;
}

.input-pill {
  flex: 1;
  background-color: #f1f5f9;
  border-radius: 20px;
  padding: 8px 16px;
  border: 1px solid transparent;
  transition: border-color 0.2s;
}

.input-pill:focus-within {
  border-color: #cbd5e1;
  background-color: #ffffff;
}

.input-pill input {
  width: 100%;
  background: transparent;
  border: none;
  color: #0f172a;
  outline: none;
  font-size: 14px;
}

.send-btn {
  background-color: #e05252;
  color: #ffffff;
  border: none;
  padding: 8px 18px;
  border-radius: 20px;
  font-size: 13.5px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.send-btn:hover:not(:disabled) {
  background-color: #c94343;
}

.send-btn:disabled {
  background-color: #f1f5f9;
  color: #94a3b8;
  cursor: not-allowed;
}

.empty-selection-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #64748b;
  text-align: center;
  padding: 20px;
}

.empty-icon {
  font-size: 40px;
  margin-bottom: 12px;
}

.empty-selection-state h3 {
  font-size: 18px;
  font-weight: 600;
  color: #0f172a;
  margin: 0 0 6px 0;
}

.empty-selection-state p {
  font-size: 13.5px;
  max-width: 300px;
  margin: 0;
}
</style>