import './Searchbar.css';
import React, { useState } from 'react';

/**
 * Searchbar 컴포넌트: 사용자의 입력값을 받아 검색 로직을 수행하는 바 형태의 UI
 * * @param {string} maxWidth - 검색창의 최대 너비 (예: "500px", "100%")
 * @param {string} fontSize - 입력창 및 아이콘의 기준 폰트 크기 (예: "16px")
 * @param {string} className - 외부에서 추가할 CSS 클래스 이름
 */
function Searchbar({ maxWidth, fontSize, className}) {
    // 사용자가 입력창에 타이핑하는 텍스트 상태 관리
    const [inputText, setInputText] = useState("");

    /**
     * 실제 검색 로직을 처리하는 함수
     */
    const handleSearch = () => {
        if (inputText.trim() !== "") {
            console.log(`검색어 전송: ${inputText}`);
        }
    };

    /**
     * 키보드 이벤트 핸들러: 'Enter' 키 감지
     */
    const onKeyPress = (e) => {
        if (e.key === 'Enter') {
            handleSearch();
        }
    };

    // Props로 받은 maxWidth와 fontSize를 인라인 스타일에 적용
    const boxStyle = {
        maxWidth: maxWidth
    };

    const inputStyle = {
        fontSize: fontSize
    };
    
    return (
        // 외부에서 전달받은 className을 기본 클래스와 결합
        <div className={`Searchbar ${className}`}>
            {/* maxWidth 스타일 적용 */}
            <div className="search-box" style={boxStyle}>
                <input 
                    type="text" 
                    placeholder="검색어를 입력하세요"
                    value={inputText}
                    onChange={(e) => setInputText(e.target.value)}
                    onKeyDown={onKeyPress}
                    style={inputStyle} // fontSize 스타일 적용
                />
                
                <button onClick={handleSearch} aria-label="search">
                    <svg 
                        xmlns="http://www.w3.org/2000/svg" 
                        viewBox="0 0 24 24" 
                        strokeLinecap="round" 
                        strokeLinejoin="round"
                        // 아이콘 크기도 폰트 크기에 비례하게 조절하고 싶다면 style 추가 가능
                        style={{ width: `calc(${fontSize} + 6px)`, height: `calc(${fontSize} + 6px)` }}
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