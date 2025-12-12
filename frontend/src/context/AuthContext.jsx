import { createContext, useState, useEffect } from 'react';
import { jwtDecode } from 'jwt-decode';
import axiosClient from '../api/axiosClient';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    // Функция проверки токена при загрузке
    useEffect(() => {
        const token = localStorage.getItem('token');
        if (token) {
            try {
                const decoded = jwtDecode(token);
                // Проверяем срок действия
                if (decoded.exp * 1000 > Date.now()) {
                    setUser({
                        id: parseInt(decoded.sub),
                        isAdmin: decoded.admin,
                        isVerified: decoded.verified
                    });
                } else {
                    logout();
                }
            } catch (e) {
                logout();
            }
        }
        setLoading(false);
    }, []);

    const login = async (email, password) => {
        const formData = new URLSearchParams();
        formData.append('username', email);
        formData.append('password', password);

        try {
            const response = await axiosClient.post('/auth/login', formData, {
                headers: { 
                    'Content-Type': 'application/x-www-form-urlencoded'
                }
            });

            const token = response.data.access_token;
            localStorage.setItem('token', token);
            
            const decoded = jwtDecode(token);
            setUser({
                id: parseInt(decoded.sub),
                isAdmin: decoded.admin,
                isVerified: decoded.verified
            });
            return true;
        } catch (error) {
            console.error("Login error:", error.response?.data || error.message);
            throw error;
        }
    };
    const logout = () => {
        localStorage.removeItem('token');
        setUser(null);
    };

    return (
        <AuthContext.Provider value={{ user, login, logout, loading }}>
            {children}
        </AuthContext.Provider>
    );
};
