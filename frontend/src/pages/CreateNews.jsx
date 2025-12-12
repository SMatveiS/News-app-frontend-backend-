import { useState, useContext } from 'react';
import axiosClient from '../api/axiosClient';
import { useNavigate } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import styles from './CreateNews.module.css';

const CreateNews = () => {
    const [title, setTitle] = useState('');
    const [text, setText] = useState('');
    const { user } = useContext(AuthContext);
    const navigate = useNavigate();

    if (!user || (!user.isVerified && !user.isAdmin)) {
        return <div>У вас нет прав для создания новостей.</div>;
    }

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            await axiosClient.post('/news/', {
                title,
                content: { text: text },
                cover: "no-cover"
            });
            navigate('/');
        } catch (err) {
            alert('Ошибка при создании: ' + err.message);
        }
    };

    return (
        <div className={styles.container}>
            <h2>Создать новость</h2>
            <form onSubmit={handleSubmit} className={styles.form}>
                <input 
                    type="text" 
                    placeholder="Заголовок" 
                    value={title}
                    onChange={e => setTitle(e.target.value)}
                    required
                />
                <textarea 
                    placeholder="Текст новости" 
                    value={text}
                    onChange={e => setText(e.target.value)}
                    required
                />
                <button type="submit">Опубликовать</button>
            </form>
        </div>
    );
};

export default CreateNews;
