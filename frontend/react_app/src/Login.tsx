import React, { useState } from 'react';
import config from './config.ts';

interface LoginProps {
    onLoginSuccess: (token: string, user: any) => void;
    onSwitchToSignup: () => void;
}

const Login: React.FC<LoginProps> = ({ onLoginSuccess, onSwitchToSignup }) => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');
    const [showPassword, setShowPassword] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        setError('');

        try {
            const response = await fetch(`${config.API_BASE_URL}/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email, password }),
            });

            const data = await response.json();

            if (response.ok) {
                onLoginSuccess(data.access_token, data.user);
            } else {
                setError(data.detail || 'Login failed');
            }
        } catch (err) {
            setError('Connection error. Please try again.');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div style={{
            minHeight: '100vh',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '20px'
        }}>
            <div style={{
                width: '100%',
                maxWidth: '420px',
                background: 'rgba(26, 26, 26, 0.4)',
                backdropFilter: 'blur(20px)',
                WebkitBackdropFilter: 'blur(20px)',
                borderRadius: '24px',
                border: '1px solid rgba(255, 255, 255, 0.18)',
                padding: '40px 35px',
                boxShadow: '0 8px 32px 0 rgba(0, 0, 0, 0.37)'
            }}>
                <h2 style={{
                    color: '#fff',
                    fontSize: '2rem',
                    fontWeight: '600',
                    marginBottom: '10px',
                    marginTop: 0
                }}>Login</h2>
                <p style={{
                    color: 'rgba(255, 255, 255, 0.7)',
                    fontSize: '0.95rem',
                    marginBottom: '30px',
                    marginTop: 0
                }}>Welcome back please login to your account</p>

                {error && (
                    <div style={{
                        color: '#ef4444',
                        marginBottom: '20px',
                        textAlign: 'center',
                        background: 'rgba(239, 68, 68, 0.1)',
                        padding: '10px',
                        borderRadius: '8px',
                        border: '1px solid rgba(239, 68, 68, 0.3)'
                    }}>{error}</div>
                )}

                <form onSubmit={handleSubmit}>
                    <div style={{ marginBottom: '20px' }}>
                        <div style={{ position: 'relative' }}>
                            <input
                                type="email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                required
                                placeholder="Email"
                                style={{
                                    width: '100%',
                                    padding: '14px 45px 14px 18px',
                                    background: 'rgba(255, 255, 255, 0.1)',
                                    border: '1px solid rgba(255, 255, 255, 0.2)',
                                    borderRadius: '12px',
                                    color: '#fff',
                                    fontSize: '0.95rem',
                                    outline: 'none',
                                    transition: 'all 0.3s',
                                    boxSizing: 'border-box'
                                }}
                                onFocus={(e) => e.target.style.border = '1px solid rgba(251, 191, 36, 0.5)'}
                                onBlur={(e) => e.target.style.border = '1px solid rgba(255, 255, 255, 0.2)'}
                            />
                            <span style={{
                                position: 'absolute',
                                right: '18px',
                                top: '50%',
                                transform: 'translateY(-50%)',
                                color: 'rgba(255, 255, 255, 0.5)',
                                fontSize: '1.2rem'
                            }}>👤</span>
                        </div>
                    </div>

                    <div style={{ marginBottom: '20px' }}>
                        <div style={{ position: 'relative' }}>
                            <input
                                type={showPassword ? 'text' : 'password'}
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                required
                                placeholder="Password"
                                style={{
                                    width: '100%',
                                    padding: '14px 45px 14px 18px',
                                    background: 'rgba(255, 255, 255, 0.1)',
                                    border: '1px solid rgba(255, 255, 255, 0.2)',
                                    borderRadius: '12px',
                                    color: '#fff',
                                    fontSize: '0.95rem',
                                    outline: 'none',
                                    transition: 'all 0.3s',
                                    boxSizing: 'border-box'
                                }}
                                onFocus={(e) => e.target.style.border = '1px solid rgba(251, 191, 36, 0.5)'}
                                onBlur={(e) => e.target.style.border = '1px solid rgba(255, 255, 255, 0.2)'}
                            />
                            <span
                                onClick={() => setShowPassword(!showPassword)}
                                style={{
                                    position: 'absolute',
                                    right: '18px',
                                    top: '50%',
                                    transform: 'translateY(-50%)',
                                    color: 'rgba(255, 255, 255, 0.5)',
                                    fontSize: '1.2rem',
                                    cursor: 'pointer'
                                }}
                            >{showPassword ? '👁️' : '🔒'}</span>
                        </div>
                    </div>

                    <button
                        type="submit"
                        disabled={isLoading}
                        style={{
                            width: '100%',
                            padding: '14px',
                            background: '#fbbf24',
                            border: 'none',
                            borderRadius: '12px',
                            color: '#000',
                            fontSize: '1.05rem',
                            fontWeight: '600',
                            cursor: isLoading ? 'not-allowed' : 'pointer',
                            marginTop: '10px',
                            transition: 'transform 0.2s, box-shadow 0.2s',
                            boxShadow: '0 4px 15px rgba(251, 191, 36, 0.3)'
                        }}
                        onMouseEnter={(e) => {
                            if (!isLoading) {
                                e.currentTarget.style.transform = 'translateY(-2px)';
                                e.currentTarget.style.boxShadow = '0 6px 20px rgba(251, 191, 36, 0.4)';
                            }
                        }}
                        onMouseLeave={(e) => {
                            e.currentTarget.style.transform = 'translateY(0)';
                            e.currentTarget.style.boxShadow = '0 4px 15px rgba(251, 191, 36, 0.3)';
                        }}
                    >
                        {isLoading ? 'Logging in...' : 'Login'}
                    </button>
                </form>

                <div style={{ marginTop: '25px', textAlign: 'center' }}>
                    <span style={{ color: 'rgba(255, 255, 255, 0.7)', fontSize: '0.95rem' }}>
                        Don't have an account?{' '}
                    </span>
                    <button
                        onClick={onSwitchToSignup}
                        style={{
                            background: 'none',
                            border: 'none',
                            color: '#fbbf24',
                            cursor: 'pointer',
                            textDecoration: 'none',
                            fontSize: '0.95rem',
                            fontWeight: '600',
                            transition: 'color 0.2s'
                        }}
                        onMouseEnter={(e) => e.currentTarget.style.color = '#10b981'}
                        onMouseLeave={(e) => e.currentTarget.style.color = '#fbbf24'}
                    >
                        Signup
                    </button>
                </div>

                <div style={{
                    marginTop: '30px',
                    textAlign: 'center',
                    color: 'rgba(255, 255, 255, 0.5)',
                    fontSize: '0.85rem'
                }}>
                    Created by <span style={{ fontStyle: 'italic' }}>SPECTER AI</span>
                </div>

                {/* Debug Info - Temporary */}
                <div style={{
                    marginTop: '20px',
                    textAlign: 'center',
                    fontSize: '0.7rem',
                    color: 'rgba(255,255,255,0.3)'
                }}>
                    API: {config.API_BASE_URL}
                </div>
            </div>
        </div>
    );
};

export default Login;
