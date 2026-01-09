import React, { useState, useEffect, useMemo } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';

// 공통 컴포넌트
import Logo from '../components/Logo';
import UserMenu from '../components/UserMenu';
import Header from '../components/Header';

import CategoryRadarChart from '../components/CategoryRadarChart';
import KeywordBarChart from '../components/KeywordBarChart';
import SubscribedKeywords from '../components/SubscribedKeywords';
import './MyPage.css';

const MOCK_USER_DATA = {
  user_real_name: "홍길동",
  email: "gildong@example.com",
  read_categories: { '정치': 85, '경제': 45, '사회': 95, '생활/문화': 60, 'IT/과학': 100, '세계': 30 },
  read_keywords: { '반도체': 15, '금리': 10, '인공지능': 25, '나스닥': 8, '재건축': 12, '우크라이나': 5, '이재명': 100, '윤석열': 300, 'AI': 55, '박나래': 44 },
  subscribed_keywords: ['AI', '재테크', '건강']
};

const MyPage = () => {
  const { login_id } = useParams();
  const [loading, setLoading] = useState(true);
  const [userData, setUserData] = useState(null);
  const [isActive, setIsActive] = useState(false);
  const [isEditMode, setIsEditMode] = useState(false);

  // 데이터 로딩
  useEffect(() => {
    const fetchUserData = async () => {
      try {
        const id = login_id || 'test_user';
        // const response = await axios.get(`YOUR_BACKEND_URL/users/${id}`);
        // setUserData(response.data);
        setUserData(MOCK_USER_DATA); 
      } catch (error) {
        setUserData(MOCK_USER_DATA);
      } finally {
        setLoading(false);
      }
    };
    fetchUserData();
  }, [login_id]);

  // 애니메이션 트리거
  useEffect(() => {
    if (!loading) {
      const timer = setTimeout(() => setIsActive(true), 100);
      return () => clearTimeout(timer);
    }
  }, [loading]);

  // 차트 최대치 계산
  const dynamicLimit = useMemo(() => {
    const values = Object.values(userData?.read_categories || {});
    return values.length > 0 ? Math.max(...values) + 10 : 100;
  }, [userData]);

  // 서버 업데이트 로직
  const updateKeywordsOnServer = async (newList) => {
    try {
      await axios.patch(`YOUR_BACKEND_URL/users/${login_id}`, { subscribed_keywords: newList });
    } catch (error) {
      console.error("서버 업데이트 실패:", error);
    }
  };

  // 키워드 삭제 핸들러
  const handleDeleteKeyword = (target) => {
    const newList = userData.subscribed_keywords.filter(k => k !== target);
    setUserData({ ...userData, subscribed_keywords: newList });
    updateKeywordsOnServer(newList);
  };

  // 키워드 추가 핸들러
  const handleAddKeyword = (newKeyword) => {
    if (newKeyword && !userData.subscribed_keywords.includes(newKeyword)) {
      const newList = [...userData.subscribed_keywords, newKeyword];
      setUserData({ ...userData, subscribed_keywords: newList });
      updateKeywordsOnServer(newList);
    }
  };

  if (loading) return <div className="loading-state">데이터 분석 중...</div>;

  return (
    <div className="mypage-container">
      <Header
        headerTop="on" headerMain="on" headerBottom="off"
        leftChild={<Logo />}
        rightChild={<UserMenu />}
      />

      <main className="mypage-main">
        <section className="profile-header">
          <h1 className="text-xl font-bold">{userData?.user_real_name} 님의 인사이트</h1>
          <p className="text-gray-400 text-sm mt-1">{userData?.email}</p>
        </section>

        <div className="content-wrapper">
          {/* 1. 레이더 차트 컴포넌트 */}
          <CategoryRadarChart 
            targetScores={userData?.read_categories} 
            dynamicLimit={dynamicLimit} 
            isActive={isActive} 
          />

          {/* 2. 바 차트 컴포넌트 */}
         
          
        </div>
        <KeywordBarChart 
          readKeywords={userData?.read_keywords} 
          isActive={isActive} 
        />
         <SubscribedKeywords 
          keywords={userData?.subscribed_keywords}
          isEditMode={isEditMode}
          onToggleEdit={() => setIsEditMode(!isEditMode)}
          onDelete={handleDeleteKeyword}
          onAdd={handleAddKeyword}
        />

        {/* 3. 구독 키워드 관리 컴포넌트 */}

      </main>
    </div>
  );
};

export default MyPage; // 💡 여기서 내보내기를 해줘야 다른 곳에서 import 가능합니다!