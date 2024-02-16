import React, { useEffect, useState } from 'react';
import './Home.css';  

const Home = () => {
  const [animationClass, setAnimationClass] = useState('');

  useEffect(() => {
    // 延迟一段时间后添加第一行字的浮出效果
    const timeout1 = setTimeout(() => {
      setAnimationClass('welcome-visible');
    }, 500);

    // 延迟一段时间后添加第二行字的浮出效果
    const timeout2 = setTimeout(() => {
      setAnimationClass('system-visible');
    }, 1500);

    // 清理定时器
    return () => {
      clearTimeout(timeout1);
      clearTimeout(timeout2);
    };
  }, []);

  return (
    <div className="home-container">
      <div className={`welcome ${animationClass}`}>欢迎使用</div>
      <div className={`system ${animationClass}`}>叉叉胖的市场风险计量系统</div>
    </div>
  );
};

export default Home;
