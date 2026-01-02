import { useNavigate } from 'react-router-dom'
import { useState } from 'react';
import './LeftSideBar.css'

/**
 
왼쪽 사이드바 컴포넌트 입니다.  
darkmode: 다크모드 배경색 ( 기본값: #ffffffff)  
textColor: 아이콘 하단 글자색. 기본값: black  
textSize: 아이콘 하단 글자 크기. 문자열로 주세요. (예: "15px") 기본값: 10px  
onClick: 아이콘 클릭 시 실행될 함수 부모 컴포넌트에서 navigate 변수 설정 / ex) const nav = useNavigate();  
className: 추가로 적용할 CSS 클래스명  
width: 사이드바 너비(px). 문자열. 기본값: 72px
*/
export default function LeftSideBar({
    darkmode = "#ffffffff",
    textColor = "black",
    textSize = "10px",
    width = "72px"
}) {
    const nav = useNavigate();
    const [showCategoryPanel, setShowCategoryPanel] = useState(false);

    return (
        <div style={{ display: "flex" }}>
            {/* 사이드바 */}
            <div className="LeftSideBar" 
            style={{
                position: 'fixed',
                top: 0,
                left: 0,
                backgroundColor: darkmode,
                color: textColor,
                fontSize: textSize,
                width: width,
                height: "100vh",
                display: "flex",
                flexDirection: "column",
                zIndex: 1000
            }}
            >
                <div className="left_sidebar_01">
                    <div className="left_sidebar_category">
                        <div 
                        className="left_sidebar_category_box"
                        onClick={() => setShowCategoryPanel(!showCategoryPanel)}
                        >
                            <div className="left_sidebar_category_icon">아이콘</div>
                            <span>카테고리</span>
                        </div>
                    </div>
                    <div className="left_sidebar_Algorithm_top_01">
                        <div 
                        className="left_sidebar_Algorithm_box_01"
                        onClick={() => nav('/Algorithm1')}>
                            <div className="left_sidebar_Algorithm_icon_01">아이콘</div>
                            <div>Algorithm1</div>
                        </div>
                    </div>
                    <div className="left_sidebar_Algorithm_top_02">
                        <div 
                        className="left_sidebar_Algorithm_box_02"
                        onClick={() => nav('/Algorithm2')}
                        >
                            <div className="left_sidebar_Algorithm_icon_02">아이콘</div>
                            <div>Algorithm2</div>
                        </div>
                    </div>
                    <div className="left_sidebar_Algorithm_top_03">
                        <div 
                        className="left_sidebar_Algorithm_box_03"
                        onClick={() => nav('/Algorithm3')}
                        >
                            <div className="left_sidebar_Algorithm_icon_03">아이콘</div>
                            <div>Algorithm3</div>
                        </div>
                    </div>
                </div>
            </div>

            {/*카테고리 패널*/}
            <div className={`category_panel ${showCategoryPanel ? 'open' : ''}`}>
                <h3>카테고리</h3>
                <ul>
                    <li onClick={() => nav('/sub1')}>정치</li>
                    <li onClick={() => nav('/sub2')}>경제</li>
                    <li onClick={() => nav('/sub3')}>사회</li>
                    <li onClick={() => nav('/sub4')}>엔터</li>
                    <li onClick={() => nav('/sub5')}>건강</li>
                    <li onClick={() => nav('/sub6')}>스포츠</li>
                    <li onClick={() => nav('/sub7')}>기후</li>
                    <li onClick={() => nav('/sub8')}>과학</li>
                    <li onClick={() => nav('/sub9')}>세계</li>
                </ul>
            </div>
        </div>
    )
};