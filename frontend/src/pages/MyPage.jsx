import React, { useState, useEffect, useMemo } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';

// 공통 컴포넌트
import Logo from '../components/Logo';
import UserMenu from '../components/UserMenu';
import Header from '../components/Header';
import Searchbar from '../components/Searchbar';

import CategoryRadarChart from '../components/CategoryRadarChart';
import KeywordBarChart from '../components/KeywordBarChart';
import SubscribedKeywords from '../components/SubscribedKeywords';
import './MyPage.css';

// MOCK_USER_DATA 제거

const MyPage = () => {
  const { login_id } = useParams();
  const [loading, setLoading] = useState(true);
  const [userData, setUserData] = useState(null);
  const [isActive, setIsActive] = useState(false);
  const [isEditMode, setIsEditMode] = useState(false);
  const MY_CATEGORIES = ['정치', '경제', '사회', 'IT/과학', '세계'];

  // 데이터 로딩
  useEffect(() => {
    const fetchUserData = async () => {
      try {
        if (!login_id) {
          setLoading(false);
          return;
        }
        const response = await axios.get(`http://localhost:8000/users/${login_id}/dashboard`);
        setUserData(response.data);
      } catch (error) {
        console.error("데이터 로딩 실패:", error);
        // Fallback for demo if needed, or just let it render empty
        setUserData(null);
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
      await axios.put(`http://localhost:8000/users/${login_id}`, { subscribed_keywords: newList });
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
        headerTop="on" headerMain="on" headerBottom="on"
        leftChild={<Logo />}
        midChild={null}
        rightChild={
          <div style={{ display: 'flex', alignItems: 'center', gap: '0', justifyContent: 'flex-end', width: 'auto' }}>
            <div style={{ position: 'relative' }}>
              <Searchbar className="always-open" />
            </div>
            <UserMenu />
          </div>
        }
      />

      <main className="mypage-main">
        <section className="profile-header">
          <h1 className="text-xl font-bold">{userData?.user_real_name} 님의 인사이트</h1>
          <p className="text-gray-400 text-sm mt-1">{userData?.email}</p>
        </section>

        <div className="content-wrapper">
          {/* 1. 레이더 차트 컴포넌트 */}
          <CategoryRadarChart
            title="나의 관심 카테고리"
            labels={MY_CATEGORIES}
            targetScores={userData?.read_categories} // { '정치': 7, '경제': 4 ... }
            dynamicLimit={dynamicLimit}
            isActive={isActive}
          />
          <KeywordBarChart
            readKeywords={userData?.read_keywords}
            isActive={isActive}
          />
          {/* 2. 바 차트 컴포넌트 */}


        </div>

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