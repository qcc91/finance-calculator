import React, { useState, useEffect } from 'react';
import './HoldingsShow.css';
import Axios from 'axios';

const HoldingsShow = () => {
  const [tableData, setTableData] = useState([]);
  const [filters, setFilters] = useState({
    selectedStockCode: '',
    selectedStartDate: '',
    selectedEndDate: '',
    selectedDepartment: '',
    selectedPortfolioCode: '',
    selectedIndustry: ''
  });

  const fetchData = () => {
    Axios.get('http://localhost:3000/holdings/show', { params: filters })
      .then((response) => {
        if (Array.isArray(response.data)) {
          setTableData(response.data);
          console.log('Received data:', response.data);
        } else {
          console.error('Received data is not an array:', response.data);
        }
      })
      .catch((error) => {
        console.error('Error fetching stock_portfolio_last data:', error);
      });
  };

  const handleFilterChange = (event) => {
    const { name, value } = event.target;
    setFilters({
      ...filters,
      [name]: value
    });
  };

  const handleFilterSubmit = () => {
    fetchData();
  };

  return (
    <div>
      <h2>持仓展示</h2>
      <div className="filter-bar">
        <label htmlFor="startDate">开始日期：</label>
        <input type="date" id="startDate" name="selectedStartDate" value={filters.selectedStartDate} onChange={handleFilterChange} />
        <label htmlFor="endDate">结束日期：</label>
        <input type="date" id="endDate" name="selectedEndDate" value={filters.selectedEndDate} onChange={handleFilterChange} />
        <label htmlFor="department">部门：</label>
        <input type="text" id="department" name="selectedDepartment" value={filters.selectedDepartment} onChange={handleFilterChange} />
        <label htmlFor="portfolio_code">组合代码：</label>
        <input type="text" id="portfolio_code" name="selectedPortfolioCode" value={filters.selectedPortfolioCode} onChange={handleFilterChange} />
        <label htmlFor="selectedIndustry">行业：</label>
        <input type="text" id="selectedIndustry" name="selectedIndustry" value={filters.selectedIndustry} onChange={handleFilterChange} />
        <label htmlFor="selectedStockCode">证券代码：</label>
        <input type="text" id="selectedStockCode" name="selectedStockCode" value={filters.selectedStockCode} onChange={handleFilterChange} />
        <button onClick={handleFilterSubmit}>查询</button>
      </div>
      <section>
        <div className="table-container-holding">
          <h3>持仓数据</h3>
          <table>
            <thead>
              <tr>
                <th>业务日期</th>
                <th>公司名称</th>
                <th>部门</th>
                <th>组合代码</th>
                <th>证券代码</th>
                <th>证券名称</th>
                <th>数量</th>
                <th>成本</th>
                <th>市值</th>     
                <th>所属行业</th>
              </tr>
            </thead>
            <tbody>
              {tableData.map((holding) => (
                <tr key={holding.id}>
                  <td>{holding.trade_date}</td>
                  <td>{holding.company}</td>
                  <td>{holding.department}</td>
                  <td>{holding.portfolio_code}</td>
                  <td>{holding.stock_symbol}</td>
                  <td>{holding.stock_name}</td>
                  <td>{holding.amount}</td>
                  <td>{holding.cost}</td>
                  <td>{holding.market_value}</td>
                  <td>{holding.industry}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
};

export default HoldingsShow;
