// 全局变量
const API_BASE_URL = 'http://localhost:8000';
let activeSessionId = null;
let sessions = [];
let messages = [];
let isProcessing = false;

    // DOM 元素
    const chatContainer = document.getElementById('chat-container');
    const messageInput = document.getElementById('message-input');
    const sendButton = document.getElementById('send-btn');
    const newChatButton = document.getElementById('new-chat-btn');
    const chatHistory = document.getElementById('chat-history');

// 页面加载时初始化
document.addEventListener('DOMContentLoaded', () => {
    // 设置事件监听器
    sendButton.addEventListener('click', sendMessage);
    messageInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    newChatButton.addEventListener('click', createNewSession);
    
    // 自动调整输入框高度
    messageInput.addEventListener('input', () => {
        messageInput.style.height = 'auto';
        messageInput.style.height = Math.min(messageInput.scrollHeight, 200) + 'px';
    });
    
    // 加载会话列表
    loadSessions();
});

// 加载会话列表
async function loadSessions() {
    try {
        const response = await fetch(`${API_BASE_URL}/sessions/list`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({})
        });
        
        if (!response.ok) throw new Error('获取会话列表失败');
        
        const data = await response.json();
        sessions = data.sessions || [];
        
        // 如果有当前活跃会话，使用它
        if (data.current_session_id) {
            activeSessionId = data.current_session_id;
            await loadSession(activeSessionId);
        } else if (sessions.length > 0) {
            // 否则使用第一个会话
            activeSessionId = sessions[0].id;
            await loadSession(activeSessionId);
        } else {
            // 如果没有会话，创建新会话
            await createNewSession();
        }
        
        renderSessionsList();
    } catch (error) {
        console.error('加载会话列表出错:', error);
        displayErrorMessage('加载会话列表失败，请刷新页面重试');
        
        // 如果出错，尝试创建新会话
        await createNewSession();
    }
}

// 加载指定会话
async function loadSession(sessionId) {
    try {
        const response = await fetch(`${API_BASE_URL}/sessions/get`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                session_id: sessionId
                })
            });
        
        if (!response.ok) throw new Error('获取会话内容失败');
            
            const data = await response.json();
        if (data.status === 'success') {
            activeSessionId = sessionId;
            messages = data.messages || [];
            
            // 设置为当前会话
            await setCurrentSession(sessionId);
            
            // 重置聊天容器并渲染消息
            resetChatContainer();
            
            // 渲染消息
            messages.forEach(msg => {
                renderMessage(msg.role, msg.content);
            });
            
            // 更新会话列表 UI
            renderSessionsList();
        } else {
            throw new Error(data.message || '加载会话失败');
        }
    } catch (error) {
        console.error('加载会话出错:', error);
        displayErrorMessage('加载会话失败，请重试');
    }
}

// 设置当前会话
async function setCurrentSession(sessionId) {
    try {
        const response = await fetch(`${API_BASE_URL}/sessions/set_current`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                session_id: sessionId
            })
        });
        
        if (!response.ok) throw new Error('设置当前会话失败');
        
        // 更新当前活跃会话 ID
        activeSessionId = sessionId;
        
        return true;
    } catch (error) {
        console.error('设置当前会话出错:', error);
        return false;
    }
}

// 创建新会话
async function createNewSession() {
    try {
        const response = await fetch(`${API_BASE_URL}/sessions/create`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) throw new Error('创建会话失败');
        
        const data = await response.json();
        if (data.status === 'success') {
            // 更新当前会话
            activeSessionId = data.session_id;
            messages = [];
            
            // 添加到会话列表并更新 UI
            const newSession = {
                id: data.session_id,
                title: '新会话',
                time: new Date().toLocaleString()
            };
            
            sessions.unshift(newSession);
            
            // 重置聊天容器
            resetChatContainer();
            
            // 渲染会话列表
            renderSessionsList();
        } else {
            throw new Error(data.message || '创建会话失败');
        }
    } catch (error) {
        console.error('创建会话出错:', error);
        displayErrorMessage('创建会话失败，请重试');
    }
}

// 删除会话
async function deleteSession(sessionId) {
    if (!confirm('确定要删除这个会话吗？此操作不可撤销。')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/sessions/delete`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                session_id: sessionId
            })
        });
        
        if (!response.ok) throw new Error('删除会话失败');
        
        const data = await response.json();
        if (data.status === 'success') {
            // 从会话列表中移除
            sessions = sessions.filter(session => session.id !== sessionId);
            
            // 如果删除的是当前会话，切换到另一个会话或创建新会话
            if (activeSessionId === sessionId) {
                if (sessions.length > 0) {
                    await loadSession(sessions[0].id);
                } else {
                    await createNewSession();
                }
            } else {
                // 只更新会话列表
                renderSessionsList();
            }
        } else {
            throw new Error(data.message || '删除会话失败');
        }
    } catch (error) {
        console.error('删除会话出错:', error);
        displayErrorMessage('删除会话失败，请重试');
    }
}

// 渲染会话列表
function renderSessionsList() {
    chatHistory.innerHTML = '';
    
    sessions.forEach(session => {
        const div = document.createElement('div');
        div.className = `chat-item${session.id === activeSessionId ? ' active' : ''}`;
        
        // 创建会话标题
        const titleSpan = document.createElement('span');
        titleSpan.className = 'session-title';
        titleSpan.textContent = session.title || '新会话';
        titleSpan.title = session.time || '';
        div.appendChild(titleSpan);
        
        // 创建删除按钮
        const deleteBtn = document.createElement('button');
        deleteBtn.className = 'delete-btn';
        deleteBtn.innerHTML = '&#10005;'; // × 符号
        deleteBtn.title = '删除会话';
        deleteBtn.addEventListener('click', (e) => {
            e.stopPropagation(); // 阻止点击事件冒泡
            deleteSession(session.id);
        });
        div.appendChild(deleteBtn);
        
        // 设置会话点击事件
        div.addEventListener('click', () => loadSession(session.id));
        
        chatHistory.appendChild(div);
    });
}

// 重置聊天容器
function resetChatContainer() {
    chatContainer.innerHTML = '';
    
    if (messages.length === 0) {
        // 显示欢迎消息
        const welcomeDiv = document.createElement('div');
        welcomeDiv.className = 'welcome-message';
        welcomeDiv.innerHTML = `
            <h2>我是周棋洛</h2>
            <p>你今天快乐吗。</p>
        `;
        chatContainer.appendChild(welcomeDiv);
    }
}

// 发送消息
async function sendMessage() {
    const userInput = messageInput.value.trim();
    if (!userInput || isProcessing) return;
    
    // 清空输入框
    messageInput.value = '';
    messageInput.style.height = 'auto';
    
    // 添加用户消息
    const userMessage = { role: 'user', content: userInput };
    messages.push(userMessage);
    
    // 渲染用户消息
    renderMessage('user', userInput);
    
    // 显示加载指示器
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'loading';
    loadingDiv.innerHTML = '<div class="dot"></div><div class="dot"></div><div class="dot"></div>';
    chatContainer.appendChild(loadingDiv);
    
    // 滚动到底部
    chatContainer.scrollTop = chatContainer.scrollHeight;
    
    isProcessing = true;
    
    try {
        // 发送请求
        const response = await fetch(`${API_BASE_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                messages: messages.map(msg => ({
                    role: msg.role,
                    content: msg.content
                })),
                stream: false,
                session_id: activeSessionId
            })
        });
        
        if (!response.ok) throw new Error('API请求失败');
        
        const data = await response.json();
        
        // 移除加载指示器
        loadingDiv.remove();
        
        // 添加助手消息
        const assistantMessage = {
            role: 'assistant',
            content: data.response
        };
        
        messages.push(assistantMessage);
        
        // 如果返回了会话ID，更新当前会话ID
        if (data.session_id) {
            activeSessionId = data.session_id;
        }
        
        // 更新会话标题（如果这是第一条消息）
        if (messages.filter(msg => msg.role === 'user').length === 1) {
            // 查找并更新会话标题
            for (let i = 0; i < sessions.length; i++) {
                if (sessions[i].id === activeSessionId) {
                    const title = userInput.substring(0, 30) + (userInput.length > 30 ? '...' : '');
                    sessions[i].title = title;
                    break;
                }
            }
            // 重新渲染会话列表
            renderSessionsList();
        }
        
        // 渲染助手消息
        renderMessage('assistant', data.response);
        
    } catch (error) {
        console.error('发送消息出错:', error);
        // 移除加载指示器
        loadingDiv.remove();
        displayErrorMessage('发送消息失败，请重试');
    } finally {
        isProcessing = false;
        // 滚动到底部
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
}

// 渲染消息
function renderMessage(role, content) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;

    // 头像
    const avatarDiv = document.createElement('div');
    avatarDiv.className = 'avatar';
    const avatarImg = document.createElement('img');
    if (role === 'user') {
        avatarImg.src = 'images/beautiful_fighter.png'; // 用户头像（本地）
        avatarImg.alt = '用户头像';
    } else {
        avatarImg.src = 'images/周棋洛.webp'; // AI助手头像（本地）
        avatarImg.alt = 'AI助手头像';
    }
    avatarDiv.appendChild(avatarImg);

    // 气泡内容
    const bubbleDiv = document.createElement('div');
    bubbleDiv.className = 'bubble';

    // 只保留消息内容，不显示角色名
    const contentDiv = document.createElement('div');
    contentDiv.className = 'content markdown-content';
    contentDiv.innerHTML = marked.parse(content);
    bubbleDiv.appendChild(contentDiv);

    // 头像和气泡排列
    if (role === 'user') {
        messageDiv.appendChild(bubbleDiv);
        messageDiv.appendChild(avatarDiv);
    } else {
        messageDiv.appendChild(avatarDiv);
        messageDiv.appendChild(bubbleDiv);
    }

    chatContainer.appendChild(messageDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;

    // 如果是第一条消息，移除欢迎信息
    const welcomeMessage = document.querySelector('.welcome-message');
    if (welcomeMessage) welcomeMessage.remove();
}

// 显示错误消息
function displayErrorMessage(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'message system';
    errorDiv.innerHTML = `<div class="content" style="color: red;">${message}</div>`;
    chatContainer.appendChild(errorDiv);
    
    // 滚动到底部
    chatContainer.scrollTop = chatContainer.scrollHeight;
} 