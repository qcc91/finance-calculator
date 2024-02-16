import React, { useState, useEffect } from 'react';
import Axios from 'axios';
import { Line, Bar } from 'react-chartjs-2';
import 'chart.js/auto';
import './MarketVar.css';

const MarketVar = () => {

  const [tradeDate, setTradeDate] = useState('');
  const [varMethod, setVarMethod] = useState('historical');
  const [confidenceLevel, setConfidenceLevel] = useState(95);
  const [historicalInterval, setHistoricalInterval] = useState(1);
  const [forecastDays, setForecastDays] = useState('1');
  const [pathCount, setPathCount] = useState('100');

  const [tierData, setTierData] = useState(null);
  const [result, setResult] = useState([]);

  const [lineChartData, setLineChartData] = useState(null);
  const [barChartData, setBarChartData] = useState(null); // 新增频率分布直方图数据

  const [calculating, setCalculating] = useState(false);
  const [calculateSuccess, setCalculateSuccess] = useState(false);

//***************************************辅助函数区域********************************************//
    // 辅助函数：计算频率分布
    const calculateFrequencyDistribution = (data) => {
      const numBins = 100;
      const binSize = (Math.max(...data) - Math.min(...data)) / numBins;
      const totalSamples = data.length;
      
      const bins = Array.from({ length: numBins }, (_, index) => {
        const start = Math.min(...data) + index * binSize;
        const end = start + binSize;
        const midPoint = (start + end) / 2; // 中点即为散点的值
        const range = `${start.toFixed(2)} - ${end.toFixed(2)}`;
        const frequency = data.filter((value) => value >= start && value <end).length;
        
        const normalizedFrequency = frequency / (binSize * totalSamples);
        return { range, midPoint, frequency:normalizedFrequency };
      });
      return bins;
    };

    // 辅助函数：计算正态分布
    const generateNormalDistributionData = (mean, stdDev, frequencyDistribution) => {
      const data = frequencyDistribution.map((bin) => {
        const y =
          (1 / (stdDev * Math.sqrt(2 * Math.PI))) *
          Math.exp(-(Math.pow((bin.midPoint - mean) / stdDev, 2) / 2));
        return { x: bin.midPoint, y };
      });
      return { absoluteDensityData: data };
    };

    // 辅助函数：计算第分位值
    const calculatePercentile = (data) => {
      const sortedData = data.slice().sort((a, b) => a - b);
      const index = Math.ceil((100 - confidenceLevel) / 100 * sortedData.length) - 1;
      return sortedData[index];
    };

    //辅助函数：将从后台获取的数据进行格式变换以适应前台的下钻表格
    const transformData = (rawData) => {
      const result = [];
    
      rawData.forEach((row, rowIndex) => {  
        const companyIndex = result.findIndex((c) => c.name === row.company);
    
        if (companyIndex === -1) {
          result.push({
            name: row.company,
            marketValue: row.company_sum,
            VaR: row.company_VaR,
            children: [
              {
                name: row.department,
                marketValue: row.department_sum,
                VaR: row.department_VaR,
                children: [
                  {
                    name: row.portfolio_code,
                    marketValue: row.portfolio_sum,
                    VaR: row.portfolio_VaR,
                    children: [
                      {
                        name: row.stock_symbol,
                        marketValue: row.market_value,
                        VaR: row.stock_VaR,
                      },
                    ],
                  },
                ],
              },
            ],
          });
        } else {
          const departmentIndex = result[companyIndex]?.children.findIndex(
            (d) => d.name === row.department
          );
    
          if (departmentIndex === -1) {
            result[companyIndex]?.children.push({
              name: row.department,
              marketValue: row.department_sum,
              VaR: row.department_VaR,
              children: [
                {
                  name: row.portfolio_code,
                  marketValue: row.portfolio_sum,
                  VaR: row.portfolio_VaR,
                  children: [
                    {
                      name: row.stock_symbol,
                      marketValue: row.market_value,
                      VaR: row.stock_VaR,
                    },
                  ],
                },
              ],
            });
          } else {
            const portfolioIndex = result[companyIndex]?.children[departmentIndex]?.children.findIndex(
              (p) => p.name === row.portfolio_code
            );
    
            if (portfolioIndex === -1) {
              result[companyIndex]?.children[departmentIndex]?.children.push({
                name: row.portfolio_code,
                marketValue: row.portfolio_sum,
                VaR: row.portfolio_VaR,
                children: [
                  {
                    name: row.stock_symbol,
                    marketValue: row.market_value,
                    VaR: row.stock_VaR,
                  },
                ],
              });
            } else {
              result[companyIndex]?.children[departmentIndex]?.children[portfolioIndex]?.children.push({
                name: row.stock_symbol,
                marketValue: row.market_value,
                VaR: row.stock_VaR,
              });
            }
          }
        }
      });
      return result;
    };

    //辅助函数：处理下钻层级结构
    const tier = (items, depth = 0) => {
      const headers =
        depth === 1
          ? ['部门名称', '部门市值', '部门VaR']
          : depth === 2
          ? ['组合代码', '组合市值', '组合VaR']
          : depth === 3
          ? ['证券代码', '证券市值', '证券VaR']
          : [];

      return (
        <React.Fragment>
          {headers.length > 0 && (
            <tr>{headers.map((header, index) => <th key={index}>{header}</th>)}</tr>
          )}
          {items.map((item, index) => (
            <React.Fragment key={index}>
              <tr onClick={() => handleItemClick(item)}>
                <td style={{ paddingLeft: `${depth * 20}px` }}>{item.name}</td>
                <td>{item.marketValue}</td>
                <td>{item.VaR}</td>
              </tr>
              {item.children && result.includes(item) && (
                <tr>
                  <td colSpan="3">
                    <table>
                      <thead>{tier(item.children, depth + 1)}</thead>
                    </table>
                  </td>
                </tr>
              )}
            </React.Fragment>
          ))}
        </React.Fragment>
      );
    };
    //辅助函数：用于绘制不同的蒙卡路线的颜色
    const getRandomColor = () => {
      const letters = '0123456789ABCDEF';
      let color = '#';
      for (let i = 0; i < 6; i++) {
        color += letters[Math.floor(Math.random() * 16)];
      }
      return color;
    };
//***************************************功能性函数区域********************************************//
//处理点击按钮
const handleItemClick = (item) => {
  if (item.children && item.children.length > 0) {
    if (result.includes(item)) {
      setResult(result.filter((i) => i !== item));
    } else {
      setResult([...result, item]);
    }
  }
};

const handleConfirm = () => {
  setCalculateSuccess(false);
};
//***************************************数据计算区域********************************************//
  //从后台获取数据
  const handleCalculateVar = () => {
    setCalculating(true);

    Axios.post('http://localhost:3000/market/var', {
      tradeDate,
      varMethod,
      confidenceLevel,
      historicalInterval,
      forecastDays,
      pathCount, 
    })
      .then((response) => {
        const hierarchicalData = transformData(response.data.table_data);
        setTierData(hierarchicalData);
        setResult([]);
        
      //---------------------------历史模拟法----------------------------// 
     if (varMethod === 'historical') {
         //计算必要参数
         const logReturns = response.data.chart_data.map((entry) => entry.log_returns_company_daily * Math.sqrt(forecastDays));
         const averageLogReturn = logReturns.reduce((sum, value) => sum + value, 0) / logReturns.length;
         const frequencyDistribution = calculateFrequencyDistribution(logReturns); 
         //折线图绘图数据处理
            const lineChartData = {
            labels: response.data.chart_data.map((entry) => entry.date),
            datasets: [
              {
                label: 'Log Returns',
                data: logReturns,
              },
              {
                label: 'Average',
                data: Array(logReturns.length).fill(averageLogReturn),
                borderColor: 'rgba(255, 0, 0, 0.5)', // Customize the color and opacity for average
                borderWidth: 1, // Adjust the width for average
                fill: false,
              },
            ],
          };
          const lineChartOptions = {
            plugins: {
              legend: {
                display: true,
              },
            },
            scales: {
              y: {
                beginAtZero: true,  // 如果您希望从0开始刻度
                ticks: {
                  callback: function(value, index, values) {
                    return (value * 100).toFixed(2) + '%';  // 将刻度值乘以100并添加百分号
                  }
                }
              }
            }
           };
           setLineChartData({ data: lineChartData, options: lineChartOptions });

          //直方图绘图数据处理
          const barChartData = {
            labels: frequencyDistribution.map((bin) => (bin.midPoint * 100).toFixed(2) + '%'),
            datasets: [
              {
                label: 'Frequency Distribution',
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 1,
                hoverBackgroundColor: 'rgba(75, 192, 192, 0.4)',
                hoverBorderColor: 'rgba(75, 192, 192, 1)',
                data: frequencyDistribution.map((bin) => bin.frequency),
              }
            ],
          };
          const barChartOptions = {
            
          };

      setBarChartData({ data: barChartData, options: barChartOptions });
    }

      //---------------------------参数法----------------------------// 
     if (varMethod === 'parametric') {
         //计算必要参数
         const logReturns = response.data.chart_data.map((entry) => entry.log_returns_company_daily * Math.sqrt(forecastDays));
         const averageLogReturn = logReturns.reduce((sum, value) => sum + value, 0) / logReturns.length;
         const mean = logReturns.reduce((sum, value) => sum + value, 0) / logReturns.length;
         const stdDev = Math.sqrt(logReturns.reduce((sum, value) => sum + Math.pow(value - mean, 2), 0) / (logReturns.length - 1));
         const frequencyDistribution = calculateFrequencyDistribution(logReturns);
         const normalDistributionData = generateNormalDistributionData(mean, stdDev, frequencyDistribution);
         //折线图绘图数据处理
            const lineChartData = {
              labels: response.data.chart_data.map((entry) => entry.date),
              datasets: [
                {
                  label: 'Log Returns',
                  data: logReturns,
                },
                {
                  label: 'Average',
                  data: Array(logReturns.length).fill(averageLogReturn),
                  borderColor: 'rgba(255, 0, 0, 0.5)', // Customize the color and opacity for average
                  borderWidth: 1, // Adjust the width for average
                  fill: false,
                },
              ],
            };

            const lineChartOptions = {
              plugins: {
                legend: {
                  display: true,
                },
              },
              scales: {
                y: {
                  beginAtZero: true,  // 如果您希望从0开始刻度
                  ticks: {
                    callback: function(value, index, values) {
                      return (value * 100).toFixed(2) + '%';  // 将刻度值乘以100并添加百分号
                    }
                  }
                }
              }
            };
            setLineChartData({ data: lineChartData, options: lineChartOptions });

            //直方图绘图数据处理
            const barChartData = {
              labels: frequencyDistribution.map((bin) => (bin.midPoint * 100).toFixed(2) + '%'),
              datasets: [
                {
                  label: 'Frequency Distribution',
                  backgroundColor: 'rgba(75, 192, 192, 0.2)',
                  borderColor: 'rgba(75, 192, 192, 1)',
                  borderWidth: 1,
                  hoverBackgroundColor: 'rgba(75, 192, 192, 0.4)',
                  hoverBorderColor: 'rgba(75, 192, 192, 1)',
                  data: frequencyDistribution.map((bin) => bin.frequency),
                },
                {
                  label: 'Normal Distribution',
                  data: normalDistributionData.absoluteDensityData.map((point) => point.y),
                  borderColor: 'rgba(255, 0, 0, 0.5)',
                  fill: false,
                }
              ],
            };
            const barChartOptions = {
              //
             };
  
        setBarChartData({ data: barChartData, options: barChartOptions });
    }

       //---------------------------蒙特卡洛模拟法----------------------------// 
    if (varMethod === 'monteCarlo') {
        //计算必要参数
        // 获取 chart_data 对象的所有属性
        const columns = Object.keys(response.data.chart_data);
        // 提取每个属性的最后一个值，形成数组
        const lastDayData = columns.map(column => {
          const columnData = response.data.chart_data[column];
          // 将对象的值转换为数组，然后获取最后一个元素
          const dataArray = Object.values(columnData);
          return dataArray.slice(-1)[0];
        });
        const frequencyDistribution = calculateFrequencyDistribution(lastDayData);
         //折线图绘图数据处理
         const lineChartData = {
          labels: Object.keys(response.data.chart_data[0]),
          datasets: response.data.chart_data.map((path, index) => ({
            label: `Path ${index + 1}`,
            data: Object.values(path),
            fill: false,
            borderColor: getRandomColor(),
            borderWidth: 2,
          })),
        };
        
        const lineChartOptions = {
          plugins: {
            legend: {
              display: false,
            },
          },
          scales: {
            y: {
              beginAtZero: true,  // 如果您希望从0开始刻度
              ticks: {
                callback: function(value, index, values) {
                  return (value * 100).toFixed(2) + '%';  // 将刻度值乘以100并添加百分号
                }
              }
            }
          }
        };
      setLineChartData({ data: lineChartData, options: lineChartOptions });
      
      
       const barChartData = {
        labels: frequencyDistribution.map((bin) => (bin.midPoint * 100).toFixed(2) + '%'),
        datasets: [
          {
            label: 'Frequency Distribution',
            backgroundColor: 'rgba(75, 192, 192, 0.2)',
            borderColor: 'rgba(75, 192, 192, 1)',
            borderWidth: 1,
            hoverBackgroundColor: 'rgba(75, 192, 192, 0.4)',
            hoverBorderColor: 'rgba(75, 192, 192, 1)',
            data: frequencyDistribution.map((bin) => bin.frequency),
          }
        ],
        
      };
      const barChartOptions = {
      
       };

     setBarChartData({ data: barChartData, options: barChartOptions });
     }

        //设置按钮状态
        setCalculating(false);
        setCalculateSuccess(true);
      })
      .catch((error) => {
        console.error('Error calculating VaR:', error);
        setCalculating(false);
      });
  };
  
  return (
    <div>
      <h2>VaR计量</h2>
      <div className="filter-bar">
        <label htmlFor="tradeDate">业务日期：</label>
        <input
          type="date"
          id="tradeDate"
          value={tradeDate}
          onChange={(e) => setTradeDate(e.target.value)}
        />

        <label htmlFor="varMethod">VaR方法：</label>
        <select
          id="varMethod"
          value={varMethod}
          onChange={(e) => setVarMethod(e.target.value)}
        >
          <option value="historical">历史模拟法</option>
          <option value="parametric">参数法</option>
          <option value="monteCarlo">蒙特卡洛模拟法</option>
        </select>

        <label htmlFor="confidenceLevel">置信度：</label>
        <select
          id="confidenceLevel"
          value={confidenceLevel}
          onChange={(e) => setConfidenceLevel(Number(e.target.value))}
        >
          <option value={95}>95%</option>
          <option value={97}>97%</option>
          <option value={99}>99%</option>
        </select>

        <label htmlFor="historicalInterval">历史区间：</label>
        <select
          id="historicalInterval"
          value={historicalInterval}
          onChange={(e) => setHistoricalInterval(Number(e.target.value))}
        >
          <option value={1}>1年</option>
          <option value={2}>2年</option>
          <option value={3}>3年</option>
        </select>

        <label htmlFor="forecastDays">预测天数：</label>
        <input
          type="number"
          id="forecastDays"
          value={forecastDays}
          onChange={(e) => setForecastDays(e.target.value)}
          placeholder="输入预测天数"
        />

        {varMethod === 'monteCarlo' && (
            <>
              <label htmlFor="pathCount">路径数：</label>
              <input
                type="number"
                id="pathCount"
                value={pathCount}
                onChange={(e) => setPathCount(e.target.value)}
                placeholder="输入路径数"
              />
            </>
          )}

        <button onClick={handleCalculateVar}>计算</button>
      </div>
      {calculating && (
        <div className="calculating-modal">
          <p>正在计算...</p>
        </div>
      )}
      {calculateSuccess && (
        <div className="calculate-success-modal">
          <p>计算成功</p>
          <button onClick={handleConfirm}>确定</button>
        </div>
      )}
      <section>
        <div className="table-container-var">
          <h3>计算结果</h3>
          <table>
            <thead>
              <tr>
                <th>公司名称</th>
                <th>公司市值</th>
                <th>公司VaR</th>
              </tr>
            </thead>
            <tbody>{tierData && tier(tierData)}</tbody>
          </table>
        </div>
        <div className="chart-container-var">
        <h3>图表展示</h3>
        {lineChartData && <Line data={lineChartData.data} options={lineChartData.options}/>}
          {barChartData && <Bar data={barChartData.data} options={barChartData.options}/>}
        </div>
      </section>
    </div>
  );
};

export default MarketVar;

