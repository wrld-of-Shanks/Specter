import React, { useState } from 'react';
import config from './config.ts';

interface SignupProps {
    onSignupSuccess: () => void;
    onSwitchToLogin: () => void;
}

const Signup: React.FC<SignupProps> = ({ onSignupSuccess, onSwitchToLogin }) => {
    const [step, setStep] = useState<'signup' | 'verify'>('signup');
    const [fullName, setFullName] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [otp, setOtp] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');
    const [successMsg, setSuccessMsg] = useState('');
    const [showPassword, setShowPassword] = useState(false);
    const [showConfirmPassword, setShowConfirmPassword] = useState(false);

    const handleSignup = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        setError('');
        setSuccessMsg('');

        if (password !== confirmPassword) {
            setError("Passwords don't match");
            setIsLoading(false);
            return;
        }

        try {
            const response = await fetch(`${config.API_BASE_URL}/auth/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    email,
                    password,
                    full_name: fullName
                }),
            });

            const data = await response.json();

            if (response.ok) {
                setSuccessMsg(data.message || 'Registration successful! Please verify your email.');
                setStep('verify');
            } else {
                setError(data.detail || 'Registration failed');
            }
        } catch (err) {
            setError('Connection error. Please try again.');
        } finally {
            setIsLoading(false);
        }
    };

    const handleVerify = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        setError('');
        setSuccessMsg('');

        try {
            const response = await fetch(`${config.API_BASE_URL}/auth/verify-email`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    email,
                    otp
                }),
            });

            const data = await response.json();

            if (response.ok) {
                setSuccessMsg('Email verified successfully! Redirecting to login...');
                setTimeout(() => {
                    onSignupSuccess();
                }, 1500);
            } else {
                setError(data.detail || 'Verification failed. Invalid OTP.');
            }
        } catch (err) {
            setError('Connection error. Please try again.');
        } finally {
            setIsLoading(false);
        }
    };

    if (step === 'verify') {
        return (
            <div className="auth-container" style={{
                maxWidth: '400px',
                margin: '40px auto',
                padding: '30px',
                background: '#1a1a1a',
                borderRadius: '12px',
                border: '1px solid #333'
            }}>
                <h2 style={{ color: '#fbbf24', textAlign: 'center', marginBottom: '20px' }}>Verify Email</h2>
                <p style={{ color: '#ccc', textAlign: 'center', marginBottom: '20px' }}>
                    We've sent a verification code to <strong>{email}</strong>.
                </p>

                {error && <div style={{ color: '#ef4444', marginBottom: '15px', textAlign: 'center' }}>{error}</div>}
                {successMsg && <div style={{ color: '#10b981', marginBottom: '15px', textAlign: 'center' }}>{successMsg}</div>}

                <form onSubmit={handleVerify} className="contact-form" style={{ margin: 0, padding: 0, border: 'none', background: 'transparent' }}>
                    <div className="form-group">
                        <label>Enter OTP</label>
                        <input
                            type="text"
                            value={otp}
                            onChange={(e) => setOtp(e.target.value)}
                            required
                            placeholder="Enter 6-digit code"
                            style={{ letterSpacing: '2px', textAlign: 'center', fontSize: '1.2rem' }}
                        />
                    </div>

                    <button type="submit" className="contact-btn" disabled={isLoading}>
                        {isLoading ? 'Verifying...' : 'Verify Email'}
                    </button>
                </form>

                <button
                    onClick={() => setStep('signup')}
                    style={{
                        background: 'none',
                        border: 'none',
                        color: '#888',
                        cursor: 'pointer',
                        marginTop: '15px',
                        width: '100%'
                    }}
                >
                    Back to Signup
                </button>
            </div>
        );
    }

    return (
        <div className="auth-container" style={{
            maxWidth: '400px',
            margin: '40px auto',
            padding: '30px',
            background: '#1a1a1a',
            borderRadius: '12px',
            border: '1px solid #333'
        }}>
            <h2 style={{ color: '#fbbf24', textAlign: 'center', marginBottom: '20px' }}>Create Account</h2>

            {error && <div style={{ color: '#ef4444', marginBottom: '15px', textAlign: 'center' }}>{error}</div>}

            <form onSubmit={handleSignup} className="contact-form" style={{ margin: 0, padding: 0, border: 'none', background: 'transparent' }}>
                <div className="form-group">
                    <label>Full Name</label>
                    <input
                        type="text"
                        value={fullName}
                        onChange={(e) => setFullName(e.target.value)}
                        required
                        placeholder="Enter your full name"
                    />
                </div>

                <div className="form-group">
                    <label>Email</label>
                    <input
                        type="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        required
                        placeholder="Enter your email"
                    />
                </div>

                <div className="form-group">
                    <label>Password</label>
                    <div style={{ position: 'relative' }}>
                        <input
                            type={showPassword ? 'text' : 'password'}
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                            placeholder="Create a password"
                        />
                        <span
                            onClick={() => setShowPassword(!showPassword)}
                            style={{
                                position: 'absolute',
                                right: '15px',
                                top: '50%',
                                transform: 'translateY(-50%)',
                                cursor: 'pointer',
                                fontSize: '1.2rem',
                                userSelect: 'none'
                            }}
                        >
                            {showPassword ? '👁️' : '🔒'}
                        </span>
                    </div>
                </div>

                <div className="form-group">
                    <label>Confirm Password</label>
                    <div style={{ position: 'relative' }}>
                        <input
                            type={showConfirmPassword ? 'text' : 'password'}
                            value={confirmPassword}
                            onChange={(e) => setConfirmPassword(e.target.value)}
                            required
                            placeholder="Confirm your password"
                        />
                        <span
                            onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                            style={{
                                position: 'absolute',
                                right: '15px',
                                top: '50%',
                                transform: 'translateY(-50%)',
                                cursor: 'pointer',
                                fontSize: '1.2rem',
                                userSelect: 'none'
                            }}
                        >
                            {showConfirmPassword ? '👁️' : '🔒'}
                        </span>
                    </div>
                </div>

                <button type="submit" className="contact-btn" disabled={isLoading}>
                    {isLoading ? 'Creating Account...' : 'Sign Up'}
                </button>
            </form>

            <div style={{ marginTop: '20px', textAlign: 'center', color: '#888' }}>
                Already have an account?{' '}
                <button
                    onClick={onSwitchToLogin}
                    style={{
                        background: 'none',
                        border: 'none',
                        color: '#fbbf24',
                        cursor: 'pointer',
                        textDecoration: 'underline',
                        fontSize: '1rem'
                    }}
                >
                    Login
                </button>
            </div>
        </div>
    );
};

export default Signup;
