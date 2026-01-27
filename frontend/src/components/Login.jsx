import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import Button from "./Button";
import Header from "./Header";
import Logo from "./Logo";
import UserMenu from "./UserMenu";
import Searchbar from "./Searchbar";
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
            <Header
                leftChild={<Logo />}
                midChild={null}
                rightChild={
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0', justifyContent: 'flex-end', width: 'auto' }}>
                        <div style={{ position: 'relative' }}>
                            <Searchbar className="always-open" />
                        </div>
                        <UserMenu />
                    </div>
                }
                headerTop="on"
                headerMain="on"
                headerBottom="on"
            />

            <div className="Login_container_wrapper">
                <div className="Login_main_box">
                    <h2 className="login-title">로그인</h2>
                    <form className="Login_total" onSubmit={handleLogin}>
                        <div className="naver_input_group">
                            <input
                                className="naver_input top"
                                placeholder="아이디"
                                name="login_id"
                                value={loginData.login_id}
                                onChange={handleChange}
                                disabled={isLoading}
                                autoComplete="off"
                            />
                            <input
                                className="naver_input bottom"
                                placeholder="비밀번호"
                                name="password"
                                type="password"
                                value={loginData.password}
                                onChange={handleChange}
                                disabled={isLoading}
                                autoComplete="off"
                            />
                        </div>

                        {error && (
                            <p className="error_login">
                                {error}
                            </p>
                        )}

                        <div className="button_wrapper">
                            <Button
                                type='submit'
                                text={isLoading ? '로그인 중...' : '로그인'}
                                textColor='white'
                                borderRadius="0px" // CSS will handle rounded corners if needed, or keep square as per theme, but standard Naver is generic. I'll stick to the requested "Naver" style which often has rounded buttons, but the user's existing theme is square. I'll keep the specialized Button component usage but maybe styling needs check. actually, the prompt implies visual style. I will update CSS to style this button to be wide and maybe slightly rounded if needed, but for now sticking to the existing Button component is safest for functionality.
                                color='#333333' // Reverted to project theme color
                                width="100%"
                                height="50px"
                                onClick={handleLogin}
                                disabled={isLoading}
                                fontWeight="bold"
                                title="로그인"
                            />
                        </div>
                    </form>

                    <div className="login_links">
                        <span>비밀번호 찾기</span>
                        <span className="bar">|</span>
                        <span>아이디 찾기</span>
                        <span className="bar">|</span>
                        <span className="link_text" onClick={() => nav('/CreateAccount')}>회원가입</span>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default Login;
