import React, { useState, useEffect, useMemo, useCallback } from 'react';
import axios from 'axios';
import { useLocation } from 'react-router-dom';
import "./SearchResult.css";
import Header from "../components/Header";
import Logo from "../components/Logo";
import UserMenu from "../components/UserMenu";
import Searchbar from "../components/Searchbar";
import TypewriterText from "../components/TypewriterText";
import Button from "../components/Button";

export default function SearchResult() {
    const location = useLocation();
    const [searchTerm, setSearchTerm] = useState("뉴스");
    const [isLoading, setIsLoading] = useState(false);
    const [articles, setArticles] = useState([]);
    const [aiSummary, setAiSummary] = useState(""); // AI 요약 상태 추가
    const [visibleNewsCount, setVisibleNewsCount] = useState(3);

    const [headerDone, setHeaderDone] = useState(false);
    const [contentDone, setContentDone] = useState(false);
    const [hotTopicDone, setHotTopicDone] = useState(false);

    // 검색 실행 함수 (실제 백엔드 연동)
    const handleSearch = useCallback(async (keyword) => {
        setSearchTerm(keyword);
        setIsLoading(true);
        setVisibleNewsCount(3); // 검색 시 초기화
        setAiSummary(""); // 요약 초기화

        // 애니메이션 상태 초기화
        setHeaderDone(false);
        setContentDone(false);
        setHotTopicDone(false);

        try {
            // 1. 기사 검색
            const articleRes = await axios.get(`http://localhost:8000/articles/search`, {
                params: {
                    keyword: keyword,
                    limit: 50
                }
            });

            // [Mock] view_count가 없으므로 임의로 생성 (500~3500)
            const augmentedData = articleRes.data.map(item => ({
                ...item,
                view_count: item.view_count || Math.floor(Math.random() * 3000) + 500
            }));

            setArticles(augmentedData);

            // 2. 이슈(AI 요약) 검색 (search.py 참고)
            const issueRes = await axios.get(`http://localhost:8000/issues/search`, {
                params: {
                    keyword: keyword,
                    limit: 1
                }
            });

            if (issueRes.data && issueRes.data.length > 0) {
                setAiSummary(issueRes.data[0].contents);
            } else {
                setAiSummary("해당 키워드에 대한 AI 분석 리포트가 아직 생성되지 않았습니다.");
            }

        } catch (error) {
            console.error("검색 중 오류 발생:", error);
            setArticles([]);
            setAiSummary("데이터를 불러오는 중 오류가 발생했습니다.");
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

    // Hot Topic 필터링: 이미지 있고 & 조회수 1000 이상 (Memoized)
    const hotTopicArticles = useMemo(() => {
        return articles.filter(item =>
            (item.img_urls && item.img_urls.length > 0) && item.view_count >= 1000
        );
    }, [articles]);

    useEffect(() => {
        if (!isLoading && contentDone && hotTopicArticles.length === 0) {
            setHotTopicDone(true);
        }
    }, [isLoading, contentDone, hotTopicArticles.length]);

    return (
        <div className="SearchResult_Main">
            <div className="Header_Container">
                <Header leftChild={<Logo />} midChild={<Searchbar maxWidth="600px" />} rightChild={<UserMenu />} headerBottom="on" />
            </div>

            <div className="Content_Section">
                <div className="Searchbar_Wrapper">

                </div>

                {/* 데이터가 있을 때 항상 표시 */}
                <div className="SearchResult_AI">
                    <div className="Title_Wrapper">
                        <h3 className="AI_Title">
                            {isLoading ? `'${searchTerm}' 검색 결과` : `'${searchTerm}' 검색 결과`}
                        </h3>

                    </div>

                    <div className="AI_Content_Wrapper" style={{ flexDirection: 'column' }}>
                        {!isLoading && articles.length === 0 ? (
                            <div className="No_Result_Container">
                                <h2>'{searchTerm}'에 대한 검색 결과가 없습니다.</h2>
                                <p>단어의 철자가 정확한지 확인해 주세요.</p>
                            </div>
                        ) : (
                            <>
                                <div style={{ display: 'flex', width: '100%' }}>
                                    <div className="AI_Left_Section">
                                        <div className="Analysis_Text_Section">
                                            <h4>
                                                {isLoading ? (
                                                    <TypewriterText text={`${searchTerm} 검색 중...`} delay={50} />
                                                ) : (
                                                    <TypewriterText
                                                        key={`header-${searchTerm}`}
                                                        text={`AI가 탐색한 ${articles.length}개의 기사 요약입니다.`}
                                                        delay={50}
                                                        onComplete={() => setHeaderDone(true)}
                                                    />
                                                )}
                                            </h4>
                                            <div className="Analysis_Contents">
                                                <div className={headerDone ? "fade-in" : "hidden"} onAnimationEnd={() => setContentDone(true)}>
                                                    {aiSummary}
                                                </div>
                                            </div>
                                        </div>



                                        <div className={`Related_News_Section ${!isLoading && hotTopicDone ? 'fade-in' : 'hidden'}`} style={{ marginTop: '40px', width: '100%', textAlign: 'left' }}>
                                            <h4>관련기사</h4>
                                            <ul className="News_List">
                                                {isLoading ? [1, 2, 3].map(i => (
                                                    <li key={i} className="skeleton_line"></li>
                                                )) : articles.slice(0, visibleNewsCount).map(item => (
                                                    <li key={item.id} onClick={() => window.open(item.url)}>
                                                        <span>[{item.company_name}]</span> {item.title}
                                                    </li>
                                                ))}
                                            </ul>
                                            {!isLoading && articles.length > 0 && (
                                                <div style={{ textAlign: 'center', marginTop: '20px', display: 'flex', gap: '10px', justifyContent: 'center' }}>
                                                    {visibleNewsCount < articles.length && (
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
                                            )}
                                        </div>
                                    </div>

                                    {(isLoading || hotTopicArticles.length > 0) && (
                                        <>
                                            <div className="Section_Divider"></div>
                                            <div className={`AI_Right_Section ${!isLoading && contentDone ? 'fade-in' : 'hidden'}`} onAnimationEnd={() => setHotTopicDone(true)}>
                                                <div className="Hot_Topic_Section">
                                                    <p style={{ fontWeight: 'bold', marginBottom: '10px', textAlign: 'left' }}>Hot Topic!</p>
                                                    <div className="Topic_Cards">
                                                        {isLoading ? [1, 2, 3, 4].map(i => (
                                                            <div key={i} className="Topic_Card skeleton"></div>
                                                        )) : hotTopicArticles.slice(0, 4).map(item => (
                                                            <div
                                                                key={item.id}
                                                                className="Topic_Card"
                                                                onClick={() => window.open(item.url)}
                                                                style={{ cursor: 'pointer' }}
                                                            >
                                                                <img
                                                                    src={item.img_urls[0]}
                                                                    alt="news"
                                                                    onError={(e) => {
                                                                        e.target.onerror = null; // Prevent infinite loop
                                                                        e.target.src = 'https://via.placeholder.com/400x300?text=No+Image';
                                                                    }}
                                                                />
                                                                <div className="Card_Text">{item.title}</div>
                                                            </div>
                                                        ))}
                                                    </div>
                                                </div>
                                            </div>
                                        </>
                                    )}
                                </div>
                            </>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}