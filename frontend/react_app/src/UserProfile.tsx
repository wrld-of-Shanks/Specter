import React, { useState, useEffect } from 'react';
import config from './config.ts';

interface UserProfileProps {
    user: any;
    token: string;
    onLogout: () => void;
    onBack: () => void;
}

const UserProfile: React.FC<UserProfileProps> = ({ user, token, onLogout, onBack }) => {
    const [plans, setPlans] = useState<any>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [msg, setMsg] = useState('');
    const [usageStats, setUsageStats] = useState<any>(null);

    useEffect(() => {
        fetchPlans();
        fetchUsageStats();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    const fetchPlans = async () => {
        try {
            const response = await fetch(`${config.API_BASE_URL}/payment/plans`);
            const data = await response.json();
            setPlans(data);
        } catch (error) {
            console.error("Failed to load plans", error);
        }
    };

    const fetchUsageStats = async () => {
        try {
            const response = await fetch(`${config.API_BASE_URL}/usage`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            const data = await response.json();
            setUsageStats(data);
        } catch (error) {
            console.error("Failed to load usage stats", error);
        }
    };

    const loadRazorpay = () => {
        return new Promise((resolve) => {
            const script = document.createElement('script');
            script.src = 'https://checkout.razorpay.com/v1/checkout.js';
            script.onload = () => resolve(true);
            script.onerror = () => resolve(false);
            document.body.appendChild(script);
        });
    };

    const handleSubscribe = async (planKey: string) => {
        setIsLoading(true);
        setMsg('');

        try {
            const res = await loadRazorpay();
            if (!res) {
                setMsg('Razorpay SDK failed to load. Are you online?');
                setIsLoading(false);
                return;
            }

            // 1. Create Order
            const orderResponse = await fetch(`${config.API_BASE_URL}/payment/create-order`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ plan: planKey })
            });

            const orderData = await orderResponse.json();

            if (!orderResponse.ok) {
                setMsg(orderData.detail || 'Failed to create order');
                setIsLoading(false);
                return;
            }

            // 2. Open Razorpay Checkout
            const options = {
                key: orderData.key_id,
                amount: orderData.amount,
                currency: orderData.currency,
                name: "SPECTER Legal Assistant",
                description: orderData.description,
                order_id: orderData.order_id,
                handler: async function (response: any) {
                    // 3. Verify Payment
                    try {
                        const verifyResponse = await fetch(`${config.API_BASE_URL}/payment/verify`, {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                                'Authorization': `Bearer ${token}`
                            },
                            body: JSON.stringify({
                                razorpay_order_id: response.razorpay_order_id,
                                razorpay_payment_id: response.razorpay_payment_id,
                                razorpay_signature: response.razorpay_signature
                            })
                        });

                        await verifyResponse.json();

                        if (verifyResponse.ok) {
                            setMsg('Subscription activated successfully! 🎉');
                            // Ideally refresh user profile here
                        } else {
                            setMsg('Payment verification failed.');
                        }
                    } catch (error) {
                        setMsg('Error verifying payment.');
                    }
                },
                prefill: {
                    name: user.full_name,
                    email: user.email,
                },
                theme: {
                    color: "#fbbf24"
                }
            };

            const paymentObject = new (window as any).Razorpay(options);
            paymentObject.open();

        } catch (error) {
            setMsg('Something went wrong.');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="profile-container" style={{ padding: '40px', maxWidth: '1200px', margin: '0 auto' }}>
            <div className="profile-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '40px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
                    <button
                        onClick={onBack}
                        style={{
                            background: 'transparent',
                            border: '1px solid #444',
                            color: '#fff',
                            padding: '8px 16px',
                            borderRadius: '6px',
                            cursor: 'pointer',
                            fontSize: '1rem'
                        }}
                    >
                        ← Back
                    </button>
                    <h1 style={{ fontSize: '2.5rem', margin: 0, color: '#fbbf24' }}>MY PROFILE</h1>
                </div>
            </div>

            <div style={{ background: '#1a1a1a', padding: '20px', borderRadius: '12px', border: '1px solid #333', marginBottom: '30px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
                    <div style={{ width: '60px', height: '60px', borderRadius: '50%', background: '#fbbf24', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1.5rem', fontWeight: 'bold', color: '#000' }}>
                        {user.full_name?.charAt(0).toUpperCase()}
                    </div>
                    <div>
                        <h3 style={{ margin: '0 0 5px 0', color: '#fff' }}>{user.full_name}</h3>
                        <p style={{ margin: 0, color: '#888' }}>{user.email}</p>
                        <div style={{ marginTop: '10px' }}>
                            <span style={{
                                background: user.subscription?.status === 'active' ? '#10b981' : '#333',
                                color: user.subscription?.status === 'active' ? '#000' : '#888',
                                padding: '4px 10px',
                                borderRadius: '4px',
                                fontSize: '0.8rem',
                                fontWeight: 'bold'
                            }}>
                                {user.subscription?.plan ? user.subscription.plan.toUpperCase() : 'FREE PLAN'}
                            </span>
                        </div>
                    </div>
                </div>
            </div>

            {/* Usage Stats */}
            {usageStats && usageStats.questions && usageStats.uploads && (
                <div style={{ background: '#1a1a1a', padding: '20px', borderRadius: '12px', border: '1px solid #333', marginBottom: '30px' }}>
                    <h3 style={{ color: '#fbbf24', marginTop: 0, marginBottom: '15px' }}>Usage This Month</h3>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '15px' }}>
                        <div style={{ background: '#222', padding: '15px', borderRadius: '8px' }}>
                            <div style={{ color: '#888', fontSize: '0.9rem', marginBottom: '5px' }}>Questions Asked</div>
                            <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#fff' }}>
                                {usageStats.questions.used} / {usageStats.questions.limit === -1 ? '∞' : usageStats.questions.limit}
                            </div>
                            {usageStats.questions.limit !== -1 && (
                                <div style={{ marginTop: '8px', background: '#333', height: '6px', borderRadius: '3px', overflow: 'hidden' }}>
                                    <div style={{
                                        width: `${Math.min((usageStats.questions.used / usageStats.questions.limit) * 100, 100)}%`,
                                        height: '100%',
                                        background: usageStats.questions.remaining > 0 ? '#fbbf24' : '#ef4444',
                                        transition: 'width 0.3s'
                                    }}></div>
                                </div>
                            )}
                        </div>
                        <div style={{ background: '#222', padding: '15px', borderRadius: '8px' }}>
                            <div style={{ color: '#888', fontSize: '0.9rem', marginBottom: '5px' }}>Documents Uploaded</div>
                            <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#fff' }}>
                                {usageStats.uploads.used} / {usageStats.uploads.limit === -1 ? '∞' : usageStats.uploads.limit}
                            </div>
                            {usageStats.uploads.limit !== -1 && (
                                <div style={{ marginTop: '8px', background: '#333', height: '6px', borderRadius: '3px', overflow: 'hidden' }}>
                                    <div style={{
                                        width: `${Math.min((usageStats.uploads.used / usageStats.uploads.limit) * 100, 100)}%`,
                                        height: '100%',
                                        background: usageStats.uploads.remaining > 0 ? '#fbbf24' : '#ef4444',
                                        transition: 'width 0.3s'
                                    }}></div>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            )}

            <h3 style={{ color: '#fbbf24', marginBottom: '20px' }}>Subscription Plans</h3>

            {msg && <div style={{ padding: '10px', background: '#333', borderRadius: '8px', marginBottom: '20px', textAlign: 'center' }}>{msg}</div>}

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '20px' }}>
                {/* Free Plan */}
                <div style={{ background: '#222', padding: '20px', borderRadius: '12px', border: '1px solid #333' }}>
                    <h4 style={{ color: '#fff', margin: '0 0 10px 0' }}>Free</h4>
                    <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#fff', marginBottom: '15px' }}>₹0<span style={{ fontSize: '1rem', color: '#888', fontWeight: 'normal' }}>/mo</span></div>
                    <ul style={{ listStyle: 'none', padding: 0, margin: '0 0 20px 0', color: '#ccc' }}>
                        <li style={{ marginBottom: '8px' }}>✓ 3 Questions/mo</li>
                        <li style={{ marginBottom: '8px' }}>✓ 1 Document Upload</li>
                        <li style={{ marginBottom: '8px' }}>✓ Basic Support</li>
                    </ul>
                    <button disabled className="contact-btn" style={{ width: '100%', background: '#333', cursor: 'default', opacity: 0.7 }}>Current Plan</button>
                </div>

                {plans && Object.entries(plans).map(([key, plan]: [string, any]) => (
                    <div key={key} style={{ background: '#222', padding: '20px', borderRadius: '12px', border: '1px solid #fbbf24', position: 'relative' }}>
                        {key === 'specter' && <div style={{ position: 'absolute', top: '-10px', right: '20px', background: '#fbbf24', color: '#000', padding: '2px 10px', borderRadius: '4px', fontSize: '0.8rem', fontWeight: 'bold' }}>RECOMMENDED</div>}
                        <h4 style={{ color: '#fff', margin: '0 0 10px 0' }}>{plan.name}</h4>
                        <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#fff', marginBottom: '15px' }}>
                            ₹{plan.amount / 100}<span style={{ fontSize: '1rem', color: '#888', fontWeight: 'normal' }}>/mo</span>
                        </div>
                        <p style={{ color: '#888', fontSize: '0.9rem', marginBottom: '15px' }}>{plan.description}</p>
                        <ul style={{ listStyle: 'none', padding: 0, margin: '0 0 20px 0', color: '#ccc' }}>
                            <li style={{ marginBottom: '8px' }}>✓ {key === 'specter' ? 'Unlimited' : '50'} Questions</li>
                            <li style={{ marginBottom: '8px' }}>✓ {key === 'specter' ? 'Unlimited' : '25'} Document Analyses</li>
                            <li style={{ marginBottom: '8px' }}>✓ Priority Support</li>
                        </ul>
                        <button
                            onClick={() => handleSubscribe(key)}
                            className="contact-btn"
                            style={{ width: '100%' }}
                            disabled={isLoading}
                        >
                            {isLoading ? 'Processing...' : `Upgrade to ${plan.name}`}
                        </button>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default UserProfile;
