import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';

function AuthForm() {
  const [visibleSpans, setVisibleSpans] = useState(new Set());
  
  useEffect(() => {
    console.log('Starting fade-in animation');
    
    // Animation timing from CodePen: 0.1s, 0.2s, 0.3s, etc.
    const delays = [100, 200, 300, 400, 500, 700, 800, 900, 1000, 1100]; // ms
    
    delays.forEach((delay, index) => {
      setTimeout(() => {
        console.log(`Making span ${index + 1} visible`);
        setVisibleSpans(prev => new Set(prev).add(index));
      }, delay);
    });
    
    return () => {
      console.log('Cleaning up fade-in animation');
    };
  }, []);
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    email: '',
    username: '',
    password: '',
    confirmPassword: ''
  });
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const { login, register } = useAuth();

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const validateForm = () => {
    const newErrors = {};

    if (isLogin) {
      // For login, email is required
      if (!formData.email.trim()) {
        newErrors.email = 'Email is required';
      } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
        newErrors.email = 'Please enter a valid email';
      }
    } else {
      // For registration, both email and username are required
      if (!formData.email.trim()) {
        newErrors.email = 'Email is required';
      } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
        newErrors.email = 'Please enter a valid email';
      }

      if (!formData.username.trim()) {
        newErrors.username = 'Username is required';
      }
    }

    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters';
    }

    if (!isLogin) {
      if (!formData.confirmPassword) {
        newErrors.confirmPassword = 'Please confirm your password';
      } else if (formData.password !== formData.confirmPassword) {
        newErrors.confirmPassword = 'Passwords do not match';
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) return;

    setLoading(true);
    try {
      let result;
      if (isLogin) {
        result = await login(formData.email, formData.password);
      } else {
        result = await register(formData.email, formData.username, formData.password);
      }

      if (!result.success) {
        setErrors({ general: result.error });
      }
    } catch (error) {
      setErrors({ general: 'An unexpected error occurred' });
    } finally {
      setLoading(false);
    }
  };

  const toggleForm = () => {
    setIsLogin(!isLogin);
    setFormData({
      email: '',
      username: '',
      password: '',
      confirmPassword: ''
    });
    setErrors({});
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[color:var(--md-sys-color-surface)] px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <div className="flex justify-center items-center gap-3 mb-6">
            <span className="material-icons text-4xl text-[color:var(--md-sys-color-primary)]">
              calendar_today
            </span>
            <h1 className="text-3xl font-medium text-[color:var(--md-sys-color-on-surface)]">
              Caltivity
            </h1>
          </div>
          <div className="mb-6 text-center tagline-container">
            <h2 
              className="text-2xl font-medium"
              style={{
                textAlign: 'center',
                lineHeight: '1.4',
                transform: 'scale(0.94)',
                animation: 'scaleUp 3s forwards cubic-bezier(0.5, 1, 0.89, 1)'
              }}
            >
              {['Turn', 'your', 'words', 'into', 'events.'].map((word, index) => (
                <span
                  key={index}
                  style={{
                    display: 'inline-block',
                    marginRight: '0.25rem',
                    opacity: visibleSpans.has(index) ? 1 : 0,
                    filter: visibleSpans.has(index) ? 'blur(0)' : 'blur(4px)',
                    transition: 'all 0.8s cubic-bezier(0.11, 0, 0.5, 0)',
                    color: '#ff1361'
                  }}
                >
                  {word}
                </span>
              ))}
              <br />
              {['Your', 'calendar', 'just', 'got', 'smarter.'].map((word, index) => (
                <span
                  key={index + 5}
                  style={{
                    display: 'inline-block',
                    marginRight: '0.25rem',
                    opacity: visibleSpans.has(index + 5) ? 1 : 0,
                    filter: visibleSpans.has(index + 5) ? 'blur(0)' : 'blur(4px)',
                    transition: 'all 0.8s cubic-bezier(0.11, 0, 0.5, 0)',
                    color: '#ff1361'
                  }}
                >
                  {word}
                </span>
              ))}
            </h2>
          </div>
          <h2 className="text-xl font-medium text-[color:var(--md-sys-color-primary)] mt-4 mb-2">
            {isLogin ? 'Sign in to your account' : 'Create your account'}
          </h2>
        </div>

        <form className="mt-4 space-y-4" onSubmit={handleSubmit}>
          <div className="bg-[color:var(--md-sys-color-surface-container)] rounded-2xl p-6 shadow-level-2">
            {errors.general && (
              <div className="mb-4 p-3 rounded-xl bg-[color:var(--md-sys-color-error-container)] text-[color:var(--md-sys-color-on-error-container)] text-sm">
                {errors.general}
              </div>
            )}

            <div className="mb-4">
              <label htmlFor="email" className="block text-sm font-medium text-[color:var(--md-sys-color-on-surface-variant)] mb-2">
                Email address
              </label>
              <input
                id="email"
                name="email"
                type="email"
                autoComplete="email"
                className="w-full px-4 py-3 rounded-xl border border-[color:var(--md-sys-color-outline)] bg-[color:var(--md-sys-color-surface)] text-[color:var(--md-sys-color-on-surface)] placeholder-[color:var(--md-sys-color-on-surface-variant)] focus:ring-2 focus:ring-[color:var(--md-sys-color-primary)] focus:border-transparent outline-none transition-all"
                placeholder="Enter your email"
                value={formData.email}
                onChange={handleInputChange}
              />
              {errors.email && (
                <p className="mt-1 text-sm text-[color:var(--md-sys-color-error)]">{errors.email}</p>
              )}
            </div>

            {!isLogin && (
              <div className="mb-4">
                <label htmlFor="username" className="block text-sm font-medium text-[color:var(--md-sys-color-on-surface-variant)] mb-2">
                  Username
                </label>
                <input
                  id="username"
                  name="username"
                  type="text"
                  autoComplete="username"
                  className="w-full px-4 py-3 rounded-xl border border-[color:var(--md-sys-color-outline)] bg-[color:var(--md-sys-color-surface)] text-[color:var(--md-sys-color-on-surface)] placeholder-[color:var(--md-sys-color-on-surface-variant)] focus:ring-2 focus:ring-[color:var(--md-sys-color-primary)] focus:border-transparent outline-none transition-all"
                  placeholder="Enter your username"
                  value={formData.username}
                  onChange={handleInputChange}
                />
                {errors.username && (
                  <p className="mt-1 text-sm text-[color:var(--md-sys-color-error)]">{errors.username}</p>
                )}
              </div>
            )}

            <div className="mb-4">
              <label htmlFor="password" className="block text-sm font-medium text-[color:var(--md-sys-color-on-surface-variant)] mb-2">
                Password
              </label>
              <input
                id="password"
                name="password"
                type="password"
                autoComplete={isLogin ? "current-password" : "new-password"}
                className="w-full px-4 py-3 rounded-xl border border-[color:var(--md-sys-color-outline)] bg-[color:var(--md-sys-color-surface)] text-[color:var(--md-sys-color-on-surface)] placeholder-[color:var(--md-sys-color-on-surface-variant)] focus:ring-2 focus:ring-[color:var(--md-sys-color-primary)] focus:border-transparent outline-none transition-all"
                placeholder="Enter your password"
                value={formData.password}
                onChange={handleInputChange}
              />
              {errors.password && (
                <p className="mt-1 text-sm text-[color:var(--md-sys-color-error)]">{errors.password}</p>
              )}
            </div>

            {!isLogin && (
              <div className="mb-6">
                <label htmlFor="confirmPassword" className="block text-sm font-medium text-[color:var(--md-sys-color-on-surface-variant)] mb-2">
                  Confirm Password
                </label>
                <input
                  id="confirmPassword"
                  name="confirmPassword"
                  type="password"
                  autoComplete="new-password"
                  className="w-full px-4 py-3 rounded-xl border border-[color:var(--md-sys-color-outline)] bg-[color:var(--md-sys-color-surface)] text-[color:var(--md-sys-color-on-surface)] placeholder-[color:var(--md-sys-color-on-surface-variant)] focus:ring-2 focus:ring-[color:var(--md-sys-color-primary)] focus:border-transparent outline-none transition-all"
                  placeholder="Confirm your password"
                  value={formData.confirmPassword}
                  onChange={handleInputChange}
                />
                {errors.confirmPassword && (
                  <p className="mt-1 text-sm text-[color:var(--md-sys-color-error)]">{errors.confirmPassword}</p>
                )}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 px-4 rounded-xl bg-[color:var(--md-sys-color-primary)] text-[color:var(--md-sys-color-on-primary)] font-medium transition-all duration-200 hover:bg-[color:var(--md-sys-color-primary)] hover:shadow-level-2 focus:ring-2 focus:ring-[color:var(--md-sys-color-primary)] focus:ring-opacity-20 outline-none disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <span className="flex items-center justify-center gap-2">
                  <div className="w-4 h-4 border-2 border-[color:var(--md-sys-color-on-primary)] border-t-transparent rounded-full animate-spin"></div>
                  {isLogin ? 'Signing in...' : 'Creating account...'}
                </span>
              ) : (
                isLogin ? 'Sign in' : 'Create account'
              )}
            </button>
          </div>

          <div className="text-center">
            <button
              type="button"
              onClick={toggleForm}
              className="bg-[color:var(--md-sys-color-surface-container-high)] text-[color:var(--md-sys-color-on-surface)] hover:bg-[color:var(--md-sys-color-primary)] hover:text-[color:var(--md-sys-color-on-primary)] font-medium transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-[color:var(--md-sys-color-primary)] focus:ring-opacity-50 rounded-xl px-6 py-3 border border-[color:var(--md-sys-color-outline)] shadow-sm"
            >
              {isLogin 
                ? "Don't have an account? Sign up" 
                : "Already have an account? Sign in"
              }
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AuthForm;