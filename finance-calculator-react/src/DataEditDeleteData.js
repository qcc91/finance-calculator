import api from './api/client';

const DataEditDeleteData = async (rowData, onSuccess, onError) => {
  try {
    // 发送删除请求到后端
    await api.post('/data/edit/delete', rowData);
    onSuccess(); // 删除成功时的回调函数
  } catch (error) {
    onError(error); // 发生错误时的回调函数
  }
};

export default DataEditDeleteData;
