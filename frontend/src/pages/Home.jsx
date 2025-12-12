import { useEffect, useState } from 'react';
import axiosClient from '../api/AxiosClient';
import NewsItem from '../components/NewsItem';
import styles from './Home.module.css';

const Home = () => {
    const [news, setNews] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        axiosClient.get('/news/')
            .then(res => {
                setNews(res.data);
                setError(null);
            })
            .catch(err => {
                console.error(err);
                setError('Не удалось загрузить новости.');
            })
            .finally(() => setLoading(false));
    }, []);

    if (loading) return <div className={styles.container}>🚀 Загрузка...</div>;
    if (error) return <div className={styles.container} style={{color: 'red'}}>❌ {error}</div>;

    return (
        <div className={styles.container}>
            <h1>Все новости</h1>
            {news.length === 0 ? (
                <p>Список новостей пуст.</p>
            ) : (
                <div className={styles.grid}>
                    {news.map(item => (
                        <NewsItem key={item.id} news={item} />
                    ))}
                </div>
            )}
        </div>
    );
};

export default Home;
