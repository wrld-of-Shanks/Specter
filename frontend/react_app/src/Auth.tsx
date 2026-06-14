import React, { useState } from 'react';
import {
  Container,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Box,
  IconButton,
  InputAdornment,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  Stack,
} from '@mui/material';
import {
  Visibility,
  VisibilityOff,
  Email,
  Lock,
  PersonOutline,
} from '@mui/icons-material';
import axios from 'axios';
import config from './config';

interface AuthProps {
  onLogin: (user: any) => void;
}

const API_BASE_URL = `${config.API_BASE_URL}/auth`;

const Auth: React.FC<AuthProps> = ({ onLogin }) => {
  const [isLogin, setIsLogin] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [forgotPasswordOpen, setForgotPasswordOpen] = useState(false);
  const [otpDialogOpen, setOtpDialogOpen] = useState(false);
  const [resetEmail, setResetEmail] = useState('');
  const [otp, setOtp] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [resetLoading, setResetLoading] = useState(false);
  const [otpLoading, setOtpLoading] = useState(false);

  // Form state
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    fullName: '',
    confirmPassword: '',
  });

  const handleInputChange = (field: string) => (event: React.ChangeEvent<HTMLInputElement>) => {
    setFormData(prev => ({
      ...prev,
      [field]: event.target.value
    }));
    setError('');
  };

  const validateForm = () => {
    if (!formData.email || !formData.password) {
      setError('Email and password are required');
      return false;
    }

    if (!isLogin && !formData.fullName) {
      setError('Full name is required');
      return false;
    }

    if (!isLogin && formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      return false;
    }

    if (formData.password.length < 6) {
      setError('Password must be at least 6 characters');
      return false;
    }

    return true;
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!validateForm()) return;

    setLoading(true);
    setError('');

    try {
      if (isLogin) {
        // Login
        const response = await axios.post(`${API_BASE_URL}/login`, {
          email: formData.email,
          password: formData.password,
        });

        const { access_token, refresh_token } = response.data;

        // Store tokens
        localStorage.setItem('access_token', access_token);
        localStorage.setItem('refresh_token', refresh_token);

        // Get user profile
        const profileResponse = await axios.get(`${API_BASE_URL}/profile`, {
          headers: { Authorization: `Bearer ${access_token}` }
        });

        onLogin(profileResponse.data);
        setSuccess('Login successful!');
      } else {
        // Register
        const response = await axios.post(`${API_BASE_URL}/register`, {
          email: formData.email,
          password: formData.password,
          full_name: formData.fullName,
        });

        // Check if registration was successful
        if (response.data.message && response.data.message.includes('successful')) {
          // Check if email was actually sent or if it's development mode
          if (response.data.message.includes('check your email')) {
            setSuccess('Registration successful! Please check your email for verification code.');
            setOtpDialogOpen(true); // Show OTP dialog for production mode
          } else {
            setSuccess('Registration successful! You can now login with your credentials.');
            // Don't show OTP dialog in development mode since backend auto-verifies
          }
        } else {
          setSuccess('Registration successful! Please check your email for verification code.');
          setOtpDialogOpen(true);
        }
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  // OTP verification removed for development - auto-verified on backend

  const handleForgotPassword = async () => {
    try {
      setResetLoading(true);
      setError('');
      setSuccess('');
      const response = await axios.post(`${API_BASE_URL}/forgot-password`, {
        email: resetEmail,
      });

      // Check if OTP is provided in response (development mode)
      if (response.data.message && response.data.message.includes('OTP:')) {
        setSuccess(response.data.message);
        setForgotPasswordOpen(false);
        // Extract OTP from message for development testing
        const otpMatch = response.data.message.match(/OTP:\s*(\d+)/);
        if (otpMatch) {
          setOtp(otpMatch[1]);
          setOtpDialogOpen(true);
        }
      } else {
        setSuccess('If the email exists, a reset code has been sent to your email.');
        setForgotPasswordOpen(false);
        setOtpDialogOpen(true); // Show OTP dialog for password reset flow
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'An error occurred');
    } finally {
      setResetLoading(false);
    }
  };

  const handleResetPassword = async () => {
    try {
      setOtpLoading(true);
      setError('');
      setSuccess('');
      await axios.post(`${API_BASE_URL}/reset-password`, {
        email: resetEmail,
        otp: otp,
        new_password: newPassword,
      });

      setSuccess('Password reset successfully! You can now login.');
      setOtpDialogOpen(false);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Invalid OTP');
    } finally {
      setOtpLoading(false);
    }
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        background: `
          linear-gradient(rgba(0,0,0,0.75), rgba(0,0,0,0.85)),
          url('./assets/hero.jpg') center/cover fixed no-repeat
        `,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: 2,
      }}
    >
      <Container maxWidth="sm">
        <Card 
          elevation={24}
          sx={{
            background: 'rgba(0, 0, 0, 0.85)',
            backdropFilter: 'blur(10px)',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            borderRadius: 3,
          }}
        >
          <CardContent sx={{ p: 4 }}>
            {/* SPECTER Logo/Title */}
            <Box textAlign="center" mb={4}>
              <Typography 
                variant="h2" 
                sx={{
                  fontFamily: 'Roboto Condensed, sans-serif',
                  fontWeight: 900,
                  color: '#FFD700',
                  textShadow: '2px 2px 4px rgba(0,0,0,0.8)',
                  mb: 1,
                  fontSize: { xs: '2.5rem', sm: '3.5rem' }
                }}
              >
                SPECTER.
              </Typography>
              <Typography 
                variant="h6" 
                sx={{
                  color: 'rgba(255, 255, 255, 0.8)',
                  mb: 1,
                  fontWeight: 300
                }}
              >
                Your AI Legal Assistant
              </Typography>
              <Typography 
                variant="body1" 
                sx={{
                  color: 'rgba(255, 255, 255, 0.6)',
                  fontSize: '0.9rem'
                }}
              >
                {isLogin ? 'Welcome back!' : 'Create your account'}
              </Typography>
            </Box>

            {error && (
              <Alert 
                severity="error" 
                sx={{ 
                  mb: 2,
                  backgroundColor: 'rgba(211, 47, 47, 0.1)',
                  color: '#ff6b6b',
                  border: '1px solid rgba(211, 47, 47, 0.3)',
                  '& .MuiAlert-icon': { color: '#ff6b6b' }
                }}
              >
                {error}
              </Alert>
            )}

            {success && (
              <Alert 
                severity="success" 
                sx={{ 
                  mb: 2,
                  backgroundColor: 'rgba(46, 125, 50, 0.1)',
                  color: '#4caf50',
                  border: '1px solid rgba(46, 125, 50, 0.3)',
                  '& .MuiAlert-icon': { color: '#4caf50' }
                }}
              >
                {success}
              </Alert>
            )}

            <Box component="form" onSubmit={handleSubmit}>
              <Stack spacing={3}>
                {!isLogin && (
                  <TextField
                    fullWidth
                    label="Full Name"
                    value={formData.fullName}
                    onChange={handleInputChange('fullName')}
                    variant="outlined"
                    required
                    sx={{
                      '& .MuiOutlinedInput-root': {
                        backgroundColor: 'rgba(255, 255, 255, 0.05)',
                        '& fieldset': {
                          borderColor: 'rgba(255, 255, 255, 0.2)',
                        },
                        '&:hover fieldset': {
                          borderColor: 'rgba(255, 255, 255, 0.3)',
                        },
                        '&.Mui-focused fieldset': {
                          borderColor: '#FFD700',
                        },
                      },
                      '& .MuiInputLabel-root': {
                        color: 'rgba(255, 255, 255, 0.7)',
                      },
                      '& .MuiOutlinedInput-input': {
                        color: '#fff',
                      },
                    }}
                  />
                )}

                <TextField
                  fullWidth
                  label="Email Address"
                  type="email"
                  value={formData.email}
                  onChange={handleInputChange('email')}
                  variant="outlined"
                  required
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <Email sx={{ color: 'rgba(255, 255, 255, 0.7)' }} />
                      </InputAdornment>
                    ),
                  }}
                  sx={{
                    '& .MuiOutlinedInput-root': {
                      backgroundColor: 'rgba(255, 255, 255, 0.05)',
                      '& fieldset': {
                        borderColor: 'rgba(255, 255, 255, 0.2)',
                      },
                      '&:hover fieldset': {
                        borderColor: 'rgba(255, 255, 255, 0.3)',
                      },
                      '&.Mui-focused fieldset': {
                        borderColor: '#FFD700',
                      },
                    },
                    '& .MuiInputLabel-root': {
                      color: 'rgba(255, 255, 255, 0.7)',
                    },
                    '& .MuiOutlinedInput-input': {
                      color: '#fff',
                    },
                  }}
                />

                <TextField
                  fullWidth
                  label="Password"
                  type={showPassword ? 'text' : 'password'}
                  value={formData.password}
                  onChange={handleInputChange('password')}
                  variant="outlined"
                  required
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <Lock sx={{ color: 'rgba(255, 255, 255, 0.7)' }} />
                      </InputAdornment>
                    ),
                    endAdornment: (
                      <InputAdornment position="end">
                        <IconButton
                          onClick={() => setShowPassword(!showPassword)}
                          edge="end"
                          sx={{ color: 'rgba(255, 255, 255, 0.7)' }}
                        >
                          {showPassword ? <VisibilityOff /> : <Visibility />}
                        </IconButton>
                      </InputAdornment>
                    ),
                  }}
                  sx={{
                    '& .MuiOutlinedInput-root': {
                      backgroundColor: 'rgba(255, 255, 255, 0.05)',
                      '& fieldset': {
                        borderColor: 'rgba(255, 255, 255, 0.2)',
                      },
                      '&:hover fieldset': {
                        borderColor: 'rgba(255, 255, 255, 0.3)',
                      },
                      '&.Mui-focused fieldset': {
                        borderColor: '#FFD700',
                      },
                    },
                    '& .MuiInputLabel-root': {
                      color: 'rgba(255, 255, 255, 0.7)',
                    },
                    '& .MuiOutlinedInput-input': {
                      color: '#fff',
                    },
                  }}
                />

                {!isLogin && (
                  <TextField
                    fullWidth
                    label="Confirm Password"
                    type="password"
                    value={formData.confirmPassword}
                    onChange={handleInputChange('confirmPassword')}
                    variant="outlined"
                    required
                    sx={{
                      '& .MuiOutlinedInput-root': {
                        backgroundColor: 'rgba(255, 255, 255, 0.05)',
                        '& fieldset': {
                          borderColor: 'rgba(255, 255, 255, 0.2)',
                        },
                        '&:hover fieldset': {
                          borderColor: 'rgba(255, 255, 255, 0.3)',
                        },
                        '&.Mui-focused fieldset': {
                          borderColor: '#FFD700',
                        },
                      },
                      '& .MuiInputLabel-root': {
                        color: 'rgba(255, 255, 255, 0.7)',
                      },
                      '& .MuiOutlinedInput-input': {
                        color: '#fff',
                      },
                    }}
                  />
                )}
              </Stack>

              <Button
                type="submit"
                fullWidth
                variant="contained"
                size="large"
                sx={{ 
                  mt: 4, 
                  mb: 2,
                  py: 1.5,
                  backgroundColor: '#FFD700',
                  color: '#000',
                  fontWeight: 600,
                  fontSize: '1.1rem',
                  textTransform: 'uppercase',
                  letterSpacing: '0.5px',
                  '&:hover': {
                    backgroundColor: '#FFC107',
                    transform: 'translateY(-1px)',
                    boxShadow: '0 8px 25px rgba(255, 215, 0, 0.3)',
                  },
                  '&:disabled': {
                    backgroundColor: 'rgba(255, 215, 0, 0.3)',
                    color: 'rgba(0, 0, 0, 0.5)',
                  },
                  transition: 'all 0.3s ease',
                }}
                disabled={loading}
                startIcon={loading ? <CircularProgress size={20} sx={{ color: '#000' }} /> : (isLogin ? <Email /> : <PersonOutline />)}
              >
                {loading ? 'Please wait...' : (isLogin ? 'Sign In' : 'Sign Up')}
              </Button>

              <Box textAlign="center">
                <Button
                  variant="text"
                  onClick={() => setIsLogin(!isLogin)}
                  sx={{ 
                    textTransform: 'none',
                    color: 'rgba(255, 255, 255, 0.7)',
                    '&:hover': {
                      color: '#FFD700',
                      backgroundColor: 'rgba(255, 215, 0, 0.1)',
                    },
                  }}
                >
                  {isLogin
                    ? "Don't have an account? Sign up"
                    : "Already have an account? Sign in"
                  }
                </Button>
              </Box>

              {isLogin && (
                <Box textAlign="center" mt={2}>
                  <Button
                    variant="text"
                    size="small"
                    onClick={() => setForgotPasswordOpen(true)}
                    sx={{ 
                      textTransform: 'none',
                      color: 'rgba(255, 255, 255, 0.6)',
                      fontSize: '0.85rem',
                      '&:hover': {
                        color: '#FFD700',
                        backgroundColor: 'rgba(255, 215, 0, 0.1)',
                      },
                    }}
                  >
                    Forgot Password?
                  </Button>
                </Box>
              )}
            </Box>
          </CardContent>
        </Card>
      </Container>

      {/* Forgot Password Dialog */}
      <Dialog 
        open={forgotPasswordOpen} 
        onClose={() => setForgotPasswordOpen(false)}
        PaperProps={{
          sx: {
            backgroundColor: 'rgba(0, 0, 0, 0.9)',
            color: '#fff',
            border: '1px solid rgba(255, 255, 255, 0.1)',
          }
        }}
      >
        <DialogTitle sx={{ color: '#FFD700' }}>Reset Password</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Email Address"
            type="email"
            fullWidth
            variant="outlined"
            value={resetEmail}
            onChange={(e) => setResetEmail(e.target.value)}
            sx={{
              '& .MuiOutlinedInput-root': {
                backgroundColor: 'rgba(255, 255, 255, 0.05)',
                '& fieldset': {
                  borderColor: 'rgba(255, 255, 255, 0.2)',
                },
                '&:hover fieldset': {
                  borderColor: 'rgba(255, 255, 255, 0.3)',
                },
                '&.Mui-focused fieldset': {
                  borderColor: '#FFD700',
                },
              },
              '& .MuiInputLabel-root': {
                color: 'rgba(255, 255, 255, 0.7)',
              },
              '& .MuiOutlinedInput-input': {
                color: '#fff',
              },
            }}
          />
        </DialogContent>
        <DialogActions>
          <Button 
            onClick={() => setForgotPasswordOpen(false)}
            sx={{ color: 'rgba(255, 255, 255, 0.7)' }}
          >
            Cancel
          </Button>
          <Button 
            onClick={handleForgotPassword} 
            variant="contained"
            sx={{
              backgroundColor: '#FFD700',
              color: '#000',
              '&:hover': {
                backgroundColor: '#FFC107',
              },
            }}
            disabled={!resetEmail || resetLoading}
            startIcon={resetLoading ? <CircularProgress size={18} sx={{ color: '#000' }} /> : undefined}
          >
            Send Reset Code
          </Button>
        </DialogActions>
      </Dialog>

      {/* OTP Verification Dialog - Used only for password reset, not registration */}
      <Dialog
        open={otpDialogOpen}
        onClose={() => setOtpDialogOpen(false)}
        PaperProps={{
          sx: {
            backgroundColor: 'rgba(0, 0, 0, 0.9)',
            color: '#fff',
            border: '1px solid rgba(255, 255, 255, 0.1)',
          }
        }}
      >
        <DialogTitle sx={{ color: '#FFD700' }}>Enter Verification Code</DialogTitle>
        <DialogContent>
          <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)', mb: 2 }}>
            Enter the 6-digit code sent to your email for password reset.
          </Typography>
          <TextField
            autoFocus
            margin="dense"
            label="Verification Code"
            fullWidth
            variant="outlined"
            value={otp}
            onChange={(e) => {
              const v = e.target.value.replace(/\D/g, '').slice(0, 6);
              setOtp(v);
            }}
            inputProps={{ inputMode: 'numeric', pattern: '[0-9]*', maxLength: 6 }}
            sx={{
              '& .MuiOutlinedInput-root': {
                backgroundColor: 'rgba(255, 255, 255, 0.05)',
                '& fieldset': {
                  borderColor: 'rgba(255, 255, 255, 0.2)',
                },
                '&:hover fieldset': {
                  borderColor: 'rgba(255, 255, 255, 0.3)',
                },
                '&.Mui-focused fieldset': {
                  borderColor: '#FFD700',
                },
              },
              '& .MuiInputLabel-root': {
                color: 'rgba(255, 255, 255, 0.7)',
              },
              '& .MuiOutlinedInput-input': {
                color: '#fff',
              },
            }}
          />
          <TextField
            margin="dense"
            label="New Password"
            type="password"
            fullWidth
            variant="outlined"
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
            sx={{
              '& .MuiOutlinedInput-root': {
                backgroundColor: 'rgba(255, 255, 255, 0.05)',
                '& fieldset': {
                  borderColor: 'rgba(255, 255, 255, 0.2)',
                },
                '&:hover fieldset': {
                  borderColor: 'rgba(255, 255, 255, 0.3)',
                },
                '&.Mui-focused fieldset': {
                  borderColor: '#FFD700',
                },
              },
              '& .MuiInputLabel-root': {
                color: 'rgba(255, 255, 255, 0.7)',
              },
              '& .MuiOutlinedInput-input': {
                color: '#fff',
              },
            }}
          />
        </DialogContent>
        <DialogActions>
          <Button
            onClick={() => setOtpDialogOpen(false)}
            sx={{ color: 'rgba(255, 255, 255, 0.7)' }}
          >
            Cancel
          </Button>
          <Button
            onClick={handleResetPassword}
            variant="contained"
            sx={{
              backgroundColor: '#FFD700',
              color: '#000',
              '&:hover': {
                backgroundColor: '#FFC107',
              },
            }}
            disabled={otpLoading || otp.length !== 6 || newPassword.length < 6 || !resetEmail}
            startIcon={otpLoading ? <CircularProgress size={18} sx={{ color: '#000' }} /> : undefined}
          >
            Reset Password
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Auth;
