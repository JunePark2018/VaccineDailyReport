import React, { useState, useEffect } from 'react';
import logo from './logo.svg';
import './App.css';
import axios from 'axios';

function App() {

  // 1. 데이터를 저장할 state 생성
  const [text, setText] = useState('Loading...'); 

  // 2. 컴포넌트가 마운트될 때 실행될 useEffect 작성
  useEffect(() => {
    // useEffect 내부에서 비동기 함수 정의
    const fetchData = async () => {
      try {
        const response = await axios.get('http://localhost:8000/hello');
        // 3. 받아온 데이터로 state 업데이트
        // axios는 결과 데이터를 data 프로퍼티에 담습니다.
        setText(response.data); 
      } catch (error) {
        console.error("Error fetching data:", error);
        setText("Error loading data");
      }
    };

    fetchData(); // 함수 실행
  }, []); // 의존성 배열을 빈 배열([])로 두어 한 번만 실행되게 함

  return (
    <div className="App">
      <header className="App-header">
        <img src={logo} className="App-logo" alt="logo" />
        <p>
          Edit <code>src/App.js</code> and save to reload.
        </p>
        <a
          className="App-link"
          href="https://reactjs.org"
          target="_blank"
          rel="noopener noreferrer"
        >
          {text}
        </a>
      </header>
    </div>
  );
}

export default App;
