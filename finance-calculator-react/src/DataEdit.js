import React, { useState, useEffect, useRef } from 'react';
import './DataEdit.css';
import Axios from 'axios';
import DataEditAddData from './DataEditAddData'; 
import DataEditModifyData from './DataEditModifyData';
import DataEditDeleteData from './DataEditDeleteData';

const DataEdit = () => {
  const [tableData, setTableData] = useState([]);
  const [filters, setFilters] = useState({
    selectedStockCode: '',
    selectedStartDate: '',
    selectedEndDate: '',
    selectedDepartment: '',
    selectedPortfolioCode: '',
    selectedIndustry: ''
  });

  const [selectedRow, setSelectedRow] = useState(null);
  const [showAddModal, setShowAddModal] = useState(false);
  const [showModifyModal, setShowModifyModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [rowData, setRowData] = useState({}); 
  const tableRef = useRef(null); 

  const handleClickOutside = (event) => {
    if (
      tableRef.current &&
      !tableRef.current.contains(event.target) &&
      !event.target.classList.contains('modify-button') && // 排除点击修改按钮的情况
      !event.target.classList.contains('delete-button') 
    ) {
      setSelectedRow(null);
    }
  };

  useEffect(() => {
    document.addEventListener('mousedown', handleClickOutside); // 添加点击事件监听器

    return () => {
      document.removeEventListener('mousedown', handleClickOutside); // 移除点击事件监听器
    };
  }, []); 

  const fetchData = () => {
    Axios.get('http://localhost:3000/data/edit/show', { params: filters })
      .then((response) => {
        if (Array.isArray(response.data)) {
          setTableData(response.data);
        } else {
          console.error('Received data is not an array:', response.data);
        }
      })
      .catch((error) => {
        console.error('Error fetching data:', error);
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

  const handleRowClick = (index) => {
    setSelectedRow(index);
    setRowData(tableData[index]);
  };
  const handleAdd = () => {
    setShowAddModal(true);
  };

  const handleModify = () => {
    setShowModifyModal(true);
  };

  const handleDelete = async () => {
    if (selectedRow !== null) {
      const rowDataToDelete = tableData[selectedRow]; // 获取选中行的数据

      try {
        // 调用 DataEditDeleteData 组件，并将选中行的数据作为参数传递进去
        await DataEditDeleteData(
          rowDataToDelete,
          async () => {
            console.log('Data deleted successfully');
            setShowDeleteModal(true);
            // 删除成功后的逻辑，例如重新加载数据等
            await refreshData();
          },
          (error) => {
            console.error('Error deleting data:', error);
            // 处理删除失败的情况，例如显示错误信息等
          }
        );
      } catch (error) {
        console.error('Error deleting data:', error);
      }
    }
  };

  const handleDeleteSuccessConfirm = () => {
    setShowDeleteModal(false);
  };

  const refreshData = async () => {
    try {
      const response = await Axios.get('http://localhost:3000/data/edit/show',  { params: filters });
      if (Array.isArray(response.data)) {
        setTableData(response.data);
      } else {
        console.error('Received data is not an array:', response.data);
      }
    } catch (error) {
      console.error('Error refreshing data:', error);
    }
  };
 
  return (
    <div>
      <h2>数据编辑</h2>
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
          <h3>持仓数据
              <button className="add-button" onClick={handleAdd}>新增</button>
              <button className="modify-button" onClick={handleModify} disabled={selectedRow === null}>修改</button>
              <button className="delete-button" onClick={handleDelete} disabled={selectedRow === null}>删除</button>
          </h3>
          <table ref={tableRef}>
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
              {tableData.map((holding, index) => (
                <tr
                  key={holding.id}
                  className={selectedRow === index ? 'selected' : ''}
                  onClick={() => handleRowClick(index)}
                >
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
      {showModifyModal && rowData && (
    
          <DataEditModifyData
            showModifyModal={showModifyModal}
            setShowModifyModal={setShowModifyModal}
            refreshData={refreshData}
            rowData={rowData}
          />
      
)}
       {showAddModal && (
        <DataEditAddData
          showAddModal={showAddModal}
          setShowAddModal={setShowAddModal}
          refreshData={refreshData}
        />
      )}
      {showDeleteModal && (
        <div className="delete-modal">
          <p>删除成功！</p>
          <button onClick={handleDeleteSuccessConfirm}>确定</button>
        </div>
      )}
    </div>
  );
};

export default DataEdit;
