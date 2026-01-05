import { useNavigate } from 'react-router-dom'
import { useState } from 'react';
import './LeftSideBar.css'

import governmentIcon from './leftsidebaricon/government.png';
import economicsIcon from './leftsidebaricon/economics.png';
import societyIcon from './leftsidebaricon/society.png';
import entertainmentIcon from './leftsidebaricon/entertainment.png';
import healthIcon from './leftsidebaricon/health.png';
import sportsIcon from './leftsidebaricon/sports.png';
import weatherIcon from './leftsidebaricon/weather.png';
import scienceIcon from './leftsidebaricon/science.png';
import worldIcon from './leftsidebaricon/world.png';
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
    let closeTimer = null;

    const handleMouseLeave = () => {
        closeTimer = setTimeout(() => {
            setShowCategoryPanel(false);
        }, 300);
    };

    const handleMouseEnter = () => {
        if (closeTimer) {
            clearTimeout(closeTimer);
        }
    };

    const categories = [
        { id: 'sub1', label: '정치', icon: governmentIcon },
        { id: 'sub2', label: '경제', icon: economicsIcon },
        { id: 'sub3', label: '사회', icon: societyIcon },
        { id: 'sub4', label: '엔터', icon: entertainmentIcon },
        { id: 'sub5', label: '건강', icon: healthIcon },
        { id: 'sub6', label: '스포츠', icon: sportsIcon },
        { id: 'sub7', label: '기후', icon: weatherIcon },
        { id: 'sub8', label: '과학', icon: scienceIcon },
        { id: 'sub9', label: '세계', icon: worldIcon },
    ];

    return (
        <div className="LeftSideBar" style={{ display: "flex" }}>
            {/* 사이드바 */}
            <div className='left_sidebar_area'
                style={{
                    top: 0,
                    left: 0,
                    width: width,
                    height: "100vh",
                    visibility: "false"
                }}
            >
            </div>
            <div className="category_buttons"
                style={{
                    position: "fixed",
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
            <div 
                className={`category_panel ${showCategoryPanel ? 'open' : ''}`}
                onMouseEnter={handleMouseEnter}
                onMouseLeave={handleMouseLeave}>             
                <h3>카테고리</h3>
                <ul>
                    {categories.map((item) => (
                        <li key={item.id} onClick={() => nav(`/${item.id}`)}>
                            <img 
                                src={item.icon} 
                                alt={item.label} 
                                className="category_icon_img" 
                            />
                            {item.label}
                        </li>
                    ))}
                </ul>
            </div>
        </div>
    )
};