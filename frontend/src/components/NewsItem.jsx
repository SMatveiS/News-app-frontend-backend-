import { Link } from 'react-router-dom';
import styles from './NewsItem.module.css';

const NewsItem = ({ news }) => {
    const authorName = news.author?.name || `ID: ${news.author_id}`;
    
    let previewText = '';
    if (news.content && typeof news.content === 'object' && news.content.text) {
        previewText = news.content.text;
    } else if (typeof news.content === 'string') {
        previewText = news.content;
    }

    return (
        <div className={styles.card}>
            <Link to={`/news/${news.id}`} className={styles.link}>
                <h3>{news.title}</h3>
            </Link>
            <div className={styles.meta}>
                <span>✍️ {authorName}</span>
                <span>📅 {new Date(news.publication_date).toLocaleDateString()}</span>
            </div>
            <p className={styles.preview}>
                {previewText.substring(0, 150)}...
            </p>
        </div>
    );
};

export default NewsItem;
