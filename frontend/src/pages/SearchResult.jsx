import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { useLocation } from 'react-router-dom';
import "./SearchResult.css";
import Header from "../components/Header";
import Logo from "../components/Logo";
import UserMenu from "../components/UserMenu";
import Searchbar from "../components/Searchbar";
import Button from "../components/Button";

export default function SearchResult() {
    const location = useLocation();
    const [searchTerm, setSearchTerm] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const [searchData, setSearchData] = useState(null);
    const [visibleNewsCount, setVisibleNewsCount] = useState(3);
    const [hasDbResult, setHasDbResult] = useState(false);

    // 검색 실행 함수 (통합 검색 API 연동)
    const handleSearch = useCallback(async (keyword) => {
        if (!keyword) return;
        setSearchTerm(keyword);
        setIsLoading(true);
        setSearchData(null);
        setHasDbResult(false);
        setVisibleNewsCount(3);

        try {
            const res = await axios.get(`http://localhost:8000/api/comprehensive-search`, {
                params: { keyword: keyword }
            });

            const data = res.data;
            setSearchData(data);

            // DB 결과 존재 여부 확인 (AI 요약, 핫토픽, 관련기사 중 하나라도 있으면 성공)
            // 위키만 있어도 성공으로 간주
            const dbExists = (data.definition) ||
                (data.ai_summaries && data.ai_summaries.issues && data.ai_summaries.issues.length > 0) ||
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
            <div className="Header_Container">
                <Header leftChild={<Logo />} midChild={<Searchbar maxWidth="600px" />} rightChild={<UserMenu />} headerBottom="on" />
            </div>

            <div className="Content_Section">
                <div className="SearchResult_Content">
                    <div className="Title_Wrapper">
                        <h3 className="AI_Title">
                            {isLoading ? `'${searchTerm}' 를 조회중입니다...` : `'${searchTerm}' 검색 결과`}
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
                                    {/* --- [왼쪽 섹션] 위키 + AI요약 + 관련기사 --- */}
                                    <div className="AI_Left_Section fade-in">

                                        {/* 1. 위키피디아 (최상단) */}
                                        {searchData.definition && (
                                            <div className="Wiki_Section" style={{
                                                marginBottom: '30px',
                                                padding: '25px',
                                                borderRadius: '4px',
                                                background: '#fcfcfc',
                                                border: '1px solid #eee'
                                            }}>
                                                <div className="Wiki_Header" style={{ marginBottom: '15px' }}>
                                                    <h2 style={{ fontSize: '1.2rem', margin: 0, color: '#333' }}>
                                                        {searchData.definition.title}에 대한 정보
                                                    </h2>
                                                </div>
                                                <p className="Wiki_Summary" style={{ fontSize: '1rem', lineHeight: '1.6', color: '#333', whiteSpace: 'pre-wrap' }}>
                                                    {searchData.definition.summary}
                                                </p>
                                            </div>
                                        )}

                                        {/* 2. AI 요약 (Analysis_Text_Section) - Issue가 있을 때만 표시 */}
                                        {searchData.ai_summaries && searchData.ai_summaries.issues && searchData.ai_summaries.issues.length > 0 && (
                                            <div className="Analysis_Text_Section">
                                                <h4>
                                                    해당 키워드의 최근 작성된 AI기사
                                                </h4>

                                                <div className="Analysis_Contents">
                                                    {/* LLM 분석 텍스트 표시 */}
                                                    {searchData.ai_summaries.analysis && (
                                                        <div className="LLM_Analysis_Text" style={{ marginBottom: '20px', whiteSpace: 'pre-wrap', lineHeight: '1.6' }}>
                                                            {searchData.ai_summaries.analysis}
                                                        </div>
                                                    )}

                                                    {/* 이슈 리스트 표시 */}
                                                    {searchData.ai_summaries.issues.map(issue => (
                                                        <div key={issue.id} className="Summary_Item">
                                                            <strong>• {issue.title}</strong>
                                                            <p>{issue.contents}</p>
                                                        </div>
                                                    ))}
                                                </div>
                                            </div>
                                        )}
                                        {/* Issue가 없으면 섹션 자체를 렌더링하지 않음 */}


                                        {/* 3. 관련기사 리스트 (Related_News_Section) - 데이터 있을 때만 표시 */}
                                        {searchData.articles && searchData.articles.length > 0 && (
                                            <div className="Related_News_Section" style={{ marginTop: '40px', width: '100%', textAlign: 'left' }}>
                                                <h4>관련기사</h4>
                                                <ul className="News_List">
                                                    {searchData.articles.slice(0, visibleNewsCount).map(item => (
                                                        <li key={item.id} onClick={() => window.open(item.url)}>
                                                            <span>[{item.company_name}]</span> {item.title}
                                                        </li>
                                                    ))}
                                                </ul>
                                                <div style={{ textAlign: 'center', marginTop: '20px', display: 'flex', gap: '10px', justifyContent: 'center' }}>
                                                    {visibleNewsCount < searchData.articles.length && (
                                                        <Button
                                                            text="더보기 ▼"
                                                            onClick={handleLoadMore}
                                                            className="Action_Button"
                                                        />
                                                    )}
                                                    {visibleNewsCount > 3 && (
                                                        <Button
                                                            text="접기 ▲"
                                                            onClick={handleCollapse}
                                                            className="Action_Button"
                                                        />
                                                    )}
                                                </div>
                                            </div>
                                        )}
                                    </div>

                                    {/* 구분선: Hot Topic이 있을 때만 표시 */}
                                    {searchData.hot_topics && searchData.hot_topics.length > 0 && (
                                        <div className="Section_Divider"></div>
                                    )}

                                    {/* --- [오른쪽 섹션] 핫토픽 - 데이터 있을 때만 표시 --- */}
                                    {searchData.hot_topics && searchData.hot_topics.length > 0 && (
                                        <div className="AI_Right_Section fade-in" style={{ animationDelay: '0.1s' }}>
                                            <div className="Hot_Topic_Section" style={{ marginTop: '-10px' }}>
                                                <p style={{ fontWeight: 'bold', marginBottom: '10px', textAlign: 'left' }}>Hot Topic!</p>
                                                <div className="Topic_Cards" style={{ gridTemplateColumns: 'repeat(2, 1fr)' }}>
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
            </div>
        </div>
    );
}
