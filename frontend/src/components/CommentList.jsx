import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import axiosClient from '../api/AxiosClient'; 
import styles from './CommentList.module.css';

const CommentList = ({ comments, onCommentDeleted, onCommentUpdated }) => {
  const { user } = useAuth();
  
  // Состояние: какой коммент сейчас редактируем (ID)
  const [editingId, setEditingId] = useState(null);
  const [editText, setEditText] = useState("");

  const handleDelete = async (commentId) => {
    if (!window.confirm('Удалить комментарий?')) return;
    try {
      await axiosClient.delete(`/comments/${commentId}`);
      onCommentDeleted();
    } catch (error) {
      alert('Ошибка при удалении');
    }
  };

  const startEdit = (comment) => {
      setEditingId(comment.id);
      setEditText(comment.text);
  };

  const cancelEdit = () => {
      setEditingId(null);
      setEditText("");
  };

  const saveEdit = async (comment) => {
      try {
          await axiosClient.put(`/comments/${comment.id}`, {
              news_id: comment.news_id,
              text: editText
          });
          setEditingId(null);
          if (onCommentUpdated) onCommentUpdated(); 
      } catch (err) {
          alert("Ошибка обновления: " + err.message);
      }
  };

  const isOwnerOrAdmin = (comment) => {
    if (!user) return false;
    return user.isAdmin || comment.author_id === parseInt(user.id);
  };

  return (
    <div className={styles.comments}>
      <h3>💬 Комментарии ({comments.length})</h3>
      {comments.length === 0 ? (
        <p className={styles.empty}>Комментариев пока нет</p>
      ) : (
        comments.map((comment) => (
          <div key={comment.id} className={styles.comment}>
            <div className={styles.header}>
              <span className={styles.author}>
                  👤 {comment.author ? comment.author.name : `#${comment.author_id}`}
              </span>
              <span className={styles.date}>
                {new Date(comment.publication_date).toLocaleString('ru-RU')}
              </span>
            </div>

            {editingId === comment.id ? (
                <div className={styles.editMode}>
                    <textarea 
                        className={styles.editTextarea}
                        value={editText} 
                        onChange={(e) => setEditText(e.target.value)} 
                    />
                    <div className={styles.editButtons}>
                        <button onClick={() => saveEdit(comment)} className={styles.saveBtn}>Сохранить</button>
                        <button onClick={cancelEdit} className={styles.cancelBtn}>Отмена</button>
                    </div>
                </div>
            ) : (
                <p className={styles.text}>{comment.text}</p>
            )}

            {isOwnerOrAdmin(comment) && editingId !== comment.id && (
              <div className={styles.actions}>
                  <button
                    onClick={() => startEdit(comment)}
                    className={styles.editBtnSimple}
                  >
                    ✏️ Ред.
                  </button>
                  <button
                    onClick={() => handleDelete(comment.id)}
                    className={styles.deleteBtn}
                  >
                    🗑️
                  </button>
              </div>
            )}
          </div>
        ))
      )}
    </div>
  );
};

export default CommentList;
