import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import "./SearchResult.css";
import Header from "../components/Header";
import Logo from "../components/Logo";
import UserMenu from "../components/UserMenu";
import Searchbar from "../components/Searchbar";
import TypewriterText from "../components/TypewriterText";

export default function SearchResult() {
    const [searchParams] = useSearchParams();
    const query = searchParams.get('q');

    // --- 1. 가 데이터를 초기 상태로 설정 ---
    const [searchTerm, setSearchTerm] = useState(query || "뉴스"); // 초기 검색어 설정
    const [isLoading, setIsLoading] = useState(false);
    const [articles, setArticles] = useState([
        {
            id: 0,
            title: "'뉴스' 관련 AI 통합 분석 보고서",
            contents: "전 세계 뉴스 데이터를 실시간으로 분석한 결과, 디지털 미디어의 소비 패턴이 급격히 변화하고 있습니다. 특히 AI 기반의 뉴스 큐레이션 서비스가 사용자들 사이에서 큰 인기를 끌고 있으며, 전통적인 언론사들 또한 기술 도입을 서두르고 있는 추세입니다.",
            category: "미디어",
            url: "https://example.com",
            company_name: "백신일보",
            img_urls: ["https://images.unsplash.com/photo-1504711432869-0df30d7eaf4d?q=80&w=500"], // 실제 이미지 경로
            time: new Date().toISOString(),
            author: "AI 리포터"
        },
        {
            id: 1,
            title: "미디어 시장의 미래 전망",
            contents: "향후 5년간 뉴스 콘텐츠 시장은...",
            company_name: "빅신테크",
            img_urls: ["https://images.unsplash.com/photo-1495020689067-958852a7765e?q=80&w=500"],
            url: "#"
        }
    ]);

    

    // 검색 실행 함수 (이후 검색창 사용 시 동작)
    const handleSearch = (keyword) => {
        setSearchTerm(keyword);
        setIsLoading(true);
        
        // 검색 시 로딩 애니메이션을 보여주기 위한 시뮬레이션
        setTimeout(() => {
            const result = [{
                id: Date.now(),
                title: `'${keyword}' 키워드 실시간 데이터`,
                contents: `'${keyword}'에 대해 분석한 결과입니다. 관련 데이터가 충분히 수집되었습니다.`,
                company_name: "AI 분석기",
                img_urls: ["https://via.placeholder.com/300x180"],
                time: new Date().toISOString(),
                url: "#"
            }];
            setArticles(result);
            setIsLoading(false);
        }, 1500);
    };

    useEffect(() => {
        if (query) {
            handleSearch(query);
        }
    }, [query]);

    return (
        <div className="SearchResult_Main">
            <div className="Header_Container">
                <Header leftChild={<Logo/>} rightChild={<UserMenu/>} headerBottom="off" />
            </div>

            <div className="Content_Section">
                <div className="Searchbar_Wrapper">
                    <Searchbar maxWidth="800px" onSearch={handleSearch} />
                </div>

                {/* 데이터가 있을 때 항상 표시 */}
                <div className="SearchResult_AI">
                    <div className="Title_Wrapper">
                        <h3 className="AI_Title">
                            {isLoading ? `'${searchTerm}' 키워드 분석 중` : `'${searchTerm}' 분석 결과`}
                        </h3>
                        {isLoading && <div className="Loading_Spinner"></div>}
                    </div>

                    <div className="AI_Content_Wrapper">
                        <div className="AI_Left_Section">
                            <div className="Hot_Topic_Section">
                                <h4>핫 토픽!</h4>
                                <div className="Topic_Cards">
                                    {isLoading ? [1, 2].map(i => (
                                        <div key={i} className="Topic_Card skeleton"></div>
                                    )) : articles.slice(0, 2).map(item => (
                                        <div key={item.id} className="Topic_Card">
                                            <img src={item.img_urls[0]} alt="news" />
                                            <div className="Card_Text">{item.title}</div>
                                        </div>
                                    ))}
                                </div>
                            </div>

                            <div className="Analysis_Text_Section">
                                <h4>
                                    {isLoading ? (
                                        <TypewriterText text={`${searchTerm} 관련 기사를 탐색 중...`} delay={50} />
                                    ) : (
                                        `AI가 탐색한 ${articles.length}개의 기사 요약입니다.`
                                    )}
                                </h4>
                                <p className="Analysis_Contents">
                                    {isLoading ? "분석 중..." : articles[0]?.contents}
                                </p>
                            </div>

                            <div className="Related_News_Section">
                                <h4>관련기사</h4>
                                <ul className="News_List">
                                    {isLoading ? [1, 2, 3].map(i => (
                                        <li key={i} className="skeleton_line"></li>
                                    )) : articles.map(item => (
                                        <li key={item.id} onClick={() => window.open(item.url)}>
                                            <span>[{item.company_name}]</span> {item.title}
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        </div>

                        <div className="AI_Right_Section">
                            <div className={`Analysis_Big_Box ${isLoading ? 'loading' : ''}`}>
                                {!isLoading && (
                                    <div className="Result_Data_View" style={{padding:'20px'}}>
                                        <p>분석 통계 시각화</p>
                                        <div style={{marginTop:'20px', height:'200px', background:'#f9f9f9', borderRadius:'10px', display:'flex', alignItems:'center', justifyContent:'center', color:'#ccc'}}>
                                            차트/그래프 영역
                                        </div>
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
