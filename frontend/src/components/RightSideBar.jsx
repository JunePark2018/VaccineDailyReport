import React from 'react';


/**
오른쪽 사이드바 컴포넌트
isOpen      열림 상태 (문단 클릭시 사이드바 출력)  
isLoading   로딩 상태 (사이드바 열린상태에서 로딩)  
source:     기사 출처 (json 형태)  
onClose:    사이드바 닫는 함수  
width:      사이드바 너비(px). 문자열. 기본값: 448px  
*/
export default function RightSideBar({ 
    isOpen,
    isLoading,
    source,
    onClose,
    width = "448px"
}) {
    return (
        <aside 
            style={{ 
                position: "fixed", top: "229px", 
                right: isOpen ? 0 : `-${width}`, 
                transition: "right 0.4s cubic-bezier(0.25, 0.8, 0.25, 1)", 
                width: width, 
                minWidth: "400px", 
                height: "100vh",
                backgroundColor: "#ffffffff", 
                color: "black", 
                zIndex: 1000,
                display: "flex", 
                flexDirection: "column"
            }}
        >
            <div style={{ padding: "20px", display: "flex", justifyContent: "space-between", alignItems: "center"}}>
                <div/>
                <button onClick={onClose} style={{ background: 'none', border: 'none', color: 'grey', cursor: "pointer", fontSize: "24px" }}>✕</button>
            </div>
            <div style={{ flex: 1, padding: "10px", overflowY: "auto" }}>
                {isLoading ? (
                    <div style={{ textAlign: 'center', marginTop: '50px' }}>
                        <div className="loader"></div>
                    </div>
                ) : source ? (
                    // 데이터가 로드 된 후 보여지는 출처 정보
                    <div style={{ animation: 'fadeIn 0.5s'}}>
                        <h4 style={{ fontSize: '20px', marginBottom: '10px' }}>{source.title}</h4>
                        <p style={{ color: '#888', fontSize: '11px' }}>발행일: {source.date}</p>
                        <p style={{ lineHeight: '1.6', color: '#000000ff', fontSize: '14px'}}>
                            이 문단은 위 기사의 핵심 내용을 바탕으로 AI가 재구성하였습니다. 
                            원본 기사의 전체 맥락을 확인하시려면 아래 링크를 참조하세요.
                        </p>
                        <hr style={{ border: '0', borderTop: '1px solid #eee', margin: '20px 0' }} />
                        <a 
                            href={source.url} 
                            target="_blank" 
                            rel="noopener noreferrer"
                            style={{ 
                                display: 'inline-block', marginTop: '5px', 
                                fontSize: "14px"
                            }}
                        >
                            {source.url}
                        </a>
                    </div>
                ) : null}
            </div>
            {/*아래는 로딩 효과 및 페이드인 효과 애니메이션*/}
            <style>{`
                .loader { border: 2px solid #333; border-top: 2px solid #7bb4ffff; border-radius: 50%; width: 25px; height: 25px; animation: spin 1s linear infinite; margin: 0 auto; }
                @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
                @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
            `}</style>
        </aside>
    );
}