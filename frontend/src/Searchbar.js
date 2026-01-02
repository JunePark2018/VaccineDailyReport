import './Searchbar.css';
import React, { useState } from 'react';

function Searchbar() {
    const [inputText, setInputText] = useState("");

    // 검색 실행 함수
    const handleSearch = () => {
        if (inputText.trim() !== "") {
            console.log(`검색어 전송: ${inputText}`);
        }
    };

    // 엔터키 지원
    const onKeyPress = (e) => {
        if (e.key === 'Enter') {
            handleSearch();
        }
    };
    
    return (
        <div className='Searchbar'>
            <div className="search-box">
                <input 
                    type="text" 
                    placeholder="검색어를 입력하세요"
                    value={inputText}
                    onChange={(e) => setInputText(e.target.value)}
                    onKeyDown={onKeyPress}
                />
                <button onClick={handleSearch} aria-label="search">
                    <svg 
                        xmlns="http://www.w3.org/2000/svg" 
                        viewBox="0 0 24 24" 
                        strokeLinecap="round" 
                        strokeLinejoin="round"
                    >
                        <circle cx="11" cy="11" r="8"></circle>
                        <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                    </svg>
                </button>
            </div>
        </div>
    );
}

export default Searchbar;