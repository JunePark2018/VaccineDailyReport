import React, { useState, useEffect } from 'react';

// =================================================
// 1. 설정 (Service Key는 본인 키로 변경 필요)
// =================================================
const SERVICE_KEY = "78f66d214af00f8d7583183ec0ed3d7ba6d672ce7efbe8377d23d6f7687a6a25";

// =================================================
// 2. 핵심 함수: 위경도(GPS) -> 기상청 격자(Grid) 변환
// 기상청은 Lambert Conformal Conic 투영법을 사용합니다.
// =================================================
// =================================================
// 2. 핵심 함수: 위경도(GPS) -> 기상청 격자(Grid) 변환
// =================================================
function mapToGrid(lat, lon) {
    const RE = 6371.00877; // 지구 반경(km)
    const GRID = 5.0;      // 격자 간격(km)
    const SLAT1 = 30.0;    // 투영 위도1(degree)
    const SLAT2 = 60.0;    // 투영 위도2(degree)
    const OLON = 126.0;    // 기준점 경도(degree)
    const OLAT = 38.0;     // 기준점 위도(degree)
    const XO = 43;         // 기준점 X좌표(GRID)
    const YO = 136;        // 기준점 Y좌표(GRID)

    const DEGRAD = Math.PI / 180.0;

    const re = RE / GRID;
    const slat1 = SLAT1 * DEGRAD;
    const slat2 = SLAT2 * DEGRAD;
    const olon = OLON * DEGRAD;
    const olat = OLAT * DEGRAD;

    let sn = Math.tan(Math.PI * 0.25 + slat2 * 0.5) / Math.tan(Math.PI * 0.25 + slat1 * 0.5);
    sn = Math.log(Math.cos(slat1) / Math.cos(slat2)) / Math.log(sn);

    let sf = Math.tan(Math.PI * 0.25 + slat1 * 0.5);
    sf = Math.pow(sf, sn) * Math.cos(slat1) / sn;

    let ro = Math.tan(Math.PI * 0.25 + olat * 0.5);
    ro = re * sf / Math.pow(ro, sn);

    let ra = Math.tan(Math.PI * 0.25 + lat * DEGRAD * 0.5);
    ra = re * sf / Math.pow(ra, sn);

    let theta = lon * DEGRAD - olon;
    if (theta > Math.PI) theta -= 2.0 * Math.PI;
    if (theta < -Math.PI) theta += 2.0 * Math.PI;
    theta *= sn;

    const x = Math.floor(ra * Math.sin(theta) + XO + 0.5);
    const y = Math.floor(ro - ra * Math.cos(theta) + YO + 0.5); // 공식 수정

    return { x, y };
}

const Weather = () => {
    const [weatherData, setWeatherData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [locationName, setLocationName] = useState("서울");

    // 날씨 데이터 가져오는 함수 (재사용 가능)
    const getWeather = async (lat, lon, name) => {
        setLoading(true);
        try {
            const { x: nx, y: ny } = mapToGrid(lat, lon);

            // 날짜/시간 계산
            // 안정적인 데이터 확보를 위해 무조건 1시간 전 데이터를 요청 (초단기실황 특성상 최신 데이터 딜레이 가능성 대비)
            const now = new Date();
            now.setHours(now.getHours() - 1);
            // if (now.getMinutes() < 40) ... 로직 제거하고 보수적으로 접근

            const year = now.getFullYear();
            const month = String(now.getMonth() + 1).padStart(2, '0');
            const day = String(now.getDate()).padStart(2, '0');
            const hour = String(now.getHours()).padStart(2, '0');

            const base_date = `${year}${month}${day}`;
            const base_time = `${hour}00`;

            // package.json의 "proxy": "https://apis.data.go.kr" 설정 사용
            const PROXY_URL = "/1360000/VilageFcstInfoService_2.0/getUltraSrtNcst";

            // dataType=XML로 설정 (브라우저 성공 사례와 동일하게 맞춤)
            const url = `${PROXY_URL}?serviceKey=${SERVICE_KEY}&pageNo=1&numOfRows=1000&dataType=XML&base_date=${base_date}&base_time=${base_time}&nx=${nx}&ny=${ny}`;

            console.log("Fetching weather (XML) from:", url);

            const response = await fetch(url);
            const textData = await response.text();
            console.log("Weather API Response (XML):", textData);

            // XML 파싱
            const parser = new DOMParser();
            const xmlDoc = parser.parseFromString(textData, "text/xml");

            // 결과 코드 확인
            const resultCodeNode = xmlDoc.getElementsByTagName("resultCode")[0];
            const resultMsgNode = xmlDoc.getElementsByTagName("resultMsg")[0];

            if (resultCodeNode && resultCodeNode.textContent !== '00') {
                console.error("API Error (XML):", resultCodeNode.textContent, resultMsgNode?.textContent);
                return;
            }

            const items = xmlDoc.getElementsByTagName("item");
            const parsedData = {};

            if (items.length === 0) {
                console.warn("No item found in XML.");
                // 데이터가 없을 경우 처리
            }

            for (let i = 0; i < items.length; i++) {
                const item = items[i];
                const category = item.getElementsByTagName("category")[0]?.textContent;
                const obsrValue = item.getElementsByTagName("obsrValue")[0]?.textContent;

                if (category === 'T1H') parsedData.temp = obsrValue;
                if (category === 'REH') parsedData.humidity = obsrValue;
                if (category === 'PTY') parsedData.rainType = obsrValue;
            }

            // 온도가 있으면 데이터 세팅
            if (parsedData.temp) {
                setWeatherData(parsedData);
                setLocationName(name);
            } else {
                console.warn("Parsed data is incomplete:", parsedData);
            }

        } catch (error) {
            console.error("날씨 정보를 불러오는 중 오류 발생:", error);
        } finally {
            setLoading(false);
        }
    };

    // 1. 초기 로딩: 서울(기본값)
    useEffect(() => {
        // 서울 영등포구 여의도동 좌표
        getWeather(37.52487, 126.92723, "서울");
    }, []);

    // 3. 역지오코딩 (위경도 -> 주소 변환)
    const getAddress = async (lat, lon) => {
        try {
            const response = await fetch(
                `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lon}&zoom=18&addressdetails=1`,
                { headers: { 'Accept-Language': 'ko-KR' } } // 한국어 요청
            );
            const data = await response.json();
            if (data && data.address) {
                const city = data.address.city || data.address.town || "";
                const borough = data.address.borough || data.address.district || "";
                const quarter = data.address.quarter || data.address.neighbourhood || "";

                // "서울시 서초구 서초4동" 형식 조합
                return `${city} ${borough} ${quarter}`.trim();
            }
        } catch (error) {
            console.error("주소 변환 실패:", error);
        }
        return "현재 위치";
    };

    // 2. 버튼 클릭 시: 현재 위치 가져오기 (User Gesture 필수)
    const handleCurrentLocation = () => {
        if (!navigator.geolocation) {
            alert("브라우저가 위치 정보를 지원하지 않습니다.");
            return;
        }

        navigator.geolocation.getCurrentPosition(
            async (position) => {
                const lat = position.coords.latitude;
                const lon = position.coords.longitude;

                // 주소 가져오기
                const addressName = await getAddress(lat, lon);
                getWeather(lat, lon, addressName);
            },
            (err) => {
                console.warn("위치 정보 접근 실패:", err);
                alert("위치 정보를 가져올 수 없습니다. 브라우저 설정에서 위치 권한을 확인해주세요.");
            },
            { timeout: 5000 }
        );
    };

    return (
        <span className="weather" style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
            {loading ? "날씨 로딩중..." :
                (weatherData ? `${locationName} ${weatherData.temp}℃ (습도 ${weatherData.humidity}%)` : "날씨 정보 없음")
            }
            <button
                onClick={handleCurrentLocation}
                style={{
                    background: 'none',
                    border: '1px solid #ccc',
                    borderRadius: '4px',
                    cursor: 'pointer',
                    fontSize: '10px',
                    padding: '2px 5px',
                    color: '#666',
                    marginLeft: '5px'
                }}
                title="현재 위치로 갱신"
            >
                📍 내 위치
            </button>
        </span>
    );
};

export default Weather;
