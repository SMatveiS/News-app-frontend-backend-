import { useState, useEffect, useContext } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axiosClient from '../api/AxiosClient';
import { AuthContext } from '../context/AuthContext';
import styles from './CreateNews.module.css';

const EditNews = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const { user } = useContext(AuthContext);
    
    const [title, setTitle] = useState('');
    const [text, setText] = useState('');
    const [cover, setCover] = useState('');
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        axiosClient.get(`/news/${id}`)
            .then(res => {
                const news = res.data;
                if (!user || (!user.isAdmin && user.id !== news.author_id)) {
                    alert('Нет прав на редактирование');
                    navigate('/');
                    return;
                }
                setTitle(news.title);
                setText(typeof news.content === 'object' ? news.content.text : news.content);
                setCover(news.cover || '');
                setLoading(false);
            })
            .catch(() => {
                alert('Ошибка загрузки новости');
                navigate('/');
            });
    }, [id, user, navigate]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            await axiosClient.put(`/news/${id}`, {
                title,
                content: { text: text },
                cover: cover || null
            });
            navigate(`/news/${id}`);
        } catch (err) {
            alert('Ошибка при сохранении: ' + (err.response?.data?.detail || err.message));
        }
    };

    if (loading) return <div>Загрузка...</div>;

    return (
        <div className={styles.container}>
            <h2>Редактировать новость</h2>
            <form onSubmit={handleSubmit} className={styles.form}>
                <input 
                    type="text" 
                    value={title} 
                    onChange={e => setTitle(e.target.value)} 
                    placeholder="Заголовок"
                    required 
                />
                <textarea 
                    value={text} 
                    onChange={e => setText(e.target.value)} 
                    placeholder="Текст"
                    required 
                />
                <input 
                    type="text" 
                    value={cover} 
                    onChange={e => setCover(e.target.value)} 
                    placeholder="Обложка (опционально)"
                />
                <button type="submit">Сохранить</button>
            </form>
        </div>
    );
};

export default EditNews;
