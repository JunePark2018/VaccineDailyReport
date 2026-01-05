import { Link, useNavigate } from "react-router-dom";
import Button from "./Button"
import './Login.css'
import { useState } from "react";

const Login = ()=>{

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

    }


    return (
        <div className="Login">
            <form className="Login_total" onSubmit={handleLogin}>
                <div>
                    <div>
                        <input 
                            className="id_box" 
                            placeholder="아이디"
                            name="username"
                            value={loginData.username}
                            onChange={handleChange}
                        />
                    </div>
                    <div>
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
                    <div>
                        <Button type='submit' text='로그인'/>
                    </div>
                    <div>
                        <Button onClick={()=> nav('/signup')} text='회원가입'/>
                    </div>
                </div>
            </form>
        </div>
    )
}

export default Login;