import { Link, useNavigate } from 'react-router-dom';
import { useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import styles from './NavBar.module.css';

const NavBar = () => {
    const { user, logout } = useContext(AuthContext);
    const navigate = useNavigate();

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    return (
        <nav className={styles.nav}>
            <div className={styles.container}>
                <div className={styles.logo}>
                    <Link to="/">📰 NewsApp</Link>
                </div>
                
                <div className={styles.actions}>
                    {user && (user.isVerified || user.isAdmin) && (
                        <Link to="/create" className={styles.createBtn}>
                            + Создать новость
                        </Link>
                    )}
                    
                    {user ? (
                        <button onClick={handleLogout} className={styles.logoutBtn}>
                            Выйти {user.isAdmin && '(Admin)'}
                        </button>
                    ) : (
                        <Link to="/login" className={styles.loginLink}>Войти</Link>
                    )}
                </div>
            </div>
        </nav>
    );
};

export default NavBar;
