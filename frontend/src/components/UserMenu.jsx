import React, { useState, useEffect, useRef } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import loginIcon from '../login_icon/login.png';
import './UserMenu.css';

const UserMenu = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [userName, setUserName] = useState('');
  const [showMenu, setShowMenu] = useState(false);
  const menuRef = useRef(null);

  useEffect(() => {
    const token = localStorage.getItem('token');
    const storedUserName = localStorage.getItem('userName');
    setIsLoggedIn(!!token);
    if (storedUserName) {
      setUserName(storedUserName);
    }

    const handleClickOutside = (event) => {
      if (menuRef.current && !menuRef.current.contains(event.target)) {
        setShowMenu(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const handleIconClick = () => {
    if (isLoggedIn) {
      setShowMenu(!showMenu);
    } else {
      navigate('/login');
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('userName');
    setIsLoggedIn(false);
    setUserName('');
    setShowMenu(false);
    navigate('/');
    window.location.reload(); // Refresh to update all components
  };

  const handleMyPage = () => {
    setShowMenu(false);
    navigate('/mypage');
  };

  const handleEditAccount = () => {
    setShowMenu(false);
    navigate('/edit-account');
  };

  return (
    <div className="user-menu-container" ref={menuRef}>
      <div className="user-info-wrapper" onClick={handleIconClick}>
        {isLoggedIn && (
          <span className="user-name">{(userName || "회원") + "님"}</span>
        )}
        <img
          src={loginIcon}
          alt={isLoggedIn ? "User Menu" : "Login"}
          className="user-icon"
        />
      </div>
      {isLoggedIn && showMenu && (
        <div className="dropdown-menu">
          {location.pathname !== '/mypage' && (
            <div className="menu-item" onClick={handleMyPage}>마이페이지</div>
          )}
          <div className="menu-item" onClick={handleEditAccount}>정보수정</div>
          <div className="menu-item" onClick={handleLogout}>로그아웃</div>
        </div>
      )}
    </div>
  );
};

export default UserMenu;
