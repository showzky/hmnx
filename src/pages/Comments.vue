<template>
  <!-- Container Mode: Display top-level comments and new comment form -->
  <div v-if="!comment" class="comments-container">
    <h1>Kommentarer</h1>
    <form @submit.prevent="postComment" class="new-comment-form">
      <textarea v-model="newComment" placeholder="Skriv din kommentar her" rows="3"></textarea>
      <button type="submit" :disabled="!newComment.trim()">Post Kommentar</button>
    </form>

    <div class="comments-list">
      <!-- Render each top-level comment recursively -->
      <Comment 
        v-for="c in comments" 
        :key="c.id" 
        :comment="c" 
        :replyMode="replyMode" 
        :newReply="newReply" 
        :formatTimestamp="formatTimestamp" 
        :threadId="threadId"
        @toggle-reply="toggleReply" 
        @post-reply="handlePostReply"
        @delete-comment="$emit('delete-comment', $event)" 
      />
    </div>
  </div>
  
  <!-- Individual Comment Mode: Display a single comment with inline editing -->
  <div v-else class="comment">
    <div class="comment-header">
      <div class="comment-avatar">
        <img v-if="comment.user && comment.user.avatar" 
             :src="comment.user.avatar" 
             alt="Avatar" 
             class="avatar" />
        <span v-else>👤</span>
      </div>
      <div class="comment-meta">
        <span v-if="comment.user">{{ comment.user.username }}</span>
        <small class="comment-timestamp">{{ formatTimestamp(comment.timestamp) }}</small>
      </div>
    </div>
    
    <!-- Inline editing for comment -->
    <div v-if="localEditMode[comment.id]" class="edit-area">
      <textarea v-model="editedContent[comment.id]" rows="2"></textarea>
      <button @click="saveEdit(comment)" class="save-button">Lagre</button>
      <button @click="cancelEdit(comment.id)" class="cancel-button">Avbryt</button>
    </div>
    <div v-else>
      <p class="comment-content">{{ comment.content }}</p>
    </div>
  
    <button @click="toggleReply(comment.id)" class="reply-button">💬 Svar</button>
    <!-- Show edit/delete buttons if logged in user is the comment owner -->
    <div v-if="auth.user && comment.user && auth.user.id === comment.user.id" class="comment-actions">
      <button @click="editComment(comment)" class="edit-button">Rediger</button>
      <button @click="deleteComment(comment)" class="delete-button">Slett</button>
    </div>
    
    <div v-if="replyMode[comment.id]" class="reply-input">
      <textarea v-model="newReply[comment.id]" placeholder="Skriv et svar" rows="2"></textarea>
      <button @click="postReply(comment.id)" 
              :disabled="!newReply[comment.id] || !newReply[comment.id].trim()">
        Post Svar
      </button>
    </div>
    
    <!-- Render nested replies recursively -->
    <div v-if="comment.replies && comment.replies.length" class="nested-replies">
      <Comment 
        v-for="reply in comment.replies" 
        :key="reply.id" 
        :comment="reply" 
        :replyMode="replyMode" 
        :newReply="newReply" 
        :formatTimestamp="formatTimestamp" 
        :threadId="threadId"
        @toggle-reply="toggleReply" 
        @post-reply="postReply"
        @delete-comment="$emit('delete-comment', $event)" 
      />
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import axios from '@/axios';
import { useAuthStore } from '@/stores/authStore';

export default {
  name: 'Comment',
  props: {
    comment: {
      type: Object,
      default: null,
    },
    formatTimestamp: {
      type: Function,
      required: true,
    },
    replyMode: {
      type: Object,
      default: () => ({}),
    },
    newReply: {
      type: Object,
      default: () => ({}),
    },
    threadId: {
      type: Number,
      default: null,
    },
  },
  emits: ['toggle-reply', 'post-reply', 'delete-comment'],
  setup(props, { emit }) {
    const auth = useAuthStore();

    // Container Mode: Top-level comments
    const comments = ref([]);
    const newComment = ref('');
    const localReplyMode = ref({});
    const localNewReply = ref({});

    // Reactive variables for inline editing of comments
    const localEditMode = ref({});
    const editedContent = ref({});

    async function fetchComments() {
      try {
        const token = localStorage.getItem('access_token');
        const endpoint = props.threadId ? `/threads/${props.threadId}/comments` : '/comments';
        const response = await axios.get(endpoint, {
          headers: { Authorization: `Bearer ${token}` },
        });
        comments.value = response.data.comments;
      } catch (error) {
        console.error('Error fetching comments:', error.response ? error.response.data : error);
      }
    }

    async function postComment() {
      try {
        const token = localStorage.getItem('access_token');
        const endpoint = props.threadId ? `/threads/${props.threadId}/comments` : '/comments';
        const response = await axios.post(
          endpoint,
          { content: newComment.value },
          { headers: { Authorization: `Bearer ${token}` } }
        );
        comments.value.unshift(response.data.comment);
        newComment.value = '';
      } catch (error) {
        console.error('Error posting comment:', error.response ? error.response.data : error);
      }
    }

    function toggleReply(commentId) {
      if (!props.comment) {
        localReplyMode.value[commentId] = !localReplyMode.value[commentId];
      } else {
        emit('toggle-reply', commentId);
      }
    }

    async function postReply(parentCommentId) {
      try {
        const token = localStorage.getItem('access_token');
        const content = props.comment
          ? props.newReply[parentCommentId]
          : localNewReply.value[parentCommentId];
        const endpoint = props.threadId ? `/threads/${props.threadId}/comments` : '/comments';
        const response = await axios.post(
          endpoint,
          { content, parent_id: parentCommentId },
          { headers: { Authorization: `Bearer ${token}` } }
        );
        if (props.comment) {
          emit('post-reply', parentCommentId, response.data.comment);
        }
        if (!props.comment) {
          localNewReply.value[parentCommentId] = '';
          localReplyMode.value[parentCommentId] = false;
        }
      } catch (error) {
        console.error('Error posting reply:', error.response ? error.response.data : error);
      }
    }

    if (!props.comment) {
      onMounted(() => {
        fetchComments();
      });
    }

    async function deleteComment(commentObj) {
      if (!window.confirm('Are you sure you want to delete this comment?')) return;
      try {
        const token = localStorage.getItem('access_token');
        await axios.delete(`/comments/${commentObj.id}`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        // In container mode, update local comments; otherwise, emit to parent
        if (!props.comment) {
          removeCommentFromLocal(commentObj.id);
        } else {
          emit('delete-comment', commentObj.id);
        }
      } catch (error) {
        console.error('Error deleting comment:', error.response ? error.response.data : error);
      }
    }

    async function editComment(commentObj) {
      startEditing(commentObj);
    }

    function startEditing(commentObj) {
      localEditMode.value[commentObj.id] = true;
      editedContent.value[commentObj.id] = commentObj.content;
    }

    async function saveEdit(commentObj) {
      const newContent = editedContent.value[commentObj.id];
      if (!newContent || newContent.trim() === "") {
        window.alert("Comment content cannot be empty");
        return;
      }
      try {
        const token = localStorage.getItem('access_token');
        await axios.put(
          `/comments/${commentObj.id}`,
          { content: newContent },
          { headers: { Authorization: `Bearer ${token}` } }
        );
        commentObj.content = newContent;
        localEditMode.value[commentObj.id] = false;
      } catch (error) {
        console.error('Error saving edited comment:', error.response ? error.response.data : error);
      }
    }

    function cancelEdit(commentId) {
      localEditMode.value[commentId] = false;
    }

    // Recursive function to remove a deleted comment from the local structure
    function removeCommentFromLocal(commentId) {
      function recurse(commentList) {
        for (let i = commentList.length - 1; i >= 0; i--) {
          const c = commentList[i];
          if (c.id === commentId) {
            commentList.splice(i, 1);
          } else if (c.replies && c.replies.length > 0) {
            recurse(c.replies);
          }
        }
      }
      if (!props.comment) {
        recurse(comments.value);
      } else {
        if (props.comment.replies && props.comment.replies.length > 0) {
          recurse(props.comment.replies);
        }
      }
    }

    return {
      comments,
      newComment,
      replyMode: props.comment ? props.replyMode : localReplyMode,
      newReply: props.comment ? props.newReply : localNewReply,
      postComment,
      toggleReply,
      postReply,
      deleteComment,
      editComment,
      saveEdit,
      cancelEdit,
      removeCommentFromLocal,
      formatTimestamp: props.formatTimestamp,
      auth,
      localEditMode,
      editedContent,
    };
  },
};
</script>

<style scoped>
:root {
  --card-bg: #1e2737;
  --text-color: #e0e0e0;
  --muted-text: #a0aec0;
  --primary-color: #2563EB;
  --primary-hover: #1D4ED8;
  --secondary-color: #4caf7d;
  --accent-color: #ff7b89;
}

/* Container for top-level comments */
.comments-container {
  max-width: 680px;
  margin: 2rem auto;
  padding: 1.5rem;
  background: var(--card-bg);
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
  border: 1px solid #2d3748;
}

/* New Comment Form */
.new-comment-form {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
}
.new-comment-form textarea {
  padding: 0.75rem;
  border: 1px solid #444;
  border-radius: 4px;
  background: #2d3748;
  color: var(--text-color);
  resize: vertical;
}

/* Individual Comment Styling */
.comment {
  background: #2d3748;
  border-radius: 10px;
  padding: 1.25rem;
  margin-bottom: 1.25rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.4);
  border: 1px solid #2d3748;
  transition: transform 0.2s ease;
}
.comment:hover {
  transform: translateY(-2px);
}

.comment-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
}

.comment-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  overflow: hidden;
  background-color: #444;
  flex-shrink: 0;
}
.comment-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.comment-meta {
  display: flex;
  flex-direction: column;
  color: var(--text-color);
}
.comment-timestamp {
  font-size: 0.8rem;
  color: var(--muted-text);
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.comment-timestamp::before {
  content: '🕑';
  opacity: 0.7;
}

.comment-content {
  margin-top: 0.5rem;
  color: var(--text-color);
}

/* Inline Editing Area */
.edit-area textarea {
  width: 100%;
  padding: 0.6rem;
  border: 1px solid #555;
  border-radius: 4px;
  background: #2d3748;
  color: var(--text-color);
  resize: vertical;
  margin-bottom: 0.5rem;
}

/* Buttons */
button {
  cursor: pointer;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  font-weight: 600;
}
button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
.reply-button {
  background: transparent;
  color: var(--primary-color);
  margin-top: 0.5rem;
}
.comment-actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.5rem;
}
.edit-button {
  background: var(--primary-color);
  color: #fff;
}
.delete-button {
  background: var(--accent-color);
  color: #fff;
}
.save-button {
  background: var(--secondary-color);
  color: #fff;
}
.cancel-button {
  background: #555;
  color: #fff;
}

/* Reply Input */
.reply-input textarea {
  width: 100%;
  padding: 0.6rem;
  border: 1px solid #555;
  border-radius: 4px;
  background: #2d3748;
  color: var(--text-color);
  resize: vertical;
  margin-bottom: 0.5rem;
}

/* Nested Replies */
.nested-replies {
  margin-left: 2rem;
  border-left: 2px dashed #444;
  padding-left: 1.5rem;
  position: relative;
}
.nested-replies::before {
  content: '🩺';
  position: absolute;
  left: -15px;
  top: -10px;
  background: var(--card-bg);
  padding: 2px;
  font-size: 0.9em;
  opacity: 0.6;
}
</style>
