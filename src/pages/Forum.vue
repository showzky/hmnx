<template>
  <div class="forum-app">
    <!-- LEFT SIDEBAR -->
    <aside class="sidebar">
      <div class="sidebar-header">
        <h2 class="logo">Forumify</h2>
      </div>
      <nav class="sidebar-menu">
        <ul>
          <li><a href="#" class="active"><i class="icon-home"></i> Home</a></li>
          <li><a href="#"><i class="icon-topics"></i> Topics</a></li>
          <li><a href="#"><i class="icon-forum"></i> Forum</a></li>
          <li><a href="#"><i class="icon-whatnew"></i> What's New</a></li>
          <li><a href="#"><i class="icon-resources"></i> Resources</a></li>
          <li><a href="#"><i class="icon-members"></i> Members</a></li>
        </ul>
      </nav>
      <div class="sidebar-footer">
        <a href="#" class="logout-btn"><i class="icon-logout"></i> Logout</a>
      </div>
    </aside>

    <!-- MAIN CONTENT -->
    <main class="main-content">
      <!-- TOPBAR / HEADER -->
      <header class="topbar">
        <div class="search-bar">
          <input type="text" placeholder="Search forum..." v-model="searchQuery" />
          <button class="search-btn" @click="search">Search</button>
        </div>
        <div class="user-actions">
          <button class="notification-btn"><i class="icon-bell"></i></button>
          <div class="user-profile">
            <img :src="auth.user?.avatar || 'https://via.placeholder.com/36'" alt="User Avatar" />
            <span class="username">{{ auth.user?.username || 'Guest' }}</span>
          </div>
        </div>
      </header>

      <!-- HERO SECTION -->
      <section class="hero-section">
        <div class="hero-content">
          <h1>Engage with Your Community</h1>
          <p>Join discussions, share ideas, and connect with others.</p>
          <button class="btn-primary">Explore Topics</button>
        </div>
        <div class="hero-image">
          <i class="icon-calendar"></i>
        </div>
      </section>

      <!-- FORUM THREADS -->
      <section class="forum-section">
        <div class="forum-container">
          <div class="forum-header">
            <h2>Forum Discussions</h2>
            <span class="total-comments">{{ totalComments }} Comments</span>
          </div>

          <!-- THREAD CREATION -->
          <div class="thread-creation">
            <h3>Create New Thread</h3>
            <form @submit.prevent="createThread" class="thread-form">
              <ThreadEditor v-model="newThreadTitle" ref="threadTitleTextarea" />
              <div class="format-buttons">
                <button type="button" @click="formatText('bold')">Bold</button>
                <button type="button" @click="formatText('italic')">Italic</button>
              </div>
              <button type="submit" class="create-thread-btn">Post Thread</button>
            </form>
          </div>

          <!-- THREADS LIST -->
          <div class="threads-list">
            <div v-for="thread in threads" :key="thread.id" class="thread-card">
              <div class="thread-card-header">
                <div class="thread-icon">
                  <i class="icon-forum"></i>
                </div>
                <div class="thread-info">
                  <!-- Inline editing -->
                  <div v-if="editMode[thread.id]" class="edit-area">
                    <ThreadEditor v-model="editedThreadTitle[thread.id]" />
                    <div class="edit-actions">
                      <button @click="saveThreadEdit(thread)" class="save-btn">Save</button>
                      <button @click="cancelThreadEdit(thread)" class="cancel-btn">Cancel</button>
                    </div>
                  </div>
                  <div v-else class="thread-title" v-html="thread.title"></div>
                  <div class="thread-meta">
                    <small>Posted: {{ formatTimestamp(thread.timestamp) }}</small>
                    <div class="thread-user" v-if="thread.user">
                      <img v-if="thread.user.avatar" :src="thread.user.avatar" alt="Avatar" class="avatar" />
                      <span>{{ thread.user.username }}</span>
                      <div v-if="auth.user && auth.user.id === thread.user.id" class="thread-actions">
                        <button @click="startEditingThread(thread)" class="edit-btn">Edit</button>
                        <button @click="deleteThread(thread.id)" class="delete-btn">Delete</button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- COMMENTS FOR THE THREAD -->
              <div class="comments-section">
                <Comments
                  v-for="comment in thread.comments"
                  :key="comment.id"
                  :comment="comment"
                  :replyMode="replyMode"
                  :newReply="newReply"
                  :formatTimestamp="formatTimestamp"
                  :threadId="thread.id"
                  @toggle-reply="toggleReply"
                  @post-reply="(parentCommentId) => postReply(thread.id, parentCommentId)"
                  @delete-comment="handleDeleteComment(thread.id, $event)"
                />
              </div>

              <!-- COMMENT FORM -->
              <form @submit.prevent="postComment(thread.id)" class="comment-form">
                <textarea v-model="newComment[thread.id]" placeholder="Write a comment..." rows="2"></textarea>
                <button type="submit" :disabled="!newComment[thread.id] || !newComment[thread.id].trim()">Comment</button>
              </form>
            </div>
          </div>
        </div>
      </section>
    </main>

    <!-- RIGHT PANEL -->
    <aside class="right-panel">
      <div class="panel-section online-staff">
        <h3>Staff Online</h3>
        <ul>
          <li>Denise Steward</li>
          <li>George Williamson</li>
          <li>Ralph Edwards</li>
          <li>Jacob Jones</li>
        </ul>
      </div>
      <div class="panel-section recent-threads">
        <h3>Recent Threads</h3>
        <ul>
          <li>
            <strong>Adventure Awaits</strong><br/>
            <small>by User123, 2 hours ago</small>
          </li>
          <li>
            <strong>Forum Rules Update</strong><br/>
            <small>by Moderator, 5 hours ago</small>
          </li>
          <li>
            <strong>Community Survey 2025</strong><br/>
            <small>by Admin, 1 day ago</small>
          </li>
        </ul>
      </div>
      <div class="panel-section latest-resources">
        <h3>Latest Resources</h3>
        <ul>
          <li>
            <strong>Resource One</strong>
            <p>Short description here.</p>
          </li>
          <li>
            <strong>Resource Two</strong>
            <p>Another short description.</p>
          </li>
        </ul>
      </div>
    </aside>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue';
import axios from '@/axios';
import { useAuthStore } from '@/stores/authStore';
import Comments from '@/pages/Comments.vue';
import { marked } from 'marked';
import ThreadEditor from '@/components/ThreadEditor.vue';

export default {
  name: 'Forum',
  components: { Comments, ThreadEditor },
  setup() {
    const auth = useAuthStore();
    const threads = ref([]);
    const newThreadTitle = ref('');
    const threadTitleTextarea = ref(null);
    const formattedThreadTitle = computed(() => marked.parse(newThreadTitle.value));
    const newComment = ref({});
    const newReply = ref({});
    const replyMode = ref({});
    const editMode = ref({});
    const editedThreadTitle = ref({});
    const searchQuery = ref('');

    const totalComments = computed(() =>
      threads.value.reduce((sum, thread) => {
        function countComments(comments) {
          return comments.reduce((count, comment) => {
            const nested = comment.replies ? countComments(comment.replies) : 0;
            return count + 1 + nested;
          }, 0);
        }
        return sum + (thread.comments ? countComments(thread.comments) : 0);
      }, 0)
    );

    async function fetchThreads() {
      try {
        const token = localStorage.getItem('access_token');
        const response = await axios.get('/threads', {
          headers: { Authorization: `Bearer ${token}` }
        });
        threads.value = response.data.threads.map(thread => ({
          ...thread,
          comments: thread.comments || []
        }));
      } catch (error) {
        console.error('Error fetching threads:', error.response ? error.response.data : error);
      }
    }

    async function createThread() {
      try {
        const token = localStorage.getItem('access_token');
        const response = await axios.post(
          '/threads',
          { title: newThreadTitle.value },
          { headers: { Authorization: `Bearer ${token}` } }
        );
        const newThread = { ...response.data.thread, comments: [] };
        threads.value.unshift(newThread);
        newThreadTitle.value = '';
      } catch (error) {
        console.error('Error creating thread:', error.response ? error.response.data : error);
      }
    }

    function startEditingThread(thread) {
      editMode.value[thread.id] = true;
      editedThreadTitle.value[thread.id] = thread.title;
    }

    async function saveThreadEdit(thread) {
      const newTitle = editedThreadTitle.value[thread.id];
      if (!newTitle || newTitle.trim() === "") {
        window.alert("Title cannot be empty");
        return;
      }
      try {
        const token = localStorage.getItem('access_token');
        await axios.put(`/threads/${thread.id}`, { title: newTitle }, {
          headers: { Authorization: `Bearer ${token}` }
        });
        thread.title = newTitle;
        editMode.value[thread.id] = false;
      } catch (error) {
        console.error('Error updating thread:', error.response ? error.response.data : error);
      }
    }

    function cancelThreadEdit(thread) {
      editMode.value[thread.id] = false;
    }

    async function postComment(threadId) {
      try {
        const token = localStorage.getItem('access_token');
        const content = newComment.value[threadId];
        const response = await axios.post(`/threads/${threadId}/comments`, { content }, {
          headers: { Authorization: `Bearer ${token}` }
        });
        const thread = threads.value.find(t => t.id === threadId);
        if (thread) {
          if (!thread.comments) {
            thread.comments = [];
          }
          const newCommentObj = { ...response.data.comment, replies: [] };
          thread.comments.unshift(newCommentObj);
        }
        newComment.value[threadId] = '';
      } catch (error) {
        console.error('Error posting comment:', error.response ? error.response.data : error);
      }
    }

    async function postReply(threadId, parentCommentId) {
      try {
        const token = localStorage.getItem('access_token');
        const content = newReply.value[parentCommentId];
        const response = await axios.post(
          `/threads/${threadId}/comments`,
          { content, parent_id: parentCommentId },
          { headers: { Authorization: `Bearer ${token}` } }
        );
        const thread = threads.value.find(t => t.id === threadId);
        if (thread) {
          function findComment(comments, id) {
            for (const comment of comments) {
              if (comment.id === id) return comment;
              if (comment.replies && comment.replies.length) {
                const found = findComment(comment.replies, id);
                if (found) return found;
              }
            }
            return null;
          }
          const parentComment = findComment(thread.comments, parentCommentId);
          if (parentComment) {
            if (!parentComment.replies) {
              parentComment.replies = [];
            }
            const newReplyComment = { ...response.data.comment, replies: [] };
            parentComment.replies.unshift(newReplyComment);
          }
        }
        newReply.value[parentCommentId] = '';
        replyMode.value[parentCommentId] = false;
      } catch (error) {
        console.error('Error posting reply:', error.response ? error.response.data : error);
      }
    }

    async function deleteThread(threadId) {
      if (!window.confirm("Are you sure you want to delete this thread?")) return;
      try {
        const token = localStorage.getItem('access_token');
        await axios.delete(`/threads/${threadId}`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        threads.value = threads.value.filter(t => t.id !== threadId);
      } catch (error) {
        console.error('Error deleting thread:', error.response ? error.response.data : error);
      }
    }

    function handleDeleteComment(threadId, deletedCommentId) {
      const thread = threads.value.find(t => t.id === threadId);
      if (thread && thread.comments) {
        thread.comments = removeCommentRecursively(thread.comments, deletedCommentId);
      }
    }

    function removeCommentRecursively(commentList, deletedId) {
      return commentList.filter(comment => {
        if (comment.id === deletedId) {
          return false;
        }
        if (comment.replies) {
          comment.replies = removeCommentRecursively(comment.replies, deletedId);
        }
        return true;
      });
    }

    function toggleReply(commentId) {
      replyMode.value[commentId] = !replyMode.value[commentId];
    }

    function formatTimestamp(timestamp) {
      return new Date(timestamp).toLocaleString();
    }

    function formatText(style) {
      const textarea = threadTitleTextarea.value?.$el.querySelector('textarea');
      if (!textarea) return;
      const start = textarea.selectionStart;
      const end = textarea.selectionEnd;
      const selectedText = textarea.value.substring(start, end);
      let formatted = "";
      if (style === 'bold') {
        formatted = `**${selectedText}**`;
      } else if (style === 'italic') {
        formatted = `*${selectedText}*`;
      }
      const before = textarea.value.substring(0, start);
      const after = textarea.value.substring(end);
      const newValue = before + formatted + after;
      newThreadTitle.value = newValue;
      setTimeout(() => {
        textarea.focus();
        textarea.selectionStart = textarea.selectionEnd = start + formatted.length;
      }, 0);
    }

    function search() {
      console.log("Searching for:", searchQuery.value);
      // Implement search functionality as needed.
    }

    onMounted(() => {
      fetchThreads();
    });

    return {
      auth,
      threads,
      newThreadTitle,
      newComment,
      newReply,
      replyMode,
      totalComments,
      createThread,
      postComment,
      postReply,
      toggleReply,
      formatTimestamp,
      editMode,
      editedThreadTitle,
      startEditingThread,
      saveThreadEdit,
      cancelThreadEdit,
      handleDeleteComment,
      formattedThreadTitle,
      formatText,
      threadTitleTextarea,
      searchQuery,
      search
    };
  }
};
</script>

<style scoped>
/* General Layout */
.forum-app {
  display: flex;
  min-height: 100vh;
  font-family: 'Roboto', sans-serif;
}

/* Sidebar */
.sidebar {
  width: 240px;
  background-color: #1F2A37;
  color: #fff;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding-bottom: 1rem;
}
.sidebar-header {
  padding: 1.5rem;
  text-align: center;
}
.logo {
  font-size: 1.8rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1px;
}
.sidebar-menu ul {
  list-style: none;
  padding: 0;
  margin: 0;
}
.sidebar-menu li {
  margin: 0.5rem 0;
}
.sidebar-menu a {
  display: block;
  padding: 0.75rem 1.5rem;
  color: #9CA3AF;
  text-decoration: none;
  transition: background 0.3s;
}
.sidebar-menu a:hover,
.sidebar-menu a.active {
  background-color: #2D3748;
  color: #F0F6FC;
}
.sidebar-footer {
  padding: 1.5rem;
  border-top: 1px solid #2D3748;
  text-align: center;
}
.logout-btn {
  color: #9CA3AF;
  text-decoration: none;
}

/* Main Content */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}
.topbar {
  background-color: #111827;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  border-bottom: 1px solid #2D3748;
}
.search-bar {
  display: flex;
  align-items: center;
}
.search-bar input {
  background-color: #1F2A37;
  border: 1px solid #2D3748;
  padding: 0.5rem 1rem;
  color: #F0F6FC;
  border-radius: 4px 0 0 4px;
  outline: none;
}
.search-btn {
  background-color: #2563EB;
  border: none;
  color: #fff;
  padding: 0.5rem 1rem;
  border-radius: 0 4px 4px 0;
  cursor: pointer;
}
.search-btn:hover {
  background-color: #1D4ED8;
}
.user-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}
.notification-btn {
  background: transparent;
  border: none;
  cursor: pointer;
  font-size: 1.2rem;
  color: #F0F6FC;
}
.user-profile {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.user-profile img {
  border-radius: 50%;
  width: 36px;
  height: 36px;
}
.username {
  font-weight: 600;
  color: #F0F6FC;
}

/* Hero Section */
.hero-section {
  display: flex;
  padding: 2rem;
  border-bottom: 1px solid #2D3748;
  background: #1e2737;
  color: #fff;
}
.hero-content {
  flex: 1;
}
.hero-content h1 {
  font-size: 2rem;
  margin-bottom: 0.5rem;
}
.hero-content p {
  margin-bottom: 1rem;
  color: #9CA3AF;
}
.btn-primary {
  background-color: #2563EB;
  border: none;
  color: #fff;
  padding: 0.75rem 1.25rem;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 600;
}
.btn-primary:hover {
  background-color: #1D4ED8;
}
.hero-image {
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 4rem;
  padding: 1rem;
}

/* Forum Section */
.forum-section {
  padding: 2rem;
  background: #f5f7fa;
  flex: 1;
}
.forum-container {
  background: #1e2737;
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  color: #e0e0e0;
}
.forum-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}
.forum-header h2 {
  color: #fff;
}
.total-comments {
  background: #2563EB;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.9rem;
  color: #fff;
}
.thread-creation {
  margin-bottom: 2rem;
}
.thread-creation h3 {
  margin-bottom: 1rem;
  color: #fff;
}
.thread-form {
  background: #2d3748;
  padding: 2rem;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.format-buttons button {
  margin-right: 0.5rem;
  padding: 0.3rem 0.6rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
.create-thread-btn {
  background-color: #3f72af;
  color: #fff;
  font-weight: 700;
  font-size: 1.1rem;
  padding: 0.75rem 2rem;
  border-radius: 8px;
  border: none;
  cursor: pointer;
  align-self: flex-start;
  transition: background-color 0.2s, transform 0.2s;
}
.create-thread-btn:hover {
  background-color: #325c8f;
  transform: translateY(-2px);
}
.threads-list {
  display: flex;
  flex-direction: column;
  gap: 1.75rem;
}
.thread-card {
  background: #2d3748;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.4);
  transition: transform 0.2s, box-shadow 0.2s;
}
.thread-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 10px 24px rgba(0, 0, 0, 0.5);
}
.thread-card-header {
  display: flex;
  align-items: center;
  gap: 1.25rem;
  border-bottom: 1px solid #4a5568;
  padding-bottom: 1rem;
  margin-bottom: 1rem;
}
.thread-icon {
  background: #2563EB;
  color: #fff;
  padding: 1rem;
  border-radius: 10px;
  font-size: 1.6em;
}
.thread-info {
  flex-grow: 1;
}
.thread-title {
  font-size: 1.5rem;
  color: #fff;
  margin-bottom: 0.5rem;
}
.thread-meta {
  color: #a0aec0;
  font-size: 0.9rem;
}
.thread-user {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 0.5rem;
}
.avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: 2px solid #2563EB;
}
.thread-actions button {
  background: transparent;
  border: none;
  color: #F0F6FC;
  cursor: pointer;
  margin-left: 0.5rem;
}
.edit-btn:hover,
.delete-btn:hover {
  text-decoration: underline;
}
.edit-area {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.edit-actions {
  display: flex;
  gap: 0.5rem;
}
.save-btn,
.cancel-btn {
  padding: 0.4rem 0.8rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
.save-btn {
  background-color: #4caf7d;
  color: #fff;
}
.save-btn:hover {
  background-color: #43a047;
}
.cancel-btn {
  background-color: #4a5568;
  color: #fff;
}
.cancel-btn:hover {
  background-color: #64748b;
}
.comments-section {
  background: #3a4456;
  border-radius: 10px;
  padding: 1.75rem;
  margin-top: 1rem;
  box-shadow: inset 0 2px 6px rgba(0, 0, 0, 0.2);
}
.comment-form textarea {
  width: 100%;
  padding: 1rem;
  border: 1px solid #5a677a;
  border-radius: 8px;
  margin-bottom: 1rem;
  background-color: #4a5568;
  color: #e0e0e0;
  resize: vertical;
}
.comment-form button {
  background-color: #4caf7d;
  color: #fff;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.2s;
}
.comment-form button:hover {
  background-color: #43a047;
}

/* Right Panel */
.right-panel {
  width: 300px;
  background-color: #1F2A37;
  padding: 1rem;
  border-left: 1px solid #2D3748;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  color: #fff;
}
.panel-section h3 {
  font-size: 1rem;
  margin-bottom: 0.5rem;
  font-weight: 600;
}
.panel-section ul {
  list-style: none;
  padding: 0;
  margin: 0;
}
.panel-section li {
  margin-bottom: 0.75rem;
  line-height: 1.3;
}

/* Icon Placeholders */
.icon-home::before { content: "🏠 "; }
.icon-topics::before { content: "📂 "; }
.icon-forum::before { content: "💬 "; }
.icon-whatnew::before { content: "✨ "; }
.icon-resources::before { content: "📚 "; }
.icon-members::before { content: "👥 "; }
.icon-logout::before { content: "🚪 "; }
.icon-bell::before { content: "🔔 "; }
.icon-calendar::before { content: "📅 "; }
</style>
