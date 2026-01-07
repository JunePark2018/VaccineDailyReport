import React from 'react';
import './header3.css';
import Logo from './Logo';
import Searchbar from './Searchbar';
import loginIcon from '../login_icon/login.png';
import { useNavigate } from 'react-router-dom';

const Header3 = () => {
    const navigate = useNavigate();
    const categories = ["정치", "경제", "사회", "생활/문화", "IT/과학", "세계", "랭킹"];

    return (
        <header className="header3">
            <div className="header3-top">
                <div className="header3-logo">
                    <Logo />
                </div>
                <div className="header3-search">
                    <Searchbar maxWidth="600px" />
                </div>
                <div className="header3-login">
                    <img 
                        src={loginIcon} 
                        alt="login" 
                        width="35px" 
                        onClick={() => navigate('/login')} 
                        style={{ cursor: 'pointer' }} 
                    />
                </div>
            </div>
            <div className="header3-bottom">
                <nav className="header3-nav">
                    <ul>
                        {categories.map((category, index) => (
                            <li key={index} onClick={() => navigate(`/category/${category}`)}>{category}</li>
                        ))}
                    </ul>
                </nav>
            </div>
        </header>
    );
};

export default Header3;
