import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import axiosClient from '../api/axiosClient';
import styles from './Login.module.css';

const Register = () => {
    const [formData, setFormData] = useState({
        name: '',
        email: '',
        password: ''
    });
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError(null);
        setLoading(true);

        try {
            await axiosClient.post('/auth/register', formData);
            
            // Если все ок - переходим на логин
            alert("Регистрация успешна! Теперь войдите.");
            navigate('/login');
        } catch (err) {
            // Обработка ошибок
            console.error("Reg error:", err);
            if (err.response) {
                // Ошибка 422 - Валидация (пароль слабый и т.д.)
                if (err.response.status === 422) {
                    const details = err.response.data.detail;
                    if (Array.isArray(details)) {
                        setError(details[0].msg.replace('Value error, ', ''));
                    } else {
                        setError("Ошибка валидации данных");
                    }
                } 
                // Ошибка 409 - Конфликт (юзер уже есть)
                else if (err.response.status === 409) {
                    setError(err.response.data.detail);
                } 
                else {
                    setError("Ошибка сервера. Попробуйте позже.");
                }
            } else {
                setError("Нет соединения с сервером");
            }
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className={styles.container}>
            <form onSubmit={handleSubmit} className={styles.form}>
                <h2>Регистрация</h2>
                
                {error && <div className={styles.error} style={{color: 'red', marginBottom: '10px'}}>{error}</div>}
                
                <input 
                    type="text" 
                    name="name"
                    placeholder="Логин (3-32 символа, латиница)" 
                    value={formData.name}
                    onChange={handleChange}
                    required
                />
                <input 
                    type="email"
                    name="email" 
                    placeholder="Email" 
                    value={formData.email}
                    onChange={handleChange}
                    required
                />
                <input 
                    type="password"
                    name="password" 
                    placeholder="Пароль (8+ симв, A-z, 0-9, !@#)" 
                    value={formData.password}
                    onChange={handleChange}
                    required
                />
                
                <button type="submit" disabled={loading}>
                    {loading ? "Регистрация..." : "Зарегистрироваться"}
                </button>

                <p style={{marginTop: '10px', fontSize: '0.9em'}}>
                    Уже есть аккаунт? <Link to="/login">Войти</Link>
                </p>
            </form>
        </div>
    );
};

export default Register;
