import { useEffect, useState, useContext } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axiosClient from '../api/AxiosClient';
import { AuthContext } from '../context/AuthContext';
import styles from './NewsDetail.module.css';

const NewsDetail = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const { user } = useContext(AuthContext);
    
    const [news, setNews] = useState(null);
    const [comments, setComments] = useState([]);
    const [newComment, setNewComment] = useState('');
    
    // Состояние для редактирования комментария (храним ID коммента и текст)
    const [editingCommentId, setEditingCommentId] = useState(null);
    const [editingCommentText, setEditingCommentText] = useState('');

    const fetchData = async () => {
        try {
            const newsRes = await axiosClient.get(`/news/${id}`);
            setNews(newsRes.data);
            
            const commentsRes = await axiosClient.get(`/comments/?news_id=${id}`);
            setComments(commentsRes.data || []);
        } catch (err) {
            console.error(err);
        }
    };

    useEffect(() => { fetchData(); }, [id]);

    const isNewsOwnerOrAdmin = user && (user.isAdmin || (news && user.id === news.author_id));

    const handleDeleteNews = async () => {
        if(confirm('Удалить новость?')) {
            await axiosClient.delete(`/news/${id}`);
            navigate('/');
        }
    };

    const handleSendComment = async (e) => {
        e.preventDefault();
        try {
            await axiosClient.post('/comments/', {
                news_id: parseInt(id),
                text: newComment
            });
            setNewComment('');
            fetchData();
        } catch (err) {
            alert('Ошибка отправки комментария');
        }
    };

    const handleDeleteComment = async (commentId) => {
        if(confirm('Удалить комментарий?')) {
            await axiosClient.delete(`/comments/${commentId}`);
            fetchData();
        }
    };

    const startEditComment = (comment) => {
        setEditingCommentId(comment.id);
        setEditingCommentText(comment.text);
    };

    const saveEditComment = async (comment) => {
        try {
            await axiosClient.put(`/comments/${comment.id}`, {
                news_id: parseInt(id),
                text: editingCommentText
            });
            setEditingCommentId(null);
            fetchData();
        } catch (err) {
            alert('Ошибка обновления: ' + err.message);
        }
    };

    if (!news) return <div className={styles.container}>Загрузка...</div>;

    const authorName = news.author?.name || news.author_id;
    const contentText = (news.content && news.content.text) ? news.content.text : JSON.stringify(news.content);

    return (
        <div className={styles.container}>
            <article className={styles.article}>
                <h1>{news.title}</h1>
                <div className={styles.meta}>
                    ✍️ {authorName} • 📅 {new Date(news.publication_date).toLocaleDateString()}
                </div>
                <div className={styles.content}>
                    {contentText}
                </div>
                
                {isNewsOwnerOrAdmin && (
                    <div className={styles.actions}>
                        <button 
                            onClick={() => navigate(`/edit-news/${id}`)}
                            className={`${styles.btn} ${styles.editBtn}`}
                        >
                            ✏️ Редактировать
                        </button>
                        <button 
                            onClick={handleDeleteNews} 
                            className={`${styles.btn} ${styles.deleteBtn}`}
                        >
                            🗑️ Удалить
                        </button>
                    </div>
                )}
            </article>

            <section className={styles.comments}>
                <h3>Комментарии ({comments.length})</h3>
                
                {user ? (
                    <form onSubmit={handleSendComment} className={styles.commentForm}>
                        <textarea 
                            value={newComment}
                            onChange={e => setNewComment(e.target.value)}
                            placeholder="Написать комментарий..."
                            required
                        />
                        <button type="submit">Отправить</button>
                    </form>
                ) : (
                    <p><i>Войдите, чтобы комментировать</i></p>
                )}

                <div className={styles.commentList}>
                    {comments.map(c => {
                        const isCommentOwner = user && (user.isAdmin || user.id === c.author_id);
                        const isEditing = editingCommentId === c.id;

                        return (
                            <div key={c.id} className={styles.commentItem}>
                                <div className={styles.commentMeta}>
                                    <b>{c.author?.name || `User #${c.author_id}`}</b>
                                    <span style={{marginLeft: '10px', fontSize: '0.8em', color: '#888'}}>
                                        {new Date(c.publication_date).toLocaleString()}
                                    </span>
                                </div>

                                {isEditing ? (
                                    <div className={styles.editBox}>
                                        <textarea 
                                            value={editingCommentText}
                                            onChange={e => setEditingCommentText(e.target.value)}
                                        />
                                        <button onClick={() => saveEditComment(c)} className={styles.saveBtn}>Сохранить</button>
                                        <button onClick={() => setEditingCommentId(null)} className={styles.cancelBtn}>Отмена</button>
                                    </div>
                                ) : (
                                    <p>{c.text}</p>
                                )}

                                {isCommentOwner && !isEditing && (
                                    <div className={styles.commentActions}>
                                        <button onClick={() => startEditComment(c)}>Ред.</button>
                                        <button onClick={() => handleDeleteComment(c.id)} style={{color: 'red'}}>Удалить</button>
                                    </div>
                                )}
                            </div>
                        );
                    })}
                </div>
            </section>
        </div>
    );
};

export default NewsDetail;
