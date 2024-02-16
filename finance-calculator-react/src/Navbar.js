// Navbar.js
import React, { useState } from 'react';
import { NavLink, Link } from 'react-router-dom';
import './Navbar.css'; 

const Navbar = () => {
  const [hoveredItem, setHoveredItem] = useState(null);
  const [subMenu, setSubMenu] = useState(null);

  const handleMouseEnter = (item) => {
    setHoveredItem(item);
    setSubMenu(null);
  };

  const handleSubMenuEnter = (subItem) => {
    setSubMenu(subItem);
  };

  const handleSubMenuLeave = () => {
    setSubMenu(null);
  };

  const handleMouseLeave = () => {
    setHoveredItem(null);
    setSubMenu(null);
  };

  return (
    <nav>
      <ul>
        <li>
          <NavLink to="/" onMouseEnter={() => handleMouseEnter('首页')} onMouseLeave={handleMouseLeave} className={hoveredItem === '首页' ? 'active' : ''}>
            首页
          </NavLink>
        </li>
        <li onMouseEnter={() => handleMouseEnter('持仓分析')} onMouseLeave={handleMouseLeave}>
          <div>
            <span>
              持仓分析
            </span>
          </div>
          {hoveredItem === '持仓分析' && (
            <ul>
              <li><Link to="/holdings/show">持仓展示</Link></li>
              <li><Link to="/holdings/analyse">持仓统计</Link></li>
            </ul>
          )}
        </li>
        <li onMouseEnter={() => handleMouseEnter('市场风险')} onMouseLeave={handleMouseLeave}>
          <div>
            <span>
              市场风险
            </span>
          </div>
          {hoveredItem === '市场风险' && (
            <ul onMouseLeave={handleSubMenuLeave}>
              <li>
                <Link to="/market/VaR">VaR计量</Link>
              </li>
              <li onMouseEnter={() => handleSubMenuEnter('敏感性分析')}>
                <span>敏感性分析</span>
                {subMenu === '敏感性分析' && (
                  <ul>
                    <li><Link to="/market/sensitivity/interest">利率敏感性</Link></li>
                    <li><Link to="/market/sensitivity/equity">权益敏感性</Link></li>
                  </ul>
                )}
              </li>
              <li onMouseEnter={() => handleSubMenuEnter('金融产品估值')}>
                <span>金融产品估值</span>
                {subMenu === '金融产品估值' && (
                  <ul>
                    <li><Link to="/market/valuation/bond">债券估值</Link></li>
                    <li><Link to="/market/valuation/derivative">衍生品估值</Link></li>
                  </ul>
                )}
              </li>
            </ul>
          )}
        </li>
        <li onMouseEnter={() => handleMouseEnter('数据处理')} onMouseLeave={handleMouseLeave}>
          <div>
            <span>
              数据处理
            </span>
          </div>
          {hoveredItem === '数据处理'&& (
            <ul onMouseLeave={handleSubMenuLeave}>
              <li onMouseEnter={() => handleSubMenuEnter('数据采集')}>
                <span>数据采集</span>
                {subMenu === '数据采集'&& (
                  <ul>
                   <li><Link to="/data/collect/import">数据导入</Link></li>
                   <li><Link to="/data/collect/etl">ETL任务</Link></li>
                  </ul>
                )}
              </li>
              <li>
              <li><Link to="/data/edit">数据编辑</Link></li>
              </li>
            </ul>
          )}
        </li>
      </ul>
    </nav>
  );
};

export default Navbar;
