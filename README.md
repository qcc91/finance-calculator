# Finance Calculator

一个面向股票持仓管理和市场风险分析的全栈项目。系统支持从 Excel 导入持仓、查询和维护持仓记录、按多个层级分析持仓，并使用历史模拟法、参数法和蒙特卡洛法计算 VaR（Value at Risk）。

> 当前项目适合本地学习和功能演示。数据库地址、文件路径和 API 地址仍在代码中配置，部署到其他环境前需要调整。

## 主要功能

- Excel 持仓数据导入与模板下载
- 持仓记录查询、新增、修改和删除
- 按公司、部门和投资组合分析持仓
- 股票、投资组合、部门和公司层级的 VaR 计算
- 历史模拟法、参数法和蒙特卡洛法
- 基于 APScheduler 的定时持仓导入任务
- 表格及图表形式的分析结果展示

利率敏感性、权益敏感性、债券估值和衍生品估值页面目前是功能占位页。

## 技术栈

| 部分 | 技术 |
| --- | --- |
| 前端 | React 18、React Router、Axios、Chart.js、D3、Recharts |
| 后端 | Python、Flask、Flask-SQLAlchemy、Pandas、NumPy、SciPy |
| 数据库 | PostgreSQL |
| 行情数据 | BaoStock |
| 定时任务 | APScheduler |

## 项目结构

```text
finance-calculator/
├── finance-calculator-react/       # React 前端
│   ├── public/
│   └── src/
├── finance-calculator-flask/       # Flask API 与计算逻辑
│   ├── class_file/
│   │   ├── data_calculate.py       # VaR 计算
│   │   ├── data_fetch.py           # 行情数据获取
│   │   ├── data_process.py         # 持仓及结果处理
│   │   ├── data_validation.py      # 数据冲突检查
│   │   ├── db_connection.py        # 数据库连接
│   │   ├── table_models.py         # SQLAlchemy 模型
│   │   └── task_schedule.py        # 定时任务
│   └── finance-calculator.py       # Flask 启动入口和 API 路由
├── finance-calculator-postgresql/  # PostgreSQL 建表脚本
├── 下载模板(Download template)/   # Excel 导入模板
└── 存放数据文件夹(The data to be collected)/
```

## 本地运行

### 1. 环境要求

- Python 3.10 或更高版本
- Node.js 18 或更高版本
- PostgreSQL
- npm

### 2. 初始化 PostgreSQL

创建名为 `finance-calculator-pgdatabase` 的数据库，然后执行以下建表脚本：

- `finance-calculator-postgresql/history_holding_show.txt`
- `finance-calculator-postgresql/etl_task_define.txt`

在 `finance-calculator-flask/class_file/db_connection.py` 中，将 `SQLALCHEMY_DATABASE_URI` 修改为本机的 PostgreSQL 连接地址。不要把真实数据库密码提交到 Git 仓库。

如需启用定时导入，还需要在 `etl_task_define` 表中添加 `task_id` 为 `000001` 的任务记录，并检查 `task_schedule.py` 中 Excel 文件路径是否适用于本机。

### 3. 启动后端

在 PowerShell 中执行：

```powershell
cd finance-calculator-flask
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install Flask flask-cors Flask-SQLAlchemy psycopg2-binary pandas numpy scipy baostock APScheduler openpyxl
python finance-calculator.py
```

后端默认运行在 `http://localhost:3000`。

### 4. 启动前端

前端目前会向 `http://localhost:3000` 发送 API 请求，因此开发服务器需要使用其他端口。打开新的 PowerShell 窗口并执行：

```powershell
cd finance-calculator-react
npm install
$env:PORT=3001
npm start
```

浏览器访问 `http://localhost:3001`。

## 数据导入

导入文件支持 `.xls` 和 `.xlsx`。可从系统的数据导入页面下载模板，仓库中也提供了示例文件：

- `下载模板(Download template)/input_Data.xlsx`
- `导入数据样式(Import data)/input_Data.xlsx`

主要字段包括：

| 字段 | 含义 |
| --- | --- |
| `trade_date` | 交易日期 |
| `company` | 公司 |
| `department` | 部门 |
| `portfolio_code` | 投资组合代码 |
| `stock_symbol` | 股票代码（BaoStock 格式） |
| `amount` | 持仓数量 |
| `cost` | 持仓成本 |

股票名称、收盘价、行业和市值由后端获取或计算。

## 主要页面

| 路径 | 功能 |
| --- | --- |
| `/holdings/show` | 持仓展示 |
| `/holdings/analyse` | 持仓分析 |
| `/market/var` | VaR 风险计算 |
| `/data/collect/import` | Excel 数据导入 |
| `/data/collect/etl` | 定时任务设置 |
| `/data/edit` | 持仓数据维护 |

## 当前限制

- 项目尚未提供统一的 Python 依赖文件，后端依赖需要手动安装。
- 数据库连接、模板位置、定时导入文件位置和前端 API 地址仍为本地配置。
- 后端和定时调度器运行在同一进程，更适合单进程本地环境。
- 项目尚未加入用户认证、权限控制和自动化测试。
- 行情获取依赖 BaoStock 服务和可用的网络连接。

## 后续改进方向

- 使用环境变量管理数据库连接、文件路径和 API 地址
- 增加 `requirements.txt` 或 `pyproject.toml`
- 为数据库变更引入迁移工具
- 拆分 Flask 路由与业务服务
- 为导入、持仓维护和 VaR 计算增加测试
- 将定时任务与 Web 服务分离

## License

本仓库目前未声明开源许可证。如需公开分发或允许他人复用，请补充合适的 License。
