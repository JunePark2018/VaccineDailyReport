import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { useLocation } from 'react-router-dom';
import "./SearchResult.css";
import Header from "../components/Header";
import Logo from "../components/Logo";
import UserMenu from "../components/UserMenu";
import Searchbar from "../components/Searchbar";
import Button from "../components/Button";

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
export default function SearchResult() {
    const location = useLocation();
    const [searchTerm, setSearchTerm] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const [searchData, setSearchData] = useState(null);
    const [visibleNewsCount, setVisibleNewsCount] = useState(3);
    const [hasDbResult, setHasDbResult] = useState(false);
    const [expandedIssues, setExpandedIssues] = useState({});
    const [isMobile, setIsMobile] = useState(window.innerWidth <= 768);

    useEffect(() => {
        const handleResize = () => setIsMobile(window.innerWidth <= 768);
        window.addEventListener('resize', handleResize);
        return () => window.removeEventListener('resize', handleResize);
    }, []);

    // ... (existing code)

    const handleSearch = useCallback(async (keyword) => {
        if (!keyword) return;
        setSearchTerm(keyword);
        setIsLoading(true);
        setSearchData(null);
        setHasDbResult(false);
        setVisibleNewsCount(3);

        try {
            const res = await axios.get(`${API_BASE_URL}/api/comprehensive-search`, {
                params: { keyword: keyword }
            });

            const data = res.data;
            setSearchData(data);

            // DB 결과 존재 여부 확인 (AI 요약, 핫토픽, 관련기사 중 하나라도 있으면 성공)
            const dbExists = (data.ai_summaries && data.ai_summaries.issues && data.ai_summaries.issues.length > 0) ||
                (data.hot_topics && data.hot_topics.length > 0) ||
                (data.articles && data.articles.length > 0);

            setHasDbResult(dbExists);

        } catch (error) {
            console.error("검색 중 오류 발생:", error);
            setHasDbResult(false);
        } finally {
            setIsLoading(false);
        }
    }, []);

    useEffect(() => {
        const searchParams = new URLSearchParams(location.search);
        const q = searchParams.get('q');
        if (q) {
            handleSearch(q);
        }
    }, [location.search, handleSearch]);

    // 더보기 버튼 핸들러
    const handleLoadMore = useCallback(() => {
        setVisibleNewsCount(prev => prev + 3);
    }, []);

    // 접기 버튼 핸들러
    const handleCollapse = useCallback(() => {
        setVisibleNewsCount(prev => Math.max(3, prev - 3));
    }, []);

    return (
        <div className="SearchResult_Main">
            <Header
                leftChild={null}
                midChild={<Logo />}
                rightChild={
                    <div style={{ display: 'flex', alignItems: 'center', gap: '5px', justifyContent: 'flex-end', width: 'auto' }}>
                        <div style={{ position: 'relative' }}>
                            <Searchbar className="always-open rounded-search" />
                        </div>
                        <UserMenu className="rounded-user-menu" />
                    </div>
                }
                headerTop="on"
                headerMain="on"
                headerBottom="on"
            />

            <div className="Content_Section">
                <div className="SearchResult_Content">
                    <div className="Title_Wrapper">
                        <h3 className="AI_Title">
                            {isLoading ? (
                                <>
                                    <span>'{searchTerm}'</span>
                                    <span style={{ fontWeight: 'normal', fontSize: '1.1rem', marginLeft: '5px' }}> 을(를) 조회중입니다...</span>
                                </>
                            ) : (
                                <>
                                    <span>'{searchTerm}'</span>
                                    <span style={{ fontWeight: 'normal', fontSize: '1.1rem', marginLeft: '5px' }}> 검색 결과</span>
                                </>
                            )}
                        </h3>
                    </div>

                    <div className="AI_Content_Wrapper">
                        {isLoading ? (
                            <div className="Loading_Container" style={{ width: '100%', minHeight: '200px', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
                                <div className="Loading_Spinner"></div>
                            </div>
                        ) : (
                            hasDbResult && searchData ? (
                                <div style={{ display: 'flex', width: '100%', gap: '40px' }}>
                                    {/* --- [왼쪽 섹션] AI요약 + 관련기사 --- */}
                                    <div className="AI_Left_Section fade-in">

                                        {/* 1. AI 요약 (Analysis_Text_Section) - Issue가 있을 때만 표시 */}
                                        {searchData.ai_summaries && searchData.ai_summaries.issues && searchData.ai_summaries.issues.length > 0 && (
                                            <div className="Analysis_Text_Section" style={{ paddingBottom: '30px' }}>
                                                <h2 className="Section_Title_Main" style={{
                                                    fontSize: '24px',
                                                    fontWeight: '800',
                                                    marginBottom: '25px',
                                                    lineHeight: '1',
                                                    color: '#000'
                                                }}>AI 요약 리포트</h2>

                                                <div className="Analysis_Contents">
                                                    {/* LLM 분석 텍스트 표시 (에러 메시지가 아닐 경우에만 표시) */}
                                                    {searchData.ai_summaries.analysis &&
                                                        !searchData.ai_summaries.analysis.includes("시스템 오류로 인해 AI 요약을 생성할 수 없습니다.") && (
                                                            <div className="LLM_Analysis_Text" style={{
                                                                marginBottom: '25px',
                                                                whiteSpace: 'pre-wrap',
                                                                lineHeight: '1.6',
                                                                fontSize: '15px',
                                                                color: '#333',
                                                                background: '#f9f9f9',
                                                                padding: '20px',
                                                                borderRadius: '5px'
                                                            }}>
                                                                {searchData.ai_summaries.analysis}
                                                            </div>
                                                        )}

                                                    {/* 이슈 리스트 표시 */}
                                                    <div className="Summary_List_Wrapper" style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
                                                        {searchData.ai_summaries.issues.slice(0, 1).map(issue => {
                                                            const isTextLong = issue.contents && issue.contents.length > 300;
                                                            const isExpanded = expandedIssues[issue.id];

                                                            return (
                                                                <div key={issue.id} className="Summary_Item_Modern" style={{ paddingBottom: '15px' }}>
                                                                    <strong style={{ fontSize: '16px', display: 'block', marginBottom: '10px' }}>• {issue.title}</strong>
                                                                    <div className={`Issue_Content_Container ${isExpanded ? 'expanded' : 'collapsed'}`} style={{
                                                                        position: 'relative',
                                                                        maxHeight: isExpanded ? 'none' : '200px',
                                                                        overflow: isExpanded ? 'visible' : 'hidden',
                                                                        transition: 'max-height 0.3s ease-out'
                                                                    }}>
                                                                        <p style={{ fontSize: '14px', color: '#333', margin: 0, whiteSpace: 'pre-wrap', lineHeight: '1.6' }}>
                                                                            {issue.contents}
                                                                        </p>
                                                                        {isTextLong && !isExpanded && (
                                                                            <div className="Fade_Overlay" style={{
                                                                                position: 'absolute',
                                                                                bottom: 0,
                                                                                left: 0,
                                                                                width: '100%',
                                                                                height: '60px',
                                                                                background: 'linear-gradient(to bottom, rgba(255, 255, 255, 0), rgba(255, 255, 255, 1))',
                                                                                pointerEvents: 'none'
                                                                            }}></div>
                                                                        )}
                                                                    </div>
                                                                    {isTextLong && (
                                                                        <div style={{
                                                                            textAlign: 'center',
                                                                            marginTop: isExpanded ? '0' : '-10px',
                                                                            position: isExpanded ? 'sticky' : 'relative',
                                                                            bottom: isExpanded ? (isMobile ? '80px' : '30px') : 'auto',
                                                                            zIndex: 100,
                                                                            width: '100%',
                                                                            pointerEvents: 'none',
                                                                            display: 'flex',
                                                                            justifyContent: 'center'
                                                                        }}>
                                                                            <div style={{
                                                                                display: 'inline-block',
                                                                                pointerEvents: 'auto',
                                                                                background: 'rgba(255, 255, 255, 0.95)',
                                                                                padding: '10px 20px',
                                                                                borderRadius: '30px',
                                                                                boxShadow: '0 4px 15px rgba(0,0,0,0.15)',
                                                                                border: '1px solid #eee'
                                                                            }}>
                                                                                <button
                                                                                    onClick={() => setExpandedIssues(prev => ({ ...prev, [issue.id]: !isExpanded }))}
                                                                                    className="show-more-button link-style"
                                                                                    style={{
                                                                                        background: 'none',
                                                                                        border: 'none',
                                                                                        color: '#5f6368',
                                                                                        cursor: 'pointer',
                                                                                        fontSize: '14px',
                                                                                        fontWeight: '600',
                                                                                        padding: 0,
                                                                                        display: 'flex',
                                                                                        alignItems: 'center',
                                                                                        gap: '5px'
                                                                                    }}
                                                                                >
                                                                                    {isExpanded ? "접기 ▲" : "펼쳐보기 ▼"}
                                                                                </button>
                                                                            </div>
                                                                        </div>
                                                                    )}
                                                                </div>
                                                            );
                                                        })}
                                                    </div>
                                                </div>
                                            </div>
                                        )}

                                        {/* 2. 관련기사 리스트 (Related_News_Section) - 데이터 있을 때만 표시 */}
                                        {searchData.articles && searchData.articles.length > 0 && (
                                            <div className="Related_News_Section" style={{ marginTop: '40px', width: '100%', textAlign: 'left' }}>
                                                <h2 style={{
                                                    fontSize: '24px',
                                                    fontWeight: '800',
                                                    marginBottom: '25px',
                                                    lineHeight: '1',
                                                    color: '#000'
                                                }}>관련 기사</h2>
                                                <ul className="News_List">
                                                    {searchData.articles.slice(0, visibleNewsCount).map(item => (
                                                        <li key={item.id} onClick={() => window.open(item.url)} style={{ fontSize: '15px' }}>
                                                            <span style={{ color: '#f33a3aff', fontWeight: 'bold' }}>[{item.company_name}]</span> {item.title}
                                                        </li>
                                                    ))}
                                                </ul>
                                                <div style={{ textAlign: 'center', marginTop: '30px', display: 'flex', gap: '15px', justifyContent: 'center' }}>
                                                    {visibleNewsCount < searchData.articles.length && (
                                                        <div style={{
                                                            display: 'inline-block',
                                                            background: '#fff',
                                                            padding: '10px 25px',
                                                            borderRadius: '30px',
                                                            boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
                                                            border: '1px solid #eee',
                                                            cursor: 'pointer',
                                                            transition: 'all 0.2s'
                                                        }}
                                                            onClick={handleLoadMore}
                                                            onMouseEnter={(e) => { e.currentTarget.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)'; e.currentTarget.style.transform = 'translateY(-2px)'; }}
                                                            onMouseLeave={(e) => { e.currentTarget.style.boxShadow = '0 2px 8px rgba(0,0,0,0.1)'; e.currentTarget.style.transform = 'none'; }}
                                                        >
                                                            <span style={{ fontSize: '14px', fontWeight: '600', color: '#5f6368', display: 'flex', alignItems: 'center', gap: '5px' }}>
                                                                더보기 ▼
                                                            </span>
                                                        </div>
                                                    )}
                                                    {visibleNewsCount > 3 && (
                                                        <div style={{
                                                            display: 'inline-block',
                                                            background: '#fff',
                                                            padding: '10px 25px',
                                                            borderRadius: '30px',
                                                            boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
                                                            border: '1px solid #eee',
                                                            cursor: 'pointer',
                                                            transition: 'all 0.2s'
                                                        }}
                                                            onClick={handleCollapse}
                                                            onMouseEnter={(e) => { e.currentTarget.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)'; e.currentTarget.style.transform = 'translateY(-2px)'; }}
                                                            onMouseLeave={(e) => { e.currentTarget.style.boxShadow = '0 2px 8px rgba(0,0,0,0.1)'; e.currentTarget.style.transform = 'none'; }}
                                                        >
                                                            <span style={{ fontSize: '14px', fontWeight: '600', color: '#5f6368', display: 'flex', alignItems: 'center', gap: '5px' }}>
                                                                접기 ▲
                                                            </span>
                                                        </div>
                                                    )}
                                                </div>
                                            </div>
                                        )}
                                    </div>

                                    {/* --- [오른쪽 섹션] 핫토픽 - 데이터 있을 때만 표시 --- */}
                                    {searchData.hot_topics && searchData.hot_topics.length > 0 && (
                                        <div className="AI_Right_Section fade-in" style={{ animationDelay: '0.1s' }}>
                                            <div className="Hot_Topic_Section" style={{ marginTop: '-10px' }}>
                                                <h2 style={{
                                                    fontSize: '24px',
                                                    fontWeight: '800',
                                                    marginBottom: '20px',
                                                    lineHeight: '1',
                                                    color: '#000'
                                                }}>핫토픽!</h2>
                                                <div className="Topic_Cards" style={{ gridTemplateColumns: '1fr' }}>
                                                    {searchData.hot_topics.slice(0, 4).map(item => (
                                                        <div
                                                            key={item.id}
                                                            className="Topic_Card"
                                                            onClick={() => window.open(item.url)}
                                                        >
                                                            <div className="Image_Wrapper">
                                                                <img
                                                                    src={item.img_urls[0]}
                                                                    alt={item.title}
                                                                    onError={(e) => {
                                                                        e.target.onerror = null;
                                                                        e.target.src = 'https://via.placeholder.com/400x300?text=No+Image';
                                                                    }}
                                                                />
                                                            </div>
                                                            <div className="Card_Text">{item.title}</div>
                                                        </div>
                                                    ))}
                                                </div>
                                            </div>
                                        </div>
                                    )}
                                </div>
                            ) : (
                                <div className="No_Result_Container">
                                    <h2>'{searchTerm}'에 대한 검색 결과가 없습니다.</h2>
                                    <p>데이터베이스 내에 일치하는 정보가 존재하지 않습니다.</p>
                                </div>
                            )
                        )}
                    </div>
                </div>
            </div >
        </div >
    );
}
