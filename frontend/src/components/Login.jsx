import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import Button from "./Button";
import Header from "./Header";
import Logo from "./Logo";
import UserMenu from "./UserMenu";
import "./Login.css";

const Login = () => {

    const nav = useNavigate();

    const [loginData, setLoginData] = useState({
        login_id: '',
        password: ''
    });

    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setLoginData(prevData => ({
            ...prevData,
            [name]: value,
        }));
        // Clear error when user types
        if (error) {
            setError('');
        }
    }

    const handleLogin = async (e) => {
        e.preventDefault();
        setError('');
        setIsLoading(true);

        try {
            // POST request to backend login API
            const response = await fetch('http://localhost:8000/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    login_id: loginData.login_id,
                    password: loginData.password
                })
            });

            const data = await response.json();

            if (response.ok && data.success) {
                // Success - Save user info to localStorage
                localStorage.setItem('isLoggedIn', 'true');
                localStorage.setItem('user_id', data.user_id);
                localStorage.setItem('login_id', data.login_id);
                localStorage.setItem('user_real_name', data.user_real_name);

                console.log('Login successful:', data);

                // Navigate to home page
                nav('/');
            } else {
                // Backend returned an error
                setError(data.detail || '로그인에 실패했습니다.');
            }
        } catch (error) {
            // Network or other error
            console.error('Login error:', error);
            setError('서버와 연결할 수 없습니다. 나중에 다시 시도해주세요.');
        } finally {
            setIsLoading(false);
        }
    }


    return (
        <div className="Login">
            <div className="Login_Logo">
                <Logo />
            </div>
            <div className="Login_main_box">
                <form className="Login_total" onSubmit={handleLogin}>
                    <div className="input_containter">
                        <input
                            className="id_box"
                            placeholder="아이디"
                            name="login_id"
                            value={loginData.login_id}
                            onChange={handleChange}
                            disabled={isLoading}
                        />
                    </div>
                    <div className="input_containter">
                        <input
                            className="pw_box"
                            placeholder="비밀번호"
                            name="password"
                            type="password"
                            value={loginData.password}
                            onChange={handleChange}
                            disabled={isLoading}
                        />
                        {error && (
                            <p className="error_login">
                                {error}
                            </p>
                        )}
                    </div>
                </form>
                <div>
                    {/*로그인 버튼 */}
                    <div className="button_wrapper">
                        <div className="button_container">
                            <Button
                                type='submit'
                                text={isLoading ? '로그인 중...' : '로그인'}
                                textColor='black'
                                borderRadius="3px"
                                color='rgba(186, 214, 205, 1)'
                                width="100%"
                                height="55px"
                                onClick={handleLogin}
                                disabled={isLoading}
                            />
                        </div>
                    </div>
                    {/* 구분선 */}
                    <div className="line">
                        <span className="line_01"></span>
                        <span className="line_text">또는</span>
                        <span className="line_01"></span>
                    </div>
                    {/*회원가입 버튼 */}
                    <div className="signup_text">
                        <Button onClick={() => nav('/CreateAccount')}
                            text='회원가입'
                            textColor='black'
                            borderRadius="3px"
                            color='rgba(220, 220, 220, 1)'
                            width="100%"
                            height="55px"

                        />
                    </div>
                </div>
            </div>
        </div>
    )
}

export default Login;
