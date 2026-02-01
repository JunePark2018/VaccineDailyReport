import React, { useState, useEffect, useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
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
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const MyPage = () => {
  const { login_id } = useParams();
  const navigate = useNavigate();
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
        const response = await axios.get(`${API_BASE_URL}/users/${login_id}/dashboard`);
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
      // Show error message from backend if available
      const errorMessage = error.response?.data?.detail || "서버 업데이트에 실패했습니다.";
      alert(errorMessage);
      // Revert to previous state by refetching
      try {
        const response = await axios.get(`${API_BASE_URL}/users/${login_id}/dashboard`);
        setUserData(response.data);
      } catch (refetchError) {
        console.error("데이터 재로딩 실패:", refetchError);
      }
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

  // 관심 키워드 통계 초기화 핸들러
  const handleResetKeywords = async () => {
    if (!window.confirm('모든 관심 키워드 기록을 초기화하시겠습니까?\n이 작업은 되돌릴 수 없습니다.')) {
      return;
    }

    try {
      const encodedLoginId = encodeURIComponent(login_id);
      const apiUrl = `${API_BASE_URL}/users/${encodedLoginId}/keywords/stats`;
      console.log('Calling API:', apiUrl);
      const response = await axios.delete(apiUrl);
      console.log('Reset response:', response.data);
      // 성공 시 UI 업데이트
      setUserData({ ...userData, read_keywords: {} });
      alert('관심 키워드가 초기화되었습니다.');
    } catch (error) {
      console.error("관심 키워드 초기화 실패:", error);
      console.error("Error response:", error.response);
      alert(`초기화에 실패했습니다. 다시 시도해주세요.\n${error.response?.data?.detail || error.message}`);
    }
  };

  // 회원탈퇴 핸들러
  const handleDeleteAccount = async () => {
    // 첫 번째 확인
    if (!window.confirm('정말로 회원탈퇴 하시겠습니까?')) {
      return;
    }

    // 두 번째 확인 (강력한 경고)
    if (!window.confirm('⚠️ 경고 ⚠️\n\n회원탈퇴 시 모든 데이터가 영구적으로 삭제되며 복구할 수 없습니다.\n\n- 조회 기록\n- 좋아요/싫어요\n- 관심 키워드 통계\n- 구독 정보\n\n정말로 계속하시겠습니까?')) {
      return;
    }

    try {
      const encodedLoginId = encodeURIComponent(login_id);
      await axios.delete(`${API_BASE_URL}/users/${encodedLoginId}`);

      // 성공 시 로그아웃 처리
      localStorage.removeItem('isLoggedIn');
      localStorage.removeItem('user_id');
      localStorage.removeItem('login_id');
      localStorage.removeItem('username');

      alert('회원탈퇴가 완료되었습니다.');
      navigate('/');
      window.location.reload(); // 완전한 로그아웃을 위해  리로드
    } catch (error) {
      console.error("회원탈퇴 실패:", error);
      alert(`회원탈퇴에 실패했습니다.\n${error.response?.data?.detail || error.message}`);
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
          <h1 className="text-xl font-bold">{userData?.username} 님의 인사이트</h1>
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
            onReset={handleResetKeywords}
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

        {/* 회원탈퇴 버튼 */}
        <div style={{
          textAlign: 'center',
          marginTop: '60px',
          paddingBottom: '40px',
          borderTop: '1px solid #e5e7eb',
          paddingTop: '20px'
        }}>
          <button
            onClick={handleDeleteAccount}
            style={{
              backgroundColor: 'white',
              border: '1px solid #e5e7eb',
              color: '#6b7280',
              fontSize: '12px',
              cursor: 'pointer',
              padding: '8px 16px',
              fontWeight: '400',
              borderRadius: '6px',
              transition: 'all 0.2s ease',
              fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
            }}
            onMouseOver={(e) => {
              e.target.style.backgroundColor = '#fef2f2';
              e.target.style.borderColor = '#fca5a5';
              e.target.style.color = '#dc2626';
            }}
            onMouseOut={(e) => {
              e.target.style.backgroundColor = 'white';
              e.target.style.borderColor = '#e5e7eb';
              e.target.style.color = '#6b7280';
            }}
          >
            회원탈퇴
          </button>
        </div>

        {/* 3. 구독 키워드 관리 컴포넌트 */}

      </main>
    </div>
  );
};

export default MyPage; // 💡 여기서 내보내기를 해줘야 다른 곳에서 import 가능합니다!