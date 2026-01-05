import { useNavigate } from 'react-router-dom';
import './LeftSideBar.css';

// Import all category icons
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
 * LeftSideBar Component
 * darkmode: Background color (default: #ffffffff)
 * textColor: Text color (default: black)
 * textSize: Font size (default: 10px)
 * width: Sidebar width (default: 72px)
 */
export default function LeftSideBar({
    darkmode = "#ffffffff",
    textColor = "black",
    textSize = "10px",
    width = "72px"
}) {
    const nav = useNavigate();

    // Data array for categories
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
            {/* Layout spacer to prevent main content from hiding behind the fixed sidebar */}
            <div className='left_sidebar_area' style={{ width: width, height: "100vh" }}></div>
            
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
                    zIndex: 1000,
                    overflowY: "auto",
                    overflowX: "hidden"
                }}
            >
                {categories.map((item) => (
                    <div 
                        key={item.id} 
                        className="sidebar_icon_item" 
                        onClick={() => nav(`/${item.id}`)}
                    >
                        <div className="icon_wrapper">
                            <img 
                                src={item.icon} 
                                alt={item.label} 
                                className="category_main_icon" 
                            />
                        </div>
                        <span>{item.label}</span>
                    </div>
                ))}
            </div>
        </div>
    );
}