import React, { useState, useEffect, useMemo } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import axios from 'axios';
import Logo from '../components/Logo';
import UserMenu from '../components/UserMenu';
import Header from '../components/Header';
import Button from '../components/Button';
import './MyPage.css';

const CATEGORIES = ['정치', '경제', '사회', '생활/문화', 'IT/과학', '세계'];

const MOCK_USER_DATA = {
  user_real_name: "홍길동",
  email: "gildong@example.com",
  read_categories: { '정치': 85, '경제': 45, '사회': 95, '생활/문화': 60, 'IT/과학': 100, '세계': 30 },
  read_keywords: { '반도체': 15, '금리': 10, '인공지능': 25, '나스닥': 8, '재건축': 12, '우크라이나': 5, '이재명':100, '윤석열':300, 'AI':55, '박나래':44 },
  subscribed_keywords: ['AI', '재테크', '건강']
};

const MyPage = () => {
  const navigate = useNavigate();
  const { login_id } = useParams();

  const [isActive, setIsActive] = useState(false);
  const [isEditMode, setIsEditMode] = useState(false);
  const [loading, setLoading] = useState(true);

  const [userData, setUserData] = useState(null);
  const [targetScores, setTargetScores] = useState({});
  const [readKeywords, setReadKeywords] = useState({});
  const [subscribedKeywords, setSubscribedKeywords] = useState([]);
  const [newKeyword, setNewKeyword] = useState('');

  // 1. 데이터 로드 로직
  useEffect(() => {
    const fetchUserData = async () => {
      try {
        const id = login_id || 'test_user'; 
        // const response = await axios.get(`YOUR_BACKEND_URL/users/${id}`); 
        // const data = response.data;
        const data = MOCK_USER_DATA; 

        setUserData(data);
        setTargetScores(data.read_categories || {});
        setReadKeywords(data.read_keywords || {});
        setSubscribedKeywords(data.subscribed_keywords || []);
        setLoading(false);
      } catch (error) {
        setUserData(MOCK_USER_DATA);
        setLoading(false);
      }
    };
    fetchUserData();
  }, [login_id]);

  useEffect(() => {
    if (!loading) {
      const timer = setTimeout(() => setIsActive(true), 100);
      return () => clearTimeout(timer);
    }
  }, [loading]);

  const dynamicLimit = useMemo(() => {
    const values = Object.values(targetScores);
    return values.length > 0 ? Math.max(...values) + 10 : 100;
  }, [targetScores]);

  const getCoordinates = (scores, limit, active) => {
    const center = 100, radius = 60;
    return CATEGORIES.map((label, i) => {
      const angle = (Math.PI / 3) * i - Math.PI / 2;
      const scoreRatio = active ? (scores[label] || 0) / limit : 0;
      return `${center + radius * scoreRatio * Math.cos(angle)},${center + radius * scoreRatio * Math.sin(angle)}`;
    }).join(' ');
  };

  const updateKeywordsOnServer = async (newList) => {
    try {
      await axios.patch(`YOUR_BACKEND_URL/users/${login_id}`, { subscribed_keywords: newList });
    } catch (error) { console.error(error); }
  };

  const handleDeleteKeyword = (target) => {
    const newList = subscribedKeywords.filter(k => k !== target);
    setSubscribedKeywords(newList);
    updateKeywordsOnServer(newList);
  };

  const handleAddKeyword = () => {
    if (newKeyword.trim() && !subscribedKeywords.includes(newKeyword)) {
      const newList = [...subscribedKeywords, newKeyword.trim()];
      setSubscribedKeywords(newList);
      updateKeywordsOnServer(newList);
      setNewKeyword('');
    }
  };

  if (loading) return <div className="loading-state">데이터 분석 중...</div>;

  return (
    <div className="mypage-container">
      <Header
        headerTop="off" headerMain="on" headerBottom="off"
        leftChild={<Logo />}
        rightChild={<UserMenu />}
      />

      <main className="mypage-main">
        <section className="profile-header">
          <h1 className="text-xl font-bold">{userData?.user_real_name} 님의 인사이트</h1>
          <p className="text-gray-400 text-sm mt-1">{userData?.email}</p>
        </section>

        <div className="content-wrapper">
          {/* 레이더 차트 */}
          <section className="info-section">
            <h3 className="section-title">나의 관심 카테고리</h3>
            <div className="chart-container" style={{ display: 'flex', justifyContent: 'center' }}>
              <div style={{ width: '500px', height: '350px' }}>
                <svg viewBox="-20 10 250 180" className="w-full h-full" style={{ overflow: 'visible' }}>
                  {[0.2, 0.4, 0.6, 0.8, 1].map((r) => (
                    <polygon key={r} points={getCoordinates({ '정치': dynamicLimit * r, '경제': dynamicLimit * r, '사회': dynamicLimit * r, '생활/문화': dynamicLimit * r, 'IT/과학': dynamicLimit * r, '세계': dynamicLimit * r }, dynamicLimit, true)} fill="none" stroke="#f0f0f0" strokeWidth="1" />
                  ))}
                  <polygon 
                    points={getCoordinates(targetScores, dynamicLimit, isActive)} 
                    fill="#0496f721" 
                    stroke="#000000ff" 
                    strokeWidth="0.1" 
                    strokeLinejoin="round"
                    style={{ transition: 'points 1.2s cubic-bezier(0.34, 1.56, 0.64, 1)' }}
                  />
                  {CATEGORIES.map((label, i) => {
                    const angle = (Math.PI / 3) * i - Math.PI / 2;
                    const x = 100 + 85 * Math.cos(angle);
                    const y = 100 + 85 * Math.sin(angle);
                    return <text key={label} x={x} y={y} textAnchor="middle" fontSize="10" fill="#4b5563" fontWeight="bold" dominantBaseline="middle">{label}</text>
                  })}
                </svg>
              </div>
            </div>
          </section>

          {/* 바 그래프 섹션 (마우스 오버 툴팁 적용) */}
          <section className="info-section">
            <h3 className="section-title">관심 키워드 Top 10</h3>
            <div style={{ display: 'flex', alignItems: 'flex-end', justifyContent: 'space-around', height: '180px', padding: '100px 0' }}>
              {Object.entries(readKeywords).sort(([, a], [, b]) => b - a).slice(0, 10).map(([keyword, count], index) => (
                <div key={keyword} className="bar-wrapper" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', width: '15%', position: 'relative' }}>
                  
                  {/* 💡 툴팁: 평소엔 숨겨져 있다가 .bar-wrapper hover 시 등장 */}
                  <div className="bar-tooltip" style={{
                    position: 'absolute',
                    top: '-30px',
                    backgroundColor: '#1e293b',
                    color: 'white',
                    padding: '4px 8px',
                    fontSize: '10px',
                    fontWeight: 'bold',
                    opacity: 0,
                    transition: 'opacity 0.2s ease',
                    pointerEvents: 'none',
                    whiteSpace: 'nowrap'
                  }}>
                    {count}회 읽음
                  </div>
                  
                  <div style={{ width: '80%', backgroundColor: '#ffffffff', height: '100px', position: 'relative',  overflow: 'hidden', cursor: 'pointer' }}>
                    <div className="bar-fill-element" style={{ 
                        position: 'absolute', bottom: 0, left: 0, right: 0, backgroundColor: '#0095f6', 
                        height: isActive ? `${(count / (Math.max(...Object.values(readKeywords)) + 5)) * 100}%` : '0%',
                        transition: `height 1s cubic-bezier(0.17, 0.67, 0.83, 0.67) ${index * 0.1}s, background-color 0.2s ease` 
                    }} />
                  </div>
                  <span style={{ fontSize: '10px', marginTop: '8px', fontWeight: '600', color: '#475569', textAlign: 'center' }}>{keyword}</span>
                </div>
              ))}
            </div>
          </section>
        </div>

        {/* 구독 키워드 편집 섹션 (기존 유지) */}
        <section className='keyword-listname' style={{ marginTop: '20px', padding: '20px', backgroundColor: 'white', border: '5px solid #e5e7eb', borderRadius: '12px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
            <span className='keyword-sub' style={{ fontWeight: 'bold', fontSize: '18px' }}>구독 중인 키워드</span>
            <Button text={isEditMode ? "저장" : "관리"} color={isEditMode ? "#111" : "transparent"} textColor={isEditMode ? "white" : "#6b7280"} fontSize="12px" width="70px" height="32px" onClick={() => setIsEditMode(!isEditMode)} />
          </div>
          <div className="keyword-list" style={{ display: 'flex', flexWrap: 'wrap', gap: '10px' }}>
            {subscribedKeywords.map(tag => (
              <span key={tag} className="keyword-tag" style={{ color: '#0095f6', backgroundColor: isEditMode ? '#f0f9ff' : 'transparent', padding: isEditMode ? '4px 12px' : '0', borderRadius: '20px', border: isEditMode ? '1px solid #bae6fd' : 'none', display: 'flex', alignItems: 'center' }}>
                #{tag}
                {isEditMode && <span onClick={() => handleDeleteKeyword(tag)} style={{ marginLeft: '8px', color: '#ef4444', cursor: 'pointer', fontWeight: 'bold' }}>×</span>}
              </span>
            ))}
          </div>
        </section>
      </main>
    </div>
  );
};

export default MyPage;
