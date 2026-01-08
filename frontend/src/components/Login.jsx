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
        username:'',
        password:''
    });

    const [error,setError] = useState('');

    const handleChange = (e) =>{
        const {name, value} = e.target;
        setLoginData(prevData => ({
            ...prevData,
            [name]: value,    
        }));
    }
    const handleLogin = (e) =>{
        e.preventDefault();
        setError('');
        
        // Test login logic: if username and password are 'test'
        if (loginData.username === 'test' && loginData.password === 'test') {
            localStorage.setItem('token', 'fake-token');
            nav('/mypage');
        } else {
            setError('아이디 또는 비밀번호가 일치하지 않습니다. (테스트 계정: test / test)');
        }
    }


    return (
        <div className="Login">
            <Header
                headerTop="off"
                headerMain="on"
                headerBottom="off"
                leftChild={<Logo />}
                rightChild={<UserMenu />}
            />
            <form className="Login_total" onSubmit={handleLogin}>
                    <div className="input_containter">
                        <input 
                            className="id_box" 
                            placeholder="아이디"
                            name="username"
                            value={loginData.username}
                            onChange={handleChange}
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
                        />
                        {error && (
                            <p className="error_login">
                                {error}
                            </p>
                        )}
                    </div>
                    <div className="button_wrapper">
                        <div className="button_container">
                            <Button type='submit' text='로그인'/>
                        </div>
                        <div className="button_container">
                            <Button onClick={() => nav('/CreateAccount')} text='회원가입'/>
                        </div>
                    </div>
            </form>
        </div>
    )
}

export default Login;
