import React, { useState } from 'react';
import { Line, Pie } from 'react-chartjs-2';
import './HoldingsAnalyse.css';
import axios from 'axios';

const HoldingsAnalyse = () => {
  const [level, setLevel] = useState('company');
  const [department, setDepartment] = useState('');
  const [portfolioCode, setPortfolioCode] = useState('');
  const [tradeDate, setTradeDate] = useState('');
  const [tableData, setTableData] = useState([]);
  const [lineChartData, setLineChartData] = useState(null); 
  const [pieChart1Data, setPieChart1Data] = useState(null); 
  const [pieChart2Data, setPieChart2Data] = useState(null); 
  const [pieChart1Name, setPieChart1Name] = useState('XX'); 

  const handleLevelChange = (event) => {
    setLevel(event.target.value);
  };

  const handleDateChange = (event) => {
    setTradeDate(event.target.value);
  };

  const handleSubmit = () => {
    axios.post('http://localhost:3000/holdings/analyse', {
      tradeDate: tradeDate,
      analyseLevel: level,
      department: department,
      portfolioCode: portfolioCode
    })
    .then(response => {
      setTableData(response.data.table_data);
      setLineChartData({
        labels: response.data.chart1_data.map((entry) => entry.trade_date),
        datasets: [
          {
            label: 'Market_value',
            data: response.data.chart1_data.map((entry) => entry.market_value),
            fill: false,
            borderColor: 'rgb(75, 192, 192)',
            tension: 0.1,
          },
        ],
      });
      
      let label = ''; // 根据不同的层级选择设置饼图1的显示名称
      if (level === 'company') {
        label = '部门';
      } else if (level === 'department') {
        label = '组合';
      } else if (level === 'portfolio') {
        label = '个券';
      }
      setPieChart1Name(label);

      setPieChart1Data({
        labels: response.data.chart2_data.map((entry) => entry.organization),
        datasets: [
          {
            data: response.data.chart2_data.map((entry) => entry.market_value),
            backgroundColor: [
              'rgba(255, 99, 132, 0.5)',
              'rgba(54, 162, 235, 0.5)',
              'rgba(255, 206, 86, 0.5)',
              'rgba(75, 192, 192, 0.5)',
              'rgba(153, 102, 255, 0.5)',
              'rgba(255, 159, 64, 0.5)',
            ],
            hoverBackgroundColor: [
              'rgba(255, 99, 132, 1)',
              'rgba(54, 162, 235, 1)',
              'rgba(255, 206, 86, 1)',
              'rgba(75, 192, 192, 1)',
              'rgba(153, 102, 255, 1)',
              'rgba(255, 159, 64, 1)',
            ],
          },
        ],
      });

      setPieChart2Data({
        labels: response.data.chart3_data.map((entry) => entry.industry),
        datasets: [
          {
            data: response.data.chart3_data.map((entry) => entry.market_value),
            backgroundColor: [
              'rgba(255, 99, 132, 0.5)',
              'rgba(54, 162, 235, 0.5)',
              'rgba(255, 206, 86, 0.5)',
              'rgba(75, 192, 192, 0.5)',
              'rgba(153, 102, 255, 0.5)',
              'rgba(255, 159, 64, 0.5)',
            ],
            hoverBackgroundColor: [
              'rgba(255, 99, 132, 1)',
              'rgba(54, 162, 235, 1)',
              'rgba(255, 206, 86, 1)',
              'rgba(75, 192, 192, 1)',
              'rgba(153, 102, 255, 1)',
              'rgba(255, 159, 64, 1)',
            ],
          },
        ],
      });
    })
    .catch(error => {
      console.error('Error:', error);
    });
  };

  const pieChartOptions = {
    plugins: {
      legend: {
        position: 'top',
      },
      tooltip: {
        callbacks: {
          label: function(context) {
            const label = context.label || '';
            if (label) {
              const index = context.dataIndex;
              const value = context.dataset.data[index];
              return `${label}: ${value}`;
            }
            return '';
          }
        }
      }
    }
  };

  return (
    <div>
      <h2>持仓统计</h2>
      <div className="filter-bar">
        <label htmlFor="tradeDate">业务日期:</label>
        <input type="date" id="tradeDate" value={tradeDate} onChange={handleDateChange} />

        <label htmlFor="level">层级:</label>
        <select id="level" value={level} onChange={handleLevelChange}>
          <option value="company">公司</option>
          <option value="department">部门</option>
          <option value="portfolio">组合</option>
        </select>

        {level === 'department' && (
          <div>
            <label htmlFor="department">部门名称:</label>
            <input type="text" id="department" value={department} onChange={(e) => setDepartment(e.target.value)} />
          </div>
        )}
        {level === 'portfolio' && (
          <div>
            <label htmlFor="department">部门名称:</label>
            <input type="text" id="department" value={department} onChange={(e) => setDepartment(e.target.value)} />
            <label htmlFor="portfolioCode">组合代码:</label>
            <input type="text" id="portfolioCode" value={portfolioCode} onChange={(e) => setPortfolioCode(e.target.value)} />
          </div>
        )}
        <button onClick={handleSubmit}>提交</button>
      </div>

<div className="table-container">
  <h3>前十大持仓股票</h3>
  <table>
    <thead>
      <tr>
        <th>股票代码</th>
        <th>股票名称</th>
        <th>市值</th>
      </tr>
    </thead>
    <tbody>
      {tableData.map((row, index) => (
        <tr key={index}>
          <td>{row.stock_symbol}</td>
          <td>{row.stock_name}</td>
          <td>{row.market_value}</td>
        </tr>
      ))}
    </tbody>
  </table>
</div>
      <div className="line-chart1-container">
        <h3>当年历史持仓</h3>
        {lineChartData && <Line data={lineChartData} />}
      </div>
      <div className="pie-chart1-container">
        <h3>{pieChart1Name}集中度</h3>
        {pieChart1Data && <Pie data={pieChart1Data} options={pieChartOptions}/>}
      </div>
      <div className="pie-chart2-container">
        <h3>行业集中度</h3>
        {pieChart2Data && <Pie data={pieChart2Data} options={pieChartOptions}/>}
      </div>
    </div>

  );
};

export default HoldingsAnalyse;
